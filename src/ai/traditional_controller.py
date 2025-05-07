import time
from src.ai.controller import TrafficController

class TraditionalController(TrafficController):
    """
    Traditional Traffic Controller implementation.
    """
    def __init__(self, junction_ids):
        """
        Initialise the traditional controller.
        """
        super().__init__(junction_ids)
        
        # Define fixed phase durations for each junction (in seconds)
        self.phase_durations = {
            junction_id: {
                "GrYr": 30.0,  # Green for north-south, red for east-west
                "yrGr": 5.0,   # Yellow transitioning to red for north-south
                "rGry": 30.0,  # Red for north-south, green for east-west
                "ryrG": 5.0    # Red for north-south, yellow transitioning to red for east-west
            }
            for junction_id in junction_ids
        }
        
        # Define phase sequence and maximum queue threshold
        self.phase_sequence = ["GrYr", "yrGr", "rGry", "ryrG"]
        self.max_queue_threshold = 8
        
        # Initialize the current phase for each junction
        for junction_id in junction_ids:
            self.current_phase[junction_id] = self.phase_sequence[0]
    
    def decide_phase(self, junction_id, current_time):
        """
        Decide the next traffic light phase for a junction.
        """
        # Record start time for response time measurement
        response_start = time.time()
        
        # Get the current phase
        current_phase = self.current_phase[junction_id]
        
        # Get the time this phase has been active
        phase_duration = current_time - self.last_change_time[junction_id]
        
        # Handle yellow phases with strict timing
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
        
        # Check for queue imbalance or excessive queuing in opposite direction
        if junction_id in self.traffic_state:
            junction_data = self.traffic_state[junction_id]
            
            # Get queue lengths
            north_queue = junction_data.get('north_queue', 0)
            south_queue = junction_data.get('south_queue', 0)
            east_queue = junction_data.get('east_queue', 0)
            west_queue = junction_data.get('west_queue', 0)
            
            # Calculate total queues by direction
            north_south_queue = north_queue + south_queue
            east_west_queue = east_queue + west_queue
            
            # Calculate dynamic minimum green time based on current queue
            if current_phase == "GrYr":
                min_green_time = min(5.0 + (north_south_queue * 1.5), 15.0)
                cross_queue = east_west_queue
            else:  # rGry
                min_green_time = min(5.0 + (east_west_queue * 1.5), 15.0)
                cross_queue = north_south_queue
            
            # Check if cross-direction queue exceeds threshold and minimum green time is met
            if cross_queue > self.max_queue_threshold and phase_duration >= min_green_time:
                current_index = self.phase_sequence.index(current_phase)
                next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
                
                # Record response time
                self.response_times.append(time.time() - response_start)
                return next_phase
            
            # Check for severe imbalance after minimum green time
            if current_phase == "GrYr" and phase_duration >= min_green_time:
                if north_south_queue == 0 and east_west_queue > 3:
                    # No vehicles in current direction but waiting in cross direction
                    current_index = self.phase_sequence.index(current_phase)
                    next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
                    
                    # Record response time
                    self.response_times.append(time.time() - response_start)
                    return next_phase
            
            elif current_phase == "rGry" and phase_duration >= min_green_time:
                if east_west_queue == 0 and north_south_queue > 3:
                    # No vehicles in current direction but waiting in cross direction
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