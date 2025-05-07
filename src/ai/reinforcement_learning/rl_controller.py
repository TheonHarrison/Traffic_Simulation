import os
import sys
import time
import numpy as np
import random
from pathlib import Path

# add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from src.ai.controller import TrafficController

class RLController(TrafficController):
    """
    Base class for reinforcement learning traffic controllers.
    
    This controller implements the core RL functionality.
    """
    def __init__(self, junction_ids, learning_rate=0.15, discount_factor=0.95, exploration_rate=0.5):
        """
        Initialise the RL controller.
        """
        # Call the parent constructor with only the junction_ids parameter
        super().__init__(junction_ids)
        
        # RL parameters
        self.learning_rate = learning_rate 
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        
        # Define the phase sequences same as other controllers for compatibility
        self.phase_sequence = ["GrYr", "yrGr", "rGry", "ryrG"]
        
        # Define phase durations for each junction (in seconds)
        self.phase_durations = {
            junction_id: {
                "GrYr": 30.0,  # Green for north-south, red for east-west
                "yrGr": 5.0,   # Yellow transitioning to red for north-south
                "rGry": 30.0,  # Red for north-south, green for east-west
                "ryrG": 5.0    # Red for north-south, yellow transitioning to red for east-west
            }
            for junction_id in junction_ids
        }
        
        # Initialise state-action values (Q-table)
        # We'll implement this in subclasses based on specific RL approach
        self.q_table = {}
        
        # Track current state for each junction
        self.current_states = {junction_id: None for junction_id in junction_ids}
        
        # Track last action for each junction
        self.last_actions = {junction_id: None for junction_id in junction_ids}
        
        # Track accumulated rewards for performance monitoring
        self.total_rewards = 0
        self.reward_history = []
        
        # Store traffic light state lengths for each junction
        self.tl_state_lengths = {}
        
        print(f"Initialised RL Controller with parameters: lr={learning_rate}, df={discount_factor}, er={exploration_rate}")
    
    def _get_state(self, junction_id):
        """
        Extract the state representation for a junction.
        """
        raise NotImplementedError("Subclasses must implement _get_state method")
    
    def _get_reward(self, junction_id):
        """
        Calculate the reward for the current state.

        """
        raise NotImplementedError("Subclasses must implement _get_reward method")
    
    def _select_action(self, state, junction_id):
        """
        Select an action using epsilon-greedy policy.
        """
        raise NotImplementedError("Subclasses must implement _select_action method")
    
    def _update_q_value(self, state, action, next_state, reward, junction_id):
        """
        Update the Q-value for a state-action pair.
        """
        raise NotImplementedError("Subclasses must implement _update_q_value method")
    
    def decide_phase(self, junction_id, current_time):
        """
        Decide the next traffic light phase using RL.
        """
        # Record start time for response time measurement
        response_start = time.time()
        
        # Get the current state
        current_state = self._get_state(junction_id)
        self.current_states[junction_id] = current_state
        
        # If this is the first time, just select an action
        if self.last_actions.get(junction_id) is None:
            action = self._select_action(current_state, junction_id)
            # Ensure action is a valid phase string
            if not isinstance(action, str) or action not in self.phase_sequence:
                print(f"Warning: Invalid action type {type(action)} or value {action}. Using default phase.")
                action = self.phase_sequence[0]
            
            self.last_actions[junction_id] = action
            
            # Record response time
            self.response_times.append(time.time() - response_start)
            
            return action
        
        # Get reward for the previous action
        reward = self._get_reward(junction_id)
        self.total_rewards += reward
        self.reward_history.append(reward)
        
        # Get the previous state and action
        prev_state = self.current_states[junction_id]
        prev_action = self.last_actions[junction_id]
        
        # Update Q-value
        self._update_q_value(prev_state, prev_action, current_state, reward, junction_id)
        
        # Select next action
        action = self._select_action(current_state, junction_id)
        # Ensure action is a valid phase string
        if not isinstance(action, str) or action not in self.phase_sequence:
            print(f"Warning: Invalid action type {type(action)} or value {action}. Using default phase.")
            action = self.phase_sequence[0]
        
        self.last_actions[junction_id] = action
        
        # Record decision time
        self.decision_times.append(time.time() - response_start)
        
        # Record response time
        self.response_times.append(time.time() - response_start)
        
        return action
    
    def get_average_reward(self):
        """get the average reward received by the controller."""
        if not self.reward_history:
            return 0
        return sum(self.reward_history) / len(self.reward_history)
    
    def save_q_table(self, filename):
        """
        Save the Q-table to a file.
        """
        raise NotImplementedError("Subclasses must implement save_q_table method")
    
    def load_q_table(self, filename):
        """
        Load the Q-table from a file.
        """
        raise NotImplementedError("Subclasses must implement load_q_table method")