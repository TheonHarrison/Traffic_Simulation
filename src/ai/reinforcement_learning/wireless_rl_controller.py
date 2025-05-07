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
    wireless network conditions (variable latency, potential packet loss).
    """
    def __init__(self, junction_ids, learning_rate=0.1, discount_factor=0.9, 
                exploration_rate=0.3, state_bins=3, model_path=None,
                base_latency=0.05, computation_factor=0.1, packet_loss_prob=0.01):
        """
        Initialise the Wireless RL controller.
        
        Args:
            junction_ids: List of junction IDs to control
            learning_rate: Alpha parameter for Q-learning updates (0-1)
            discount_factor: Gamma parameter for future reward discounting (0-1)
            exploration_rate: Epsilon parameter for exploration vs. exploitation (0-1)
            state_bins: Number of bins to discretize continuous state variables
            model_path: Path to load a pre-trained Q-table (optional)
            base_latency: Base network latency in seconds
            computation_factor: Factor for additional computation time
            packet_loss_prob: Probability of packet loss (0-1)
        """
        # call the parent constructor with the correct number of arguments
        super().__init__(junction_ids, learning_rate, discount_factor, 
                        exploration_rate, state_bins, model_path)
        
        # wireless network simulation parameters
        self.base_latency = base_latency
        self.computation_factor = computation_factor
        self.packet_loss_prob = packet_loss_prob
        
        # Stats for network conditions
        self.total_latency = 0
        self.packet_losses = 0
        self.decision_count = 0
        
        # platoon processing parameters
        self.min_platoon_size = 2  # Minimum vehicles to consider as a platoon
        self.max_platoon_gap = 3.0  # Maximum gap (in seconds) between vehicles in a platoon
        self.platoon_extension_time = 2.0  # Time to extend green for each additional vehicle in platoon
        self.max_platoon_extension = 15.0  # Maximum extension time for platoons
        
        # modified phase durations to better handle platoons
        self.phase_durations = {
            junction_id: {
                "GrYr": 15.0,  # Base green time (will be extended for platoons)
                "yrGr": 5.0,   # Yellow transition time (fixed)
                "rGry": 15.0,  # Base green time (will be extended for platoons)
                "ryrG": 5.0    # Yellow transition time (fixed)
            }
            for junction_id in junction_ids
        }
        
        # track active platoons for each junction
        self.active_platoons = {junction_id: None for junction_id in junction_ids}
        
        # track the last measured queues for each junction to detect changes
        self.last_queue_measurements = {junction_id: {
            'north_south_queue': 0,
            'east_west_queue': 0,
            'time': 0
        } for junction_id in junction_ids}
        
        print(f"Initialised Wireless RL Controller with base_latency={base_latency}, " 
                f"computation_factor={computation_factor}, packet_loss_prob={packet_loss_prob}")
    
    def _detect_platoons(self, junction_id, traffic_state):
        """
        Detect vehicle platoons in the current traffic state.
        """
        if junction_id not in traffic_state:
            return {'north_south': 0, 'east_west': 0}
        
        junction_data = traffic_state[junction_id]
        
        # calculate total queue lengths in each direction
        north_south_queue = junction_data.get('north_queue', 0) + junction_data.get('south_queue', 0)
        east_west_queue = junction_data.get('east_queue', 0) + junction_data.get('west_queue', 0)
        
        # consider queues over min_platoon_size as potential platoons
        ns_platoon = north_south_queue >= self.min_platoon_size
        ew_platoon = east_west_queue >= self.min_platoon_size
        
        # calculate queue change rates to detect moving platoons
        current_time = time.time()
        last_measurement = self.last_queue_measurements[junction_id]
        time_diff = current_time - last_measurement['time']

        # only update if enough time has passed
        if time_diff > 1.0:  
            ns_change = north_south_queue - last_measurement['north_south_queue']
            ew_change = east_west_queue - last_measurement['east_west_queue']
            
            # Update last measurements
            self.last_queue_measurements[junction_id] = {
                'north_south_queue': north_south_queue,
                'east_west_queue': east_west_queue,
                'time': current_time
            }
            
            # adjust the platoon detection based on queue dynamics
            # if queue is decreasing, it means vehicles are moving - part of an active platoon
            if ns_change < 0 and north_south_queue > 0:
                ns_platoon = True
            if ew_change < 0 and east_west_queue > 0:
                ew_platoon = True
        
        return {
            'north_south': north_south_queue if ns_platoon else 0,
            'east_west': east_west_queue if ew_platoon else 0
        }
    
    def _calculate_platoon_green_time(self, platoon_size, base_green_time=15.0):
        """
        Calculate the appropriate green time to service a platoon.
        """
        if platoon_size <= 1:
            return base_green_time
        
        # each vehicle beyond the first extends the green time
        extension = min(self.max_platoon_extension, 
                       (platoon_size - 1) * self.platoon_extension_time)
        
        return base_green_time + extension
    
    def _calculate_dynamic_latency(self, traffic_complexity):
        """
        Calculate dynamic latency based on traffic complexity and random factors
        """
        # base latency - reduced for training purposes
        latency = self.base_latency * 0.5
        
        # add computation time based on traffic complexity - more reasonable scaling
        computation_time = traffic_complexity * self.computation_factor * 0.5
        
        # add random fluctuation to simulate wireless interference
        # keep this minimal during training to allow learning
        interference = random.uniform(0, 0.05) * traffic_complexity
        
        total_latency = latency + computation_time + interference
        
        # cap maximum latency for training purposes
        return min(total_latency, 0.1)  # Max 100ms latency during training
    
    def _simulate_packet_loss(self):
        """
        Simulate packet loss in wireless network.
        """
        # during training, use much lower packet loss probability
        training_packet_loss_prob = min(0.001, self.packet_loss_prob)
        
        if random.random() < training_packet_loss_prob:
            self.packet_losses += 1
            return True
        return False
    
    def _get_reward(self, junction_id):
        """
        Calculate the reward for the current state, with emphasis on platoon processing.

        """
        # get the basic reward from the parent class
        base_reward = super()._get_reward(junction_id)
        
        # add platoon-based reward components
        if junction_id in self.traffic_state:
            junction_data = self.traffic_state[junction_id]
            
            # extract metrics
            north_count = junction_data.get('north_count', 0)
            south_count = junction_data.get('south_count', 0)
            east_count = junction_data.get('east_count', 0)
            west_count = junction_data.get('west_count', 0)
            
            north_queue = junction_data.get('north_queue', 0)
            south_queue = junction_data.get('south_queue', 0)
            east_queue = junction_data.get('east_queue', 0)
            west_queue = junction_data.get('west_queue', 0)
            
            # calculate vehicles passing through (not queued)
            ns_passing = max(0, north_count + south_count - north_queue - south_queue)
            ew_passing = max(0, east_count + west_count - east_queue - west_queue)
            
            # reward for processing vehicles in platoons
            platoon_reward = 0
            
            # reward for north-south platoon / give bonus per vehicle in platoon
            if ns_passing >= self.min_platoon_size and self.current_phase.get(junction_id) == "GrYr":
                platoon_reward += ns_passing * 0.5  
            
            # reward for east-west platoon / give bonus per vehicle in platoon
            if ew_passing >= self.min_platoon_size and self.current_phase.get(junction_id) == "rGry":
                platoon_reward += ew_passing * 0.5  
            
            # total reward with platoon component
            total_reward = base_reward + platoon_reward
            return total_reward
        
        return base_reward
    
    def decide_phase(self, junction_id, current_time):
        """
        Decide the next traffic light phase using RL with simulated wireless conditions.
        """
        # get the current traffic state for complexity calculation
        if junction_id in self.traffic_state:
            traffic_state = self.traffic_state[junction_id]
            
            # calculate traffic complexity based on total vehicles and balance
            north_count = traffic_state.get('north_count', 0)
            south_count = traffic_state.get('south_count', 0)
            east_count = traffic_state.get('east_count', 0)
            west_count = traffic_state.get('west_count', 0)
            
            total_vehicles = north_count + south_count + east_count + west_count
            
            if total_vehicles > 0:
                ns_total = north_count + south_count
                ew_total = east_count + west_count
                
                # improved balance calculation
                balance = abs(ns_total - ew_total) / total_vehicles
                
                # normalize total vehicles (assuming max of 50 is high complexity)
                volume_factor = min(1.0, total_vehicles / 50.0)
                
                # calculate traffic complexity with more weight on volume
                traffic_complexity = (volume_factor * 0.8) + (balance * 0.2)
            else:
                traffic_complexity = 0.0
        else:
            traffic_complexity = 0.3  # Default complexity
        
        # store the current state before applying network effects
        # this ensures i have the state for learning regardless of network conditions
        current_state = self._get_state(junction_id)
        self.current_states[junction_id] = current_state
        
        # detect vehicle platoons in the current traffic state
        platoons = self._detect_platoons(junction_id, self.traffic_state)
        
        # simulate wireless network conditions
        dynamic_latency = self._calculate_dynamic_latency(traffic_complexity)
        
        # use reduced latency during training
        actual_latency = dynamic_latency * 0.1 if self.exploration_rate > 0.1 else dynamic_latency
        time.sleep(actual_latency)
        
        self.total_latency += dynamic_latency
        self.decision_count += 1
        
        # simulate potential packet loss
        packet_lost = self._simulate_packet_loss()
        
        # get reward for the previous action / to ensure learning happens even with packet loss
        reward = self._get_reward(junction_id)
        
        # always record rewards for tracking learning progress
        self.total_rewards += reward
        self.reward_history.append(reward)
        
        # only update Q-values if we have previous state and action
        prev_state = self.current_states.get(junction_id)
        prev_action = self.last_actions.get(junction_id)
        
        if prev_state is not None and prev_action is not None:
            # update Q-value
            self._update_q_value(prev_state, prev_action, current_state, reward, junction_id)
        
        # if packet loss, return the last action but still learn
        if packet_lost and junction_id in self.last_actions and self.last_actions[junction_id] is not None:
            return self.last_actions[junction_id]
        
        # get the current phase
        current_phase = self.current_phase.get(junction_id)
        if current_phase is None:
            # initialize with a default phase
            current_phase = self.phase_sequence[0]
            self.current_phase[junction_id] = current_phase
        
        # for yellow phases, must enforce strict timing
        if current_phase in ["yrGr", "ryrG"]:
            phase_duration = current_time - self.last_change_time[junction_id]
            if phase_duration >= self.phase_durations[junction_id][current_phase]:
                # record start time for response time measurement
                response_start = time.time()
                
                # get the next phase from RL after yellow completes
                action = self._select_action(current_state, junction_id)
                
                # record response time
                self.response_times.append(time.time() - response_start)
                
                # store the action
                self.last_actions[junction_id] = action
                
                # ensure action is a valid phase string
                if not isinstance(action, str) or action not in self.phase_sequence:
                    action = self.phase_sequence[0]
                
                # ensure the phase matches the expected length for this junction
                if hasattr(self, 'tl_state_lengths') and junction_id in self.tl_state_lengths:
                    expected_length = self.tl_state_lengths[junction_id]
                    if len(action) != expected_length:
                        # Adjust phase length to match expected length
                        if len(action) < expected_length:
                            action = action * (expected_length // len(action)) + action[:expected_length % len(action)]
                        else:
                            action = action[:expected_length]
                
                return action
            else:
                # keep yellow phase until duration is met
                return current_phase
        
        # for green phases, check if we need to extend for platoons
        phase_duration = current_time - self.last_change_time[junction_id]
        
        # Check for active platoons that need servicing
        if current_phase == "GrYr" and platoons['north_south'] > 0:
            platoon_size = platoons['north_south']
            green_time = self._calculate_platoon_green_time(platoon_size, 
                                                            self.phase_durations[junction_id][current_phase])
            
            if phase_duration < green_time:
                # Keep green to service the platoon
                # Record this active platoon
                self.active_platoons[junction_id] = {
                    'direction': 'north_south',
                    'size': platoon_size,
                    'remaining': green_time - phase_duration
                }
                
                return current_phase
        
        elif current_phase == "rGry" and platoons['east_west'] > 0:
            platoon_size = platoons['east_west']
            green_time = self._calculate_platoon_green_time(platoon_size,
                                                            self.phase_durations[junction_id][current_phase])
            
            if phase_duration < green_time:
                # Keep green to service the platoon
                self.active_platoons[junction_id] = {
                    'direction': 'east_west',
                    'size': platoon_size,
                    'remaining': green_time - phase_duration
                }
                
                return current_phase
        
        # no active platoon needs servicing, use RL to decide phase
        self.active_platoons[junction_id] = None
        
        # record start time for response time measurement
        response_start = time.time()
        
        # select next action
        action = self._select_action(current_state, junction_id)
        
        # record response time
        self.response_times.append(time.time() - response_start)
        
        # ensure action is a valid phase string
        if not isinstance(action, str) or action not in self.phase_sequence:
            print(f"Warning: Invalid action type {type(action)} or value {action}. Using default phase.")
            action = self.phase_sequence[0]
        
        # store the action
        self.last_actions[junction_id] = action
        
        # ensure the phase matches the expected length for this junction
        if hasattr(self, 'tl_state_lengths') and junction_id in self.tl_state_lengths:
            expected_length = self.tl_state_lengths[junction_id]
            if len(action) != expected_length:
                # adjust phase length to match expected length
                if len(action) < expected_length:
                    action = action * (expected_length // len(action)) + action[:expected_length % len(action)]
                else:
                    action = action[:expected_length]
        
        return action
    
    def reset_metrics(self):
        """Reset accumulated metrics for a new episode"""
        self.total_rewards = 0
        self.reward_history = []
        self.response_times = []
        self.decision_times = []
        self.total_latency = 0
        self.packet_losses = 0
        self.decision_count = 0
        
        # don't reset the Q-tables as those need to persist between episodes
    
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