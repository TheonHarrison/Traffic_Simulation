
import os
import sys
import argparse
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.utils.sumo_integration import SumoSimulation
from src.ai.controller_factory import ControllerFactory
from src.utils.config_utils import find_latest_model
import traci

def run_comparison(controller_types, steps=1000, runs=3):
    """
    Run a comparison of different controllers on the 3x3 grid.
    
    Args:
        controller_types: List of controller types to compare
        steps: Number of simulation steps per run
        runs: Number of runs per controller for statistical significance
    
    Returns:
        Dictionary of comparison results
    """
    # Path to the 3x3 grid configuration
    config_path = os.path.join(project_root, "config", "maps", "grid_network_3x3.sumocfg")
    
    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}")
        return {}
    
    # Initialise results
    results = {
        controller_type: {
            "waiting_times": [],
            "speeds": [],
            "throughputs": [],
            "response_times": [],
            "decision_times": [],
            "avg_waiting_time": 0,
            "avg_speed": 0,
            "avg_throughput": 0,
            "avg_response_time": 0,
            "avg_decision_time": 0
        }
        for controller_type in controller_types
    }
    
    # Run comparison for each controller
    for controller_type in controller_types:
        print(f"\nTesting {controller_type}...")
        
        # Look for a trained model if RL controller
        model_path = None
        if "RL" in controller_type:
            model_path = find_latest_model(controller_type)
            if model_path:
                print(f"Using trained model: {model_path}")
            else:
                print(f"Warning: No trained model found for {controller_type}")
        
        # Run multiple times for statistical significance
        for run in range(runs):
            print(f"  Run {run+1}/{runs}...")
            
            # Initialise simulation
            sim = SumoSimulation(config_path, gui=False)
            sim.start()
            
            try:
                # Get traffic light IDs
                tl_ids = traci.trafficlight.getIDList()
                
                if not tl_ids:
                    print("  No traffic lights found!")
                    sim.close()
                    continue
                
                # Create controller
                controller_kwargs = {}
                if model_path:
                    controller_kwargs["model_path"] = model_path
                    
                controller = ControllerFactory.create_controller(controller_type, tl_ids, **controller_kwargs)
                
                # Run metrics
                waiting_times = []
                speeds = []
                throughput = 0
                
                # Run the simulation
                for step in range(steps):
                    # Collect traffic state (same as in training script)
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
                                if len(phase) < len(current_state):
                                    phase = phase * (len(current_state) // len(phase)) + phase[:len(current_state) % len(phase)]
                                else:
                                    phase = phase[:len(current_state)]
                            
                            traci.trafficlight.setRedYellowGreenState(tl_id, phase)
                        except Exception as e:
                            print(f"  Error setting traffic light state for {tl_id}: {e}")
                    
                    # Collect metrics
                    vehicles = traci.vehicle.getIDList()
                    if vehicles:
                        avg_wait = sum(traci.vehicle.getWaitingTime(v) for v in vehicles) / len(vehicles)
                        avg_speed = sum(traci.vehicle.getSpeed(v) for v in vehicles) / len(vehicles)
                        waiting_times.append(avg_wait)
                        speeds.append(avg_speed)
                    
                    # Update throughput
                    throughput += traci.simulation.getArrivedNumber()
                    
                    # Step the simulation
                    sim.step()
                    
                    # Print progress
                    if step % 200 == 0:
                        print(f"    Step {step}/{steps}")
                
                # Store run results
                if waiting_times:
                    results[controller_type]["waiting_times"].append(sum(waiting_times) / len(waiting_times))
                
                if speeds:
                    results[controller_type]["speeds"].append(sum(speeds) / len(speeds))
                
                results[controller_type]["throughputs"].append(throughput)
                
                # Store controller metrics
                if hasattr(controller, 'response_times') and controller.response_times:
                    avg_response = sum(controller.response_times) / len(controller.response_times)
                    results[controller_type]["response_times"].append(avg_response)
                
                if hasattr(controller, 'decision_times') and controller.decision_times:
                    avg_decision = sum(controller.decision_times) / len(controller.decision_times)
                    results[controller_type]["decision_times"].append(avg_decision)
                
                # Print run metrics
                print(f"    Run {run+1} completed:")
                print(f"      Avg waiting time: {results[controller_type]['waiting_times'][-1]:.2f}s")
                print(f"      Avg speed: {results[controller_type]['speeds'][-1]:.2f}m/s")
                print(f"      Throughput: {results[controller_type]['throughputs'][-1]} vehicles")
            
            finally:
                # Close the simulation
                sim.close()
        
        # Calculate averages across runs
        for metric in ["waiting_times", "speeds", "throughputs", "response_times", "decision_times"]:
            values = results[controller_type][metric]
            if values:
                results[controller_type][f"avg_{metric[:-1]}"] = sum(values) / len(values)
        
        # Print controller summary
        print(f"\n{controller_type} Summary:")
        print(f"  Avg waiting time: {results[controller_type]['avg_waiting_time']:.2f}s")
        print(f"  Avg speed: {results[controller_type]['avg_speed']:.2f}m/s")
        print(f"  Avg throughput: {results[controller_type]['avg_throughput']:.2f} vehicles")
        if results[controller_type]["response_times"]:
            print(f"  Avg response time: {results[controller_type]['avg_response_time']*1000:.2f}ms")
        if results[controller_type]["decision_times"]:
            print(f"  Avg decision time: {results[controller_type]['avg_decision_time']*1000:.2f}ms")
    
    return results

def visualise_comparison(results):
    """
    Create visualisation of comparison results.
    
    Args:
        results: Dictionary of comparison results
    """
    # Create output directory
    output_dir = os.path.join(project_root, "data", "outputs", "3x3_comparison")
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract controller types
    controller_types = list(results.keys())
    
    # Create comparison plots for different metrics
    metrics = [
        ("avg_waiting_time", "Average Waiting Time (s)"),
        ("avg_speed", "Average Speed (m/s)"),
        ("avg_throughput", "Throughput (vehicles)")
    ]
    
    # Add controller-specific metrics if available
    if any("avg_response_time" in results[c] and results[c]["avg_response_time"] > 0 for c in controller_types):
        metrics.append(("avg_response_time", "Average Response Time (ms)"))
    
    if any("avg_decision_time" in results[c] and results[c]["avg_decision_time"] > 0 for c in controller_types):
        metrics.append(("avg_decision_time", "Average Decision Time (ms)"))
    
    # Create a figure with subplots
    fig, axs = plt.subplots(len(metrics), 1, figsize=(10, 4*len(metrics)))
    
    # Ensure axs is always a list
    if len(metrics) == 1:
        axs = [axs]
    
    # Plot each metric
    for i, (metric, title) in enumerate(metrics):
        values = []
        for controller in controller_types:
            # Convert milliseconds for time metrics in the plot
            if metric in ["avg_response_time", "avg_decision_time"]:
                values.append(results[controller].get(metric, 0) * 1000)  # Convert to ms
            else:
                values.append(results[controller].get(metric, 0))
        
        # Create bar chart
        bars = axs[i].bar(range(len(controller_types)), values, color=plt.cm.tab10.colours[:len(controller_types)])
        
        # Add value labels on bars
        for j, bar in enumerate(bars):
            height = bar.get_height()
            axs[i].text(bar.get_x() + bar.get_width()/2., height + 0.01*max(values) if values else 0,
                    f'{values[j]:.2f}', ha='center', va='bottom')
        
        # Set title and labels
        axs[i].set_title(title)
        axs[i].set_ylabel(title.split('(')[0].strip())
        axs[i].set_xticks(range(len(controller_types)))
        axs[i].set_xticklabels(controller_types, rotation=45, ha='right')
        axs[i].grid(True, axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    
    # Save the figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"controller_comparison_3x3_{timestamp}.png")
    plt.savefig(filename, dpi=300)
    plt.close()
    
    print(f"Comparison visualisation saved to {filename}")
    
    # Save results as JSON
    results_file = os.path.join(output_dir, f"controller_comparison_3x3_{timestamp}.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Comparison results saved to {results_file}")

def main():
    """Run comparison of controllers on the 3x3 grid."""
    parser = argparse.ArgumentParser(description='Compare controllers on 3x3 grid')
    parser.add_argument('--controllers', type=str, nargs='+',
                    choices=["Traditional", "Wired AI", "Wireless AI", "Wired RL", "Wireless RL"],
                    default=["Traditional", "Wired AI", "Wireless AI"],
                    help='Controller types to compare')
    parser.add_argument('--steps', type=int, default=1000,
                    help='Number of simulation steps')
    parser.add_argument('--runs', type=int, default=3,
                    help='Number of runs per controller')
    args = parser.parse_args()
    
    print(f"Comparing controllers on 3x3 grid: {args.controllers}")
    print(f"Running {args.runs} runs of {args.steps} steps each")
    
    # Run the comparison
    results = run_comparison(args.controllers, args.steps, args.runs)
    
    # Visualize the results
    if results:
        visualise_comparison(results)
    else:
        print("No results to visualise")

if __name__ == "__main__":
    main()