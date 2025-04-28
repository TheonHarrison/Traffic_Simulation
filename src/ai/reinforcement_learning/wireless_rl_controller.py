import os
import sys
import time
import random
import numpy as np
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from src.ai.reinforcement_learning.q_learning_controller import QLearningController

class WirelessRLController(QLearningController):
    """
    Wireless Reinforcement Learning Controller.
    
    This controller extends the Q-Learning controller and simulates
    wireless network conditions (variable latency, potential packet loss).
    """
    def __init__(self, junction_ids, learning_rate=0.1, discount_factor=0.9, 
                exploration_rate=0.3, state_bins=3, model_path=None,
                base_latency=0.05, computation_factor=0.1, packet_loss_prob=0.01):
        """
        Initialize the Wireless RL controller.
        
        Args:
            junction_ids (list): List of junction IDs to control
            learning_rate (float): Alpha parameter for Q-learning updates (0-1)
            discount_factor (float): Gamma parameter for future reward discounting (0-1)
            exploration_rate (float): Epsilon parameter for exploration vs. exploitation (0-1)
            state_bins (int): Number of bins to discretize continuous state variables
            model_path (str): Path to load a pre-trained Q-table (optional)
            base_latency (float): Base network latency in seconds
            computation_factor (float): Factor for additional computation time
            packet_loss_prob (float): Probability of packet loss (0-1)
        """
        # Call the parent constructor with the correct number of arguments
        super().__init__(junction_ids, learning_rate, discount_factor, 
                        exploration_rate, state_bins, model_path)
        
        # Wireless network simulation parameters
        self.base_latency = base_latency
        self.computation_factor = computation_factor
        self.packet_loss_prob = packet_loss_prob
        
        # Statistics for network conditions
        self.total_latency = 0
        self.packet_losses = 0
        self.decision_count = 0
        
        print(f"Initialized Wireless RL Controller with base_latency={base_latency}, " 
                f"computation_factor={computation_factor}, packet_loss_prob={packet_loss_prob}")
    
    def _calculate_dynamic_latency(self, traffic_complexity):
        """
        Calculate dynamic latency based on traffic complexity and random factors
        (simulating wireless interference, computation time, etc.)
        
        Args:
            traffic_complexity (float): Measure of traffic complexity (0.0-1.0)
            
        Returns:
            float: Total latency time in seconds
        """
        # Base latency
        latency = self.base_latency
        
        # Add computation time based on traffic complexity
        computation_time = traffic_complexity * self.computation_factor
        
        # Add random fluctuation to simulate wireless interference
        # More traffic means more devices, potentially more interference
        interference = random.uniform(0, 0.1) * traffic_complexity
        
        return latency + computation_time + interference
    
    def _simulate_packet_loss(self):
        """
        Simulate packet loss in wireless network.
        
        Returns:
            bool: True if packet was lost, False otherwise
        """
        if random.random() < self.packet_loss_prob:
            self.packet_losses += 1
            return True
        return False
    
def decide_phase(self, junction_id, current_time):
    """
    Decide the next traffic light phase using RL and simulating wired conditions.
    
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
    
    # Get the phase from the base RL implementation
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
        """Get statistics about the simulated wireless network."""
        if self.decision_count == 0:
            return {
                "avg_latency": 0,
                "packet_loss_rate": 0,
                "decision_count": 0
            }
        
        return {
            "avg_latency": self.total_latency / self.decision_count,
            "packet_loss_rate": self.packet_losses / self.decision_count,
            "decision_count": self.decision_count
        }