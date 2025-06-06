import os
import sys
import time
from pathlib import Path

# add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

import traci
from src.utils.sumo_integration import SumoSimulation
from src.ai.controller_factory import ControllerFactory
from src.ui.enhanced_sumo_visualisation import EnhancedSumoVisualisation

class ScenarioRunner:
    """
    Class for running SUMO traffic scenarios with different controllers.
    """
    def __init__(self, network_file=None):
        """
        Initialise the scenario runner.
        """
        self.project_root = project_root
        
        if network_file is None:
            network_file = os.path.join(project_root, "config", "maps", "traffic_grid_3x3.net.xml")
        
        self.network_file = network_file
        self.results_dir = os.path.join(project_root, "data", "outputs", "scenarios")
        
        # ensure results directory exists
        os.makedirs(self.results_dir, exist_ok=True)
    
    def create_temp_config(self, route_file):
        """
        Create a temporary SUMO configuration file.
        """
        # create a unique config file name
        config_name = f"temp_{os.path.basename(route_file).split('.')[0]}.sumocfg"
        config_path = os.path.join(project_root, "config", "scenarios", config_name)
        
        # write the config file
        with open(config_path, 'w') as f:
            f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
                            <configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
                                <input>
                                    <net-file value="{self.network_file}"/>
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
        
        return config_path
    
    def run_scenario(self, scenario_file, controller_type, steps=1000, 
                    gui=False, delay=0, collect_metrics=True, model_path=None):
        """
        run a specific scenario with a given controller type.
        """
        # create a SUMO configuration file for this run
        sumo_config = self.create_temp_config(scenario_file)
        
        # initialise metrics collection
        metrics = {
            "controller_type": controller_type,
            "scenario": os.path.basename(scenario_file),
            "steps": steps,
            "waiting_times": [],
            "speeds": [],
            "throughput": 0,
            "response_times": [],
            "decision_times": []
        }
        
        controller = None
        
        # choose between GUI and non-GUI simulation
        if gui:
            # use Python GUI (EnhancedSumoVisualisation)
            visualisation = EnhancedSumoVisualisation(sumo_config, width=1024, height=768, use_gui=False)
            visualisation.set_mode(controller_type)
            
            if not visualisation.start():
                print("Failed to start visualisation")
                return metrics
            
            # get traffic light IDs
            tl_ids = traci.trafficlight.getIDList()
            
            if not tl_ids:
                print("Warning: No traffic lights found in the simulation!")
                visualisation.close()
                return metrics
            
            # create controller with model_path if provided
            controller_kwargs = {}
            if model_path and "RL" in controller_type:
                controller_kwargs["model_path"] = model_path
                
            controller = ControllerFactory.create_controller(controller_type, tl_ids, **controller_kwargs)
            
            print(f"Running scenario {os.path.basename(scenario_file)} with {controller_type} controller using Python GUI...")
            
            # main simulation loop
            for step in range(steps):
                # collect traffic state
                traffic_state = self._collect_traffic_state(tl_ids)
                
                # update controller with traffic state
                controller.update_traffic_state(traffic_state)
                
                # get current simulation time
                current_time = traci.simulation.getTime()
                
                # get phase decisions from controller for each junction
                for tl_id in tl_ids:
                    phase = controller.get_phase_for_junction(tl_id, current_time)
                    
                    # set traffic light phase in SUMO
                    current_sumo_state = traci.trafficlight.getRedYellowGreenState(tl_id)
                    
                    # ensure phase length matches traffic light state length
                    if len(phase) != len(current_sumo_state):
                        if len(phase) < len(current_sumo_state):
                            # Extend by repeating the pattern
                            phase = phase * (len(current_sumo_state) // len(phase)) + phase[:len(current_sumo_state) % len(phase)]
                        else:
                            # Truncate to expected length
                            phase = phase[:len(current_sumo_state)]
                    
                    # only update if phase is different
                    if phase != current_sumo_state:
                        traci.trafficlight.setRedYellowGreenState(tl_id, phase)
                
                # collect metrics if enabled
                if collect_metrics:
                    self._update_metrics(metrics)
                
                # step the visualisation
                if not visualisation.step(delay):
                    break
                
                # print progress
                if step % 100 == 0:
                    print(f"Step {step}/{steps}")
            
            # close visualisation
            visualisation.close()
            
        else:
            # non-GUI simulation / use standard SUMO
            sim = SumoSimulation(sumo_config, gui=False)
            sim.start()
            
            try:
                # get traffic light IDs
                tl_ids = traci.trafficlight.getIDList()
                
                if not tl_ids:
                    print("Warning: No traffic lights found in the simulation!")
                    return metrics
                
                # create controller with model_path if provided
                controller_kwargs = {}
                if model_path and "RL" in controller_type:
                    controller_kwargs["model_path"] = model_path
                    
                controller = ControllerFactory.create_controller(controller_type, tl_ids, **controller_kwargs)
                
                print(f"Running scenario {os.path.basename(scenario_file)} with {controller_type} controller...")
                
                # main simulation loop
                for step in range(steps):
                    # Collect traffic state
                    traffic_state = self._collect_traffic_state(tl_ids)
                    
                    # update controller with traffic state
                    controller.update_traffic_state(traffic_state)
                    
                    # get current simulation time
                    current_time = traci.simulation.getTime()
                    
                    # get phase decisions from controller for each junction
                    for tl_id in tl_ids:
                        phase = controller.get_phase_for_junction(tl_id, current_time)
                        
                        # set traffic light phase in SUMO
                        current_sumo_state = traci.trafficlight.getRedYellowGreenState(tl_id)
                        
                        # ensure phase length matches traffic light state length
                        if len(phase) != len(current_sumo_state):
                            if len(phase) < len(current_sumo_state):
                                # extend by repeating the pattern
                                phase = phase * (len(current_sumo_state) // len(phase)) + phase[:len(current_sumo_state) % len(phase)]
                            else:
                                # truncate to expected length
                                phase = phase[:len(current_sumo_state)]
                        
                        # only update if phase is different
                        if phase != current_sumo_state:
                            traci.trafficlight.setRedYellowGreenState(tl_id, phase)
                    
                    # collect metrics if enabled
                    if collect_metrics:
                        self._update_metrics(metrics)
                    
                    # step the simulation
                    sim.step()
                    
                    # add delay if specified
                    if delay > 0:
                        time.sleep(delay / 1000.0)
                    
                    # print progress
                    if step % 100 == 0:
                        print(f"Step {step}/{steps}")
            
            finally:
                # make sure to always close the simulation
                if 'sim' in locals() and sim.running:
                    sim.close()
        
        # store final metrics for both GUI and non-GUI modes
        if collect_metrics and controller:
            # calculate final averages for metrics that aren't already calculated
            if "avg_waiting_time" not in metrics and metrics["waiting_times"]:
                metrics["avg_waiting_time"] = sum(metrics["waiting_times"]) / len(metrics["waiting_times"])
            elif "avg_waiting_time" not in metrics:
                metrics["avg_waiting_time"] = 0
            
            if "avg_speed" not in metrics and metrics["speeds"]:
                metrics["avg_speed"] = sum(metrics["speeds"]) / len(metrics["speeds"])
            elif "avg_speed" not in metrics:
                metrics["avg_speed"] = 0
                
            # get controller metrics
            if hasattr(controller, 'response_times') and controller.response_times:
                metrics["response_times"] = controller.response_times
                metrics["avg_response_time"] = sum(controller.response_times) / len(controller.response_times)
            else:
                metrics["avg_response_time"] = 0
            
            if hasattr(controller, 'decision_times') and controller.decision_times:
                metrics["decision_times"] = controller.decision_times
                metrics["avg_decision_time"] = sum(controller.decision_times) / len(controller.decision_times)
            else:
                metrics["avg_decision_time"] = 0
            
            # print summary
            print("\nScenario Results:")
            print(f"Average Waiting Time: {metrics['avg_waiting_time']:.2f} seconds")
            print(f"Average Speed: {metrics['avg_speed']:.2f} m/s")
            print(f"Total Throughput: {metrics['throughput']} vehicles")
            print(f"Average Response Time: {metrics['avg_response_time']*1000:.2f} ms")
            print(f"Average Decision Time: {metrics['avg_decision_time']*1000:.2f} ms")
        
        return metrics
    
    def _collect_traffic_state(self, tl_ids):
        """
        Collect the current traffic state for all traffic lights.
        """
        traffic_state = {}
        
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
                # determine direction based on lane ID - updated for 3x3 grid
                direction = "unknown"
                
                # for vertical lanes (north direction)
                if any(pattern in lane for pattern in ["A0A1", "B0B1", "C0C1", "A1A2", "B1B2", "C1C2"]):
                    direction = "north"
                # for vertical lanes (south direction)
                elif any(pattern in lane for pattern in ["A1A0", "B1B0", "C1C0", "A2A1", "B2B1", "C2C1"]):
                    direction = "south"
                # for horizontal lanes (east direction)
                elif any(pattern in lane for pattern in ["A0B0", "B0C0", "A1B1", "B1C1", "A2B2", "B2C2"]):
                    direction = "east"
                # for horizontal lanes (west direction)
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
            
            # calculate average waiting times (avoiding division by zero)
            avg_north_wait = north_wait / max(1, north_count) if north_count > 0 else 0
            avg_south_wait = south_wait / max(1, south_count) if south_count > 0 else 0
            avg_east_wait = east_wait / max(1, east_count) if east_count > 0 else 0
            avg_west_wait = west_wait / max(1, west_count) if west_count > 0 else 0
            
            # store traffic state for this junction
            traffic_state[tl_id] = {
                'north_count': north_count,
                'south_count': south_count,
                'east_count': east_count,
                'west_count': west_count,
                'north_wait': avg_north_wait,
                'south_wait': avg_south_wait,
                'east_wait': avg_east_wait,
                'west_wait': avg_west_wait,
                'north_queue': north_queue,
                'south_queue': south_queue,
                'east_queue': east_queue,
                'west_queue': west_queue
            }
        
        return traffic_state
    
    def _update_metrics(self, metrics):
        """
        Update performance metrics with current simulation state.
        """
        # Get all vehicles
        vehicles = traci.vehicle.getIDList()
        
        # update throughput (vehicles that have arrived at destination)
        arrived = traci.simulation.getArrivedNumber()
        metrics["throughput"] += arrived
        
        # skip other metrics if no vehicles
        if not vehicles:
            return
        
        # calculate average waiting time
        total_waiting_time = sum(traci.vehicle.getWaitingTime(v) for v in vehicles)
        avg_waiting_time = total_waiting_time / len(vehicles)
        metrics["waiting_times"].append(avg_waiting_time)
        
        # calculate average speed
        total_speed = sum(traci.vehicle.getSpeed(v) for v in vehicles)
        avg_speed = total_speed / len(vehicles)
        metrics["speeds"].append(avg_speed)