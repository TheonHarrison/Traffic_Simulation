from src.ai.wired_controller import WiredController
from src.ai.wireless_controller import WirelessController
from src.ai.traditional_controller import TraditionalController

# Check if the RL modules are available
try:
    from src.ai.reinforcement_learning.wired_rl_controller import WiredRLController
    from src.ai.reinforcement_learning.wireless_rl_controller import WirelessRLController
    from src.ai.reinforcement_learning.dqn_controller import DQNController
    from src.ai.reinforcement_learning.wired_dqn_controller import WiredDQNController
    from src.ai.reinforcement_learning.wireless_dqn_controller import WirelessDQNController
    RL_AVAILABLE = True
    DQN_AVAILABLE = True
except ImportError:
    RL_AVAILABLE = False
    DQN_AVAILABLE = False
    # Check if just DQN is available
    try:
        from src.ai.reinforcement_learning.dqn_controller import DQNController
        from src.ai.reinforcement_learning.wired_dqn_controller import WiredDQNController
        from src.ai.reinforcement_learning.wireless_dqn_controller import WirelessDQNController
        DQN_AVAILABLE = True
    except ImportError:
        DQN_AVAILABLE = False

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
                                ('Wired AI', 'Wireless AI', 'Traditional',
                                'Wired RL', 'Wireless RL', 'DQN', 'Wired DQN', 'Wireless DQN')
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
            return WirelessController(junction_ids, **kwargs)
        elif controller_type == "Traditional":
            return TraditionalController(junction_ids, **kwargs)
        elif controller_type == "Wired RL" and RL_AVAILABLE:
            return WiredRLController(junction_ids, **kwargs)
        elif controller_type == "Wireless RL" and RL_AVAILABLE:
            return WirelessRLController(junction_ids, **kwargs)
        elif controller_type in ["Wired RL", "Wireless RL"] and not RL_AVAILABLE:
            raise ImportError(f"Reinforcement Learning controllers are not available. Please check your installation.")
        elif controller_type == "Wired DQN" and DQN_AVAILABLE:
            return WiredDQNController(junction_ids, **kwargs)
        elif controller_type == "Wireless DQN" and DQN_AVAILABLE:
            return WirelessDQNController(junction_ids, **kwargs)
        elif controller_type in ["Wired DQN", "Wireless DQN"] and not DQN_AVAILABLE:
            raise ImportError(f"DQN controllers are not available. Please check your installation.")
        else:
            raise ValueError(f"Invalid controller type: {controller_type}")