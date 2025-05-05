import os
import sys
import argparse
import numpy as np
from pathlib import Path
import time
import traci

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.utils.sumo_integration import SumoSimulation
from src.ai.reinforcement_learning.q_learning_controller import QLearningController
from src.ai.reinforcement_learning.wired_rl_controller import WiredRLController
from src.ai.reinforcement_learning.wireless_rl_controller import WirelessRLController

def train_rl_controller(controller_type, episodes=100, steps_per_episode=500, 
                        learning_rate=0.15, discount_factor=0.95, exploration_rate=0.5,
                        exploration_decay=0.99, model_path=None):
    """
    Train an RL controller on the 3x3 grid network.
    
    Args:
        controller_type (str): Type of RL controller ('Wired RL' or 'Wireless RL')
        episodes (int): Number of training episodes
        steps_per_episode (int): Number of steps per episode
        learning_rate (float): Learning rate for Q-learning
        discount_factor (float): Discount factor for future rewards
        exploration_rate (float): Initial exploration rate
        exploration_decay (float): Rate at which exploration decreases
        model_path (str): Path to a pre-trained model (optional)
    """
    # Path to the 3x3 grid configuration
    config_path = os.path.join(project_root, "config", "maps", "grid_network_3x3.sumocfg")
    
    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}")
        return
    
    # Create output directory for models
    output_dir = os.path.join(project_root, "data", "models", "3x3_grid")
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
        "throughputs": []
    }
    
    # Main training loop
    for episode in range(episodes):
        print(f"\nEpisode {episode+1}/{episodes}")
        
        # Calculate exploration rate for this episode
        current_exploration = exploration_rate * (exploration_decay ** episode)
        stats["exploration_rates"].append(current_exploration)
        print(f"Exploration rate: {current_exploration:.4f}")
        
        # Initialize simulation
        sim = SumoSimulation(config_path, gui=False)
        sim.start()
        
        # Get traffic light IDs
        tl_ids = traci.trafficlight.getIDList()
        
        if not tl_ids:
            print("No traffic lights found!")
            sim.close()
            continue
        
        # Create controller
        if controller_type == "Wired RL":
            controller = WiredRLController(
                tl_ids,
                learning_rate=learning_rate,
                discount_factor=discount_factor,
                exploration_rate=current_exploration,
                model_path=model_path if episode == 0 and model_path else None
            )
        elif controller_type == "Wireless RL":
            controller = WirelessRLController(
                tl_ids,
                learning_rate=learning_rate,
                discount_factor=discount_factor,
                exploration_rate=current_exploration,
                model_path=model_path if episode == 0 and model_path else None
            )
        else:
            print(f"Invalid controller type: {controller_type}")
            sim.close()
            return
        
        # Episode statistics
        episode_rewards = []
        episode_waiting_times = []
        episode_speeds = []
        
        # Run the episode
        for step in range(steps_per_episode):
            # Collect traffic state
            traffic_state = {}
            for tl_id in tl_ids:
                # Similar traffic state collection as in run_3x3_simulation.py
                # (For brevity, this part is similar to the previous script)
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
                    # Determine direction based on lane ID and network structure
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
                if north_count > 0:
                    north_wait /= north_count
                if south_count > 0:
                    south_wait /= south_count
                if east_count > 0:
                    east_wait /= east_count
                if west_count > 0:
                    west_wait /= west_count
                
                # Store traffic state for this junction
                traffic_state[tl_id] = {
                    'north_count': north_count,
                    'south_count': south_count,
                    'east_count': east_count,
                    'west_count': west_count,
                    'north_wait': north_wait,
                    'south_wait': south_wait,
                    'east_wait': east_wait,
                    'west_wait': west_wait,
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
            
            # Print progress occasionally
            if step % 100 == 0:
                print(f"  Step {step}/{steps_per_episode}")
                if episode_rewards:
                    print(f"  Avg Reward: {sum(episode_rewards[-20:]) / min(len(episode_rewards[-20:]), 20):.2f}")
                if episode_waiting_times:
                    print(f"  Avg Wait Time: {sum(episode_waiting_times[-20:]) / min(len(episode_waiting_times[-20:]), 20):.2f}s")
        
        # Episode statistics
        if episode_rewards:
            avg_reward = sum(episode_rewards) / len(episode_rewards)
            stats["rewards"].append(avg_reward)
            print(f"Episode avg reward: {avg_reward:.2f}")
        
        if episode_waiting_times:
            avg_waiting_time = sum(episode_waiting_times) / len(episode_waiting_times)
            stats["waiting_times"].append(avg_waiting_time)
            print(f"Episode avg waiting time: {avg_waiting_time:.2f}s")
        
        if episode_speeds:
            avg_speed = sum(episode_speeds) / len(episode_speeds)
            stats["speeds"].append(avg_speed)
            print(f"Episode avg speed: {avg_speed:.2f}m/s")
        
        # Track throughput
        throughput = sim.stats.get("throughput", 0) if hasattr(sim, "stats") else 0
        stats["throughputs"].append(throughput)
        print(f"Episode throughput: {throughput} vehicles")
        
        # Close the simulation
        sim.close()
        
        # Save the model periodically
        if (episode + 1) % 5 == 0 or episode == episodes - 1:
            if hasattr(controller, 'save_q_table'):
                model_filename = os.path.join(output_dir, f"{controller_type.replace(' ', '_').lower()}_3x3_episode_{episode+1}.pkl")
                controller.save_q_table(model_filename)
                print(f"Saved model to {model_filename}")
    
    # Save training statistics
    import json
    stats_filename = os.path.join(output_dir, f"{controller_type.replace(' ', '_').lower()}_3x3_training_stats.json")
    with open(stats_filename, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Training completed. Statistics saved to {stats_filename}")
    
    # Create learning curves
    import matplotlib.pyplot as plt
    
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot rewards
    if stats["rewards"]:
        axs[0, 0].plot(range(1, episodes+1), stats["rewards"])
        axs[0, 0].set_title('Average Reward per Episode')
        axs[0, 0].set_xlabel('Episode')
        axs[0, 0].set_ylabel('Average Reward')
        axs[0, 0].grid(True)
    
    # Plot waiting times
    if stats["waiting_times"]:
        axs[0, 1].plot(range(1, episodes+1), stats["waiting_times"])
        axs[0, 1].set_title('Average Waiting Time per Episode')
        axs[0, 1].set_xlabel('Episode')
        axs[0, 1].set_ylabel('Waiting Time (s)')
        axs[0, 1].grid(True)
    
    # Plot speeds
    if stats["speeds"]:
        axs[1, 0].plot(range(1, episodes+1), stats["speeds"])
        axs[1, 0].set_title('Average Speed per Episode')
        axs[1, 0].set_xlabel('Episode')
        axs[1, 0].set_ylabel('Speed (m/s)')
        axs[1, 0].grid(True)
    
    # Plot exploration rate
    axs[1, 1].plot(range(1, episodes+1), stats["exploration_rates"])
    axs[1, 1].set_title('Exploration Rate')
    axs[1, 1].set_xlabel('Episode')
    axs[1, 1].set_ylabel('Exploration Rate')
    axs[1, 1].grid(True)
    
    plt.tight_layout()
    plot_filename = os.path.join(output_dir, f"{controller_type.replace(' ', '_').lower()}_3x3_learning_curves.png")
    plt.savefig(plot_filename)
    plt.close()
    
    print(f"Learning curves saved to {plot_filename}")
    
    return stats

def main():
    """Train an RL controller on the 3x3 grid."""
    parser = argparse.ArgumentParser(description='Train RL controller on 3x3 grid')
    parser.add_argument('--controller', type=str, default="Wired RL",
                    choices=["Wired RL", "Wireless RL"],
                    help='Type of RL controller to train')
    parser.add_argument('--episodes', type=int, default=50,
                    help='Number of training episodes')
    parser.add_argument('--steps', type=int, default=500,
                    help='Number of steps per episode')
    parser.add_argument('--lr', type=float, default=0.15,
                    help='Learning rate')
    parser.add_argument('--discount', type=float, default=0.95,
                    help='Discount factor')
    parser.add_argument('--exploration', type=float, default=0.5,
                    help='Initial exploration rate')
    parser.add_argument('--decay', type=float, default=0.99,
                    help='Exploration decay rate')
    parser.add_argument('--model', type=str, default=None,
                    help='Path to a pre-trained model (optional)')
    args = parser.parse_args()
    
    print(f"Training {args.controller} on 3x3 grid for {args.episodes} episodes")
    print(f"Parameters: lr={args.lr}, discount={args.discount}, exploration={args.exploration}, decay={args.decay}")
    
    train_rl_controller(
        args.controller,
        episodes=args.episodes,
        steps_per_episode=args.steps,
        learning_rate=args.lr,
        discount_factor=args.discount,
        exploration_rate=args.exploration,
        exploration_decay=args.decay,
        model_path=args.model
    )

if __name__ == "__main__":
    main()