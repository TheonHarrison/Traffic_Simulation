import abc
import time
import random
import numpy as np

class TrafficController(abc.ABC):
    """
    Abstract base class for traffic light controllers.
    This defines the interface that both wired and wireless controllers will implement.
    """
    def __init__(self, junction_ids):
        """
        Initialize the traffic controller.

        Args:
            junction_ids (list): List of junction IDs to control
        """
        self.junction_ids = junction_ids
        # Initialize current_phase to None, we will decide a phase at first step
        self.current_phase = {junction_id: None for junction_id in junction_ids}
        self.phase_durations = {}  # Will be set by subclasses
        self.last_change_time = {junction_id: 0 for junction_id in junction_ids}

        # Statistics for performance evaluation
        self.response_times = []
        self.decision_times = []

        # Traffic state information
        self.traffic_state = {}
        
        # Store the expected traffic light state lengths for each junction
        self.tl_state_lengths = {}
        
        # Initialize phase sequence
        self.phase_sequence = ["GrYr", "yrGr", "rGry", "ryrG"]

    def update_traffic_state(self, traffic_state):
        """
        Update the controller's knowledge of the current traffic state.

        Args:
            traffic_state (dict): Dictionary containing traffic information
                                 for each junction and connecting road
        """
        self.traffic_state = traffic_state

    @abc.abstractmethod
    def decide_phase(self, junction_id, current_time):
        """
        Decide the traffic light phase for a junction.
        To be implemented by specific controller types.

        Args:
            junction_id (str): The ID of the junction to control
            current_time (float): Current simulation time

        Returns:
            str: The traffic light state to set
        """
        pass

    def get_phase_for_junction(self, junction_id, current_time):
        """
        Get the current phase for a specific junction.

        Args:
            junction_id (str): The ID of the junction
            current_time (float): Current simulation time

        Returns:
            str: Traffic light state string
        """
        import traci
        
        # Initialize tl_state_lengths if not already done
        if junction_id not in self.tl_state_lengths:
            try:
                # Get the current state to determine expected length
                current_state = traci.trafficlight.getRedYellowGreenState(junction_id)
                self.tl_state_lengths[junction_id] = len(current_state)
            except:
                # Default value if we can't get the current state
                self.tl_state_lengths[junction_id] = 4  # Default length
        
        current = self.current_phase[junction_id]

        # If no valid phase yet or if phase duration expired, decide a new phase
        if (current is None
            or junction_id not in self.phase_durations
            or current not in self.phase_durations[junction_id]
            or (current_time - self.last_change_time[junction_id] >= self.phase_durations[junction_id][current])):

            # Record start time for decision time measurement
            decision_start = time.time()

            # Get the new phase
            new_phase = self.decide_phase(junction_id, current_time)

            # Record decision time
            self.decision_times.append(time.time() - decision_start)

            # Update current phase and last change time
            self.current_phase[junction_id] = new_phase
            self.last_change_time[junction_id] = current_time

            # Adjust phase length to match expected length
            expected_length = self.tl_state_lengths.get(junction_id, 4)
            if len(new_phase) != expected_length:
                if len(new_phase) < expected_length:
                    # Extend by repeating the pattern
                    new_phase = new_phase * (expected_length // len(new_phase) + 1)
                    new_phase = new_phase[:expected_length]
                else:
                    # Truncate to expected length
                    new_phase = new_phase[:expected_length]
            
            return new_phase

        # Adjust current phase length if needed
        expected_length = self.tl_state_lengths.get(junction_id, 4)
        if len(current) != expected_length:
            if len(current) < expected_length:
                # Extend by repeating the pattern
                current = current * (expected_length // len(current) + 1)
                current = current[:expected_length]
            else:
                # Truncate to expected length
                current = current[:expected_length]
        
        return current

    def get_average_response_time(self):
        """Get the average response time for the controller's decisions"""
        if not self.response_times:
            return 0
        return sum(self.response_times) / len(self.response_times)

    def get_average_decision_time(self):
        """Get the average time taken to make decisions"""
        if not self.decision_times:
            return 0
        return sum(self.decision_times) / len(self.decision_times)