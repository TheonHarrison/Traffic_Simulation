import os
import sys
import argparse
import numpy as np
from pathlib import Path
import time
import traci
import multiprocessing as mp
from tqdm import tqdm

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.utils.sumo_integration import SumoSimulation
from src.ai.reinforcement_learning.q_learning_controller import QLearningController
from src.ai.reinforcement_learning.wired_rl_controller import WiredRLController
from src.ai.reinforcement_learning.wireless_rl_controller import WirelessRLController

def train_worker(config_path, controller_type, episode, exploration_rate, 
                steps_per_episode, learning_rate, discount_factor, model_path=None):
    """Worker function for parallel training"""
    # Initialize simulation
    sim = SumoSimulation(config_path, gui=False)
    sim.start()
    
    # Get traffic light IDs
    tl_ids = traci.trafficlight.getIDList()
    
    if not tl_ids:
        print("No traffic lights found!")
        sim.close()
        return None
    
    # Create controller
    if controller_type == "Wired RL":
        controller = WiredRLController(
            tl_ids,
            learning_rate=learning_rate,
            discount_factor=discount_factor,
            exploration_rate=exploration_rate,
            network_latency=0.01,  # Reduced latency for faster training
            model_path=model_path
        )
    elif controller_type == "Wireless RL":
        controller = WirelessRLController(
            tl_ids,
            learning_rate=learning_rate,
            discount_factor=discount_factor,
            exploration_rate=exploration_rate,
            base_latency=0.005,  # Reduced latency for faster training
            computation_factor=0.01,
            packet_loss_prob=0.001,  # Minimal packet loss for faster training
            model_path=model_path
        )
    else:
        print(f"Invalid controller type: {controller_type}")
        sim.close()
        return None
    
    # Episode statistics
    episode_rewards = []
    episode_waiting_times = []
    episode_speeds = []
    
    # Run the episode
    for step in range(steps_per_episode):
        # Collect traffic state (optimized)
        traffic_state = collect_traffic_state(tl_ids)
        
        # Update controller with traffic state
        controller.update_traffic_state(traffic_state)
        
        # Get current simulation time
        current_time = traci.simulation.getTime()
        
        # Get phase decisions from controller for each junction
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
        
        # Collect episode stats
        if hasattr(controller, 'reward_history') and controller.reward_history:
            episode_rewards.append(controller.reward_history[-1])
        
        # Collect metrics
        vehicles = traci.vehicle.getIDList()
        if vehicles:
            avg_wait = sum(traci.vehicle.getWaitingTime(v) for v in vehicles) / len(vehicles)
            avg_speed = sum(traci.vehicle.getSpeed(v) for v in vehicles) / len(vehicles)
            episode_waiting_times.append(avg_wait)
            episode_speeds.append(avg_speed)
        
        # Step the simulation
        sim.step()
    
    # Episode statistics
    stats = {
        "episode": episode,
        "rewards": sum(episode_rewards) / len(episode_rewards) if episode_rewards else 0,
        "waiting_times": sum(episode_waiting_times) / len(episode_waiting_times) if episode_waiting_times else 0,
        "speeds": sum(episode_speeds) / len(episode_speeds) if episode_speeds else 0,
        "throughput": sim.get_throughput(),
        "q_table_size": len(controller.q_tables.get(tl_ids[0], {})) if hasattr(controller, 'q_tables') else 0
    }
    
    # Save the model for this episode
    if hasattr(controller, 'save_q_table'):
        model_filename = os.path.join(
            project_root, "data", "models", 
            f"{controller_type.replace(' ', '_').lower()}_optimized_episode_{episode}.pkl")
        controller.save_q_table(model_filename)
    
    # Close the simulation
    sim.close()
    
    return controller, stats

def collect_traffic_state(tl_ids):
    """Optimized traffic state collection"""
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
        
        # Initialize direction counts
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
            
            # Get lane data in optimized way (batch query)
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

