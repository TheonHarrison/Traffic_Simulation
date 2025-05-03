# src/ai/controller_factory.py
from src.ai.wired_controller import WiredController
from src.ai.wireless_controller import WirelessController
from src.ai.traditional_controller import TraditionalController
from src.ai.reinforcement_learning.wired_rl_controller import WiredRLController
from src.ai.reinforcement_learning.wireless_rl_controller import WirelessRLController

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
                                ('Wired AI', 'Wireless AI', 'Traditional', 'Wired RL', 'Wireless RL')
            junction_ids (list): List of junction IDs to control
            **kwargs: Additional parameters to pass to the controller constructor
                      (model_path is required for RL controllers to load trained models)
            
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
        elif controller_type == "Wired RL":
            return WiredRLController(junction_ids, **kwargs)
        elif controller_type == "Wireless RL":
            return WirelessRLController(junction_ids, **kwargs)
        else:
            raise ValueError(f"Invalid controller type: {controller_type}")