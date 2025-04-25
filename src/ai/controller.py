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
        self.current_phase = {junction_id: 0 for junction_id in junction_ids}
        self.phase_durations = {}  # Will be set by subclasses
        self.last_change_time = {junction_id: 0 for junction_id in junction_ids}
        
        # Statistics for performance evaluation
        self.response_times = []
        self.decision_times = []
        
        # Traffic state information
        self.traffic_state = {}
    
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
        # Check if it's time to change the phase
        time_since_last_change = current_time - self.last_change_time[junction_id]
        
        # If current phase duration has passed, decide on a new phase
        if junction_id in self.phase_durations and \
           self.current_phase[junction_id] in self.phase_durations[junction_id] and \
           time_since_last_change >= self.phase_durations[junction_id][self.current_phase[junction_id]]:
            
            # Record start time for decision time measurement
            decision_start = time.time()
            
            # Get the new phase
            new_phase = self.decide_phase(junction_id, current_time)
            
            # Record decision time
            self.decision_times.append(time.time() - decision_start)
            
            # Update current phase and last change time
            self.current_phase[junction_id] = new_phase
            self.last_change_time[junction_id] = current_time
        
        return self.current_phase[junction_id]
    
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