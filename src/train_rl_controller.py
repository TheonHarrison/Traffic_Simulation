import os
import sys
import time
import argparse
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import pickle
import json
import glob
import re

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import traci
from src.utils.sumo_integration import SumoSimulation
from src.ai.reinforcement_learning.wired_rl_controller import WiredRLController
from src.ai.reinforcement_learning.wireless_rl_controller import WirelessRLController

def find_latest_model(controller_type):
    """
    Find the latest trained model for the specified controller type.
    
    Args:
        controller_type (str): Type of controller ("Wired RL" or "Wireless RL")
    
    Returns:
        str or None: Path to the latest model file, or None if no model is found
    """
    # Convert controller type to filename format
    model_prefix = controller_type.replace(' ', '_').lower()
    
    # Define the models directory
    models_dir = os.path.join(project_root, "data", "models")
    
    if not os.path.exists(models_dir):
        print(f"Models directory not found: {models_dir}")
        return None
    
    # Find all model files for this controller type
    model_pattern = os.path.join(models_dir, f"{model_prefix}_episode_*.pkl")
    model_files = glob.glob(model_pattern)
    
    if not model_files:
        print(f"No existing models found for {controller_type}")
        return None
    
    # Extract episode numbers and find the highest one
    episode_numbers = []
    for model_file in model_files:
        match = re.search(r'_episode_(\d+)\.pkl$', model_file)
        if match:
            episode_numbers.append((int(match.group(1)), model_file))
    
    if not episode_numbers:
        print(f"Could not parse episode numbers from model filenames")
        return None
    
    # Sort by episode number and get the latest
    episode_numbers.sort(key=lambda x: x[0], reverse=True)
    latest_episode, latest_model = episode_numbers[0]
    
    print(f"Found latest model for {controller_type}: Episode {latest_episode}")
    print(f"Model path: {latest_model}")
    
    return latest_model

