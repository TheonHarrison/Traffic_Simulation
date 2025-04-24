import pygame
import os
import sys
import traci
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.ui.visualization import Visualization
from src.ui.traffic_renderer import TrafficRenderer, VehicleType
from src.ui.sumo_pygame_mapper import SumoNetworkParser, SumoPygameMapper
from src.utils.sumo_integration import SumoSimulation

class SumoVisualization:
    """
    Integrates SUMO simulation with Pygame visualization.
    """
    def __init__(self, sumo_config_path, width=1024, height=768, use_gui=False):
        """
        Initialize the SUMO visualization.
        
        Args:
            sumo_config_path (str): Path to the SUMO configuration file
            width (int): Width of the visualization window
            height (int): Height of the visualization window
            use_gui (bool): Whether to use SUMO GUI alongside the visualization
        """
        self.sumo_config_path = sumo_config_path
        self.width = width
        self.height = height
        self.use_gui = use_gui
        
        # Get the SUMO network file path from the config directory
        self.net_file_path = self._get_net_file_path()
        
        # Initialize the SUMO simulation
        self.simulation = SumoSimulation(sumo_config_path, gui=use_gui)
        
        # Initialize the visualization
        self.visualization = Visualization(width, height, "SUMO Traffic Visualization", self.net_file_path)
        
        # Create network parser and mapper
        self.network_parser = SumoNetworkParser(self.net_file_path)
        self.mapper = SumoPygameMapper(self.network_parser, width, height)
        
        # Create traffic renderer
        self.traffic_renderer = TrafficRenderer(self.visualization.screen, self.mapper)
        
        # Traffic light positions (will be filled during simulation)
        self.traffic_light_positions = {}
        
        # Simulation running flag
        self.running = False
        
        # Statistics
        self.stats = {
            "vehicles": 0,
            "avg_speed": 0.0,
            "avg_wait_time": 0.0,
            "throughput": 0,
            "step": 0,
            "mode": "Wired AI"  # Default mode, can be changed
        }
        
        # Performance metrics (to be collected during simulation)
        self.performance_metrics = {
            "wait_times": [],
            "speeds": [],
            "throughput": []
        }
        
        print(f"SUMO Visualization initialized with {width}x{height} window")
    
    def _get_net_file_path(self):
        """Extract the network file path from the SUMO configuration file."""
        import xml.etree.ElementTree as ET
        
        try:
            # Parse the SUMO config file
            tree = ET.parse(self.sumo_config_path)
            root = tree.getroot()
            
            # Find the net-file entry
            net_file = root.find(".//net-file")
            if net_file is not None:
                net_file_value = net_file.get("value")
                
                # If it's a relative path, convert to absolute path
                if not os.path.isabs(net_file_value):
                    config_dir = os.path.dirname(self.sumo_config_path)
                    return os.path.join(config_dir, net_file_value)
                return net_file_value
            
            print("Warning: Could not find net-file in SUMO config. Using default.")
            # Try to find a .net.xml file in the same directory as the config
            config_dir = os.path.dirname(self.sumo_config_path)
            net_files = [f for f in os.listdir(config_dir) if f.endswith(".net.xml")]
            if net_files:
                return os.path.join(config_dir, net_files[0])
            
            raise FileNotFoundError("No .net.xml file found in the config directory.")
        
        except Exception as e:
            print(f"Error getting net file path: {e}")
            return None
    
    def start(self):
        """Start the SUMO simulation and visualization."""
        try:
            # Start the SUMO simulation
            self.simulation.start()
            
            # Initialize traffic light positions
            self._initialize_traffic_light_positions()
            
            self.running = True
            print("SUMO Visualization started")
            return True
        
        except Exception as e:
            print(f"Error starting SUMO visualization: {e}")
            return False
    
    def _initialize_traffic_light_positions(self):
        """Initialize traffic light positions based on SUMO network."""
        try:
            # Get all traffic lights
            tl_ids = traci.trafficlight.getIDList()
            
            for tl_id in tl_ids:
                # Get the controlled junction
                junction_id = tl_id  # In SUMO, traffic light IDs often match junction IDs
                
                # If there's a junction with this ID, use its position
                if junction_id in self.network_parser.nodes:
                    self.traffic_light_positions[tl_id] = self.network_parser.nodes[junction_id]
                    continue
                
                # Otherwise, get the controlled links and use the first one's position
                links = traci.trafficlight.getControlledLinks(tl_id)
                if links and links[0]:
                    # Get the incoming lane
                    incoming_lane = links[0][0][0]
                    
                    # Get the lane shape
                    lane_shape = traci.lane.getShape(incoming_lane)
                    
                    # Use the last point of the lane shape (closest to the junction)
                    if lane_shape:
                        self.traffic_light_positions[tl_id] = lane_shape[-1]
                        continue
            
            print(f"Initialized {len(self.traffic_light_positions)} traffic light positions")
        
        except Exception as e:
            print(f"Error initializing traffic light positions: {e}")
    
    def _update_stats(self):
        """Update simulation statistics."""
        try:
            # Update vehicle count
            vehicles = traci.vehicle.getIDList()
            self.stats["vehicles"] = len(vehicles)
            
            # Update average speed and wait time
            if vehicles:
                total_speed = sum(traci.vehicle.getSpeed(v) for v in vehicles)
                total_wait_time = sum(traci.vehicle.getWaitingTime(v) for v in vehicles)
                
                self.stats["avg_speed"] = total_speed / len(vehicles)
                self.stats["avg_wait_time"] = total_wait_time / len(vehicles)
                
                # Store for performance metrics
                self.performance_metrics["speeds"].append(self.stats["avg_speed"])
                self.performance_metrics["wait_times"].append(self.stats["avg_wait_time"])
            else:
                self.stats["avg_speed"] = 0.0
                self.stats["avg_wait_time"] = 0.0
            
            # Update throughput (vehicles that have arrived at their destination)
            arrived = traci.simulation.getArrivedNumber()
            self.stats["throughput"] += arrived
            self.performance_metrics["throughput"].append(arrived)
            
            # Update step number
            self.stats["step"] = traci.simulation.getTime()
        
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def step(self, delay_ms=100):
        """
        Perform one simulation and visualization step with delay to slow down simulation.
        
        Args:
            delay_ms (int): Delay in milliseconds to slow down the simulation
        """
        if not self.running:
            return False
        
        try:
            # Add delay to slow down simulation
            pygame.time.delay(delay_ms)
            
            # Step the SUMO simulation
            self.simulation.step()
            
            # Update statistics
            self._update_stats()
            
            # Handle visualization events
            running = self.visualization.handle_events()
            if not running:
                self.close()
                return False
            
            # Clear the visualization
            self.visualization.clear()
            
            # Update renderer with current visualization settings
            self.traffic_renderer.update_view_settings(
                self.visualization.offset_x,
                self.visualization.offset_y,
                self.visualization.zoom
            )
            
            # Render the network
            self.traffic_renderer.render_network()
            
            # Render all vehicles
            vehicles = traci.vehicle.getIDList()
            for vehicle_id in vehicles:
                try:
                    # Get vehicle position
                    position = traci.vehicle.getPosition(vehicle_id)
                    
                    # Get vehicle angle (heading)
                    angle = traci.vehicle.getAngle(vehicle_id)
                    
                    # Get vehicle type
                    v_type = traci.vehicle.getTypeID(vehicle_id)
                    vehicle_type = self.traffic_renderer.map_vehicle_type(v_type)
                    
                    # Get speed and waiting time
                    speed = traci.vehicle.getSpeed(vehicle_id)
                    waiting_time = traci.vehicle.getWaitingTime(vehicle_id)
                    
                    # Render the vehicle
                    self.traffic_renderer.render_vehicle(
                        vehicle_id, position, angle, vehicle_type, 
                        speed, waiting_time, None  # Skip label for better performance
                    )
                
                except Exception as e:
                    print(f"Error rendering vehicle {vehicle_id}: {e}")
                    continue
            
            # Render all traffic lights
            for tl_id in traci.trafficlight.getIDList():
                try:
                    # Get traffic light state
                    state = traci.trafficlight.getRedYellowGreenState(tl_id)
                    
                    # Get position
                    if tl_id in self.traffic_light_positions:
                        position = self.traffic_light_positions[tl_id]
                        
                        # Render the traffic light
                        self.traffic_renderer.render_traffic_light(tl_id, position, state)
                
                except Exception as e:
                    print(f"Error rendering traffic light {tl_id}: {e}")
                    continue
            
            # Render junctions
            for junction_id in self.network_parser.nodes:
                self.traffic_renderer.render_junction(junction_id)
            
            # Render statistics
            formatted_stats = {
                "Vehicles": self.stats["vehicles"],
                "Avg Speed": f"{self.stats['avg_speed']:.2f} m/s",
                "Avg Wait Time": f"{self.stats['avg_wait_time']:.2f} s",
                "Throughput": self.stats["throughput"],
                "Simulation Time": f"{self.stats['step']:.1f} s",
                "Mode": self.stats["mode"]
            }
            self.visualization.draw_stats(formatted_stats)
            
            # Draw debug information including traffic light states
            self.draw_debug_info()
            
            # Update the visualization
            self.visualization.update()
            
            return True
        
        except Exception as e:
            print(f"Error in simulation step: {e}")
            return False
    
    def draw_debug_info(self):
        """Draw debug information including traffic light states."""
        y_offset = 100  # Start below the regular stats
        
        # Display traffic light states
        self.visualization.draw_text("Traffic Light States:", 10, y_offset, (0, 0, 0))
        y_offset += 20
        
        for tl_id in traci.trafficlight.getIDList()[:5]:  # Show first 5 traffic lights
            state = traci.trafficlight.getRedYellowGreenState(tl_id)
            phase_duration = traci.trafficlight.getPhaseDuration(tl_id)
            time_to_change = traci.trafficlight.getNextSwitch(tl_id) - traci.simulation.getTime()
            
            text = f"{tl_id}: {state} (next change in {time_to_change:.1f}s)"
            self.visualization.draw_text(text, 15, y_offset, (0, 0, 100))
            y_offset += 20
    
    def run(self, steps=1000, delay_ms=100):
        """
        Run the simulation for a specified number of steps.
        
        Args:
            steps (int): Number of simulation steps to run
            delay_ms (int): Delay in milliseconds between steps
        """
        if not self.start():
            return False
        
        for _ in range(steps):
            if not self.step(delay_ms):
                break
        
        self.close()
        return True
    
    def set_mode(self, mode):
        """Set the simulation mode (e.g., 'Wired AI', 'Wireless AI')."""
        self.stats["mode"] = mode
    
    def close(self):
        """Close the simulation and visualization."""
        if self.running:
            self.simulation.close()
            self.visualization.close()
            self.running = False
            print("SUMO Visualization closed")

# Test the SUMO visualization
if __name__ == "__main__":
    import os
    
    # Path to the SUMO configuration file
    sumo_config_path = os.path.join(project_root, "config", "maps", "grid_network.sumocfg")
    
    # Create and run the visualization
    visualization = SumoVisualization(sumo_config_path, width=1024, height=768, use_gui=False)
    visualization.run(steps=1000, delay_ms=100)  # Run for 1000 steps with 100ms delay