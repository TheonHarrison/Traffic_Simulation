import os
import sys
import time
import argparse
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import json
import tensorflow as tf

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import traci
from src.utils.sumo_integration import SumoSimulation
from src.ai.reinforcement_learning.dqn_controller import DQNController
from src.ai.reinforcement_learning.wired_dqn_controller import WiredDQNController
from src.ai.reinforcement_learning.wireless_dqn_controller import WirelessDQNController

def train_dqn_controller(controller_type, config_path, episodes=50, steps_per_episode=1000, 
                        learning_rate=0.001, discount_factor=0.95, exploration_rate=0.3,
                        memory_size=10000, batch_size=32, target_update_frequency=100,
                        exploration_decay=0.99, output_dir=None, verbose=True):
    """
    Train a DQN controller on a SUMO simulation.
    
    Args:
        controller_type (str): Type of controller to train ('DQN', 'Wired DQN', or 'Wireless DQN')
        config_path (str): Path to the SUMO configuration file
        episodes (int): Number of training episodes
        steps_per_episode (int): Number of steps per episode
        learning_rate (float): Learning rate for the neural network
        discount_factor (float): Discount factor for the RL algorithm
        exploration_rate (float): Initial exploration rate
        memory_size (int): Size of replay memory
        batch_size (int): Number of samples to use for training
        target_update_frequency (int): How often to update target network
        exploration_decay (float): Rate at which exploration decreases over episodes
        output_dir (str): Directory to save trained models and results
        verbose (bool): Whether to print progress updates
        
    Returns:
        dict: Training statistics and results
    """
    if output_dir is None:
        output_dir = os.path.join(project_root, "data", "models", "dqn")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Statistics tracking
    training_stats = {
        "controller_type": controller_type,
        "episodes": episodes,
        "steps_per_episode": steps_per_episode,
        "learning_rate": learning_rate,
        "discount_factor": discount_factor,
        "initial_exploration_rate": exploration_rate,
        "exploration_decay": exploration_decay,
        "memory_size": memory_size,
        "batch_size": batch_size,
        "target_update_frequency": target_update_frequency,
        "episode_rewards": [],
        "episode_avg_wait_times": [],
        "episode_avg_speeds": [],
        "episode_throughputs": [],
        "training_steps": [],
        "memory_usage": [],
        "episode_times": [],
        "exploration_rates": [],
        "losses": []
    }
    
    # Create simulation
    sim = SumoSimulation(config_path, gui=False)
    
    for episode in range(episodes):
        episode_start_time = time.time()
        current_exploration_rate = exploration_rate * (exploration_decay ** episode)
        
        if verbose:
            print(f"\nEpisode {episode+1}/{episodes} - Exploration rate: {current_exploration_rate:.3f}")
        
        # Start the simulation
        sim.start()
        
        # Get traffic light IDs
        tl_ids = traci.trafficlight.getIDList()
        
        if not tl_ids:
            print("No traffic lights found in the simulation.")
            sim.close()
            return training_stats
        
        # Create the appropriate controller
        if controller_type == "DQN":
            controller = DQNController(
                tl_ids, 
                learning_rate=learning_rate,
                discount_factor=discount_factor,
                exploration_rate=current_exploration_rate,
                memory_size=memory_size,
                batch_size=batch_size,
                target_update_frequency=target_update_frequency
            )
        elif controller_type == "Wired DQN":
            controller = WiredDQNController(
                tl_ids,
                learning_rate=learning_rate,
                discount_factor=discount_factor,
                exploration_rate=current_exploration_rate,
                memory_size=memory_size,
                batch_size=batch_size,
                target_update_frequency=target_update_frequency,
                network_latency=0.01  # Use small latency for faster training
            )
        elif controller_type == "Wireless DQN":
            controller = WirelessDQNController(
                tl_ids,
                learning_rate=learning_rate,
                discount_factor=discount_factor,
                exploration_rate=current_exploration_rate,
                memory_size=memory_size,
                batch_size=batch_size,
                target_update_frequency=target_update_frequency,
                base_latency=0.005,  # Use small latency for faster training
                computation_factor=0.01,
                packet_loss_prob=0.001  # Minimal packet loss for training
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
            if verbose:
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
                    
                    # Set traffic light phase in SUMO
                    current_sumo_state = traci.trafficlight.getRedYellowGreenState(tl_id)
                    
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
        
        # Get training info
        training_info = controller.get_training_info()
        
        # Close the simulation
        sim.close()
        
        # Record episode results
        training_stats["episode_rewards"].append(avg_reward)
        training_stats["episode_avg_wait_times"].append(avg_wait_time)
        training_stats["episode_avg_speeds"].append(avg_speed)
        training_stats["episode_throughputs"].append(throughput)
        training_stats["training_steps"].append(training_info["training_steps"])
        # Take average memory usage across junctions
        avg_memory = sum(training_info["memory_size"].values()) / len(training_info["memory_size"]) if training_info["memory_size"] else 0
        training_stats["memory_usage"].append(avg_memory)
        training_stats["episode_times"].append(episode_time)
        training_stats["exploration_rates"].append(current_exploration_rate)
        
        if verbose:
            print(f"  Episode {episode+1} completed in {episode_time:.1f}s")
            print(f"  Average reward: {avg_reward:.2f}")
            print(f"  Average wait time: {avg_wait_time:.2f}s")
            print(f"  Average speed: {avg_speed:.2f}m/s")
            print(f"  Throughput: {throughput} vehicles")
            print(f"  Training steps: {training_info['training_steps']}")
            print(f"  Memory usage: {avg_memory:.2f} experiences")
        
        # Save controller after each episode
        if (episode % 5 == 0 or episode == episodes - 1):
            try:
                model_filename = os.path.join(
                    output_dir, f"{controller_type.replace(' ', '_').lower()}_episode_{episode+1}")
                controller.save_model(model_filename)
                
                if verbose:
                    print(f"  Model saved to {model_filename}")
            except Exception as e:
                print(f"Error saving model: {e}")
    
    # Save training statistics
    stats_filename = os.path.join(
        output_dir, f"{controller_type.replace(' ', '_').lower()}_training_stats.json")
    
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
        plot_learning_curves(training_stats, output_dir, controller_type)
    except Exception as e:
        print(f"Error plotting learning curves: {e}")
    
    return training_stats

def plot_learning_curves(stats, output_dir, controller_type):
    """
    Plot learning curves from training statistics.
    
    Args:
        stats (dict): Training statistics
        output_dir (str): Directory to save plots
        controller_type (str): Type of controller
    """
    controller_name = controller_type.replace(' ', '_').lower()
    
    # Create figure with multiple subplots
    fig, axs = plt.subplots(3, 2, figsize=(15, 15))
    
    # Plot average rewards
    if stats["episode_rewards"]:
        axs[0, 0].plot(stats["episode_rewards"])
        axs[0, 0].set_title('Average Reward per Episode')
        axs[0, 0].set_xlabel('Episode')
        axs[0, 0].set_ylabel('Average Reward')
        axs[0, 0].grid(True)
    
    # Plot average waiting times
    axs[0, 1].plot(stats["episode_avg_wait_times"])
    axs[0, 1].set_title('Average Waiting Time per Episode')
    axs[0, 1].set_xlabel('Episode')
    axs[0, 1].set_ylabel('Average Waiting Time (s)')
    axs[0, 1].grid(True)
    
    # Plot average speeds
    axs[1, 0].plot(stats["episode_avg_speeds"])
    axs[1, 0].set_title('Average Speed per Episode')
    axs[1, 0].set_xlabel('Episode')
    axs[1, 0].set_ylabel('Average Speed (m/s)')
    axs[1, 0].grid(True)
    
    # Plot throughput
    axs[1, 1].plot(stats["episode_throughputs"])
    axs[1, 1].set_title('Throughput per Episode')
    axs[1, 1].set_xlabel('Episode')
    axs[1, 1].set_ylabel('Number of Vehicles')
    axs[1, 1].grid(True)
    
    # Plot exploration rate
    axs[2, 0].plot(stats["exploration_rates"])
    axs[2, 0].set_title('Exploration Rate Decay')
    axs[2, 0].set_xlabel('Episode')
    axs[2, 0].set_ylabel('Exploration Rate')
    axs[2, 0].grid(True)
    
    # Plot memory usage
    axs[2, 1].plot(stats["memory_usage"])
    axs[2, 1].set_title('Memory Usage')
    axs[2, 1].set_xlabel('Episode')
    axs[2, 1].set_ylabel('Number of Experiences')
    axs[2, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{controller_name}_learning_curves.png"))
    plt.close()
    
    # Create a second figure for comparing metrics
    fig, axs = plt.subplots(1, 3, figsize=(18, 6))
    
    # Plot waiting time vs. training steps
    axs[0].plot(stats["training_steps"], stats["episode_avg_wait_times"])
    axs[0].set_title('Waiting Time vs. Training Steps')
    axs[0].set_xlabel('Training Steps')
    axs[0].set_ylabel('Average Waiting Time (s)')
    axs[0].grid(True)
    
    # Plot speed vs. training steps
    axs[1].plot(stats["training_steps"], stats["episode_avg_speeds"])
    axs[1].set_title('Speed vs. Training Steps')
    axs[1].set_xlabel('Training Steps')
    axs[1].set_ylabel('Average Speed (m/s)')
    axs[1].grid(True)
    
    # Plot throughput vs. training steps
    axs[2].plot(stats["training_steps"], stats["episode_throughputs"])
    axs[2].set_title('Throughput vs. Training Steps')
    axs[2].set_xlabel('Training Steps')
    axs[2].set_ylabel('Number of Vehicles')
    axs[2].grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{controller_name}_metrics_vs_training.png"))
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
    config_name = f"temp_dqn_training_{base_name}.sumocfg"
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
    """Main function to train DQN controllers."""
    parser = argparse.ArgumentParser(description='Train DQN traffic controllers')
    parser.add_argument('--controller', type=str, default="DQN",
                        choices=["DQN", "Wired DQN", "Wireless DQN"],
                        help='Type of controller to train')
    parser.add_argument('--scenario', type=str, default="light_traffic",
                        help='Traffic scenario to use for training')
    parser.add_argument('--episodes', type=int, default=20,
                        help='Number of training episodes')
    parser.add_argument('--steps', type=int, default=500,
                        help='Steps per episode')
    parser.add_argument('--learning-rate', type=float, default=0.001,
                        help='Learning rate for the DQN')
    parser.add_argument('--discount-factor', type=float, default=0.95,
                        help='Discount factor for future rewards')
    parser.add_argument('--exploration-rate', type=float, default=0.3,
                        help='Initial exploration rate')
    parser.add_argument('--exploration-decay', type=float, default=0.9,
                        help='Exploration rate decay factor')
    parser.add_argument('--memory-size', type=int, default=10000,
                        help='Size of replay memory')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Batch size for training')
    parser.add_argument('--target-update', type=int, default=100,
                        help='Target network update frequency')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Directory to save trained models and results')
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed progress information')
    args = parser.parse_args()
    
    # Ensure TensorFlow is using GPU if available
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"Using {len(gpus)} GPU(s) for training")
        except RuntimeError as e:
            print(f"Error setting up GPU: {e}")
    
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
    
    print(f"Training {args.controller} on {args.scenario} for {args.episodes} episodes")
    
    # Train the controller
    train_dqn_controller(
        args.controller,
        scenario_path,
        episodes=args.episodes,
        steps_per_episode=args.steps,
        learning_rate=args.learning_rate,
        discount_factor=args.discount_factor,
        exploration_rate=args.exploration_rate,
        memory_size=args.memory_size,
        batch_size=args.batch_size,
        target_update_frequency=args.target_update,
        exploration_decay=args.exploration_decay,
        output_dir=args.output_dir,
        verbose=args.verbose
    )

if __name__ == "__main__":
    main()