def train_controller(controller_type, config_path, episodes=200, steps_per_episode=1000, 
                    learning_rate=0.15, discount_factor=0.95, exploration_rate=0.5,
                    exploration_decay=0.998, output_dir=None, verbose=True, auto_load_model=True):
    """
    Train a reinforcement learning controller on a SUMO simulation.
    
    Args:
        controller_type (str): Type of controller to train ('Wired RL' or 'Wireless RL')
        config_path (str): Path to the SUMO configuration file
        episodes (int): Number of training episodes
        steps_per_episode (int): Number of steps per episode
        learning_rate (float): Learning rate for the RL algorithm
        discount_factor (float): Discount factor for the RL algorithm
        exploration_rate (float): Initial exploration rate
        exploration_decay (float): Rate at which exploration decreases over episodes
        output_dir (str): Directory to save trained models and results
        verbose (bool): Whether to print progress updates
        auto_load_model (bool): Whether to automatically load the latest model
        
    Returns:
        dict: Training statistics and results
    """
    if output_dir is None:
        output_dir = os.path.join(project_root, "data", "models")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Try to find and load the latest model if auto_load_model is True
    model_path = None
    initial_episode = 0
    
    if auto_load_model:
        model_path = find_latest_model(controller_type)
        if model_path:
            # Extract the episode number from the model path
            match = re.search(r'_episode_(\d+)\.pkl$', model_path)
            if match:
                initial_episode = int(match.group(1))
                print(f"Continuing training from episode {initial_episode}")
                
                # Adjust exploration rate based on progress
                # This allows us to start with a lower exploration rate for continued training
                if exploration_rate > 0.1:
                    adjusted_exploration = exploration_rate * (exploration_decay ** initial_episode)
                    exploration_rate = max(0.05, adjusted_exploration)
                    print(f"Adjusted exploration rate to {exploration_rate:.4f} based on previous training")
    
    # Statistics tracking
    training_stats = {
        "controller_type": controller_type,
        "episodes": episodes,
        "steps_per_episode": steps_per_episode,
        "learning_rate": learning_rate,
        "discount_factor": discount_factor,
        "initial_exploration_rate": exploration_rate,
        "exploration_decay": exploration_decay,
        "episode_rewards": [],
        "episode_avg_wait_times": [],
        "episode_avg_speeds": [],
        "episode_throughputs": [],
        "q_table_sizes": [],
        "episode_times": [],
        "exploration_rates": [],
        "continued_from_episode": initial_episode if model_path else 0
    }
    
    # Create simulation
    sim = SumoSimulation(config_path, gui=False)
    
    # Track the total number of episodes (including previous training)
    total_episodes = initial_episode + episodes
    
    for episode in range(episodes):
        episode_start_time = time.time()
        current_exploration_rate = exploration_rate * (exploration_decay ** episode)
        
        if verbose:
            print(f"\nEpisode {episode+1}/{episodes} (Total: {initial_episode + episode + 1}) - Exploration rate: {current_exploration_rate:.3f}")
        
        # Start the simulation
        sim.start()
        
        # Get traffic light IDs
        tl_ids = traci.trafficlight.getIDList()
        
        if not tl_ids:
            print("No traffic lights found in the simulation.")
            sim.close()
            return training_stats
        
        # Create the appropriate controller
        if controller_type == "Wired RL":
            controller = WiredRLController(
                tl_ids, 
                learning_rate=learning_rate,
                discount_factor=discount_factor,
                exploration_rate=current_exploration_rate,
                network_latency=0.01,  # Use small latency for faster training
                model_path=model_path if episode == 0 and model_path else None  # Only load on first episode
            )
        elif controller_type == "Wireless RL":
            controller = WirelessRLController(
                tl_ids,
                learning_rate=learning_rate,
                discount_factor=discount_factor,
                exploration_rate=current_exploration_rate,
                base_latency=0.005,  # Use small latency for faster training
                computation_factor=0.01,
                packet_loss_prob=0.001,  # Minimal packet loss for training
                model_path=model_path if episode == 0 and model_path else None  # Only load on first episode
            )
        else:
            print(f"Invalid controller type: {controller_type}")
            sim.close()
            return training_stats
        
        # Store the state lengths for each traffic light
        controller.tl_state_lengths = {}
        for tl_id in tl_ids:
            current_state = traci.trafficlight.getRedYellowGreenState(tl_id)
            controller.tl_state_lengths[tl_id] = len(current_state)
            if verbose and episode == 0:
                print(f"Traffic light {tl_id} has state length: {len(current_state)}")
        
        # Episode statistics
        episode_rewards = []
        total_waiting_time = 0
        total_speed = 0
        vehicle_count = 0
        throughput = 0
        
        # Run the episode
        for step in range(steps_per_episode):
            # Collect traffic state
            traffic_state = {}
            for tl_id in tl_ids:
                # Get incoming lanes for this traffic light
                incoming_lanes = []
                for connection in traci.trafficlight.getControlledLinks(tl_id):
                    if connection and connection[0]:  # Check if connection exists
                        incoming_lane = connection[0][0]
                        if incoming_lane not in incoming_lanes:
                            incoming_lanes.append(incoming_lane)
                
                # Count vehicles and collect metrics for each direction
                north_count = south_count = east_count = west_count = 0
                north_wait = south_wait = east_wait = west_wait = 0
                north_queue = south_queue = east_queue = west_queue = 0
                
                for lane in incoming_lanes:
                    # Determine direction based on lane ID
                    direction = "unknown"
                    if "A0A1" in lane or "B0B1" in lane:
                        direction = "north"
                    elif "A1A0" in lane or "B1B0" in lane:
                        direction = "south"
                    elif "A0B0" in lane or "A1B1" in lane:
                        direction = "east"
                    elif "B0A0" in lane or "B1A1" in lane:
                        direction = "west"
                    
                    # Count vehicles on this lane
                    vehicle_count_lane = traci.lane.getLastStepVehicleNumber(lane)
                    vehicles_lane = traci.lane.getLastStepVehicleIDs(lane)
                    waiting_time = sum(traci.vehicle.getWaitingTime(v) for v in vehicles_lane) if vehicles_lane else 0
                    queue_length = traci.lane.getLastStepHaltingNumber(lane)
                    
                    if direction == "north":
                        north_count += vehicle_count_lane
                        north_wait += waiting_time
                        north_queue += queue_length
                    elif direction == "south":
                        south_count += vehicle_count_lane
                        south_wait += waiting_time
                        south_queue += queue_length
                    elif direction == "east":
                        east_count += vehicle_count_lane
                        east_wait += waiting_time
                        east_queue += queue_length
                    elif direction == "west":
                        west_count += vehicle_count_lane
                        west_wait += waiting_time
                        west_queue += queue_length
                
                # Calculate average waiting times
                traffic_state[tl_id] = {
                    'north_count': north_count,
                    'south_count': south_count,
                    'east_count': east_count,
                    'west_count': west_count,
                    'north_wait': north_wait / max(1, north_count) if north_count > 0 else 0,
                    'south_wait': south_wait / max(1, south_count) if south_count > 0 else 0,
                    'east_wait': east_wait / max(1, east_count) if east_count > 0 else 0,
                    'west_wait': west_wait / max(1, west_count) if west_count > 0 else 0,
                    'north_queue': north_queue,
                    'south_queue': south_queue,
                    'east_queue': east_queue,
                    'west_queue': west_queue
                }
            
            # Update controller with traffic state
            controller.update_traffic_state(traffic_state)
            
            # Get current simulation time
            current_time = traci.simulation.getTime()
            
            # Get phase decisions from controller for each junction
            for tl_id in tl_ids:
                try:
                    phase = controller.get_phase_for_junction(tl_id, current_time)
                    
                    # Debug output
                    if verbose and step % 50 == 0:
                        print(f"DEBUG - Phase type: {type(phase)}, Phase value: {phase}")
                    
                    # Set traffic light phase in SUMO
                    current_sumo_state = traci.trafficlight.getRedYellowGreenState(tl_id)
                    
                    if verbose and step % 50 == 0:
                        print(f"DEBUG - Current state: {current_sumo_state} (len={len(current_sumo_state)})")
                    
                    # Only update if phase is different and is a valid string
                    if isinstance(phase, str):
                        # Adjust phase length if needed
                        if len(phase) != len(current_sumo_state):
                            if verbose:
                                print(f"Adjusting phase length for {tl_id}. Expected {len(current_sumo_state)}, got {len(phase)}.")
                            if len(phase) < len(current_sumo_state):
                                # Repeat the pattern
                                phase = phase * (len(current_sumo_state) // len(phase)) + phase[:len(current_sumo_state) % len(phase)]
                            else:
                                # Truncate
                                phase = phase[:len(current_sumo_state)]
                        
                        # Only update if phase is different
                        if phase != current_sumo_state:
                            try:
                                traci.trafficlight.setRedYellowGreenState(tl_id, phase)
                            except Exception as e:
                                print(f"Error setting traffic light state for {tl_id}: {e}")
                                print(f"Current state: {current_sumo_state} (len={len(current_sumo_state)})")
                                print(f"Attempted phase: {phase} (len={len(phase)})")
                                # Continue with next traffic light without crashing
                                continue
                    else:
                        print(f"WARNING: Invalid phase type for {tl_id}: {type(phase)}. Skipping update.")
                except Exception as e:
                    print(f"Error processing traffic light {tl_id}: {e}")
                    continue
            
            # Collect metrics
            vehicles_all = traci.vehicle.getIDList()
            if vehicles_all:
                total_waiting_time += sum(traci.vehicle.getWaitingTime(v) for v in vehicles_all)
                total_speed += sum(traci.vehicle.getSpeed(v) for v in vehicles_all)
                vehicle_count += len(vehicles_all)
            
            throughput += traci.simulation.getArrivedNumber()
            
            # Step the simulation
            sim.step()
            
            # Track rewards
            if hasattr(controller, "reward_history") and controller.reward_history:
                episode_rewards.append(controller.reward_history[-1])
            
            # Print progress
            if verbose and step % 100 == 0 and step > 0:
                print(f"  Step {step}/{steps_per_episode} - "
                      f"Avg reward: {sum(episode_rewards[-100:]) / max(1, len(episode_rewards[-100:])):.2f}" if episode_rewards else "N/A")
        
        # Calculate episode statistics
        episode_time = time.time() - episode_start_time
        avg_reward = sum(episode_rewards) / len(episode_rewards) if episode_rewards else 0
        avg_wait_time = total_waiting_time / vehicle_count if vehicle_count > 0 else 0
        avg_speed = total_speed / vehicle_count if vehicle_count > 0 else 0
        
        # Get Q-table stats if available
        q_table_stats = {"total_entries": 0, "unique_states": 0}
        if hasattr(controller, "get_q_table_stats"):
            q_table_stats = controller.get_q_table_stats()
        
        # Close the simulation
        sim.close()
        
        # Record episode results
        training_stats["episode_rewards"].append(avg_reward)
        training_stats["episode_avg_wait_times"].append(avg_wait_time)
        training_stats["episode_avg_speeds"].append(avg_speed)
        training_stats["episode_throughputs"].append(throughput)
        training_stats["q_table_sizes"].append(q_table_stats.get("total_entries", 0))
        training_stats["episode_times"].append(episode_time)
        training_stats["exploration_rates"].append(current_exploration_rate)
        
        if verbose:
            print(f"  Episode {episode+1} completed in {episode_time:.1f}s")
            print(f"  Average reward: {avg_reward:.2f}")
            print(f"  Average wait time: {avg_wait_time:.2f}s")
            print(f"  Average speed: {avg_speed:.2f}m/s")
            print(f"  Throughput: {throughput} vehicles")
            print(f"  Q-table size: {q_table_stats.get('total_entries', 0)} entries")
            print(f"  Total episodes trained: {initial_episode + episode + 1}")
        
        # Save controller after each episode
        if hasattr(controller, "save_q_table") and (episode % 5 == 0 or episode == episodes - 1):
            try:
                # Save with overall episode number (initial + current)
                overall_episode = initial_episode + episode + 1
                model_filename = os.path.join(
                    output_dir, f"{controller_type.replace(' ', '_').lower()}_episode_{overall_episode}.pkl")
                controller.save_q_table(model_filename)
                
                # Update model_path for next episode
                model_path = model_filename
                
                if verbose:
                    print(f"  Model saved to {model_filename}")
            except Exception as e:
                print(f"Error saving model: {e}")
    
    # Save training statistics
    stats_filename = os.path.join(
        output_dir, f"{controller_type.replace(' ', '_').lower()}_training_stats_{total_episodes}.json")
    
    try:
        with open(stats_filename, 'w') as f:
            # Convert numpy arrays to lists for JSON serialization
            json_compatible_stats = {}
            for key, value in training_stats.items():
                if isinstance(value, np.ndarray):
                    json_compatible_stats[key] = value.tolist()
                else:
                    json_compatible_stats[key] = value
            json.dump(json_compatible_stats, f, indent=2)
        
        if verbose:
            print(f"\nTraining completed. Statistics saved to {stats_filename}")
    except Exception as e:
        print(f"Error saving training statistics: {e}")
    
    # Plot learning curves
    try:
        plot_learning_curves(training_stats, output_dir, controller_type, initial_episode)
    except Exception as e:
        print(f"Error plotting learning curves: {e}")
    
    return training_stats

def plot_learning_curves(stats, output_dir, controller_type, initial_episode=0):
    """
    Plot learning curves from training statistics.
    
    Args:
        stats (dict): Training statistics
        output_dir (str): Directory to save plots
        controller_type (str): Type of controller
        initial_episode (int): Starting episode number (for continued training)
    """
    controller_name = controller_type.replace(' ', '_').lower()
    
    # Create figure with multiple subplots
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    
    # Calculate episode numbers including initial episodes
    episodes = range(initial_episode + 1, initial_episode + len(stats["episode_rewards"]) + 1)
    
    # Plot average rewards
    if stats["episode_rewards"]:
        axs[0, 0].plot(episodes, stats["episode_rewards"])
        axs[0, 0].set_title('Average Reward per Episode')
        axs[0, 0].set_xlabel('Episode')
        axs[0, 0].set_ylabel('Average Reward')
        axs[0, 0].grid(True)
    
    # Plot average waiting times
    axs[0, 1].plot(episodes, stats["episode_avg_wait_times"])
    axs[0, 1].set_title('Average Waiting Time per Episode')
    axs[0, 1].set_xlabel('Episode')
    axs[0, 1].set_ylabel('Average Waiting Time (s)')
    axs[0, 1].grid(True)
    
    # Plot average speeds
    axs[1, 0].plot(episodes, stats["episode_avg_speeds"])
    axs[1, 0].set_title('Average Speed per Episode')
    axs[1, 0].set_xlabel('Episode')
    axs[1, 0].set_ylabel('Average Speed (m/s)')
    axs[1, 0].grid(True)
    
    # Plot Q-table size
    axs[1, 1].plot(episodes, stats["q_table_sizes"])
    axs[1, 1].set_title('Q-Table Size')
    axs[1, 1].set_xlabel('Episode')
    axs[1, 1].set_ylabel('Number of State-Action Pairs')
    axs[1, 1].grid(True)
    
    # Add a note about continued training if applicable
    if initial_episode > 0:
        fig.suptitle(f'{controller_type} Learning Curves (Continued from Episode {initial_episode})', fontsize=16)
    else:
        fig.suptitle(f'{controller_type} Learning Curves', fontsize=16)
    
    plt.tight_layout()
    
    # Include initial episode in filename for continued training
    if initial_episode > 0:
        plt.savefig(os.path.join(output_dir, f"{controller_name}_learning_curves_continued_{initial_episode+len(stats['episode_rewards'])}.png"))
    else:
        plt.savefig(os.path.join(output_dir, f"{controller_name}_learning_curves_{len(stats['episode_rewards'])}.png"))
    
    plt.close()
    
    # Plot exploration rate decay
    plt.figure(figsize=(10, 5))
    plt.plot(episodes, stats["exploration_rates"])
    plt.title('Exploration Rate Decay')
    plt.xlabel('Episode')
    plt.ylabel('Exploration Rate')
    plt.grid(True)
    
    # Include initial episode in filename for continued training
    if initial_episode > 0:
        plt.savefig(os.path.join(output_dir, f"{controller_name}_exploration_rate_continued_{initial_episode+len(stats['episode_rewards'])}.png"))
    else:
        plt.savefig(os.path.join(output_dir, f"{controller_name}_exploration_rate_{len(stats['episode_rewards'])}.png"))
    
    plt.close()

def create_temp_config(route_file):
    """
    Create a temporary SUMO configuration file.
    
    Args:
        route_file (str): Path to the route file
        
    Returns:
        str: Path to the created config file
    """
    # Get base name without extension
    base_name = os.path.basename(route_file).split('.')[0]
    
    # Network file
    network_file = os.path.join(project_root, "config", "maps", "traffic_grid.net.xml")
    
    # Create a unique config file name
    config_name = f"temp_training_{base_name}.sumocfg"
    config_path = os.path.join(project_root, "config", "scenarios", config_name)
    
    # Write the config file
    with open(config_path, 'w') as f:
        f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="{network_file}"/>
        <route-files value="{route_file}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="3600"/>
        <step-length value="1.0"/>
    </time>
    <processing>
        <time-to-teleport value="-1"/>
    </processing>
    <report>
        <verbose value="false"/>
        <no-step-log value="true"/>
    </report>
</configuration>""")
    
    print(f"Created temporary config file: {config_path}")
    return config_path

def main():
    """Main function to train RL controllers."""
    parser = argparse.ArgumentParser(description='Train reinforcement learning traffic controllers')
    parser.add_argument('--controller', type=str, default="Wired RL",
                        choices=["Wired RL", "Wireless RL"],
                        help='Type of controller to train')
    parser.add_argument('--scenario', type=str, default="light_traffic",
                        help='Traffic scenario to use for training')
    parser.add_argument('--episodes', type=int, default=50,
                        help='Number of training episodes')
    parser.add_argument('--steps', type=int, default=500,
                        help='Steps per episode')
    parser.add_argument('--learning-rate', type=float, default=0.15,
                        help='Learning rate for the RL algorithm')
    parser.add_argument('--discount-factor', type=float, default=0.95,
                        help='Discount factor for the RL algorithm')
    parser.add_argument('--exploration-rate', type=float, default=0.5,
                        help='Initial exploration rate')
    parser.add_argument('--exploration-decay', type=float, default=0.99,
                        help='Exploration rate decay factor')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Directory to save trained models and results')
    parser.add_argument('--no-auto-load', action='store_true',
                        help='Disable automatic loading of the latest model')
    args = parser.parse_args()
    
    # Construct the path to the scenario
    scenario_path = os.path.join(
        project_root, "config", "scenarios", f"{args.scenario}.sumocfg")
    
    if not os.path.exists(scenario_path):
        # Try to create a temp config if the scenario file exists
        route_file = os.path.join(
            project_root, "config", "scenarios", f"{args.scenario}.rou.xml")
        
        if os.path.exists(route_file):
            scenario_path = create_temp_config(route_file)
        else:
            print(f"Scenario {args.scenario} not found.")
            return
    
    print(f"\n{'='*80}")
    print(f"Training {args.controller} on {args.scenario} for {args.episodes} episodes")
    print(f"{'='*80}\n")
    
    if not args.no_auto_load:
        print("Auto-loading latest model is enabled. The training will continue from the latest saved model if found.")
    else:
        print("Auto-loading is disabled. Starting training from scratch.")
    
    # Train the controller
    train_controller(
        args.controller,
        scenario_path,
        episodes=args.episodes,
        steps_per_episode=args.steps,
        learning_rate=args.learning_rate,
        discount_factor=args.discount_factor,
        exploration_rate=args.exploration_rate,
        exploration_decay=args.exploration_decay,
        output_dir=args.output_dir,
        auto_load_model=not args.no_auto_load
    )

if __name__ == "__main__":
    main()