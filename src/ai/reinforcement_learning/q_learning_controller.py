import os
import sys
import time
import numpy as np
import json
import pickle
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from src.ai.reinforcement_learning.rl_controller import RLController

class QLearningController(RLController):
    """
    Q-Learning for traffic control.
    
    this controller uses the Q-learning algorithm to learn traffic signal 
    timing based on traffic conditions.
    """
    def __init__(self, junction_ids, learning_rate=0.15, discount_factor=0.95, 
                exploration_rate=0.5, state_bins=8, model_path=None):
        """
        Initialise the Q-Learning controller.
        
        Argsument:
            junction_ids: List of junction IDs to control
            learning_rate: Alpha parameter for Q-learning updates (0-1)
            discount_factor: Gamma parameter for future reward discounting (0-1)
            exploration_rate: Epsilon parameter for exploration vs. exploitation (0-1)
            state_bins: Number of bins to discretize continuous state variables
            model_path: Path to load a pre-trained Q-table (optional)
        """
        super().__init__(junction_ids, learning_rate, discount_factor, exploration_rate)
        
        # Number of bins for state discretization
        self.state_bins = state_bins
        
        # Initialise Q-table for each junction
        self.q_tables = {junction_id: {} for junction_id in junction_ids}
        
        # Load pre-trained model if its there
        if model_path and os.path.exists(model_path):
            self.load_q_table(model_path)
            print(f"Loaded pre-trained Q-table from {model_path}")
        
        # Additional stats
        self.exploration_count = 0
        self.exploitation_count = 0
        
        print(f"Initialised Q-Learning Controller with {state_bins} state bins")
    
    def _discretize_state(self, traffic_state, junction_id):
        """
        Convert continuous traffic state into a discrete state representation.
        """
        # Extract relevant metrics
        north_count = traffic_state.get('north_count', 0)
        south_count = traffic_state.get('south_count', 0)
        east_count = traffic_state.get('east_count', 0)
        west_count = traffic_state.get('west_count', 0)
        
        north_queue = traffic_state.get('north_queue', 0)
        south_queue = traffic_state.get('south_queue', 0)
        east_queue = traffic_state.get('east_queue', 0)
        west_queue = traffic_state.get('west_queue', 0)
        
        # calculate aggregate metrics
        ns_count = north_count + south_count
        ew_count = east_count + west_count
        
        ns_queue = north_queue + south_queue
        ew_queue = east_queue + west_queue
        
        # calculate total waiting time - using the actual total waiting time values
        north_wait = traffic_state.get('north_wait', 0) * north_count if north_count > 0 else 0
        south_wait = traffic_state.get('south_wait', 0) * south_count if south_count > 0 else 0
        east_wait = traffic_state.get('east_wait', 0) * east_count if east_count > 0 else 0
        west_wait = traffic_state.get('west_wait', 0) * west_count if west_count > 0 else 0
        total_wait_time = north_wait + south_wait + east_wait + west_wait
        
        # initialise last_wait_times if it doesn't exist
        if not hasattr(self, 'last_wait_times'):
            self.last_wait_times = {}
        
        # Add to the state representation - track trend in waiting time
        if junction_id in self.last_wait_times:
            wait_time_increase = total_wait_time > self.last_wait_times[junction_id]
            trend_indicator = 1 if wait_time_increase else 0
        else:
            trend_indicator = 0
        self.last_wait_times[junction_id] = total_wait_time
        
        # discretize waiting time for the state representation
        # Assuming max waiting time around 300 seconds (5 minutes) and dividing into state_bins
        discretized_wait_time = min(self.state_bins-1, int(total_wait_time / (300.0 / self.state_bins)))
        
        # Discretize using more fine-grained bins
        discretized_ns_count = min(self.state_bins-1, int(ns_count / 2))
        discretized_ew_count = min(self.state_bins-1, int(ew_count / 2))
        discretized_ns_queue = min(self.state_bins-1, int(ns_queue / 1.5))
        discretized_ew_queue = min(self.state_bins-1, int(ew_queue / 1.5))
        
        # Add queue ratio for better differentiation of states
        if ew_queue + ns_queue > 0:
            queue_ratio = min(self.state_bins-1, 
                            int((ns_queue / (ns_queue + ew_queue)) * self.state_bins))
        else:
            queue_ratio = 0
        
        # Include in state tuple - add both total wait time and trend indicator
        return (discretized_ns_count, discretized_ew_count, 
                discretized_ns_queue, discretized_ew_queue, 
                queue_ratio, discretized_wait_time, trend_indicator)
    
    def _get_state(self, junction_id):
        """
        Extract the state representation for a junction.
        """
        # Get the traffic state for this junction
        if junction_id not in self.traffic_state:
            # Return a default state if no data available
            return (0, 0, 0, 0, 0)
        
        traffic_state = self.traffic_state[junction_id]
        
        # Convert to discrete state
        return self._discretize_state(traffic_state, junction_id)
    
    def _get_reward(self, junction_id):
        """
        Calculate the reward for the current state.
        
        The reward function is designed to:
        - Minimize waiting time (negative reward for waiting)
        - Maximize throughput (positive reward for moving vehicles)
        - Balance flow (penalize imbalanced vehicle distribution)
        """
        if junction_id not in self.traffic_state:
            return 0  # No data, no reward
        
        traffic_state = self.traffic_state[junction_id]
        
        # Extract metrics
        north_count = traffic_state.get('north_count', 0)
        south_count = traffic_state.get('south_count', 0)
        east_count = traffic_state.get('east_count', 0)
        west_count = traffic_state.get('west_count', 0)
        
        north_wait = traffic_state.get('north_wait', 0)
        south_wait = traffic_state.get('south_wait', 0)
        east_wait = traffic_state.get('east_wait', 0)
        west_wait = traffic_state.get('west_wait', 0)
        
        north_queue = traffic_state.get('north_queue', 0)
        south_queue = traffic_state.get('south_queue', 0)
        east_queue = traffic_state.get('east_queue', 0)
        west_queue = traffic_state.get('west_queue', 0)
        
        # Calculate reward components
        
        # Waiting time penalty (more negative for longer waits)
        wait_penalty = -1.0 * (north_wait + south_wait + east_wait + west_wait)
        
        #Queue length penalty (more negative for longer queues)
        queue_penalty = -2.0 * (north_queue + south_queue + east_queue + west_queue)
        
        # Exponential penalty for long queues
        for queue_length in [north_queue, south_queue, east_queue, west_queue]:
            if queue_length > 3:  # If queue is getting long
                queue_penalty -= (queue_length - 3) ** 2  # Exponential penalty

        #Throughput reward (more positive for more vehicles moving)
        total_vehicles = north_count + south_count + east_count + west_count
        total_queues = north_queue + south_queue + east_queue + west_queue
        moving_vehicles = max(0, total_vehicles - total_queues)
        throughput_reward = 0.8 * moving_vehicles  # Increased from 0.3 to 0.8
        
        # balance reward (penalize imbalance between directions)
        ns_total = north_count + south_count
        ew_total = east_count + west_count
        
        if total_vehicles > 0:
            imbalance = abs(ns_total - ew_total) / total_vehicles
            balance_reward = 0.5 * (1.0 - imbalance)
        else:
            balance_reward = 0.5
        
        # queue reduction reward
        prev_state = self.current_states.get(junction_id)
        if prev_state is not None:
            prev_traffic_state = self.traffic_state.get(junction_id, {})
            prev_total_queue = (prev_traffic_state.get('north_queue', 0) + 
                            prev_traffic_state.get('south_queue', 0) + 
                            prev_traffic_state.get('east_queue', 0) + 
                            prev_traffic_state.get('west_queue', 0))
            
            queue_reduction = max(0, prev_total_queue - total_queues)
            queue_reduction_reward = 1.0 * queue_reduction  # Increased from 0.4 to 1.0
        else:
            queue_reduction_reward = 0
        
        # Combine all reward components with modified weights
        total_reward = wait_penalty * 1.5 + queue_penalty + throughput_reward + balance_reward + queue_reduction_reward * 1.5
        
        return total_reward
    
    def _get_q_value(self, state, action, junction_id):
        """
        Get Q-value for a state-action pair.
        Returns: The Q-value
        """
        q_table = self.q_tables.get(junction_id, {})
        return q_table.get((state, action), 0.0)
    
    def _select_action(self, state, junction_id):
        """
        Select an action using epsilon-greedy policy.
        """
        # Exploration: random action
        if np.random.random() < self.exploration_rate:
            self.exploration_count += 1
            # Make sure we return a phase string, not an index
            return np.random.choice(self.phase_sequence)
        
        # Exploitation: best known action
        self.exploitation_count += 1
        
        # Find the action with the highest Q-value for this state
        best_action = None
        best_value = float('-inf')
        
        for action in self.phase_sequence:
            q_value = self._get_q_value(state, action, junction_id)
            if q_value > best_value:
                best_value = q_value
                best_action = action
        
        # If all Q-values are the same (or not set), choose randomly
        if best_action is None:
            best_action = np.random.choice(self.phase_sequence)
        
        # Make sure we're returning a phase string
        if not isinstance(best_action, str):
            print(f"WARNING: Converting non-string action {best_action} ({type(best_action)}) to string")
            # Fall back to a default phase if something went wrong
            best_action = self.phase_sequence[0]
        
        return best_action
    
    def _update_q_value(self, state, action, next_state, reward, junction_id):
        """
        Update the Q-value for a state-action pair using the Q-learning update rule =
        
        Q(s,a) = Q(s,a) + α * [r + γ * max(Q(s',a')) - Q(s,a)]
        
        """
        # Get the current Q-value
        current_q = self._get_q_value(state, action, junction_id)
        
        # Find the maximum Q-value for the next state
        max_next_q = float('-inf')
        for next_action in self.phase_sequence:
            next_q = self._get_q_value(next_state, next_action, junction_id)
            max_next_q = max(max_next_q, next_q)
        
        # If no value exists yet, initialize to 0
        if max_next_q == float('-inf'):
            max_next_q = 0
        
        # Calculate the new Q-value
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q)
        
        # Update the Q-table
        if junction_id not in self.q_tables:
            self.q_tables[junction_id] = {}
        
        self.q_tables[junction_id][(state, action)] = new_q
    
    def save_q_table(self, filename):
        """ Save the Q-table to a file.        """
        
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Convert dictionary keys to strings for JSON serialization
        serializable_q_tables = {}
        for junction_id, q_table in self.q_tables.items():
            serializable_q_tables[junction_id] = {
                str(key): value for key, value in q_table.items()
            }
        
        # Save model information
        model_info = {
            "q_tables": serializable_q_tables,
            "learning_rate": self.learning_rate,
            "discount_factor": self.discount_factor,
            "exploration_rate": self.exploration_rate,
            "state_bins": self.state_bins,
            "exploration_count": self.exploration_count,
            "exploitation_count": self.exploitation_count,
            "total_rewards": self.total_rewards,
            "reward_history": self.reward_history
        }
        
        # Use pickle for more efficient serialization of complex data
        with open(filename, 'wb') as f:
            pickle.dump(model_info, f)
        
        print(f"Q-table saved to {filename}")
        return True
    
    def load_q_table(self, filename):
        """ Load the Q-table from a file."""
        
        if not os.path.exists(filename):
            print(f"File not found: {filename}")
            return False
        
        try:
            # Load model data
            with open(filename, 'rb') as f:
                model_info = pickle.load(f)
            
            # Extract Q-tables and convert string keys back to tuples
            serialized_q_tables = model_info.get("q_tables", {})
            for junction_id, q_table in serialized_q_tables.items():
                self.q_tables[junction_id] = {}
                for key, value in q_table.items():
                    state, action = eval(key)
                    if not isinstance(action, str):
                        print(f"WARNING: Invalid action type {type(action)} in loaded Q-table. Converting...")
                        action = self.phase_sequence[action] if isinstance(action, int) else self.phase_sequence[0]
                    self.q_tables[junction_id][(state, action)] = value

            
            # Extract other parameters
            self.learning_rate = model_info.get("learning_rate", self.learning_rate)
            self.discount_factor = model_info.get("discount_factor", self.discount_factor)
            self.exploration_rate = model_info.get("exploration_rate", self.exploration_rate)
            self.state_bins = model_info.get("state_bins", self.state_bins)
            self.exploration_count = model_info.get("exploration_count", 0)
            self.exploitation_count = model_info.get("exploitation_count", 0)
            self.total_rewards = model_info.get("total_rewards", 0)
            self.reward_history = model_info.get("reward_history", [])
            
            print(f"Q-table loaded successfully from {filename}")
            return True
        
        except Exception as e:
            print(f"Error loading Q-table: {e}")
            return False
    
    def get_exploration_stats(self):
        """Get exploration vs. exploitation stats"""
        total_actions = self.exploration_count + self.exploitation_count
        if total_actions == 0:
            return 0, 0
        
        exploration_ratio = self.exploration_count / total_actions
        exploitation_ratio = self.exploitation_count / total_actions
        
        return exploration_ratio, exploitation_ratio
    
    def get_q_table_stats(self):
        """Get statistics about the Q-table."""
        total_entries = 0
        state_counts = {}
        action_counts = {}
        
        for junction_id, q_table in self.q_tables.items():
            total_entries += len(q_table)
            
            for (state, action) in q_table.keys():
                state_counts[state] = state_counts.get(state, 0) + 1
                action_counts[action] = action_counts.get(action, 0) + 1
        
        return {
            "total_entries": total_entries,
            "unique_states": len(state_counts),
            "unique_actions": len(action_counts),
            "most_common_state": max(state_counts.items(), key=lambda x: x[1])[0] if state_counts else None,
            "most_common_action": max(action_counts.items(), key=lambda x: x[1])[0] if action_counts else None
        }