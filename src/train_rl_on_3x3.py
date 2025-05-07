import os
import sys
import argparse
import numpy as np
from pathlib import Path
import time
import traci
import glob
import re
import shutil

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.utils.sumo_integration import SumoSimulation
from src.ai.reinforcement_learning.q_learning_controller import QLearningController
from src.ai.reinforcement_learning.wired_rl_controller import WiredRLController
from src.ai.reinforcement_learning.wireless_rl_controller import WirelessRLController
from src.utils.config_utils import find_latest_model

def migrate_models():
    """Migrate models from optimised directory to main models directory"""
    optimised_dir = os.path.join(project_root, "data", "models", "optimised")
    models_dir = os.path.join(project_root, "data", "models")
    
    if not os.path.exists(optimised_dir):
        print("No optimised directory found, nothing to migrate")
        return
    
    # Find all model files in the optimised directory
    model_files = glob.glob(os.path.join(optimised_dir, "*.pkl"))
    
    if not model_files:
        print("No model files found in optimised directory")
        return
    
    print(f"Found {len(model_files)} model files to migrate")
    
    # Migrate each file
    for model_file in model_files:
        filename = os.path.basename(model_file)
        
        # Rename files to remove "optimised_" from the name
        new_filename = filename.replace("_optimised_", "_")
        new_path = os.path.join(models_dir, new_filename)
        
        # Copy the file
        shutil.copy2(model_file, new_path)
        print(f"Migrated: {filename} -> {new_filename}")
    
    print("Migration complete")

def collect_traffic_state(tl_ids):
    """Optimised traffic state collection"""
    traffic_state = {}
    
    # Cache lane direction mapping for faster lookup
    lane_directions = {}
    
    for tl_id in tl_ids:
        # Get incoming lanes for this traffic light
        incoming_lanes = []
        for connection in traci.trafficlight.getControlledLinks(tl_id):
            if connection and connection[0]:  # Check if connection exists
                incoming_lane = connection[0][0]
                if incoming_lane not in incoming_lanes:
                    incoming_lanes.append(incoming_lane)
        
        # Initialise direction counts
        north_count = south_count = east_count = west_count = 0
        north_wait = south_wait = east_wait = west_wait = 0
        north_queue = south_queue = east_queue = west_queue = 0
        
        for lane in incoming_lanes:
            # Determine direction based on lane ID - use cached value if available
            if lane in lane_directions:
                direction = lane_directions[lane]
            else:
                direction = "unknown"
                # For vertical lanes
                if any(pattern in lane for pattern in ["A0A1", "B0B1", "C0C1", "A1A2", "B1B2", "C1C2"]):
                    direction = "north"
                elif any(pattern in lane for pattern in ["A1A0", "B1B0", "C1C0", "A2A1", "B2B1", "C2C1"]):
                    direction = "south"
                # For horizontal lanes
                elif any(pattern in lane for pattern in ["A0B0", "B0C0", "A1B1", "B1C1", "A2B2", "B2C2"]):
                    direction = "east"
                elif any(pattern in lane for pattern in ["B0A0", "C0B0", "B1A1", "C1B1", "B2A2", "C2B2"]):
                    direction = "west"
                lane_directions[lane] = direction
            
            # Get lane data in optimised way (batch query)
            vehicle_count = traci.lane.getLastStepVehicleNumber(lane)
            vehicles = traci.lane.getLastStepVehicleIDs(lane)
            
            if vehicles:
                # Use numpy for more efficient calculations
                waiting_times = np.array([traci.vehicle.getWaitingTime(v) for v in vehicles])
                waiting_time = np.sum(waiting_times)
            else:
                waiting_time = 0
                
            queue_length = traci.lane.getLastStepHaltingNumber(lane)
            
            # Aggregate data by direction
            if direction == "north":
                north_count += vehicle_count
                north_wait += waiting_time
                north_queue += queue_length
            elif direction == "south":
                south_count += vehicle_count
                south_wait += waiting_time
                south_queue += queue_length
            elif direction == "east":
                east_count += vehicle_count
                east_wait += waiting_time
                east_queue += queue_length
            elif direction == "west":
                west_count += vehicle_count
                west_wait += waiting_time
                west_queue += queue_length
        
        # Calculate average waiting times efficiently
        north_wait_avg = north_wait / max(1, north_count)
        south_wait_avg = south_wait / max(1, south_count)
        east_wait_avg = east_wait / max(1, east_count)
        west_wait_avg = west_wait / max(1, west_count)
        
        # Store traffic state for this junction
        traffic_state[tl_id] = {
            'north_count': north_count,
            'south_count': south_count,
            'east_count': east_count,
            'west_count': west_count,
            'north_wait': north_wait_avg,
            'south_wait': south_wait_avg,
            'east_wait': east_wait_avg,
            'west_wait': west_wait_avg,
            'north_queue': north_queue,
            'south_queue': south_queue,
            'east_queue': east_queue,
            'west_queue': west_queue
        }
    
    return traffic_state

