import os
import sys
import argparse
from pathlib import Path

# add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.ui.enhanced_sumo_visualisation import EnhancedSumoVisualisation
from src.ai.controller_factory import ControllerFactory
from src.utils.config_utils import find_latest_model
import traci

def run_visualisation(controller_type, steps=1000, delay=50):
    """
    Run the enhanced visualisation on the 3x3 grid.
    
    Args:
        controller_type: Type of controller to use
        steps: Number of simulation steps
        delay: Delay between steps in milliseconds
        
    """
    # path to the 3x3 grid configuration
    config_path = os.path.join(project_root, "config", "maps", "grid_network_3x3.sumocfg")
    
    if not os.path.exists(config_path):
        print(f"Error: Config file not found: {config_path}")
        return
    
    # create the visualisation
    visualisation = EnhancedSumoVisualisation(config_path, width=1200, height=800, use_gui=False)
    visualisation.set_mode(controller_type)
    
    # start the visualisation
    if not visualisation.start():
        print("Failed to start visualisation")
        return
    
    try:
        # get traffic light IDs
        tl_ids = traci.trafficlight.getIDList()
        
        if not tl_ids:
            print("No traffic lights found in the simulation!")
            visualisation.close()
            return
        
        print(f"Found {len(tl_ids)} traffic lights: {tl_ids}")
        
        # look for a trained model if RL controller
        model_path = None
        if "RL" in controller_type:
            model_path = find_latest_model(controller_type)
            if model_path:
                print(f"Using trained model: {model_path}")
        
        # controller arguments
        controller_kwargs = {}
        if model_path:
            controller_kwargs["model_path"] = model_path
            
        controller = ControllerFactory.create_controller(controller_type, tl_ids, **controller_kwargs)
        
        print(f"Created {controller_type} controller")
        
        # run the visualisation
        for step in range(steps):
            # update traffic state in the controller
            traffic_state = {}
            
            # collect traffic state for each junction
            for tl_id in tl_ids:
                # get incoming lanes for this traffic light
                incoming_lanes = []
                for connection in traci.trafficlight.getControlledLinks(tl_id):
                    if connection and connection[0]:  # Check if connection exists
                        incoming_lane = connection[0][0]
                        if incoming_lane not in incoming_lanes:
                            incoming_lanes.append(incoming_lane)
                
                # count vehicles and collect metrics for each direction
                north_count = south_count = east_count = west_count = 0
                north_wait = south_wait = east_wait = west_wait = 0
                north_queue = south_queue = east_queue = west_queue = 0
                
                for lane in incoming_lanes:
                    # determine direction based on lane ID
                    direction = "unknown"
                    
                    # for vertical lanes
                    if any(pattern in lane for pattern in ["A0A1", "B0B1", "C0C1", "A1A2", "B1B2", "C1C2"]):
                        direction = "north"
                    elif any(pattern in lane for pattern in ["A1A0", "B1B0", "C1C0", "A2A1", "B2B1", "C2C1"]):
                        direction = "south"
                    # for horizontal lanes
                    elif any(pattern in lane for pattern in ["A0B0", "B0C0", "A1B1", "B1C1", "A2B2", "B2C2"]):
                        direction = "east"
                    elif any(pattern in lane for pattern in ["B0A0", "C0B0", "B1A1", "C1B1", "B2A2", "C2B2"]):
                        direction = "west"
                    
                    # count vehicles on this lane
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
                
                # calculate average waiting times
                if north_count > 0:
                    north_wait /= north_count
                if south_count > 0:
                    south_wait /= south_count
                if east_count > 0:
                    east_wait /= east_count
                if west_count > 0:
                    west_wait /= west_count
                
                # store traffic state for this junction
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
            
            # update controller with traffic state
            controller.update_traffic_state(traffic_state)
            
            # get current simulation time
            current_time = traci.simulation.getTime()
            
            # get phase decisions from controller for each junction
            for tl_id in tl_ids:
                phase = controller.get_phase_for_junction(tl_id, current_time)
                
                # set traffic light phase in SUMO
                try:
                    # get the current state length
                    current_state = traci.trafficlight.getRedYellowGreenState(tl_id)
                    
                    # ensure phase length matches traffic light state length
                    if len(phase) != len(current_state):
                        # adjust phase length silently without warning
                        if len(phase) < len(current_state):
                            phase = phase * (len(current_state) // len(phase)) + phase[:len(current_state) % len(phase)]
                        else:
                            phase = phase[:len(current_state)]
                    
                    traci.trafficlight.setRedYellowGreenState(tl_id, phase)
                except Exception as e:
                    print(f"Error setting traffic light state for {tl_id}: {e}")
            
            # step the visualisation
            if not visualisation.step(delay):
                break
            
            # print progress occasionally
            if step % 100 == 0:
                print(f"Step {step}/{steps}")
        
        # close the visualisation
        visualisation.close()
        
    except Exception as e:
        print(f"Error in visualisation: {e}")
        import traceback
        traceback.print_exc()
        visualisation.close()

def main():
    """Run the enhanced visualisation on the 3x3 grid."""
    parser = argparse.ArgumentParser(description='Visualize 3x3 grid traffic simulation')
    parser.add_argument('--controller', type=str, default="Traditional",
                        choices=["Traditional", "Wired AI", "Wireless AI", "Wired RL", "Wireless RL"],
                        help='Type of controller to use')
    parser.add_argument('--steps', type=int, default=1000,
                        help='Number of simulation steps')
    parser.add_argument('--delay', type=int, default=50,
                        help='Delay between steps in milliseconds')
    args = parser.parse_args()
    
    print(f"Running visualisation with {args.controller} controller for {args.steps} steps")
    run_visualisation(args.controller, args.steps, args.delay)

if __name__ == "__main__":
    main()