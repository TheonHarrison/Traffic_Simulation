import os
import sys
import argparse
from pathlib import Path

# add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import traci
from src.ai.controller_factory import ControllerFactory
from src.utils.sumo_integration import SumoSimulation
from src.utils.config_utils import find_latest_model

def run_simulation(controller_type, steps=1000, gui=False, delay=0):
    """
    Run a simulation with the 3x3 grid and specified controller type.
    
    Args:
        controller_type: Type of controller to use
        steps: Number of simulation steps to run
        gui: Whether to use the SUMO GUI
        delay: Delay between steps in milliseconds
        
    """
    # Set up configuration paths
    config_path = os.path.join(project_root, "config", "maps", "grid_network_3x3.sumocfg")
    
    # Check if the configuration file exists
    if not os.path.exists(config_path):
        print(f"Configuration file not found: {config_path}")
        return
    
    # Initialise the simulation
    sim = SumoSimulation(config_path, gui=gui)
    
    # Start the simulation
    sim.start()
    
    try:
        # Get traffic light IDs
        tl_ids = traci.trafficlight.getIDList()
        
        if not tl_ids:
            print("No traffic lights found in the simulation!")
            return
        
        print(f"Found {len(tl_ids)} traffic lights: {tl_ids}")
        
        # Determine if we should load a model (for RL controllers)
        model_path = None
        if "RL" in controller_type:
            model_path = find_latest_model(controller_type)
            if model_path:
                print(f"Using pre-trained model: {model_path}")
        
        # Create the controller
        controller_kwargs = {}
        if model_path:
            controller_kwargs["model_path"] = model_path
            
        controller = ControllerFactory.create_controller(controller_type, tl_ids, **controller_kwargs)
        
        print(f"Created {controller_type} controller")
        
        # Initialise throughput tracking
        throughput = 0
        
        # Run the simulation
        for step in range(steps):
            # Collect traffic state data
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
                # Mapping based on 3x3 grid naming convention
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
                
                # Calculate average waiting times for vehicles in each direction
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
                        print(f"Warning: Phase length mismatch for {tl_id}. Adjusting...")
                        if len(phase) < len(current_state):
                            # Extend phase by repeating
                            phase = phase * (len(current_state) // len(phase) + 1)
                            phase = phase[:len(current_state)]
                        else:
                            # Truncate phase
                            phase = phase[:len(current_state)]
                    
                    # Update the traffic light state
                    traci.trafficlight.setRedYellowGreenState(tl_id, phase)
                except Exception as e:
                    print(f"Error setting traffic light state for {tl_id}: {e}")
            
            # Apply delay if specified
            if delay > 0:
                import time
                time.sleep(delay / 1000.0)
            
            # Step the simulation
            sim.step()
            
            # Update throughput - track vehicles that have completed their routes
            throughput += traci.simulation.getArrivedNumber()
            
            # Print progress occasionally
            if step % 100 == 0:
                # Calculate some metrics
                vehicles = traci.vehicle.getIDList()
                avg_speed = 0
                avg_wait = 0
                if vehicles:
                    avg_speed = sum(traci.vehicle.getSpeed(v) for v in vehicles) / len(vehicles)
                    avg_wait = sum(traci.vehicle.getWaitingTime(v) for v in vehicles) / len(vehicles)
                
                print(f"Step {step}/{steps} - Vehicles: {len(vehicles)}, "
                      f"Avg Speed: {avg_speed:.2f} m/s, Avg Wait: {avg_wait:.2f} s")
        
        # calculate final metrics
        vehicles = traci.vehicle.getIDList()
        avg_speed = 0
        avg_wait = 0
        
        if vehicles:
            avg_speed = sum(traci.vehicle.getSpeed(v) for v in vehicles) / len(vehicles)
            avg_wait = sum(traci.vehicle.getWaitingTime(v) for v in vehicles) / len(vehicles)
        
        print("\nSimulation Completed")
        print(f"Final Metrics:")
        print(f"  Vehicles in network: {len(vehicles)}")
        print(f"  Throughput: {throughput}")
        print(f"  Average Speed: {avg_speed:.2f} m/s")
        print(f"  Average Wait Time: {avg_wait:.2f} s")
        
        # if using an RL controller, print training stats
        if "RL" in controller_type and hasattr(controller, 'get_q_table_stats'):
            q_stats = controller.get_q_table_stats()
            print("\nRL Controller Stats:")
            print(f"  Q-table Entries: {q_stats.get('total_entries', 0)}")
            print(f"  Unique States: {q_stats.get('unique_states', 0)}")
        
    finally:
        # Close the simulation
        sim.close()

def main():
    """Run the 3x3 grid simulation with a specified controller."""
    parser = argparse.ArgumentParser(description='Run 3x3 grid traffic simulation')
    parser.add_argument('--controller', type=str, default="Traditional",
                        choices=["Traditional", "Wired AI", "Wireless AI", "Wired RL", "Wireless RL"],
                        help='Type of controller to use')
    parser.add_argument('--steps', type=int, default=1000,
                        help='Number of simulation steps')
    parser.add_argument('--gui', action='store_true',
                        help='Use SUMO GUI')
    parser.add_argument('--delay', type=int, default=0,
                        help='Delay between steps in milliseconds')
    args = parser.parse_args()
    
    print(f"Running 3x3 grid simulation with {args.controller} controller")
    run_simulation(args.controller, args.steps, args.gui, args.delay)

if __name__ == "__main__":
    main()