import os
import sys
import time
import random
import numpy as np
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from src.ai.reinforcement_learning.dqn_controller import DQNController

class WirelessDQNController(DQNController):
    """
    Wireless Deep Q-Network Controller.
    
    This controller extends the DQN controller and simulates
    wireless network conditions (variable latency, potential packet loss).
    """
    def __init__(self, junction_ids, learning_rate=0.001, discount_factor=0.95, 
                exploration_rate=0.3, memory_size=10000, batch_size=32, 
                target_update_frequency=100, model_path=None,
                base_latency=0.05, computation_factor=0.1, packet_loss_prob=0.01):
        """
        Initialize the Wireless DQN controller.
        
        Args:
            junction_ids (list): List of junction IDs to control
            learning_rate (float): Learning rate for the neural network
            discount_factor (float): Gamma parameter for future reward discounting (0-1)
            exploration_rate (float): Epsilon parameter for exploration vs. exploitation (0-1)
            memory_size (int): Size of replay memory
            batch_size (int): Number of samples to use for training
            target_update_frequency (int): How often to update target network
            model_path (str): Path to load a pre-trained model (optional)
            base_latency (float): Base network latency in seconds
            computation_factor (float): Factor for additional computation time
            packet_loss_prob (float): Probability of packet loss (0-1)
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
        
        # Wireless network simulation parameters
        self.base_latency = base_latency
        self.computation_factor = computation_factor
        self.packet_loss_prob = packet_loss_prob
        
        # Statistics for network conditions
        self.total_latency = 0
        self.packet_losses = 0
        self.decision_count = 0
        
        # Initialize traffic light state lengths dictionary if not exists
        if not hasattr(self, 'tl_state_lengths'):
            self.tl_state_lengths = {}
        
        print(f"Initialized Wireless DQN Controller with base_latency={base_latency}, "
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
        # Neural network inference is more computationally intensive
        computation_time = traffic_complexity * self.computation_factor * 1.5  # 50% more than basic Q-learning
        
        # Add random fluctuation to simulate wireless interference
        # More traffic means more devices, potentially more interference
        interference = random.uniform(0, 0.15) * traffic_complexity  # Increased interference for neural network
        
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
        Decide the next traffic light phase using DQN with simulated wireless conditions.
        
        Args:
            junction_id (str): The ID of the junction to control
            current_time (float): Current simulation time
            
        Returns:
            str: The traffic light state to set
        """
        # Get the current traffic state for complexity calculation
        if junction_id in self.traffic_state:
            traffic_state = self.traffic_state[junction_id]
            
            # Calculate traffic complexity based on total vehicles and balance
            north_count = traffic_state.get('north_count', 0)
            south_count = traffic_state.get('south_count', 0)
            east_count = traffic_state.get('east_count', 0)
            west_count = traffic_state.get('west_count', 0)
            
            total_vehicles = north_count + south_count + east_count + west_count
            if total_vehicles > 0:
                ns_total = north_count + south_count
                ew_total = east_count + west_count
                balance = abs(ns_total - ew_total) / total_vehicles
                # Normalize total vehicles (assuming max of 50 is high complexity)
                volume_factor = min(1.0, total_vehicles / 50.0)
                traffic_complexity = (volume_factor * 0.7) + (balance * 0.3)
            else:
                traffic_complexity = 0.0
        else:
            traffic_complexity = 0.5  # Default medium complexity
        
        # Simulate wireless network conditions
        dynamic_latency = self._calculate_dynamic_latency(traffic_complexity)
        time.sleep(dynamic_latency)
        self.total_latency += dynamic_latency
        self.decision_count += 1
        
        # Simulate potential packet loss
        if self._simulate_packet_loss():
            # If packet loss, return the last action (no update)
            if junction_id in self.last_actions and self.last_actions[junction_id] is not None:
                return self.last_actions[junction_id]
            else:
                # If no last action, return a random phase
                return random.choice(self.phase_sequence)
        
        # Get phase from the base DQN implementation
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