# src/run_enhanced_visualisation.py
import os
import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.ui.enhanced_sumo_visualisation import EnhancedSumoVisualisation
from src.ai.controller_factory import ControllerFactory
from src.utils.config_utils import create_temp_config

def run_enhanced_visualisation(config_path, controller_type, steps=1000, delay=50, model_path=None):
    """
    Run the enhanced visualisation with a specific controller.
    
    Args:
        config_path: Path to the SUMO configuration file
        controller_type: Type of controller to use
        steps: Number of simulation steps to run
        delay: Delay in milliseconds between steps
        model_path: Optional path to a specific model file for RL controllers
    """
    # Create the visualisation
    visualisation = EnhancedSumoVisualisation(config_path, width=1024, height=768, use_gui=False)
    visualisation.set_mode(controller_type)
    
    # Start the visualisation
    if not visualisation.start():
        print("Failed to start visualisation")
        return
    
    try:
        # Get traffic light IDs
        import traci
        tl_ids = traci.trafficlight.getIDList()
        
        if not tl_ids:
            print("No traffic lights found in the simulation!")
            visualisation.close()
            return
        
        # Create controller based on selected type
        controller_kwargs = {}
        if model_path and "RL" in controller_type and os.path.exists(model_path):
            controller_kwargs["model_path"] = model_path
        
        # Create the controller
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
                north_wait_avg = north_wait / max(1, north_count) if north_count > 0 else 0
                south_wait_avg = south_wait / max(1, south_count) if south_count > 0 else 0
                east_wait_avg = east_wait / max(1, east_count) if east_count > 0 else 0
                west_wait_avg = west_wait / max(1, west_count) if west_count > 0 else 0
                
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
        
        print(f"Total throughput: {sum(throughput)} vehicles")
    
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
                        help='Scenario file to run (without .rou.xml extension)')
    parser.add_argument('--controller', type=str, default="Wired AI",
                        choices=["Wired AI", "Wireless AI", "Traditional", "Wired RL", "Wireless RL"],
                        help='Controller type to use')
    parser.add_argument('--steps', type=int, default=1000,
                        help='Number of simulation steps to run')
    parser.add_argument('--delay', type=int, default=50,
                        help='Delay in milliseconds between steps')
    parser.add_argument('--model', type=str, default=None,
                        help='Path to a model file for RL controllers')
    args = parser.parse_args()
    
    # Define path to scenario directory
    scenarios_dir = os.path.join(project_root, "config", "scenarios")
    
    # Determine which configuration file to use
    if args.scenario:
        # First check if a temp config file for this scenario already exists
        temp_config = os.path.join(scenarios_dir, f"temp_{args.scenario}.sumocfg")
        if os.path.exists(temp_config):
            config_path = temp_config
        else:
            # Otherwise, check for the scenario .rou.xml file
            route_file = os.path.join(scenarios_dir, f"{args.scenario}.rou.xml")
            if os.path.exists(route_file):
                # Create a temporary config file
                network_file = os.path.join(project_root, "config", "maps", "traffic_grid_3x3.net.xml")
                config_path = create_temp_config(route_file, network_file, project_root)
            else:
                print(f"Scenario file not found: {route_file}")
                print(f"Available scenarios:")
                route_files = [f[:-8] for f in os.listdir(scenarios_dir) if f.endswith('.rou.xml')]
                for scenario in route_files:
                    print(f"  - {scenario}")
                return
    else:
        # Use the default configuration
        config_path = os.path.join(project_root, "config", "maps", "traffic_grid_3x3.sumocfg")
    
    print(f"Using configuration file: {config_path}")

    model_path = args.model
    if model_path and not os.path.exists(model_path) and "RL" in args.controller:
        print(f"Error: Model file not found: {model_path}")
        print("Using default parameters for RL controller")
        model_path = None

    # Run the visualisation
    run_enhanced_visualisation(config_path, args.controller, args.steps, args.delay, model_path)

if __name__ == "__main__":
    main()