import os
import sys
import time
import numpy as np
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from src.ai.reinforcement_learning.dqn_controller import DQNController

class WiredDQNController(DQNController):
    """
    Wired Deep Q-Network Controller.
    
    This controller extends the DQN controller and simulates
    wired network conditions (fixed latency, reliable communication).
    """
    def __init__(self, junction_ids, learning_rate=0.001, discount_factor=0.95, 
                exploration_rate=0.3, memory_size=10000, batch_size=32, 
                target_update_frequency=100, model_path=None,
                network_latency=0.1):
        """
        Initialize the Wired DQN controller.
        
        Args:
            junction_ids (list): List of junction IDs to control
            learning_rate (float): Learning rate for the neural network
            discount_factor (float): Gamma parameter for future reward discounting (0-1)
            exploration_rate (float): Epsilon parameter for exploration vs. exploitation (0-1)
            memory_size (int): Size of replay memory
            batch_size (int): Number of samples to use for training
            target_update_frequency (int): How often to update target network
            model_path (str): Path to load a pre-trained model (optional)
            network_latency (float): Fixed network latency in seconds
        """
        # Call the parent class constructor
        super().__init__(
            junction_ids, 
            learning_rate=learning_rate, 
            discount_factor=discount_factor, 
            exploration_rate=exploration_rate,
            memory_size=memory_size,
            batch_size=batch_size,
            target_update_frequency=target_update_frequency,
            model_path=model_path
        )
        
        # Wired network simulation parameter
        self.network_latency = network_latency
        
        # Statistics
        self.total_latency = 0
        self.decision_count = 0
        
        # Initialize traffic light state lengths dictionary if not exists
        if not hasattr(self, 'tl_state_lengths'):
            self.tl_state_lengths = {}
        
        print(f"Initialized Wired DQN Controller with network_latency={network_latency}")
    
    def decide_phase(self, junction_id, current_time):
        """
        Decide the next traffic light phase using DQN and simulating wired conditions.
        
        Args:
            junction_id (str): The ID of the junction to control
            current_time (float): Current simulation time
            
        Returns:
            str: The traffic light state to set
        """
        # Simulate network latency for the wired connection
        time.sleep(self.network_latency)
        self.total_latency += self.network_latency
        self.decision_count += 1
        
        # Get the phase from the base DQN implementation
        phase = super().decide_phase(junction_id, current_time)
        
        # Ensure the phase matches the expected length for this junction
        if junction_id in self.tl_state_lengths:
            expected_length = self.tl_state_lengths[junction_id]
            if len(phase) != expected_length:
                # Adjust phase length to match expected length
                if len(phase) < expected_length:
                    # Repeat the pattern to match length
                    phase = phase * (expected_length // len(phase)) + phase[:expected_length % len(phase)]
                else:
                    # Truncate to expected length
                    phase = phase[:expected_length]
        
        return phase
    
    def get_network_stats(self):
        """Get statistics about the simulated wired network."""
        if self.decision_count == 0:
            return {
                "avg_latency": self.network_latency,
                "packet_loss_rate": 0.0,
                "decision_count": 0
            }
        
        return {
            "avg_latency": self.total_latency / self.decision_count,
            "packet_loss_rate": 0.0,  # No packet loss in wired network
            "decision_count": self.decision_count
        }