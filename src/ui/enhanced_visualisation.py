import pygame
import os
import sys
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

class EnhancedVisualisation:
    """
    Enhanced visualisation with improved graphics for traffic simulation.
    """
    def __init__(self, width=800, height=600, title="Enhanced AI Traffic Control Simulation", net_file=None):
        """
        Initialise the enhanced visualisation window.

            width (int): Width of the window in pixels
            height (int): Height of the window in pixels
            title (str): Title of the window
            net_file (str): Path to the SUMO network file
        """
        # Initialise pygame
        pygame.init()
        
        # Set up the display
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.fps = 30
        
        # Load assets
        self.assets_path = Path(__file__).resolve().parent.parent.parent / "assets"
        self.assets = self._load_assets()
        
        # SUMO Network mapping
        self.net_file = net_file
        self.network_parser = None
        self.mapper = None
        if net_file:
            self._setup_network_mapping()
        
        # Simulation view settings
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 2.0  # Higher default zoom
        
        # Font for displaying information
        self.font = pygame.font.SysFont("Arial", 16)
        
        # Mouse tracking for dragging
        self.dragging = False
        self.drag_start = None
        
        # Key toggles for debug information
        self.show_ids = True
        self.show_speeds = True
        self.show_waiting = True
        
        # Add keybindings for toggling debug info
        self.controls_help = [
            "Mouse Drag: Pan view",
            "Mouse Wheel: Zoom in/out",
            "I: Toggle vehicle IDs",
            "S: Toggle speed display",
            "W: Toggle waiting time display",
            "ESC: Quit"
        ]
        
        print("Enhanced visualisation initialized")
    
    def _load_assets(self):
        """Load image assets for the visualisation"""
        assets = {}
        
        # Create the assets directory if it doesn't exist
        os.makedirs(self.assets_path, exist_ok=True)
        
        # For now, return empty assets dictionary
        # We'll add real assets later
        return assets
    
    def _setup_network_mapping(self):
        """Set up the SUMO to Pygame coordinate mapping."""
        if not os.path.exists(self.net_file):
            print(f"Warning: Network file not found: {self.net_file}")
            return
        
        try:
            from src.ui.sumo_pygame_mapper import SumoNetworkParser, SumoPygameMapper
            self.network_parser = SumoNetworkParser(self.net_file)
            self.mapper = SumoPygameMapper(self.network_parser, self.width, self.height)
            print("SUMO network successfully loaded and mapped to Pygame coordinates")
        except Exception as e:
            print(f"Error setting up network mapping: {str(e)}")
    
    def handle_events(self):
        """Handle pygame events and return whether to continue running"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                # Press ESC to quit
                if event.key == pygame.K_ESCAPE:
                    return False
                # Toggle vehicle IDs with I key
                elif event.key == pygame.K_i:
                    self.show_ids = not self.show_ids
                    print(f"Vehicle IDs display: {'On' if self.show_ids else 'Off'}")
                # Toggle speed display with S key
                elif event.key == pygame.K_s:
                    self.show_speeds = not self.show_speeds
                    print(f"Vehicle speeds display: {'On' if self.show_speeds else 'Off'}")
                # Toggle waiting time display with W key
                elif event.key == pygame.K_w:
                    self.show_waiting = not self.show_waiting
                    print(f"Vehicle waiting times display: {'On' if self.show_waiting else 'Off'}")
            # Handle mouse panning with left button
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.dragging = True
                    self.drag_start = event.pos
                # Mouse wheel zooming
                elif event.button == 4:  # Scroll up
                    self.zoom *= 1.1
                elif event.button == 5:  # Scroll down
                    self.zoom /= 1.1
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
        
        return True
    
    def clear(self):
        """Clear the screen to prepare for drawing"""
        self.screen.fill((240, 240, 240))  # Light gray background
    
    def draw_text(self, text, x, y, color=(0, 0, 0)):
        """Draw text on the screen"""
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
    
    def draw_stats(self, stats):
        """Draw simulation statistics"""
        # Create a semi-transparent background for stats
        stats_bg = pygame.Surface((250, len(stats) * 20 + 10), pygame.SRCALPHA)
        stats_bg.fill((240, 240, 255, 200))  # Semi-transparent background
        self.screen.blit(stats_bg, (5, 5))
        
        # Draw stats
        y_offset = 10
        for key, value in stats.items():
            self.draw_text(f"{key}: {value}", 10, y_offset)
            y_offset += 20
    
    def draw_help(self):
        """Draw help text with keybinding information"""
        y_offset = self.height - len(self.controls_help) * 20 - 10
        
        # Create a semi-transparent background for help text
        help_bg = pygame.Surface((300, len(self.controls_help) * 20 + 10), pygame.SRCALPHA)
        help_bg.fill((240, 240, 255, 200))  # Semi-transparent background
        self.screen.blit(help_bg, (5, y_offset - 5))
        
        # Draw help text
        for i, help_text in enumerate(self.controls_help):
            self.draw_text(help_text, 10, y_offset + i * 20)
    
    def _center_view(self):
        """Center the view on the network"""
        if self.mapper:
            # Get network bounds
            min_x, min_y = self.mapper.min_x, self.mapper.min_y
            max_x, max_y = self.mapper.max_x, self.mapper.max_y
            
            # Calculate center of network
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            
            # Set offsets to center the view
            self.offset_x = self.width / 2 - center_x * self.zoom * self.mapper.scale
            self.offset_y = self.height / 2 - center_y * self.zoom * self.mapper.scale
    
    def update(self):
        """Update the display"""
        pygame.display.flip()
        self.clock.tick(self.fps)
    
    def close(self):
        """Close the visualisation"""
        pygame.quit()