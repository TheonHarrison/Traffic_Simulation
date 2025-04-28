import os
import sys
import time
import argparse
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import pickle
import json

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import traci
from src.utils.sumo_integration import SumoSimulation
from src.ai.reinforcement_learning.wired_rl_controller import WiredRLController
from src.ai.reinforcement_learning.wireless_rl_controller import WirelessRLController

def train_controller(controller_type, config_path, episodes=50, steps_per_episode=1000, 
                    learning_rate=0.1, discount_factor=0.9, exploration_rate=0.3,
                    exploration_decay=0.99, output_dir=None, verbose=True):
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
        
    Returns:
        dict: Training statistics and results
    """
    if output_dir is None:
        output_dir = os.path.join(project_root, "data", "models")
    
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
        "episode_rewards": [],
        "episode_avg_wait_times": [],
        "episode_avg_speeds": [],
        "episode_throughputs": [],
        "q_table_sizes": [],
        "episode_times": [],
        "exploration_rates": []
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
        if controller_type == "Wired RL":
            controller = WiredRLController(
                tl_ids, 
                learning_rate=learning_rate,
                discount_factor=discount_factor,
                exploration_rate=current_exploration_rate,
                network_latency=0.01  # Use small latency for faster training
            )
        elif controller_type == "Wireless RL":
            controller = WirelessRLController(
                tl_ids,
                learning_rate=learning_rate,
                discount_factor=discount_factor,
                exploration_rate=current_exploration_rate,
                base_latency=0.005,  # Use small latency for faster training
                computation_factor=0.01,
                packet_loss_prob=0.001  # Minimal packet loss for training
            )
        else:
            print(f"Invalid controller type: {controller_type}")
            sim.close()
            return training_stats
        
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
                    vehicle_count = traci.lane.getLastStepVehicleNumber(lane)
                    vehicles = traci.lane.getLastStepVehicleIDs(lane)
                    waiting_time = sum(traci.vehicle.getWaitingTime(v) for v in vehicles) if vehicles else 0
                    queue_length = traci.lane.getLastStepHaltingNumber(lane)
                    
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
                phase = controller.get_phase_for_junction(tl_id, current_time)
                
                # Set traffic light phase in SUMO
                current_sumo_state = traci.trafficlight.getRedYellowGreenState(tl_id)
                
                # Only update if phase is different
                if phase != current_sumo_state:
                    traci.trafficlight.setRedYellowGreenState(tl_id, phase)
            
            # Collect metrics
            vehicles = traci.vehicle.getIDList()
            if vehicles:
                total_waiting_time += sum(traci.vehicle.getWaitingTime(v) for v in vehicles)
                total_speed += sum(traci.vehicle.getSpeed(v) for v in vehicles)
                vehicle_count += len(vehicles)
            
            throughput += traci.simulation.getArrivedNumber()
            
            # Step the simulation
            sim.step()
            
            # Track rewards
            if controller.reward_history:
                episode_rewards.append(controller.reward_history[-1])
            
            # Print progress
            if verbose and step % 100 == 0 and step > 0:
                print(f"  Step {step}/{steps_per_episode} - "
                      f"Avg reward: {sum(episode_rewards[-100:]) / 100:.2f}")
        
        # Calculate episode statistics
        episode_time = time.time() - episode_start_time
        avg_reward = sum(episode_rewards) / len(episode_rewards) if episode_rewards else 0
        avg_wait_time = total_waiting_time / vehicle_count if vehicle_count > 0 else 0
        avg_speed = total_speed / vehicle_count if vehicle_count > 0 else 0
        
        # Get Q-table stats
        q_table_stats = controller.get_q_table_stats()
        
        # Close the simulation
        sim.close()
        
        # Record episode results
        training_stats["episode_rewards"].append(avg_reward)
        training_stats["episode_avg_wait_times"].append(avg_wait_time)
        training_stats["episode_avg_speeds"].append(avg_speed)
        training_stats["episode_throughputs"].append(throughput)
        training_stats["q_table_sizes"].append(q_table_stats["total_entries"])
        training_stats["episode_times"].append(episode_time)
        training_stats["exploration_rates"].append(current_exploration_rate)
        
        if verbose:
            print(f"  Episode {episode+1} completed in {episode_time:.1f}s")
            print(f"  Average reward: {avg_reward:.2f}")
            print(f"  Average wait time: {avg_wait_time:.2f}s")
            print(f"  Average speed: {avg_speed:.2f}m/s")
            print(f"  Throughput: {throughput} vehicles")
            print(f"  Q-table size: {q_table_stats['total_entries']} entries")
        
        # Save controller after each episode
        if episode % 5 == 0 or episode == episodes - 1:
            model_filename = os.path.join(
                output_dir, f"{controller_type.replace(' ', '_').lower()}_episode_{episode+1}.pkl")
            controller.save_q_table(model_filename)
            
            if verbose:
                print(f"  Model saved to {model_filename}")
    
    # Save training statistics
    stats_filename = os.path.join(
        output_dir, f"{controller_type.replace(' ', '_').lower()}_training_stats.json")
    
    with open(stats_filename, 'w') as f:
        # Convert numpy arrays to lists for JSON serialization
        for key, value in training_stats.items():
            if isinstance(value, np.ndarray):
                training_stats[key] = value.tolist()
        json.dump(training_stats, f, indent=2)
    
    if verbose:
        print(f"\nTraining completed. Statistics saved to {stats_filename}")
    
    # Plot learning curves
    plot_learning_curves(training_stats, output_dir, controller_type)
    
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
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot average rewards
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
    
    # Plot Q-table size
    axs[1, 1].plot(stats["q_table_sizes"])
    axs[1, 1].set_title('Q-Table Size')
    axs[1, 1].set_xlabel('Episode')
    axs[1, 1].set_ylabel('Number of State-Action Pairs')
    axs[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{controller_name}_learning_curves.png"))
    plt.close()
    
    # Plot exploration rate decay
    plt.figure(figsize=(10, 5))
    plt.plot(stats["exploration_rates"])
    plt.title('Exploration Rate Decay')
    plt.xlabel('Episode')
    plt.ylabel('Exploration Rate')
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, f"{controller_name}_exploration_rate.png"))
    plt.close()

def main():
    """Main function to train RL controllers."""
    parser = argparse.ArgumentParser(description='Train reinforcement learning traffic controllers')
    parser.add_argument('--controller', type=str, default="Wired RL",
                        choices=["Wired RL", "Wireless RL"],
                        help='Type of controller to train')
    parser.add_argument('--scenario', type=str, default="light_traffic",
                        help='Traffic scenario to use for training')
    parser.add_argument('--episodes', type=int, default=20,
                        help='Number of training episodes')
    parser.add_argument('--steps', type=int, default=500,
                        help='Steps per episode')
    parser.add_argument('--learning-rate', type=float, default=0.1,
                        help='Learning rate for the RL algorithm')
    parser.add_argument('--discount-factor', type=float, default=0.9,
                        help='Discount factor for the RL algorithm')
    parser.add_argument('--exploration-rate', type=float, default=0.3,
                        help='Initial exploration rate')
    parser.add_argument('--exploration-decay', type=float, default=0.9,
                        help='Exploration rate decay factor')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Directory to save trained models and results')
    args = parser.parse_args()
    
    # Construct the path to the scenario
    scenario_path = os.path.join(
        project_root, "config", "scenarios", f"{args.scenario}.sumocfg")
    
    if not os.path.exists(scenario_path):
        # Try to create a temp config if the scenario file exists
        route_file = os.path.join(project_root, "config", "scenarios", f"{scenario}.rou.xml")
        if os.path.exists(route_file):
            scenario_path = create_temp_config(route_file)
        else:
            print(f"Scenario {scenario} not found.")
            return {}
    
    # Initialize comparison results
    comparison = {
        "scenario": scenario,
        "controllers": {},
        "summary": {}
    }
    
    # Run test for each controller
    for controller_type in controllers:
        # Get model path for this controller if provided
        model_path = None
        if model_paths and controller_type in model_paths:
            model_path = model_paths[controller_type]
        
        print(f"\nTesting {controller_type} on scenario {scenario}...")
        
        # Run the test
        metrics = run_test(
            controller_type, 
            scenario_path, 
            model_path=model_path, 
            steps=steps, 
            gui=gui
        )
        
        # Store results
        comparison["controllers"][controller_type] = metrics
    
    # Calculate summary statistics for comparison
    if comparison["controllers"]:
        # Initialize summary metrics
        summary = {
            "avg_waiting_time": {},
            "avg_speed": {},
            "throughput": {},
            "avg_decision_time": {},
            "avg_response_time": {}
        }
        
        # Extract metrics for each controller
        for controller_type, metrics in comparison["controllers"].items():
            summary["avg_waiting_time"][controller_type] = metrics.get("avg_waiting_time", 0)
            summary["avg_speed"][controller_type] = metrics.get("avg_speed", 0)
            summary["throughput"][controller_type] = metrics.get("throughput", 0)
            summary["avg_decision_time"][controller_type] = metrics.get("avg_decision_time", 0) * 1000  # ms
            summary["avg_response_time"][controller_type] = metrics.get("avg_response_time", 0) * 1000  # ms
        
        # Find the best controller for each metric
        for metric, values in summary.items():
            if not values:
                continue
                
            if metric in ["avg_waiting_time", "avg_decision_time", "avg_response_time"]:
                # Lower is better
                best_controller = min(values.items(), key=lambda x: x[1])[0]
            else:
                # Higher is better
                best_controller = max(values.items(), key=lambda x: x[1])[0]
            
            # Add best controller to summary
            if "best_controller" not in summary:
                summary["best_controller"] = {}
            
            summary["best_controller"][metric] = best_controller
        
        comparison["summary"] = summary
    
    # Save comparison results
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    results_file = os.path.join(
        output_dir, f"comparison_{scenario}_{timestamp}.json")
    
    with open(results_file, 'w') as f:
        json.dump(comparison, f, indent=2)
    
    print(f"\nComparison results saved to {results_file}")
    
    # Generate comparison plots
    generate_comparison_plots(comparison, output_dir, scenario)
    
    return comparison

def generate_comparison_plots(comparison, output_dir, scenario):
    """
    Generate plots comparing controller performance.
    
    Args:
        comparison (dict): Comparison results
        output_dir (str): Directory to save plots
        scenario (str): Scenario name
    """
    # Create plots directory
    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    # Check if we have controllers to compare
    if not comparison["controllers"]:
        print("No controllers to compare.")
        return
    
    # Get controller names
    controllers = list(comparison["controllers"].keys())
    
    # 1. Waiting Time Comparison
    plt.figure(figsize=(10, 6))
    wait_times = [comparison["controllers"][ctrl].get("avg_waiting_time", 0) for ctrl in controllers]
    
    bars = plt.bar(controllers, wait_times, color=['blue', 'green', 'red', 'orange', 'purple'][:len(controllers)])
    
    # Add values on top of bars
    for bar, value in zip(bars, wait_times):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{value:.2f}', ha='center', va='bottom')
    
    plt.ylabel('Average Waiting Time (s)')
    plt.title(f'Average Waiting Time Comparison - {scenario}')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(plots_dir, f"{scenario}_waiting_time_comparison.png"))
    plt.close()
    
    # 2. Speed Comparison
    plt.figure(figsize=(10, 6))
    speeds = [comparison["controllers"][ctrl].get("avg_speed", 0) for ctrl in controllers]
    
    bars = plt.bar(controllers, speeds, color=['blue', 'green', 'red', 'orange', 'purple'][:len(controllers)])
    
    # Add values on top of bars
    for bar, value in zip(bars, speeds):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{value:.2f}', ha='center', va='bottom')
    
    plt.ylabel('Average Speed (m/s)')
    plt.title(f'Average Speed Comparison - {scenario}')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(plots_dir, f"{scenario}_speed_comparison.png"))
    plt.close()
    
    # 3. Throughput Comparison
    plt.figure(figsize=(10, 6))
    throughput = [comparison["controllers"][ctrl].get("throughput", 0) for ctrl in controllers]
    
    bars = plt.bar(controllers, throughput, color=['blue', 'green', 'red', 'orange', 'purple'][:len(controllers)])
    
    # Add values on top of bars
    for bar, value in zip(bars, throughput):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{value}', ha='center', va='bottom')
    
    plt.ylabel('Total Throughput (vehicles)')
    plt.title(f'Throughput Comparison - {scenario}')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(plots_dir, f"{scenario}_throughput_comparison.png"))
    plt.close()
    
    # 4. Response Time Comparison
    plt.figure(figsize=(10, 6))
    response_times = [comparison["controllers"][ctrl].get("avg_response_time", 0) * 1000 for ctrl in controllers]
    
    bars = plt.bar(controllers, response_times, color=['blue', 'green', 'red', 'orange', 'purple'][:len(controllers)])
    
    # Add values on top of bars
    for bar, value in zip(bars, response_times):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{value:.2f}', ha='center', va='bottom')
    
    plt.ylabel('Average Response Time (ms)')
    plt.title(f'Response Time Comparison - {scenario}')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(plots_dir, f"{scenario}_response_time_comparison.png"))
    plt.close()
    
    # 5. All Metrics Radar Chart
    # Normalize metrics for radar chart
    metrics = ['Waiting Time', 'Speed', 'Throughput', 'Response Time', 'Decision Time']
    
    # Get values for each controller
    controller_values = {}
    for ctrl in controllers:
        controller_values[ctrl] = [
            comparison["controllers"][ctrl].get("avg_waiting_time", 0),
            comparison["controllers"][ctrl].get("avg_speed", 0),
            comparison["controllers"][ctrl].get("throughput", 0),
            comparison["controllers"][ctrl].get("avg_response_time", 0) * 1000,
            comparison["controllers"][ctrl].get("avg_decision_time", 0) * 1000
        ]
    
    # Normalize values (min-max scaling)
    normalized_values = {}
    for i, metric in enumerate(metrics):
        values = [controller_values[ctrl][i] for ctrl in controllers]
        
        # For waiting time and response/decision time, lower is better
        if metric in ['Waiting Time', 'Response Time', 'Decision Time']:
            if max(values) != min(values):
                norm_values = [1 - (val - min(values)) / (max(values) - min(values)) for val in values]
            else:
                norm_values = [0.5 for _ in values]
        else:
            # For speed and throughput, higher is better
            if max(values) != min(values):
                norm_values = [(val - min(values)) / (max(values) - min(values)) for val in values]
            else:
                norm_values = [0.5 for _ in values]
        
        for j, ctrl in enumerate(controllers):
            if ctrl not in normalized_values:
                normalized_values[ctrl] = []
            normalized_values[ctrl].append(norm_values[j])
    
    # Create radar chart
    plt.figure(figsize=(10, 8))
    
    # Plot radar chart
    angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]  # Close the loop
    
    ax = plt.subplot(111, polar=True)
    
    for i, ctrl in enumerate(controllers):
        values = normalized_values[ctrl]
        values += values[:1]  # Close the loop
        
        ax.plot(angles, values, linewidth=2, label=ctrl)
        ax.fill(angles, values, alpha=0.1)
    
    # Set labels
    ax.set_thetagrids(np.degrees(angles[:-1]), metrics)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8'])
    ax.grid(True)
    
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.title(f'Performance Metrics Comparison - {scenario}')
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, f"{scenario}_radar_comparison.png"))
    plt.close()

def main():
    """Compare RL controllers with traditional controllers."""
    parser = argparse.ArgumentParser(description='Test and compare traffic controllers')
    parser.add_argument('--scenario', type=str, default="light_traffic",
                        help='Traffic scenario to test')
    parser.add_argument('--controllers', type=str, nargs='+',
                        default=["Wired AI", "Wireless AI", "Traditional", "Wired RL", "Wireless RL"],
                        help='Controllers to compare')
    parser.add_argument('--steps', type=int, default=1000,
                        help='Number of simulation steps')
    parser.add_argument('--gui', action='store_true',
                        help='Show SUMO GUI during simulation')
    parser.add_argument('--models-dir', type=str, default=None,
                        help='Directory containing trained models')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='Directory to save results')
    args = parser.parse_args()
    
    # Set default models directory if not specified
    if args.models_dir is None:
        args.models_dir = os.path.join(project_root, "data", "models")
    
    # Set default output directory if not specified
    if args.output_dir is None:
        args.output_dir = os.path.join(project_root, "data", "outputs")
    
    # Get model paths for RL controllers
    model_paths = {}
    if "Wired RL" in args.controllers:
        # Find the latest Wired RL model
        wired_models = [f for f in os.listdir(args.models_dir) 
                        if f.startswith("wired_rl_") and f.endswith(".pkl")]
        if wired_models:
            latest_wired = sorted(wired_models)[-1]  # Get the latest model
            model_paths["Wired RL"] = os.path.join(args.models_dir, latest_wired)
            print(f"Using Wired RL model: {latest_wired}")
    
    if "Wireless RL" in args.controllers:
        # Find the latest Wireless RL model
        wireless_models = [f for f in os.listdir(args.models_dir) 
                          if f.startswith("wireless_rl_") and f.endswith(".pkl")]
        if wireless_models:
            latest_wireless = sorted(wireless_models)[-1]  # Get the latest model
            model_paths["Wireless RL"] = os.path.join(args.models_dir, latest_wireless)
            print(f"Using Wireless RL model: {latest_wireless}")
    
    # Run comparison
    compare_controllers(
        args.controllers,
        args.scenario,
        model_paths=model_paths,
        steps=args.steps,
        output_dir=args.output_dir,
        gui=args.gui
    )

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
    config_name = f"temp_test_{base_name}.sumocfg"
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

if __name__ == "__main__":
    main()
    _file = os.path.join(
            project_root, "config", "scenarios", f"{args.scenario}.rou.xml")
        
        if os.path.exists(route_file):
            scenario_path = create_temp_config(route_file)
        else:
            print(f"Scenario {args.scenario} not found.")
            return
    
    print(f"Training {args.controller} on {args.scenario} for {args.episodes} episodes")
    
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
        output_dir=args.output_dir
    )

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

if __name__ == "__main__":
    main()
    