def get_highest_episode_number(controller_type):
    """
    Find the highest episode number for the specified controller type.

    """
    # Convert controller type to filename format
    model_prefix = controller_type.replace(' ', '_').lower()
    
    # Define the models directory
    models_dir = os.path.join(project_root, "data", "models")
    
    if not os.path.exists(models_dir):
        print(f"Models directory not found: {models_dir}")
        return 0
    
    # find all model files for this controller type
    model_pattern = os.path.join(models_dir, f"{model_prefix}_episode_*.pkl")
    model_files = glob.glob(model_pattern)
    
    if not model_files:
        print(f"No existing models found for {controller_type}")
        return 0
    
    # extract episode numbers and find the highest one
    episode_numbers = []
    for model_file in model_files:
        match = re.search(r'_episode_(\d+)\.pkl$', model_file)
        if match:
            episode_numbers.append(int(match.group(1)))
    
    if not episode_numbers:
        print(f"Could not parse episode numbers from model filenames")
        return 0
    
    highest_episode = max(episode_numbers)
    print(f"Highest existing episode for {controller_type}: {highest_episode}")
    
    return highest_episode

def train_episode(config_path, controller_type, episode_num, exploration_rate, 
                  steps_per_episode, learning_rate, discount_factor, model_path=None):
    """Train a single episode"""
    # Initialise simulation
    sim = SumoSimulation(config_path, gui=False)
    sim.start()
    
    # Get traffic light IDs
    tl_ids = traci.trafficlight.getIDList()
    
    if not tl_ids:
        print("No traffic lights found!")
        sim.close()
        return None, None
    
    # create controller with improved parameters
    if controller_type == "Wired RL":
        controller = WiredRLController(
            tl_ids,
            learning_rate=learning_rate,
            discount_factor=discount_factor,
            exploration_rate=exploration_rate,
            network_latency=0.005,
            state_bins=8,
            model_path=model_path
        )
    elif controller_type == "Wireless RL":
        controller = WirelessRLController(
            tl_ids,
            learning_rate=learning_rate,
            discount_factor=discount_factor,
            exploration_rate=exploration_rate,
            base_latency=0.002,
            computation_factor=0.005,
            packet_loss_prob=0.0005,
            state_bins=8,
            model_path=model_path
        )
    else:
        print(f"Invalid controller type: {controller_type}")
        sim.close()
        return None, None
    
    # episode statistics
    episode_rewards = []
    episode_waiting_times = []
    episode_speeds = []
    
    # Run the episode
    for step in range(steps_per_episode):
        # collect traffic state
        traffic_state = collect_traffic_state(tl_ids)
        
        # update controller with traffic state
        controller.update_traffic_state(traffic_state)
        
        # get current simulation time
        current_time = traci.simulation.getTime()
        
        # get phase decisions from controller for each junction
        for tl_id in tl_ids:
            phase = controller.get_phase_for_junction(tl_id, current_time)
            
            # Set traffic light phase in SUMO
            try:
                # Get the current state length
                current_state = traci.trafficlight.getRedYellowGreenState(tl_id)
                
                # Ensure phase length matches traffic light state length
                if len(phase) != len(current_state):
                    # Adjust phase length to match expected length
                    if len(phase) < len(current_state):
                        # Repeat the pattern to match length
                        phase = phase * (len(current_state) // len(phase)) + phase[:len(current_state) % len(phase)]
                    else:
                        # Truncate to expected length
                        phase = phase[:len(current_state)]
                
                traci.trafficlight.setRedYellowGreenState(tl_id, phase)
            except Exception as e:
                print(f"Error setting traffic light state for {tl_id}: {e}")
        
        # collect episode stats
        if hasattr(controller, 'reward_history') and controller.reward_history:
            episode_rewards.append(controller.reward_history[-1])
        
        # collect metrics
        vehicles = traci.vehicle.getIDList()
        if vehicles:
            avg_wait = sum(traci.vehicle.getWaitingTime(v) for v in vehicles) / len(vehicles)
            avg_speed = sum(traci.vehicle.getSpeed(v) for v in vehicles) / len(vehicles)
            episode_waiting_times.append(avg_wait)
            episode_speeds.append(avg_speed)
        
        # step the simulation
        sim.step()
        
        # progress indicator for long episodes
        if step % 100 == 0 and step > 0:
            print(f"  Episode {episode_num} - Step {step}/{steps_per_episode}")
    
    # episode statistics
    stats = {
        "episode": episode_num,
        "rewards": sum(episode_rewards) / len(episode_rewards) if episode_rewards else 0,
        "waiting_times": sum(episode_waiting_times) / len(episode_waiting_times) if episode_waiting_times else 0,
        "speeds": sum(episode_speeds) / len(episode_speeds) if episode_speeds else 0,
        "throughput": traci.simulation.getArrivedNumber() if hasattr(traci.simulation, 'getArrivedNumber') else 0,
        "q_table_size": len(controller.q_tables.get(tl_ids[0], {})) if hasattr(controller, 'q_tables') else 0
    }
    
    # save the model for this episode
    if hasattr(controller, 'save_q_table'):
        model_filename = os.path.join(
            project_root, "data", "models", 
            f"{controller_type.replace(' ', '_').lower()}_episode_{episode_num}.pkl")
        controller.save_q_table(model_filename)
    
    # close the simulation
    sim.close()
    
    return controller, stats

def train_rl_controller(controller_type, episodes=40, steps_per_episode=400, 
                        learning_rate=0.3, discount_factor=0.8, exploration_rate=0.9,
                        exploration_decay=0.8, continue_training=True):
    """
    Train an RL controller with optimised parameters.
    
    Args:
        controller_type : Type of RL controller ('Wired RL' or 'Wireless RL')
        episodes : Number of training episodes
        steps_per_episode : Number of steps per episode
        learning_rate : Learning rate for Q-learning
        discount_factor : Discount factor for future rewards
        exploration_rate : Initial exploration rate
        exploration_decay : Rate at which exploration decreases
        continue_training : Whether to continue from previous training
        
    """
    # Path to the grid configuration
    config_path = os.path.join(project_root, "config", "maps", "grid_network_3x3.sumocfg")
    
    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}")
        return
    
    # Create output directory for models
    models_dir = os.path.join(project_root, "data", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    # Find the latest model and the highest episode number to continue training
    start_episode = 0
    latest_model_path = None
    
    if continue_training:
        # Find the highest episode number
        start_episode = get_highest_episode_number(controller_type)
        
        # If we found previous episodes, get the latest model
        if start_episode > 0:
            latest_model_path = find_latest_model(controller_type)
            print(f"Continuing training from episode {start_episode} using model: {latest_model_path}")
            
            # Adjust exploration rate based on progress
            adjusted_exploration_rate = exploration_rate * (exploration_decay ** start_episode)
            exploration_rate = max(0.05, adjusted_exploration_rate)
            print(f"Adjusted exploration rate to {exploration_rate:.4f} based on previous training")
        else:
            print("No previous training found. Starting from scratch.")
    
    # calculate total episodes to train
    total_episodes = start_episode + episodes
    
    # training statistics
    stats = {
        "start_episode": start_episode,
        "total_episodes": total_episodes,
        "steps_per_episode": steps_per_episode,
        "learning_rate": learning_rate,
        "discount_factor": discount_factor,
        "initial_exploration_rate": exploration_rate,
        "exploration_decay": exploration_decay,
        "exploration_rates": [],
        "rewards": [],
        "waiting_times": [],
        "speeds": [],
        "throughputs": [],
        "q_table_sizes": []
    }
    
    print(f"Starting training for {episodes} episodes ({start_episode+1} to {total_episodes})")
    
    # main training loop
    for episode in range(start_episode, total_episodes):
        # Calculate exploration rate for this episode
        current_exploration = exploration_rate * (exploration_decay ** (episode - start_episode))
        
        print(f"\nTraining episode {episode+1}/{total_episodes} - Exploration rate: {current_exploration:.4f}")
        
        # train a single episode
        controller, episode_stats = train_episode(
            config_path, 
            controller_type, 
            episode + 1,  # save episodes starting from 1, not 0
            current_exploration, 
            steps_per_episode, 
            learning_rate, 
            discount_factor, 
            latest_model_path
        )
        
        if controller is None or episode_stats is None:
            print(f"Error training episode {episode+1}. Skipping.")
            continue
        
        # update latest model path for the next episode
        latest_model_path = os.path.join(
            models_dir, 
            f"{controller_type.replace(' ', '_').lower()}_episode_{episode+1}.pkl"
        )
        
        # update stats
        stats["exploration_rates"].append(current_exploration)
        stats["rewards"].append(episode_stats["rewards"])
        stats["waiting_times"].append(episode_stats["waiting_times"])
        stats["speeds"].append(episode_stats["speeds"])
        stats["throughputs"].append(episode_stats["throughput"])
        stats["q_table_sizes"].append(episode_stats["q_table_size"])
        
        # Print progress
        print(f"Episode {episode+1} completed: Reward={episode_stats['rewards']:.2f}, "
              f"Wait={episode_stats['waiting_times']:.2f}s, Speed={episode_stats['speeds']:.2f}m/s")
    
    # save final model in a special file
    if controller is not None and hasattr(controller, 'save_q_table'):
        final_model_path = os.path.join(models_dir, f"{controller_type.replace(' ', '_').lower()}_final.pkl")
        controller.save_q_table(final_model_path)
        print(f"Final model saved to {final_model_path}")
    
    # save training statistics
    import json
    stats_filename = os.path.join(models_dir, f"{controller_type.replace(' ', '_').lower()}_training_stats.json")
    
    # Load existing stats if they exist and update
    if os.path.exists(stats_filename):
        try:
            with open(stats_filename, 'r') as f:
                existing_stats = json.load(f)
            
            # Merge the stats
            if isinstance(existing_stats, dict):
                for key in ["exploration_rates", "rewards", "waiting_times", "speeds", "throughputs", "q_table_sizes"]:
                    if key in existing_stats and key in stats:
                        existing_stats[key].extend(stats[key])
                        stats[key] = existing_stats[key]
                
                # Update other fields
                stats["total_episodes"] = total_episodes
                stats["start_episode"] = existing_stats.get("start_episode", 0)
        except Exception as e:
            print(f"Error merging existing stats: {e}")
    
    with open(stats_filename, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Training completed. Statistics saved to {stats_filename}")
    
    # Create learning curves
    import matplotlib.pyplot as plt
    
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot rewards
    if stats["rewards"]:
        x_values = range(stats["start_episode"] + 1, stats["start_episode"] + len(stats["rewards"]) + 1)
        axs[0, 0].plot(x_values, stats["rewards"])
        axs[0, 0].set_title('Average Reward per Episode')
        axs[0, 0].set_xlabel('Episode')
        axs[0, 0].set_ylabel('Average Reward')
        axs[0, 0].grid(True)
    
    # Plot waiting times
    if stats["waiting_times"]:
        x_values = range(stats["start_episode"] + 1, stats["start_episode"] + len(stats["waiting_times"]) + 1)
        axs[0, 1].plot(x_values, stats["waiting_times"])
        axs[0, 1].set_title('Average Waiting Time per Episode')
        axs[0, 1].set_xlabel('Episode')
        axs[0, 1].set_ylabel('Waiting Time (s)')
        axs[0, 1].grid(True)
    
    # Plot speeds
    if stats["speeds"]:
        x_values = range(stats["start_episode"] + 1, stats["start_episode"] + len(stats["speeds"]) + 1)
        axs[1, 0].plot(x_values, stats["speeds"])
        axs[1, 0].set_title('Average Speed per Episode')
        axs[1, 0].set_xlabel('Episode')
        axs[1, 0].set_ylabel('Speed (m/s)')
        axs[1, 0].grid(True)
    
    # Plot exploration rate
    if stats["exploration_rates"]:
        x_values = range(stats["start_episode"] + 1, stats["start_episode"] + len(stats["exploration_rates"]) + 1)
        axs[1, 1].plot(x_values, stats["exploration_rates"])
        axs[1, 1].set_title('Exploration Rate')
        axs[1, 1].set_xlabel('Episode')
        axs[1, 1].set_ylabel('Exploration Rate')
        axs[1, 1].grid(True)
    
    plt.tight_layout()
    plot_filename = os.path.join(models_dir, f"{controller_type.replace(' ', '_').lower()}_learning_curves.png")
    plt.savefig(plot_filename)
    plt.close()
    
    print(f"Learning curves saved to {plot_filename}")
    
    return stats

def main():
    """Train an RL controller with continuing from previous training."""
    parser = argparse.ArgumentParser(description='Train RL controller with optimised parameters')
    parser.add_argument('--controller', type=str, default="Wired RL",
                        choices=["Wired RL", "Wireless RL"],
                        help='Type of RL controller to train')
    parser.add_argument('--episodes', type=int, default=40,
                        help='Number of additional training episodes')
    parser.add_argument('--steps', type=int, default=400,
                        help='Number of steps per episode')
    parser.add_argument('--lr', type=float, default=0.3,
                        help='Learning rate')
    parser.add_argument('--discount', type=float, default=0.8,
                        help='Discount factor')
    parser.add_argument('--exploration', type=float, default=0.9,
                        help='Initial exploration rate (will be adjusted based on previous training)')
    parser.add_argument('--decay', type=float, default=0.8,
                        help='Exploration decay rate')
    parser.add_argument('--no-continue', action='store_true',
                        help='Do not continue from previous training (start fresh)')
    parser.add_argument('--migrate', action='store_true',
                        help='Migrate models from optimised directory to main directory')
    args = parser.parse_args()
    
    # migrate models if requested
    if args.migrate:
        migrate_models()
    
    continue_training = not args.no_continue
    
    if continue_training:
        print(f"Training {args.controller} for {args.episodes} additional episodes (continuing from previous training)")
    else:
        print(f"Training {args.controller} for {args.episodes} episodes (starting fresh)")
        
    print(f"Parameters: lr={args.lr}, discount={args.discount}, exploration={args.exploration}, decay={args.decay}")
    
    train_rl_controller(
        args.controller,
        episodes=args.episodes,
        steps_per_episode=args.steps,
        learning_rate=args.lr,
        discount_factor=args.discount,
        exploration_rate=args.exploration,
        exploration_decay=args.decay,
        continue_training=continue_training
    )

if __name__ == "__main__":
    main()