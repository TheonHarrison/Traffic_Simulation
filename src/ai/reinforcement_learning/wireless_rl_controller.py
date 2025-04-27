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
        Decide the next traffic light phase using RL and simulating wireless conditions.
        
        Args:
            junction_id (str): The ID of the junction to control
            current_time (float): Current simulation time
            
        Returns:
            str: The traffic light state to set
        """
        # Calculate traffic complexity for latency simulation
        traffic_complexity = 0.5  # Default complexity
        
        if junction_id in self.traffic_state:
            # Get vehicle counts
            traffic_data = self.traffic_state[junction_id]
            total_vehicles = (traffic_data.get('north_count', 0) + 
                              traffic_data.get('south_count', 0) +
                              traffic_data.get('east_count', 0) + 
                              traffic_data.get('west_count', 0))
            
            # Normalize to 0-1 range (assuming max of 50 vehicles is high complexity)
            traffic_complexity = min(1.0, total_vehicles / 50.0)
        
        # Simulate wireless latency
        dynamic_latency = self._calculate_dynamic_latency(traffic_complexity)
        self.total_latency += dynamic_latency
        self.decision_count += 1
        
        # Simulate the network delay
        time.sleep(dynamic_latency)
        
        # Simulate packet loss (random communication failure)
        if self._simulate_packet_loss():
            # If packet is lost, return the last action or a default action
            if junction_id in self.last_actions and self.last_actions[junction_id] is not None:
                return self.last_actions[junction_id]
            else:
                return self.phase_sequence[0]  # Default to first phase
        
        # No packet loss, proceed with normal RL decision
        return super().decide_phase(junction_id, current_time)
    
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