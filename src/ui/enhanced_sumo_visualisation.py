import pygame
import os
import sys
import traci
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.ui.enhanced_renderer import EnhancedTrafficRenderer
from src.ui.sumo_pygame_mapper import SumoNetworkParser, SumoPygameMapper
from src.utils.sumo_integration import SumoSimulation

class EnhancedSumoVisualisation:
    """
    Enhanced SUMO visualisation with improved graphics.
    """
    def __init__(self, sumo_config_path, width=1024, height=768, use_gui=False):
        """
        Initialise the enhanced SUMO visualisation.
        
        Args:
            sumo_config_path (str): Path to the SUMO configuration file
            width (int): Width of the visualisation window
            height (int): Height of the visualisation window
            use_gui (bool): Whether to use SUMO GUI alongside the visualisation
        """
        self.sumo_config_path = sumo_config_path
        self.width = width
        self.height = height
        self.use_gui = use_gui
        
        # get the SUMO network file path from the config directory
        self.net_file_path = self._get_net_file_path()
        
        # Initialise the SUMO simulation
        self.simulation = SumoSimulation(sumo_config_path, gui=use_gui)
        
        # Initialise pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Enhanced SUMO Traffic Visualisation")
        
        # Create network parser and mapper
        self.network_parser = SumoNetworkParser(self.net_file_path)
        self.mapper = SumoPygameMapper(self.network_parser, width, height)
        
        # Set a better initial view position and zoom
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 2.0
        self._center_view()
        
        # Create traffic renderer
        self.traffic_renderer = EnhancedTrafficRenderer(self.screen, self.mapper,
                                                     self.offset_x, 
                                                     self.offset_y,
                                                     self.zoom)
        
        # traffic light positions (will be filled during simulation)
        self.traffic_light_positions = {}
        
        # mouse tracking for dragging
        self.dragging = False
        self.drag_start = None
        
        # clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.fps = 30
        
        # load fonts
        self.font = pygame.font.SysFont("Arial", 16)
        self.id_font = pygame.font.SysFont("Arial", 12)
        
        # simulation running flag
        self.running = False
        
        # stats
        self.stats = {
            "vehicles": 0,
            "avg_speed": 0.0,
            "avg_wait_time": 0.0,
            "throughput": 0,
            "step": 0,
            "mode": "Wired AI"  # Default mode
        }
        
        # Performance metrics (to be collected during simulation)
        self.performance_metrics = {
            "wait_times": [],
            "speeds": [],
            "throughput": []
        }
        
        print(f"Enhanced SUMO Visualisation initialized with {width}x{height} window")
    
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
                
                # if it's a relative path, convert to absolute path
                if not os.path.isabs(net_file_value):
                    config_dir = os.path.dirname(self.sumo_config_path)
                    return os.path.join(config_dir, net_file_value)
                return net_file_value
            
            print("Warning: Could not find net-file in SUMO config. Using default.")
            # try to find a .net.xml file in the same directory as the config
            config_dir = os.path.dirname(self.sumo_config_path)
            net_files = [f for f in os.listdir(config_dir) if f.endswith(".net.xml")]
            if net_files:
                return os.path.join(config_dir, net_files[0])
            
            raise FileNotFoundError("No .net.xml file found in the config directory.")
        
        except Exception as e:
            print(f"Error getting net file path: {e}")
            return None
    
    def _center_view(self):
        """center the view on the simulation area"""
        if hasattr(self.mapper, 'min_x') and hasattr(self.mapper, 'max_x'):
            # calculate center of the network
            center_x = (self.mapper.min_x + self.mapper.max_x) / 2
            center_y = (self.mapper.min_y + self.mapper.max_y) / 2
            
            # set offsets to center the view
            self.offset_x = self.width / 2 - center_x * self.zoom * self.mapper.scale
            self.offset_y = self.height / 2 - center_y * self.zoom * self.mapper.scale
            
            # update traffic renderer
            if hasattr(self, 'traffic_renderer'):
                self.traffic_renderer.update_view_settings(
                    self.offset_x,
                    self.offset_y,
                    self.zoom
                )
    
    def start(self):
        """Start the SUMO simulation and visualisation."""
        try:
            # Start the SUMO simulation
            self.simulation.start()
            
            # Initialise traffic light positions
            self._initialise_traffic_light_positions()
            
            self.running = True
            print("Enhanced SUMO Visualisation started")
            return True
        
        except Exception as e:
            print(f"Error starting SUMO visualisation: {e}")
            return False
    
    def _initialise_traffic_light_positions(self):
        """Initialise traffic light positions based on SUMO network."""
        try:
            # Get all traffic lights
            tl_ids = traci.trafficlight.getIDList()
            print(f"Found traffic lights: {tl_ids}")
            
            if not tl_ids:
                print("WARNING: No traffic lights found in the simulation!")
                print("This might be because you're using a network without traffic lights.")
                return
            
            for tl_id in tl_ids:
                # If we have a known position in the network parser, use it
                if tl_id in self.network_parser.nodes:
                    self.traffic_light_positions[tl_id] = self.network_parser.nodes[tl_id]
                    continue
                
                # Try to get controlled junctions
                try:
                    controlled_junctions = traci.trafficlight.getControlledJunctions(tl_id)
                    for junction_id in controlled_junctions:
                        if junction_id in self.network_parser.nodes:
                            self.traffic_light_positions[tl_id] = self.network_parser.nodes[junction_id]
                            break
                except:
                    # Fallback to a default position if needed
                    if tl_id not in self.traffic_light_positions:
                        self.traffic_light_positions[tl_id] = (0, 0)
                        print(f"WARNING: Using default position for traffic light {tl_id}")
            
            print(f"Initialised {len(self.traffic_light_positions)} traffic light positions out of {len(tl_ids)} traffic lights")
            
        except Exception as e:
            print(f"Error initializing traffic light positions: {e}")   
    
    def _update_stats(self):
        """Update simulation statistics."""
        try:
            # update vehicle count
            vehicles = traci.vehicle.getIDList()
            self.stats["vehicles"] = len(vehicles)
            
            # update average speed and wait time
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
            
            # update throughput (vehicles that have arrived at their destination)
            arrived = traci.simulation.getArrivedNumber()
            self.stats["throughput"] += arrived
            self.performance_metrics["throughput"].append(arrived)
            
            # update step number
            self.stats["step"] = traci.simulation.getTime()
        
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def _draw_ui_overlay(self):
        """Draw UI overlay"""
        # Draw help text in the bottom left
        help_texts = [
            "Mouse Drag: Pan view",
            "Mouse Wheel: Zoom in/out",
            "I: Toggle vehicle IDs",
            "S: Toggle speed display",
            "W: Toggle waiting time display",
            "ESC: Quit"
        ]
        
        y_offset = self.height - len(help_texts) * 20 - 10
        
        for i, help_text in enumerate(help_texts):
            text = self.font.render(help_text, True, (50, 50, 50))
            self.screen.blit(text, (10, y_offset + i * 20))

    def step(self, delay_ms=100):
        """
        Perform one simulation and visualisation step with delay to slow down simulation.
        """
        if not self.running:
            return False
        
        try:
            # add delay to slow down simulation
            pygame.time.delay(delay_ms)
            
            # step the SUMO simulation
            self.simulation.step()
            
            # update statistics
            self._update_stats()
            
            # handle visualisation events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                    return False
                elif event.type == pygame.KEYDOWN:
                    # Press ESC to quit
                    if event.key == pygame.K_ESCAPE:
                        self.close()
                        return False
                    # Toggle vehicle IDs with I key
                    elif event.key == pygame.K_i:
                        self.traffic_renderer.toggle_vehicle_ids()
                    # Toggle speed display with S key
                    elif event.key == pygame.K_s:
                        self.traffic_renderer.toggle_speeds()
                    # Toggle waiting time display with W key
                    elif event.key == pygame.K_w:
                        self.traffic_renderer.toggle_waiting_times()
                # Handle mouse panning with left button
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        self.dragging = True
                        self.drag_start = event.pos
                    # Mouse wheel zooming
                    elif event.button == 4:  # Scroll up
                        self.zoom *= 1.1
                        self.traffic_renderer.update_view_settings(
                            self.offset_x, 
                            self.offset_y, 
                            self.zoom)
                    elif event.button == 5:  # Scroll down
                        self.zoom /= 1.1
                        self.traffic_renderer.update_view_settings(
                            self.offset_x, 
                            self.offset_y, 
                            self.zoom)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left mouse button
                        self.dragging = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        # Calculate the drag distance
                        dx = event.pos[0] - self.drag_start[0]
                        dy = event.pos[1] - self.drag_start[1]
                        self.offset_x += dx
                        self.offset_y += dy
                        self.drag_start = event.pos
                        
                        # Update the renderer view settings
                        self.traffic_renderer.update_view_settings(
                            self.offset_x, 
                            self.offset_y, 
                            self.zoom)
            
            # Clear the screen
            self.screen.fill((240, 240, 240))  # Light gray background
            
            # Update renderer with current visualisation settings
            self.traffic_renderer.update_view_settings(
                self.offset_x,
                self.offset_y,
                self.zoom
            )
            
            # Render the network
            self.traffic_renderer.render_network()
            
            # Render junctions
            for junction_id in self.network_parser.nodes.keys():
                self.traffic_renderer.render_junction(junction_id)
            
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
                    vehicle_type = self._map_vehicle_type(v_type)
                    
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
            
            # Render statistics
            formatted_stats = {
                "Vehicles": self.stats["vehicles"],
                "Avg Speed": f"{self.stats['avg_speed']:.2f} m/s",
                "Avg Wait Time": f"{self.stats['avg_wait_time']:.2f} s",
                "Throughput": self.stats["throughput"],
                "Simulation Time": f"{self.stats['step']:.1f} s",
                "Mode": self.stats["mode"]
            }
            self._draw_stats(formatted_stats)
            
            # Draw additional UI overlay
            self._draw_ui_overlay()
            
            # Update the display
            pygame.display.flip()
            self.clock.tick(self.fps)
            
            return True
        
        except Exception as e:
            print(f"Error in simulation step: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _draw_stats(self, stats):
        """Draw simulation statistics"""
        # Create a semi-transparent panel for statistics
        panel_rect = pygame.Rect(self.width - 260, 10, 250, 140)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((240, 240, 255, 220))  # Semi-transparent background
        
        # Add border to panel
        pygame.draw.rect(panel_surface, (100, 100, 150), (0, 0, panel_rect.width, panel_rect.height), 2)
        
        # Draw the panel
        self.screen.blit(panel_surface, panel_rect)
        
        # Draw title
        title = self.font.render("Simulation Statistics", True, (0, 0, 0))
        self.screen.blit(title, (panel_rect.centerx - title.get_width()//2, panel_rect.top + 5))
        
        # Draw stats
        y_offset = panel_rect.top + 30
        for key, value in stats.items():
            text = self.font.render(f"{key}: {value}", True, (0, 0, 0))
            self.screen.blit(text, (panel_rect.left + 10, y_offset))
            y_offset += 20

    def _map_vehicle_type(self, sumo_type):
        """Map SUMO vehicle type to our internal vehicle type"""
        sumo_type = sumo_type.lower()
        if "bus" in sumo_type:
            return "bus"
        elif "truck" in sumo_type or "trailer" in sumo_type:
            return "truck"
        elif "emergency" in sumo_type or "police" in sumo_type or "ambulance" in sumo_type:
            return "emergency"
        else:
            return "car"

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
        """Close the simulation and visualisation."""
        if self.running:
            self.simulation.close()
            pygame.quit()
            self.running = False
            print("Enhanced SUMO Visualisation closed")