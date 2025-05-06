import os
import re
from pathlib import Path

# Correctly identify the project root
project_root = Path(__file__).resolve().parent.parent  # Go up one more level
models_dir = os.path.join(project_root, "data", "models")
optimized_dir = os.path.join(models_dir, "optimized")

# Create directories if they don't exist
os.makedirs(models_dir, exist_ok=True)
os.makedirs(optimized_dir, exist_ok=True)

# Function to extract episode number from filename
def get_episode_number(filename):
    match = re.search(r'episode_(\d+)', filename)
    if match:
        return int(match.group(1))
    return 0

# Check regular models
wired_models = []
wireless_models = []
if os.path.exists(models_dir):
    wired_models = [f for f in os.listdir(models_dir) if f.startswith('wired_rl_episode_')]
    wireless_models = [f for f in os.listdir(models_dir) if f.startswith('wireless_rl_episode_')]

# Check optimized models if directory exists
wired_optimized = []
wireless_optimized = []
if os.path.exists(optimized_dir):
    wired_optimized = [f for f in os.listdir(optimized_dir) if f.startswith('wired_rl_optimized_episode_')]
    wireless_optimized = [f for f in os.listdir(optimized_dir) if f.startswith('wireless_rl_optimized_episode_')]

# Find highest episode numbers
wired_max = max([get_episode_number(f) for f in wired_models]) if wired_models else 0
wireless_max = max([get_episode_number(f) for f in wireless_models]) if wireless_models else 0
wired_opt_max = max([get_episode_number(f) for f in wired_optimized]) if wired_optimized else 0
wireless_opt_max = max([get_episode_number(f) for f in wireless_optimized]) if wireless_optimized else 0

print(f"Wired RL: {wired_max} episodes (regular), {wired_opt_max} episodes (optimized)")
print(f"Wireless RL: {wireless_max} episodes (regular), {wireless_opt_max} episodes (optimized)")

print("\nFound model files:")
if wired_models:
    print(f"Wired RL models: {wired_models}")
if wireless_models:
    print(f"Wireless RL models: {wireless_models}")
if wired_optimized:
    print(f"Wired RL optimized models: {wired_optimized}")
if wireless_optimized:
    print(f"Wireless RL optimized models: {wireless_optimized}")