def train_rl_faster(controller_type, episodes=20, steps_per_episode=200, 
                   learning_rate=0.2, discount_factor=0.9, exploration_rate=0.6,
                   exploration_decay=0.9, parallel_episodes=4, model_path=None):
    """
    Train an RL controller with optimized parameters for faster learning.
    
    Args:
        controller_type (str): Type of RL controller ('Wired RL' or 'Wireless RL')
        episodes (int): Number of training episodes (reduced)
        steps_per_episode (int): Number of steps per episode (reduced)
        learning_rate (float): Learning rate for Q-learning (increased)
        discount_factor (float): Discount factor for future rewards (reduced)
        exploration_rate (float): Initial exploration rate (increased)
        exploration_decay (float): Rate at which exploration decreases (faster decay)
        parallel_episodes (int): Number of episodes to run in parallel
        model_path (str): Path to a pre-trained model (optional)
    """
    # Path to the grid configuration
    config_path = os.path.join(project_root, "config", "maps", "grid_network_3x3.sumocfg")
    
    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}")
        return
    
    # Create output directory for models
    output_dir = os.path.join(project_root, "data", "models", "optimized")
    os.makedirs(output_dir, exist_ok=True)
    
    # Training statistics
    stats = {
        "episodes": episodes,
        "steps_per_episode": steps_per_episode,
        "learning_rate": learning_rate,
        "discount_factor": discount_factor,
        "exploration_rates": [],
        "rewards": [],
        "waiting_times": [],
        "speeds": [],
        "throughputs": [],
        "q_table_sizes": []
    }
    
    # Determine available CPU cores
    max_cores = mp.cpu_count() - 1  # Leave one core free
    parallel_episodes = min(parallel_episodes, max_cores)
    print(f"Training with {parallel_episodes} parallel episodes on {max_cores} available cores")
    
    # Main training loop with progress bar
    episode = 0
    latest_controller = None
    
    with tqdm(total=episodes, desc="Training Progress") as pbar:
        while episode < episodes:
            # Calculate batch size for parallel processing
            batch_size = min(parallel_episodes, episodes - episode)
            
            # Prepare batch of episodes
            batch_args = []
            for i in range(batch_size):
                current_episode = episode + i
                current_exploration = exploration_rate * (exploration_decay ** current_episode)
                
                # Get the latest model path if we have a controller
                current_model_path = model_path
                if latest_controller is not None and hasattr(latest_controller, 'save_q_table'):
                    # Save a temporary model for this batch
                    temp_model_path = os.path.join(output_dir, f"temp_model_{current_episode}.pkl")
                    latest_controller.save_q_table(temp_model_path)
                    current_model_path = temp_model_path
                
                batch_args.append((
                    config_path, controller_type, current_episode, current_exploration,
                    steps_per_episode, learning_rate, discount_factor, current_model_path
                ))
            
            # Run batch of episodes in parallel
            pool = mp.Pool(processes=batch_size)
            results = pool.starmap(train_worker, batch_args)
            pool.close()
            pool.join()
            
            # Process results
            for i, result in enumerate(results):
                if result is None:
                    continue
                    
                controller, episode_stats = result
                current_episode = episode + i
                
                # Update the latest controller (from the last episode)
                if i == batch_size - 1:
                    latest_controller = controller
                
                # Update stats
                stats["exploration_rates"].append(exploration_rate * (exploration_decay ** current_episode))
                stats["rewards"].append(episode_stats["rewards"])
                stats["waiting_times"].append(episode_stats["waiting_times"])
                stats["speeds"].append(episode_stats["speeds"])
                stats["throughputs"].append(episode_stats["throughput"])
                stats["q_table_sizes"].append(episode_stats["q_table_size"])
                
                # Print progress
                print(f"Episode {current_episode+1}: Reward={episode_stats['rewards']:.2f}, "
                     f"Wait={episode_stats['waiting_times']:.2f}s, Speed={episode_stats['speeds']:.2f}m/s")
            
            # Clean up temporary model files
            for i in range(batch_size):
                temp_model_path = os.path.join(output_dir, f"temp_model_{episode + i}.pkl")
                if os.path.exists(temp_model_path):
                    os.remove(temp_model_path)
            
            # Update progress
            episode += batch_size
            pbar.update(batch_size)
    
    # Save final model
    if latest_controller is not None and hasattr(latest_controller, 'save_q_table'):
        final_model_path = os.path.join(output_dir, f"{controller_type.replace(' ', '_').lower()}_optimized_final.pkl")
        latest_controller.save_q_table(final_model_path)
        print(f"Final model saved to {final_model_path}")
    
    # Save training statistics
    import json
    stats_filename = os.path.join(output_dir, f"{controller_type.replace(' ', '_').lower()}_optimized_stats.json")
    with open(stats_filename, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Training completed. Statistics saved to {stats_filename}")
    
    # Create learning curves
    import matplotlib.pyplot as plt
    
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot rewards
    if stats["rewards"]:
        axs[0, 0].plot(range(1, len(stats["rewards"])+1), stats["rewards"])
        axs[0, 0].set_title('Average Reward per Episode')
        axs[0, 0].set_xlabel('Episode')
        axs[0, 0].set_ylabel('Average Reward')
        axs[0, 0].grid(True)
    
    # Plot waiting times
    if stats["waiting_times"]:
        axs[0, 1].plot(range(1, len(stats["waiting_times"])+1), stats["waiting_times"])
        axs[0, 1].set_title('Average Waiting Time per Episode')
        axs[0, 1].set_xlabel('Episode')
        axs[0, 1].set_ylabel('Waiting Time (s)')
        axs[0, 1].grid(True)
    
    # Plot speeds
    if stats["speeds"]:
        axs[1, 0].plot(range(1, len(stats["speeds"])+1), stats["speeds"])
        axs[1, 0].set_title('Average Speed per Episode')
        axs[1, 0].set_xlabel('Episode')
        axs[1, 0].set_ylabel('Speed (m/s)')
        axs[1, 0].grid(True)
    
    # Plot exploration rate
    axs[1, 1].plot(range(1, len(stats["exploration_rates"])+1), stats["exploration_rates"])
    axs[1, 1].set_title('Exploration Rate')
    axs[1, 1].set_xlabel('Episode')
    axs[1, 1].set_ylabel('Exploration Rate')
    axs[1, 1].grid(True)
    
    plt.tight_layout()
    plot_filename = os.path.join(output_dir, f"{controller_type.replace(' ', '_').lower()}_optimized_learning_curves.png")
    plt.savefig(plot_filename)
    plt.close()
    
    print(f"Learning curves saved to {plot_filename}")
    
    return stats

def main():
    """Train an RL controller with optimized parameters for faster learning."""
    parser = argparse.ArgumentParser(description='Train RL controller with optimized parameters')
    parser.add_argument('--controller', type=str, default="Wired RL",
                    choices=["Wired RL", "Wireless RL"],
                    help='Type of RL controller to train')
    parser.add_argument('--episodes', type=int, default=20,
                    help='Number of training episodes')
    parser.add_argument('--steps', type=int, default=200,
                    help='Number of steps per episode')
    parser.add_argument('--lr', type=float, default=0.2,
                    help='Learning rate')
    parser.add_argument('--discount', type=float, default=0.9,
                    help='Discount factor')
    parser.add_argument('--exploration', type=float, default=0.6,
                    help='Initial exploration rate')
    parser.add_argument('--decay', type=float, default=0.9,
                    help='Exploration decay rate')
    parser.add_argument('--parallel', type=int, default=4,
                    help='Number of episodes to run in parallel')
    parser.add_argument('--model', type=str, default=None,
                    help='Path to a pre-trained model (optional)')
    args = parser.parse_args()
    
    print(f"Fast training of {args.controller} for {args.episodes} episodes")
    print(f"Parameters: lr={args.lr}, discount={args.discount}, exploration={args.exploration}, decay={args.decay}")
    print(f"Parallel episodes: {args.parallel}")
    
    train_rl_faster(
        args.controller,
        episodes=args.episodes,
        steps_per_episode=args.steps,
        learning_rate=args.lr,
        discount_factor=args.discount,
        exploration_rate=args.exploration,
        exploration_decay=args.decay,
        parallel_episodes=args.parallel,
        model_path=args.model
    )

if __name__ == "__main__":
    main()