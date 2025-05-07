import pygame
import math
from enum import Enum

# Define colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

class EnhancedTrafficRenderer:
    """
    enhanced renderer for traffic elements with improved graphics.
    """
    def __init__(self, screen, mapper, offset_x=0, offset_y=0, zoom=1.0):
        """
        initialise the enhanced traffic renderer.
        
        Args:
            screen: Pygame screen to draw on
            mapper: SumoPygameMapper for coordinate conversion
            offset_x: X offset for panning the view
            offset_y: Y offset for panning the view
            zoom: Zoom factor for the view
        """
        self.screen = screen
        self.mapper = mapper
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.zoom = zoom
        
        # Load fonts
        self.font = pygame.font.SysFont("Arial", 10)
        self.id_font = pygame.font.SysFont("Arial", 8)
        
        # Set colours
        self.colours = {
            "car": (0, 100, 200),      # Blue
            "bus": (0, 150, 0),        # Green
            "truck": (120, 120, 120),  # Gray
            "emergency": (255, 0, 0),  # Red
            "road": (80, 80, 80),      # Dark Gray
            "lane_marking": (255, 255, 255),  # White
            "traffic_light_housing": (50, 50, 50),  # Dark Gray
            "red_light": (255, 0, 0),  # Red
            "yellow_light": (255, 255, 0),  # Yellow
            "green_light": (0, 255, 0),  # Green
            "junction": (100, 100, 100)  # Gray
        }
        
        # create glow surfaces for traffic lights
        self.glow_surfaces = self._create_glow_surfaces()
        
        # debug options
        self.show_vehicle_ids = True
        self.show_speeds = True
        self.show_waiting_times = True
        
        print("Enhanced traffic renderer initialized")
    
    def _create_glow_surfaces(self):
        """Create glow effect surfaces for traffic lights"""
        glow_surfaces = {}
        
        for color_name in ["red_light", "yellow_light", "green_light"]:
            base_color = self.colours[color_name]
            
            # create surfaces of different sizes for the glow effect
            for size in [12, 16, 20, 24]:
                # create a surface with alpha channel
                surface = pygame.Surface((size, size), pygame.SRCALPHA)
                
                # calculate center and radius
                center = (size // 2, size // 2)
                max_radius = size // 2
                
                # draw concentric circles with decreasing alpha
                for radius in range(max_radius, 0, -1):
                    alpha = 150 * (radius / max_radius) ** 2  # Non-linear falloff
                    glow_color = (*base_color, int(alpha))
                    pygame.draw.circle(surface, glow_color, center, radius)
                
                # store in dictionary
                glow_surfaces[(color_name, size)] = surface
        
        return glow_surfaces
    
    def update_view_settings(self, offset_x, offset_y, zoom):
        """Update the view settings for panning and zooming."""
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.zoom = zoom
    
    def toggle_vehicle_ids(self):
        """Toggle display of vehicle IDs"""
        self.show_vehicle_ids = not self.show_vehicle_ids
        print(f"Vehicle IDs display: {'On' if self.show_vehicle_ids else 'Off'}")
        return self.show_vehicle_ids
    
    def toggle_speeds(self):
        """Toggle display of vehicle speeds"""
        self.show_speeds = not self.show_speeds
        print(f"Vehicle speeds display: {'On' if self.show_speeds else 'Off'}")
        return self.show_speeds
    
    def toggle_waiting_times(self):
        """Toggle display of vehicle waiting times"""
        self.show_waiting_times = not self.show_waiting_times
        print(f"Vehicle waiting times display: {'On' if self.show_waiting_times else 'Off'}")
        return self.show_waiting_times
    
    def _transform_coordinates(self, x, y):
        """Transform SUMO coordinates to screen coordinates with view settings."""
        pygame_x, pygame_y = self.mapper.sumo_to_pygame(x, y)
        return (pygame_x * self.zoom + self.offset_x, 
                pygame_y * self.zoom + self.offset_y)
    
    def render_vehicle(self, vehicle_id, position, angle, vehicle_type, 
                       speed=None, waiting_time=None, label=None):
        """
        Render a vehicle with improved graphics.
        
        Args :
            vehicle_id: ID of the vehicle
            position: (x, y) position in SUMO coordinates
            angle: Heading angle in degrees (0 = East, 90 = North)
            vehicle_type: Type of vehicle ('car', 'bus', 'truck', 'emergency')
            speed: Current speed in m/s (optional)
            waiting_time: Time spent waiting in seconds (optional)
            label: Text label to display (optional)
        """
        # transform coordinates
        screen_x, screen_y = self._transform_coordinates(position[0], position[1])
        
        # convert angle to pygame angle (SUMO: 0 = east, 90 = north, Pygame rotation: clockwise)
        pygame_angle = -angle + 90
        
        # determine if the vehicle is waiting
        is_waiting = waiting_time is not None and waiting_time > 0
        
        # determine vehicle size based on type
        if vehicle_type == 'emergency':
            base_width, base_height = 12, 6
        elif vehicle_type == 'truck':
            base_width, base_height = 16, 8
        elif vehicle_type == 'bus':
            base_width, base_height = 18, 7
        else:  # car or default
            base_width, base_height = 10, 5
        
        # scale by zoom factor
        width = base_width * self.zoom
        height = base_height * self.zoom
        
        # create a vehicle surface
        vehicle_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # determine color based on vehicle type
        color = self.colours.get(vehicle_type, self.colours["car"])
        
        # If waiting, make it pulsate red
        if is_waiting:
            # blend color with red based on waiting time
            wait_factor = min(1.0, waiting_time / 60.0)
            
            # pulsate effect for longer waiting times
            if waiting_time > 10.0:
                pulse = 0.7 + 0.3 * math.sin(pygame.time.get_ticks() * 0.01)
                wait_factor *= pulse
            
            color = tuple(int(c * (1 - wait_factor) + 255 * wait_factor * (i == 0)) for i, c in enumerate(color))
        
        # fill the vehicle surface
        vehicle_surface.fill(color)
        
        # draw a direction indicator (arrow)
        arrow_points = [
            (width * 0.8, height // 2),  # Tip of arrow
            (width * 0.5, height * 0.2),  # Left corner
            (width * 0.5, height * 0.8),  # Right corner
        ]
        pygame.draw.polygon(vehicle_surface, BLACK, arrow_points)
        
        # rotate and position
        rotated_surface = pygame.transform.rotate(vehicle_surface, pygame_angle)
        rotated_rect = rotated_surface.get_rect(center=(screen_x, screen_y))
        
        # draw the vehicle
        self.screen.blit(rotated_surface, rotated_rect.topleft)
        
        # draw vehicle ID if enabled
        label_y_offset = height / 2 + 5
        if self.show_vehicle_ids:
            id_text = self.id_font.render(vehicle_id, True, WHITE, (0, 0, 0, 180))
            id_rect = id_text.get_rect(center=(screen_x, screen_y + label_y_offset))
            self.screen.blit(id_text, id_rect.topleft)
            label_y_offset += id_rect.height + 2
        
        # draw speed if enabled
        if self.show_speeds and speed is not None:
            speed_text = self.id_font.render(f"{speed:.1f} m/s", True, WHITE, (0, 0, 100, 180))
            speed_rect = speed_text.get_rect(center=(screen_x, screen_y + label_y_offset))
            self.screen.blit(speed_text, speed_rect.topleft)
            label_y_offset += speed_rect.height + 2
        
        # draw waiting time if enabled and vehicle is waiting
        if self.show_waiting_times and is_waiting:
            wait_text = self.id_font.render(f"Wait: {waiting_time:.1f}s", True, WHITE, (150, 0, 0, 180))
            wait_rect = wait_text.get_rect(center=(screen_x, screen_y + label_y_offset))
            self.screen.blit(wait_text, wait_rect.topleft)
    
    def render_traffic_light(self, tl_id, position, state):
        """
        Render a traffic light with the given state.
        
        Args =
            tl_id: ID of the traffic light
            position: (x, y) position in SUMO coordinates
            state: Traffic light state string (e.g., 'GrYy')
        """
        # transform coordinates
        screen_x, screen_y = self._transform_coordinates(position[0], position[1])
        
        # calculate sizes based on zoom
        housing_width = 30 * self.zoom
        housing_height = (len(state) * 20 + 10) * self.zoom
        light_radius = 6 * self.zoom
        light_spacing = 20 * self.zoom
        
        # draw the traffic light housing
        housing_rect = pygame.Rect(
            screen_x - housing_width / 2,
            screen_y - housing_height / 2,
            housing_width,
            housing_height
        )
        
        # draw the outer housing with a slight bevel
        pygame.draw.rect(self.screen, (30, 30, 30), housing_rect, border_radius=int(5 * self.zoom))
        pygame.draw.rect(self.screen, self.colours["traffic_light_housing"], 
                        housing_rect.inflate(-4, -4), border_radius=int(3 * self.zoom))
        
        # draw the ID on top of the traffic light
        id_text = self.font.render(tl_id, True, WHITE)
        id_rect = id_text.get_rect(center=(screen_x, screen_y - housing_height / 2 - 10 * self.zoom))
        self.screen.blit(id_text, id_rect.topleft)
        
        # draw each light
        for i, light in enumerate(state):
            # Calculate position
            light_y = screen_y - housing_height / 2 + (i + 0.5) * light_spacing + 5 * self.zoom
            
            # Determine color based on the state character
            if light in ('G', 'g'):  # Green
                color = self.colours["green_light"]
                glow_color = "green_light"
            elif light in ('Y', 'y'):  # Yellow
                color = self.colours["yellow_light"]
                glow_color = "yellow_light"
            elif light in ('r', 'R'):  # Red
                color = self.colours["red_light"]
                glow_color = "red_light"
            else:  # Off or unknown
                color = (80, 80, 80)
                glow_color = None
            
            # draw glow effect first if it's on
            if glow_color:
                # Get appropriate sized glow surface
                glow_size = int(24 * self.zoom)
                glow_size = min(24, max(12, glow_size))  # Clamp to available sizes
                
                glow_key = (glow_color, glow_size)
                if glow_key in self.glow_surfaces:
                    glow_surface = self.glow_surfaces[glow_key]
                    glow_rect = glow_surface.get_rect(center=(screen_x, light_y))
                    self.screen.blit(glow_surface, glow_rect.topleft)
            
            # Draw the light circle with a black outline for better visibility
            pygame.draw.circle(self.screen, BLACK, (int(screen_x), int(light_y)), 
                               int(light_radius + 1))
            pygame.draw.circle(self.screen, color, (int(screen_x), int(light_y)), 
                               int(light_radius))
            
            # Add a small reflection highlight
            highlight_pos = (int(screen_x - light_radius/3), int(light_y - light_radius/3))
            highlight_radius = max(1, int(light_radius/4))
            pygame.draw.circle(self.screen, (255, 255, 255, 180), highlight_pos, highlight_radius)
    
    def render_network(self):
        """Render the road network with improved graphics."""
        # Render all edges from the network parser
        for edge_id, edge_data in self.mapper.net_parser.edges.items():
            shape = self.mapper.get_edge_shape(edge_id)
            if shape and len(shape) >= 2:
                for i in range(len(shape) - 1):
                    start = shape[i]
                    end = shape[i + 1]
                    
                    # Apply view transformations
                    start = (start[0] * self.zoom + self.offset_x, 
                           start[1] * self.zoom + self.offset_y)
                    end = (end[0] * self.zoom + self.offset_x, 
                           end[1] * self.zoom + self.offset_y)
                    
                    # Calculate length for lane markings
                    road_length = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                    
                    # Draw the road (increased width by 50%)
                    road_width = 30 * self.zoom
                    pygame.draw.line(self.screen, self.colours["road"], start, end, int(road_width))
                    
                    # Draw lane markings if long enough
                    if road_length > 30 * self.zoom:
                        # Normalize direction
                        if road_length > 0:
                            dx = (end[0] - start[0]) / road_length
                            dy = (end[1] - start[1]) / road_length
                            
                            # Draw dashed line
                            dash_length = 5 * self.zoom
                            gap_length = 5 * self.zoom
                            distance = 0
                            drawing = True
                            
                            while distance < road_length:
                                if drawing:
                                    line_start = (start[0] + distance * dx, start[1] + distance * dy)
                                    line_end = (start[0] + min(distance + dash_length, road_length) * dx, 
                                                start[1] + min(distance + dash_length, road_length) * dy)
                                    pygame.draw.line(self.screen, self.colours["lane_marking"], 
                                                   line_start, line_end, max(1, int(self.zoom)))
                                distance += dash_length if drawing else gap_length
                                drawing = not drawing
    
    def render_junction(self, junction_id):
        """
        Render a junction (intersection).
        
        Args:
            junction_id: ID of the junction in the SUMO network
        """
        # Get the junction position
        pos = self.mapper.get_node_position(junction_id)
        if not pos:
            return
        
        # Transform coordinates
        screen_x, screen_y = pos[0] * self.zoom + self.offset_x, pos[1] * self.zoom + self.offset_y
        
        # Draw the junction (50% larger)
        radius = max(7, 15 * self.zoom)
        pygame.draw.circle(self.screen, self.colours["junction"], (screen_x, screen_y), radius)
        pygame.draw.circle(self.screen, (50, 50, 50), (screen_x, screen_y), radius, width=2)