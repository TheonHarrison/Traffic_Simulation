import os
import sys
import argparse
import traci
from pathlib import Path
import glob
import re

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

import pygame
import time
from src.ui.enhanced_sumo_visualisation import EnhancedSumoVisualisation
from src.ai.controller_factory import ControllerFactory

def find_latest_model(controller_type):
    """
    Find the latest trained model for the specified controller type.
    """
    # convert controller type to filename format
    model_prefix = controller_type.replace(' ', '_').lower()
    
    # define the models directory
    models_dir = os.path.join(project_root, "data", "models")
    
    if not os.path.exists(models_dir):
        print(f"Models directory not found: {models_dir}")
        return None
    
    # find all model files for this controller type
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

def run_enhanced_visualisation(config_path, controller_type, steps=1000, delay=50, model_path=None):
    """
    visualisation with a specific controller.
    
    Args:
    
        config_path: Path to the SUMO configuration file
        controller_type: Type of controller to use
        steps: Number of simulation steps to run
        delay: Delay in milliseconds between steps
        model_path: Optional path to a specific model file for RL controllers
    """
    # create the visualisation
    visualisation = EnhancedSumoVisualisation(config_path, width=1024, height=768, use_gui=False)
    visualisation.set_mode(controller_type)
    
    # start the visualisation
    if not visualisation.start():
        print("Failed to start visualisation")
        return
    
    try:
        # Get traffic light IDs
        tl_ids = traci.trafficlight.getIDList()
        
        if not tl_ids:
            print("No traffic lights found in the simulation!")
            visualisation.close()
            return
        
        # Create controller based on selected type
        controller_kwargs = {}
        
        # For RL controllers, find and use the appropriate model
        if "RL" in controller_type:
            # If model path is provided directly, use it
            if model_path and os.path.exists(model_path):
                controller_kwargs["model_path"] = model_path
                print(f"Using specified model: {model_path}")
            # otherwise, find the latest trained model
            else:
                latest_model = find_latest_model(controller_type)
                if latest_model:
                    controller_kwargs["model_path"] = latest_model
                    print(f"Using latest model: {latest_model}")
                else:
                    print(f"Warning: No model found for {controller_type}. Will use default parameters.")
        
        # create the controller
        controller = ControllerFactory.create_controller(controller_type, tl_ids, **controller_kwargs)
        
        print(f"Created {controller_type} controller for traffic lights: {tl_ids}")
        
        # Run the simulation for specified number of steps
        for step in range(steps):
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
                    
                    # count vehicles on this lane
                    vehicle_count = traci.lane.getLastStepVehicleNumber(lane)
                    waiting_time = sum(traci.vehicle.getWaitingTime(v) for v in traci.lane.getLastStepVehicleIDs(lane))
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
                
                # Store traffic state for this junction
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
            
            # get phase decisions from controller for each junction
            for tl_id in tl_ids:
                phase = controller.get_phase_for_junction(tl_id, current_time)
                
                # Set traffic light phase in SUMO
                current_sumo_state = traci.trafficlight.getRedYellowGreenState(tl_id)
                
                # Only update if phase is different
                if phase != current_sumo_state:
                    traci.trafficlight.setRedYellowGreenState(tl_id, phase)
                    if step % 50 == 0:  # Don't print too much
                        print(f"Step {step}: Traffic light {tl_id} changed to {phase}")
            
            # Display step in the simulation
            if step % 50 == 0:
                print(f"Step #{step}/{steps} (Time: {current_time:.2f}s)")
            
            # Step the visualisation
            result = visualisation.step(delay)
            if not result:
                break
        
        # Close everything properly
        visualisation.close()
        
        # Report performance metrics
        if controller.response_times:
            avg_resp = sum(controller.response_times) / len(controller.response_times)
            print(f"Average controller response time: {avg_resp * 1000:.2f} ms")
        
        if controller.decision_times:
            avg_dec = sum(controller.decision_times) / len(controller.decision_times)
            print(f"Average controller decision time: {avg_dec * 1000:.2f} ms")
        
        # Report other simulation metrics
        wait_times = visualisation.performance_metrics["wait_times"]
        speeds = visualisation.performance_metrics["speeds"]
        throughput = visualisation.performance_metrics["throughput"]
        
        if wait_times:
            avg_wait = sum(wait_times) / len(wait_times)
            print(f"Average wait time: {avg_wait:.2f} seconds")
        
        if speeds:
            avg_speed = sum(speeds) / len(speeds)
            print(f"Average speed: {avg_speed:.2f} m/s")
        
        if throughput:
            total_throughput = sum(throughput)
            print(f"Total throughput: {total_throughput} vehicles")
    
    except Exception as e:
        print(f"Error during simulation: {e}")
        import traceback
        traceback.print_exc()
        visualisation.close()

def main():
    """Main function to run the enhanced visualisation"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run enhanced traffic visualisation')
    parser.add_argument('--scenario', type=str, default=None,
                        help='Scenario file to run (without .sumocfg extension)')
    parser.add_argument('--controller', type=str, default="Wired AI",
                        choices=["Wired AI", "Wireless AI", "Traditional", "Wired RL", "Wireless RL"],
                        help='Controller type to use')
    parser.add_argument('--steps', type=int, default=1000,
                        help='Number of simulation steps to run')
    parser.add_argument('--delay', type=int, default=50,
                        help='Delay in milliseconds between steps')
    parser.add_argument('--model', type=str, default=None,
                        help='Specific model path for RL controllers (optional)')
    args = parser.parse_args()
    
    # Determine which configuration file to use
    if args.scenario:
        # Use the specified scenario
        config_path = os.path.join(project_root, "config", "scenarios", f"{args.scenario}.sumocfg")
        if not os.path.exists(config_path):
            print(f"Scenario configuration file not found: {config_path}")
            return
    else:
        # Use the default configuration
        config_path = os.path.join(project_root, "config", "maps", "traffic_grid_3x3.sumocfg")
    
    print(f"Using configuration file: {config_path}")
    
    # Run the visualisation
    run_enhanced_visualisation(config_path, args.controller, args.steps, args.delay, args.model)

if __name__ == "__main__":
    main()