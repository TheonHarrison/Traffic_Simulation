# src/ai/reinforcement_learning/wired_rl_controller.py
import os
import sys
import time
import numpy as np
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from src.ai.reinforcement_learning.q_learning_controller import QLearningController

class WiredRLController(QLearningController):
    """
    Wired Reinforcement Learning Controller wired network conditions
    (fixed latency, reliable communication).
    """
    def __init__(self, junction_ids, learning_rate=0.1, discount_factor=0.9, 
                exploration_rate=0.3, state_bins=3, model_path=None,
                network_latency=0.1):
        """
        Initialise the Wired RL controller.
        """
        # Call the parent class constructor
        super().__init__(junction_ids, learning_rate=learning_rate, 
                        discount_factor=discount_factor, 
                        exploration_rate=exploration_rate,
                        state_bins=state_bins, 
                        model_path=model_path)
        
        # wired network simulation parameter
        self.network_latency = network_latency
        
        # statistics
        self.total_latency = 0
        self.decision_count = 0
        
        # initialise traffic light state lengths dictionary if not exists
        if not hasattr(self, 'tl_state_lengths'):
            self.tl_state_lengths = {}
        
        # processing parameters
        self.min_platoon_size = 2  # minimum vehicles to consider as a platoon
        self.max_platoon_gap = 3.0  # maximum gap (in seconds) between vehicles in a platoon
        self.platoon_extension_time = 2.0  # time to extend green for each additional vehicle in platoon
        self.max_platoon_extension = 15.0  # maximum extension time for platoons
        
        # modified phase durations to better handle platoons
        self.phase_durations = {
            junction_id: {
                "GrYr": 15.0,  # Base green time (will be extended for platoons)
                "yrGr": 5.0,   # yellow transition time (fixed)
                "rGry": 15.0,  # base green time (will be extended for platoons)
                "ryrG": 5.0    # yellow transition time (fixed)
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
        
        print(f"Initialised Wired RL Controller with network_latency={network_latency}")
    
    def _detect_platoons(self, junction_id, traffic_state):
        """
        Detect vehicle platoons in the current traffic state.
        """
        if junction_id not in traffic_state:
            return {'north_south': 0, 'east_west': 0}
        
        junction_data = traffic_state[junction_id]
        
        # Calculate total queue lengths in each direction
        north_south_queue = junction_data.get('north_queue', 0) + junction_data.get('south_queue', 0)
        east_west_queue = junction_data.get('east_queue', 0) + junction_data.get('west_queue', 0)
        
        # Consider queues over min_platoon_size as potential platoons
        ns_platoon = north_south_queue >= self.min_platoon_size
        ew_platoon = east_west_queue >= self.min_platoon_size
        
        # Calculate queue change rates to detect moving platoons
        current_time = time.time()
        last_measurement = self.last_queue_measurements[junction_id]
        time_diff = current_time - last_measurement['time']
        
        if time_diff > 1.0:  # Only update if enough time has passed
            ns_change = north_south_queue - last_measurement['north_south_queue']
            ew_change = east_west_queue - last_measurement['east_west_queue']
            
            # Update last measurements
            self.last_queue_measurements[junction_id] = {
                'north_south_queue': north_south_queue,
                'east_west_queue': east_west_queue,
                'time': current_time
            }
            
            # Adjust platoon detection based on queue dynamics
            # if queue is decreasing, it means vehicles are moving part of an active platoon
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
        
        # Each vehicle beyond the first extends the green time
        extension = min(self.max_platoon_extension, 
                       (platoon_size - 1) * self.platoon_extension_time)
        
        return base_green_time + extension
    
    def _get_reward(self, junction_id):
        """
        Calculate the reward for the current state, with emphasis on platoon processing.
        """
        # Get the basic reward from the parent class
        base_reward = super()._get_reward(junction_id)
        
        # Add platoon-based reward components
        if junction_id in self.traffic_state:
            junction_data = self.traffic_state[junction_id]
            
            # Extract metrics
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
            
            # reward for north-south platoon
            if ns_passing >= self.min_platoon_size and self.current_phase.get(junction_id) == "GrYr":
                platoon_reward += ns_passing * 0.5  # Bonus per vehicle in platoon
            
            # reward for east-west platoon
            if ew_passing >= self.min_platoon_size and self.current_phase.get(junction_id) == "rGry":
                platoon_reward += ew_passing * 0.5  # Bonus per vehicle in platoon
            
            # total reward with platoon component
            total_reward = base_reward + platoon_reward
            return total_reward
        
        return base_reward
    
    def decide_phase(self, junction_id, current_time):
        """
        Decide the next traffic light phase using RL and simulating wired conditions.
        """
        # simulate network latency for the wired connection
        time.sleep(self.network_latency)
        self.total_latency += self.network_latency
        self.decision_count += 1
        
        # detect vehicle platoons in the current traffic state
        platoons = self._detect_platoons(junction_id, self.traffic_state)
        
        # get the current phase
        current_phase = self.current_phase[junction_id]
        
        # for yellow phases, enforce strict timing
        if current_phase in ["yrGr", "ryrG"]:
            phase_duration = current_time - self.last_change_time[junction_id]
            if phase_duration >= self.phase_durations[junction_id][current_phase]:
                # get the phase from RL after yellow completes
                phase = super().decide_phase(junction_id, current_time)
            else:
                # keep yellow phase until duration is met
                phase = current_phase
        else:
            # for green phases, check if we need to extend for platoons
            phase_duration = current_time - self.last_change_time[junction_id]
            
            # check for active platoons that need servicing
            active_platoon = False
            
            if current_phase == "GrYr" and platoons['north_south'] > 0:
                platoon_size = platoons['north_south']
                green_time = self._calculate_platoon_green_time(platoon_size, 
                                                                self.phase_durations[junction_id][current_phase])
                
                if phase_duration < green_time:
                    # Keep green to service the platoon
                    active_platoon = True
                    phase = current_phase
                    # Record this active platoon
                    self.active_platoons[junction_id] = {
                        'direction': 'north_south',
                        'size': platoon_size,
                        'remaining': green_time - phase_duration
                    }
            
            elif current_phase == "rGry" and platoons['east_west'] > 0:
                platoon_size = platoons['east_west']
                green_time = self._calculate_platoon_green_time(platoon_size,
                                                                self.phase_durations[junction_id][current_phase])
                
                if phase_duration < green_time:
                    # Keep green to service the platoon
                    active_platoon = True
                    phase = current_phase
                    # Record this active platoon
                    self.active_platoons[junction_id] = {
                        'direction': 'east_west',
                        'size': platoon_size,
                        'remaining': green_time - phase_duration
                    }
            
            if not active_platoon:
                # no active platoon needs servicing, use RL to decide phase
                self.active_platoons[junction_id] = None
                phase = super().decide_phase(junction_id, current_time)
        
        # Ensure phase is a string
        if not isinstance(phase, str):
            print(f"Warning: decide_phase returned a non-string value: {phase} ({type(phase)}). Using default phase.")
            phase = self.phase_sequence[0]
        
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