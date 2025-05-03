from src.ai.wired_controller import WiredController
from src.ai.wireless_controller import WirelessController
from src.ai.traditional_controller import TraditionalController

class ControllerFactory:
    """
    Factory class to create different types of traffic controllers.
    This makes it easy to switch between controller types in the simulation.
    """
    @staticmethod
    def create_controller(controller_type, junction_ids, **kwargs):
        """
        Create a controller of the specified type.
        
        Args:
            controller_type (str): Type of controller to create
                                ('Wired AI', 'Wireless AI', 'Traditional')
            junction_ids (list): List of junction IDs to control
            **kwargs: Additional parameters to pass to the controller constructor
            
        Returns:
            TrafficController: An instance of the specified controller type
            
        Raises:
            ValueError: If an invalid controller type is specified
        """
        if controller_type == "Wired AI":
            return WiredController(junction_ids, **kwargs)
        elif controller_type == "Wireless AI":
            return WirelessController(junction_ids, **kwargs)
        elif controller_type == "Traditional":
            return TraditionalController(junction_ids, **kwargs)
        else:
            raise ValueError(f"Invalid controller type: {controller_type}")