import os
import sys
import time
import random
import numpy as np
import tensorflow as tf
from collections import deque
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from src.ai.reinforcement_learning.rl_controller import RLController

class DQNController(RLController):
    """
    Deep Q-Network (DQN) implementation for traffic control.
    
    This controller uses a neural network to approximate the Q-function,
    allowing it to handle more complex state representations without discretization.
    """
    def __init__(self, junction_ids, learning_rate=0.001, discount_factor=0.95, 
                exploration_rate=0.3, memory_size=10000, batch_size=32, 
                target_update_frequency=100, model_path=None):
        """
        Initialize the DQN controller.
        
        Args:
            junction_ids (list): List of junction IDs to control
            learning_rate (float): Learning rate for the neural network
            discount_factor (float): Gamma parameter for future reward discounting (0-1)
            exploration_rate (float): Epsilon parameter for exploration vs. exploitation (0-1)
            memory_size (int): Size of replay memory
            batch_size (int): Number of samples to use for training
            target_update_frequency (int): How often to update target network
            model_path (str): Path to load a pre-trained model (optional)
        """
        # Initialize parent class with basic parameters
        super().__init__(junction_ids, learning_rate, discount_factor, exploration_rate)
        
        # DQN specific parameters
        self.memory_size = memory_size
        self.batch_size = batch_size
        self.target_update_frequency = target_update_frequency
        
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
        
        # Initialize replay memory
        self.replay_memory = {}
        
        # Initialize neural network models for each junction
        self.models = {}
        self.target_models = {}
        
        # Initialize step counters for target network update
        self.step_counters = {junction_id: 0 for junction_id in junction_ids}
        
        # For each junction, create a separate model
        for junction_id in junction_ids:
            # Initialize replay memory for this junction
            self.replay_memory[junction_id] = deque(maxlen=memory_size)
            
            # Create main model
            self.models[junction_id] = self._build_model()
            
            # Create target model with same weights
            self.target_models[junction_id] = self._build_model()
            self.target_models[junction_id].set_weights(self.models[junction_id].get_weights())
        
        # If a model path is provided, load the model
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
            print(f"Loaded pre-trained DQN model from {model_path}")
        
        # Track training steps
        self.training_steps = 0
        
        print(f"Initialized DQN Controller with lr={learning_rate}, df={discount_factor}, er={exploration_rate}")
    
    def _build_model(self):
        """
        Build a neural network model for Q-value prediction.
        
        Returns:
            tf.keras.Model: A compiled neural network model
        """
        # Input shape depends on our state representation
        # State representation: [north_count, south_count, east_count, west_count,
        #                       north_wait, south_wait, east_wait, west_wait,
        #                       north_queue, south_queue, east_queue, west_queue]
        input_dim = 12  # Adjust based on your state representation
        
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(24, input_dim=input_dim, activation='relu'),
            tf.keras.layers.Dense(24, activation='relu'),
            tf.keras.layers.Dense(len(self.phase_sequence), activation='linear')  # Output one Q-value per action
        ])
        
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
                     loss='mse')
        
        return model
    
    def _get_state(self, junction_id):
        """
        Extract the state representation for a junction.
        
        Args:
            junction_id (str): The ID of the junction
            
        Returns:
            numpy.ndarray: State vector for the neural network
        """
        # Default state if no traffic data
        default_state = np.zeros(12)
        
        if junction_id not in self.traffic_state:
            return default_state
        
        traffic_state = self.traffic_state[junction_id]
        
        # Extract traffic metrics
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
        
        # Normalize state values (this helps neural networks learn more effectively)
        max_vehicle_count = 30.0  # Assumed maximum, adjust based on your simulation
        max_wait_time = 60.0
        max_queue_length = 20.0
        
        # Create and normalize the state vector
        state = np.array([
            north_count / max_vehicle_count,
            south_count / max_vehicle_count,
            east_count / max_vehicle_count,
            west_count / max_vehicle_count,
            north_wait / max_wait_time,
            south_wait / max_wait_time,
            east_wait / max_wait_time,
            west_wait / max_wait_time,
            north_queue / max_queue_length,
            south_queue / max_queue_length,
            east_queue / max_queue_length,
            west_queue / max_queue_length
        ])
        
        return state
    
    def _get_reward(self, junction_id):
        """
        Calculate the reward for the current state.
        
        The reward function is designed to:
        - Minimize waiting time (negative reward for waiting)
        - Maximize throughput (positive reward for moving vehicles)
        - Balance flow (penalize imbalanced vehicle distribution)
        
        Args:
            junction_id (str): The ID of the junction
            
        Returns:
            float: The calculated reward
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
        
        # 1. Waiting time penalty (more negative for longer waits)
        # Squared penalty for waiting time creates exponentially growing penalties for longer waits
        wait_penalty = -0.5 * ((north_wait ** 2) + (south_wait ** 2) + 
                               (east_wait ** 2) + (west_wait ** 2))
        
        # 2. Queue length penalty (more negative for longer queues)
        queue_penalty = -0.2 * (north_queue + south_queue + east_queue + west_queue)
        
        # 3. Throughput reward (more positive for more vehicles moving)
        total_vehicles = north_count + south_count + east_count + west_count
        total_queue = north_queue + south_queue + east_queue + west_queue
        moving_vehicles = max(0, total_vehicles - total_queue)
        throughput_reward = 0.1 * moving_vehicles
        
        # 4. Balance reward (penalize imbalance between directions)
        ns_total = north_count + south_count
        ew_total = east_count + west_count
        
        if total_vehicles > 0:
            balance_factor = min(ns_total, ew_total) / max(1, max(ns_total, ew_total))
            balance_reward = 0.3 * balance_factor
        else:
            balance_reward = 0.3  # Perfect balance with no vehicles
        
        # Combine all reward components
        total_reward = wait_penalty + queue_penalty + throughput_reward + balance_reward
        
        return total_reward
    
    def _select_action(self, state, junction_id):
        """
        Select an action using epsilon-greedy policy based on Q-values from the neural network.
        
        Args:
            state: The current state (numpy array)
            junction_id (str): The ID of the junction
            
        Returns:
            str: The selected phase (action)
        """
        # Exploration: random action
        if np.random.random() < self.exploration_rate:
            return np.random.choice(self.phase_sequence)
        
        # Exploitation: best action according to the model
        # Reshape state for the neural network (batch size of 1)
        state_tensor = np.reshape(state, [1, len(state)])
        
        # Get Q-values for all actions
        q_values = self.models[junction_id].predict(state_tensor, verbose=0)[0]
        
        # Get the action with the highest Q-value
        action_index = np.argmax(q_values)
        
        # Return the phase corresponding to this action
        return self.phase_sequence[action_index]
    
    def _remember(self, junction_id, state, action, reward, next_state, done=False):
        """
        Store experience in replay memory.
        
        Args:
            junction_id (str): The ID of the junction
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether this is a terminal state
        """
        # Convert action (phase string) to index
        action_index = self.phase_sequence.index(action)
        
        # Store the experience tuple
        self.replay_memory[junction_id].append((state, action_index, reward, next_state, done))
    
    def _replay(self, junction_id):
        """
        Train the neural network by replaying experiences.
        
        Args:
            junction_id (str): The ID of the junction
        """
        # Skip if not enough experiences
        if len(self.replay_memory[junction_id]) < self.batch_size:
            return
        
        # Sample a batch of experiences
        minibatch = random.sample(self.replay_memory[junction_id], self.batch_size)
        
        # Prepare batches for the neural network
        states = np.zeros((self.batch_size, 12))  # Adjust shape based on state representation
        targets = np.zeros((self.batch_size, len(self.phase_sequence)))
        
        for i, (state, action, reward, next_state, done) in enumerate(minibatch):
            # Reshape state for prediction
            state_tensor = np.reshape(state, [1, len(state)])
            next_state_tensor = np.reshape(next_state, [1, len(next_state)])
            
            # Predict current Q-values
            target = self.models[junction_id].predict(state_tensor, verbose=0)[0]
            
            if done:
                # Terminal state
                target[action] = reward
            else:
                # Non-terminal state
                # Use target network for stable Q-value estimates
                t = self.target_models[junction_id].predict(next_state_tensor, verbose=0)[0]
                target[action] = reward + self.discount_factor * np.amax(t)
            
            states[i] = state
            targets[i] = target
        
        # Train the model
        self.models[junction_id].fit(states, targets, epochs=1, verbose=0)
        
        # Increment training steps counter
        self.training_steps += 1
    
    def _update_target_model(self, junction_id):
        """
        Update the target model weights with the main model weights.
        
        Args:
            junction_id (str): The ID of the junction
        """
        self.target_models[junction_id].set_weights(self.models[junction_id].get_weights())
        print(f"Updated target model for junction {junction_id}")
    
    def decide_phase(self, junction_id, current_time):
        """
        Decide the next traffic light phase using DQN.
        
        Args:
            junction_id (str): The ID of the junction to control
            current_time (float): Current simulation time
            
        Returns:
            str: The traffic light state to set
        """
        # Record start time for response time measurement
        response_start = time.time()
        
        # Get the current state
        current_state = self._get_state(junction_id)
        
        # If this is the first time, just select an action
        if self.last_actions.get(junction_id) is None:
            action = self._select_action(current_state, junction_id)
            self.last_actions[junction_id] = action
            self.current_states[junction_id] = current_state
            
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
        
        # Store the experience
        self._remember(junction_id, prev_state, prev_action, reward, current_state)
        
        # Train the model by replaying experiences
        self._replay(junction_id)
        
        # Increment step counter
        self.step_counters[junction_id] += 1
        
        # Update target network periodically
        if self.step_counters[junction_id] % self.target_update_frequency == 0:
            self._update_target_model(junction_id)
        
        # Select next action
        action = self._select_action(current_state, junction_id)
        self.last_actions[junction_id] = action
        self.current_states[junction_id] = current_state
        
        # Record decision time
        self.decision_times.append(time.time() - response_start)
        
        # Record response time
        self.response_times.append(time.time() - response_start)
        
        return action
    
    def save_model(self, filepath):
        """
        Save the models for all junctions.
        
        Args:
            filepath (str): Base path to save the models
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save each junction's model
        for junction_id in self.junction_ids:
            model_path = f"{filepath}_{junction_id}.h5"
            self.models[junction_id].save(model_path)
        
        print(f"Models saved to {filepath}_[junction_id].h5")
        return True
    
    def load_model(self, filepath):
        """
        Load the models for all junctions.
        
        Args:
            filepath (str): Base path to load the models from
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        success = True
        
        # Load each junction's model
        for junction_id in self.junction_ids:
            model_path = f"{filepath}_{junction_id}.h5"
            
            if os.path.exists(model_path):
                try:
                    self.models[junction_id] = tf.keras.models.load_model(model_path)
                    # Update target model with the same weights
                    self.target_models[junction_id].set_weights(self.models[junction_id].get_weights())
                    print(f"Loaded model for junction {junction_id}")
                except Exception as e:
                    print(f"Error loading model for junction {junction_id}: {e}")
                    success = False
            else:
                print(f"Model file not found for junction {junction_id}: {model_path}")
                success = False
        
        return success
    
    def get_training_info(self):
        """Get information about the training progress."""
        return {
            "training_steps": self.training_steps,
            "memory_size": {junction_id: len(memory) for junction_id, memory in self.replay_memory.items()},
            "exploration_rate": self.exploration_rate,
            "total_rewards": self.total_rewards,
            "average_reward": self.get_average_reward()
        }