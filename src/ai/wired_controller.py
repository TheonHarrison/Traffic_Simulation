import time
import random
import numpy as np
from src.ai.controller import TrafficController

class WiredController(TrafficController):
    """
    Wired AI Traffic Controller implementation.
    """
    def __init__(self, junction_ids, network_latency=0.1):
        """
        Initialise the wired controller.
        """
        super().__init__(junction_ids)
        self.network_latency = network_latency
        
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
        
        # Define the phase sequence for each junction
        self.phase_sequence = ["GrYr", "yrGr", "rGry", "ryrG"]
        
        # Define queue thresholds and max green time
        self.max_queue_threshold = 8
        self.max_green_time = 45.0
        
        # Initialise the current phase for each junction
        for junction_id in junction_ids:
            self.current_phase[junction_id] = self.phase_sequence[0]
        
        # Track last queue lengths to detect changes
        self.last_queue_lengths = {}
    
    def decide_phase(self, junction_id, current_time):
        """
        Decide the next traffic light phase for a junction.
        """
        # Simulate network latency for the wired connection
        time.sleep(self.network_latency)
        
        # Record start time for response time measurement
        response_start = time.time()
        
        # Get the current phase
        current_phase = self.current_phase[junction_id]
        
        # Get the time this phase has been active
        phase_duration = current_time - self.last_change_time[junction_id]
        
        # For yellow phases, enforce strict timing
        if current_phase in ["yrGr", "ryrG"]:
            if phase_duration >= self.phase_durations[junction_id][current_phase]:
                current_index = self.phase_sequence.index(current_phase)
                next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
                
                # Record response time
                self.response_times.append(time.time() - response_start)
                return next_phase
            else:
                # Keep yellow phase until duration is met
                self.response_times.append(time.time() - response_start)
                return current_phase
        
        # If green phase has exceeded maximum time, move to next phase
        if phase_duration > self.max_green_time:
            current_index = self.phase_sequence.index(current_phase)
            next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
            
            # Record response time
            self.response_times.append(time.time() - response_start)
            return next_phase
        
        # Basic AI logic based on traffic state
        if junction_id in self.traffic_state:
            junction_data = self.traffic_state[junction_id]
            
            # Get vehicle counts and queue lengths on each approach
            north_count = junction_data.get('north_count', 0)
            south_count = junction_data.get('south_count', 0)
            east_count = junction_data.get('east_count', 0)
            west_count = junction_data.get('west_count', 0)
            
            north_queue = junction_data.get('north_queue', 0)
            south_queue = junction_data.get('south_queue', 0)
            east_queue = junction_data.get('east_queue', 0)
            west_queue = junction_data.get('west_queue', 0)
            
            north_wait = junction_data.get('north_wait', 0)
            south_wait = junction_data.get('south_wait', 0)
            east_wait = junction_data.get('east_wait', 0)
            west_wait = junction_data.get('west_wait', 0)
            
            # Group by direction
            north_south_count = north_count + south_count
            east_west_count = east_count + west_count
            
            north_south_queue = north_queue + south_queue
            east_west_queue = east_queue + west_queue
            
            # Calculate average wait times per direction
            ns_wait = (north_wait * north_count + south_wait * south_count) / max(1, north_south_count)
            ew_wait = (east_wait * east_count + west_wait * west_count) / max(1, east_west_count)
            
            # Initialize queue history if not yet tracked
            if junction_id not in self.last_queue_lengths:
                self.last_queue_lengths[junction_id] = {
                    'north_south_queue': north_south_queue,
                    'east_west_queue': east_west_queue,
                    'last_check_time': current_time
                }
            
            # Check if queues are growing or shrinking
            time_since_last_check = current_time - self.last_queue_lengths[junction_id]['last_check_time']
            
            if time_since_last_check >= 3.0:  # Check every 3 seconds
                prev_ns_queue = self.last_queue_lengths[junction_id]['north_south_queue']
                prev_ew_queue = self.last_queue_lengths[junction_id]['east_west_queue']
                
                # Calculate rate of change in queue lengths
                ns_queue_change = north_south_queue - prev_ns_queue
                ew_queue_change = east_west_queue - prev_ew_queue
                
                # Update last queue lengths
                self.last_queue_lengths[junction_id] = {
                    'north_south_queue': north_south_queue,
                    'east_west_queue': east_west_queue,
                    'last_check_time': current_time
                }
            else:
                # Use previous values if not enough time has passed
                ns_queue_change = 0
                ew_queue_change = 0
            
            # Calculate dynamic minimum green time based on current queue
            if current_phase == "GrYr":
                min_green_time = min(5.0 + (north_south_queue * 1.0), 15.0)
                adjusted_max_green = max(15.0, self.max_green_time - (east_west_queue * 1.5))
            else:  # rGry
                min_green_time = min(5.0 + (east_west_queue * 1.0), 15.0)
                adjusted_max_green = max(15.0, self.max_green_time - (north_south_queue * 1.5))
            
            # If green phase has exceeded adjusted maximum time, move to next phase
            if phase_duration > adjusted_max_green:
                current_index = self.phase_sequence.index(current_phase)
                next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
                
                # Record response time
                self.response_times.append(time.time() - response_start)
                return next_phase
            
            # Check if cross-direction queue exceeds threshold and minimum green time is met
            if current_phase == "GrYr" and east_west_queue > self.max_queue_threshold and phase_duration >= min_green_time:
                current_index = self.phase_sequence.index(current_phase)
                next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
                
                # Record response time
                self.response_times.append(time.time() - response_start)
                return next_phase
            
            elif current_phase == "rGry" and north_south_queue > self.max_queue_threshold and phase_duration >= min_green_time:
                current_index = self.phase_sequence.index(current_phase)
                next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
                
                # Record response time
                self.response_times.append(time.time() - response_start)
                return next_phase
            
            # Check for waiting time imbalance
            if current_phase == "GrYr" and phase_duration >= min_green_time:
                if ew_wait > ns_wait * 2.0 and east_west_queue > 0:
                    # Cross direction waiting much longer
                    current_index = self.phase_sequence.index(current_phase)
                    next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
                    
                    # Record response time
                    self.response_times.append(time.time() - response_start)
                    return next_phase
            
            elif current_phase == "rGry" and phase_duration >= min_green_time:
                if ns_wait > ew_wait * 2.0 and north_south_queue > 0:
                    # Cross direction waiting much longer
                    current_index = self.phase_sequence.index(current_phase)
                    next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
                    
                    # Record response time
                    self.response_times.append(time.time() - response_start)
                    return next_phase
            
            # Check for empty queues in current direction but vehicles waiting in cross direction
            if current_phase == "GrYr" and phase_duration >= min_green_time:
                if north_south_queue == 0 and east_west_queue > 0:
                    current_index = self.phase_sequence.index(current_phase)
                    next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
                    
                    # Record response time
                    self.response_times.append(time.time() - response_start)
                    return next_phase
            
            elif current_phase == "rGry" and phase_duration >= min_green_time:
                if east_west_queue == 0 and north_south_queue > 0:
                    current_index = self.phase_sequence.index(current_phase)
                    next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
                    
                    # Record response time
                    self.response_times.append(time.time() - response_start)
                    return next_phase
        
        # Follow standard phase durations if no special conditions
        if phase_duration >= self.phase_durations[junction_id][current_phase]:
            current_index = self.phase_sequence.index(current_phase)
            next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
            
            # Record response time
            self.response_times.append(time.time() - response_start)
            return next_phase
        
        # Otherwise, maintain the current phase
        self.response_times.append(time.time() - response_start)
        return current_phase