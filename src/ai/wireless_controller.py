import time
import random
import numpy as np
from src.ai.controller import TrafficController

class WirelessController(TrafficController):
    """
    Wireless AI Traffic Controller implementation.
    """
    def __init__(self, junction_ids, base_latency=0.05, computation_factor=0.1):
        """
        Initialise the wireless controller.
        """
        super().__init__(junction_ids)
        self.base_latency = base_latency
        self.computation_factor = computation_factor
        
        # define phase durations for each junction (in seconds)
        self.phase_durations = {
            junction_id: {
                "GrYr": 30.0,  # green for north-south, red for east-west
                "yrGr": 5.0,   # yellow transitioning to red for north-south
                "rGry": 30.0,  # red for north-south, green for east-west
                "ryrG": 5.0    # red for north-south, yellow transitioning to red for east-west
            }
            for junction_id in junction_ids
        }
        
        # define the phase sequence for each junction
        self.phase_sequence = ["GrYr", "yrGr", "rGry", "ryrG"]
        
        # define queue thresholds and max green time
        self.max_queue_threshold = 7  # Lower threshold for wireless
        self.max_green_time = 40.0  # Slightly shorter max green time
        
        # initialise the current phase for each junction
        for junction_id in junction_ids:
            self.current_phase[junction_id] = self.phase_sequence[0]
        
        # track queue dynamics
        self.queue_history = {}
        
        # last decision parameters
        self.last_decision_params = {}
    
    def _calculate_dynamic_latency(self, traffic_complexity):
        """
        Calculate dynamic latency based on traffic complexity and random factors.
        """
        # base latency
        latency = self.base_latency
        
        # add computation time based on traffic complexity
        computation_time = traffic_complexity * self.computation_factor
        
        # add random fluctuation to simulate wireless interference
        interference = random.uniform(0, 0.1) * traffic_complexity
        
        return latency + computation_time + interference
    
    def decide_phase(self, junction_id, current_time):
        """
        Decide the next traffic light phase for a junction.
        """
        # get the current phase
        current_phase = self.current_phase[junction_id]
        
        # get the time this phase has been active
        phase_duration = current_time - self.last_change_time[junction_id]
        
        # default complexity for the case where we don't have traffic data
        traffic_complexity = 0.5
        
        # initialise variables for AI decision
        north_south_count = 0
        east_west_count = 0
        north_south_queue = 0
        east_west_queue = 0
        waiting_times = {"north": 0, "south": 0, "east": 0, "west": 0}
        queue_lengths = {"north": 0, "south": 0, "east": 0, "west": 0}
        
        # if we have traffic data, extract relevant metrics
        if junction_id in self.traffic_state:
            junction_data = self.traffic_state[junction_id]
            
            # extract vehicle counts, waiting times, and queue lengths
            north_count = junction_data.get('north_count', 0)
            south_count = junction_data.get('south_count', 0)
            east_count = junction_data.get('east_count', 0)
            west_count = junction_data.get('west_count', 0)
            
            north_south_count = north_count + south_count
            east_west_count = east_count + west_count
            
            for direction in ['north', 'south', 'east', 'west']:
                waiting_times[direction] = junction_data.get(f'{direction}_wait', 0)
                queue_lengths[direction] = junction_data.get(f'{direction}_queue', 0)
            
            # group queue lengths by direction
            north_south_queue = queue_lengths['north'] + queue_lengths['south']
            east_west_queue = queue_lengths['east'] + queue_lengths['west']
            
            # calculate traffic complexity based on total vehicle count and balance
            total_vehicles = north_south_count + east_west_count
            if total_vehicles > 0:
                # balance factor: 0 for perfectly balanced, 1 for completely imbalanced
                balance = abs(north_south_count - east_west_count) / total_vehicles
                # normalize total vehicles to a 0-1 scale (assuming max of 50 vehicles is high complexity)
                volume_factor = min(1.0, total_vehicles / 50.0)
                # combine factors to get overall complexity
                traffic_complexity = (volume_factor * 0.7) + (balance * 0.3)
            else:
                traffic_complexity = 0.0
            
            # track queue history for this junction
            if junction_id not in self.queue_history:
                self.queue_history[junction_id] = {
                    'times': [current_time],
                    'north_south_queue': [north_south_queue],
                    'east_west_queue': [east_west_queue]
                }
            else:
                # add new data point
                self.queue_history[junction_id]['times'].append(current_time)
                self.queue_history[junction_id]['north_south_queue'].append(north_south_queue)
                self.queue_history[junction_id]['east_west_queue'].append(east_west_queue)
                
                # keep only recent history (last 8 time steps)
                if len(self.queue_history[junction_id]['times']) > 8:
                    self.queue_history[junction_id]['times'].pop(0)
                    self.queue_history[junction_id]['north_south_queue'].pop(0)
                    self.queue_history[junction_id]['east_west_queue'].pop(0)
        
        # simulate dynamic latency based on traffic complexity
        dynamic_latency = self._calculate_dynamic_latency(traffic_complexity)
        
        # simulate the wireless latency and computation time
        time.sleep(dynamic_latency)
        
        # record start time for response time measurement
        response_start = time.time()
        
        # for yellow phases, enforce strict timing
        if current_phase in ["yrGr", "ryrG"]:
            if phase_duration >= self.phase_durations[junction_id][current_phase]:
                current_index = self.phase_sequence.index(current_phase)
                next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
                
                # record response time
                self.response_times.append(time.time() - response_start)
                return next_phase
            else:
                # keep yellow phase until duration is met
                self.response_times.append(time.time() - response_start)
                return current_phase
        
        # if green phase has exceeded maximum time, move to next phase
        if phase_duration > self.max_green_time:
            current_index = self.phase_sequence.index(current_phase)
            next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
            
            # record response time
            self.response_times.append(time.time() - response_start)
            return next_phase
        
        # calculate queue change rates if we have history
        queue_change_ns = 0
        queue_change_ew = 0
        
        if junction_id in self.queue_history and len(self.queue_history[junction_id]['times']) >= 2:
            # calculate rate of change for last two time steps
            ns_queues = self.queue_history[junction_id]['north_south_queue']
            ew_queues = self.queue_history[junction_id]['east_west_queue']
            
            latest_ns = ns_queues[-1]
            prev_ns = ns_queues[-2]
            
            latest_ew = ew_queues[-1]
            prev_ew = ew_queues[-2]
            
            queue_change_ns = latest_ns - prev_ns
            queue_change_ew = latest_ew - prev_ew
        
        # calculate dynamic minimum green time based on current queue
        if current_phase == "GrYr":
            min_green_time = min(5.0 + (north_south_queue * 0.8), 12.0)  # Reduced from 15.0
            adjusted_max_green = max(15.0, self.max_green_time - (east_west_queue * 2.0))
            cross_queue = east_west_queue
        else:  # rGry
            min_green_time = min(5.0 + (east_west_queue * 0.8), 12.0)  # Reduced from 15.0
            adjusted_max_green = max(15.0, self.max_green_time - (north_south_queue * 2.0))
            cross_queue = north_south_queue
        
        # if green phase has exceeded adjusted maximum time, move to next phase
        if phase_duration > adjusted_max_green:
            current_index = self.phase_sequence.index(current_phase)
            next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
            
            # record response time
            self.response_times.append(time.time() - response_start)
            return next_phase
        
        # check if cross-direction queue exceeds threshold and minimum green time is met
        if cross_queue > self.max_queue_threshold and phase_duration >= min_green_time:
            current_index = self.phase_sequence.index(current_phase)
            next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
            
            # record response time
            self.response_times.append(time.time() - response_start)
            return next_phase
        
        # calculate average wait times by direction
        ns_wait = (waiting_times['north'] * queue_lengths['north'] + 
                  waiting_times['south'] * queue_lengths['south']) / max(1, north_south_queue)
        ew_wait = (waiting_times['east'] * queue_lengths['east'] + 
                  waiting_times['west'] * queue_lengths['west']) / max(1, east_west_queue)
        
        # apply waiting time factors for urgency
        ns_wait_factor = 1.0 + (ns_wait / 10.0)  # Higher waiting time increases urgency
        ew_wait_factor = 1.0 + (ew_wait / 10.0)
        
        # calculate weighted queue values using waiting time factors
        weighted_ns_queue = north_south_queue * ns_wait_factor
        weighted_ew_queue = east_west_queue * ew_wait_factor
        
        # check for waiting time imbalance after minimum time
        if current_phase == "GrYr" and phase_duration >= min_green_time:
            if weighted_ew_queue > weighted_ns_queue * 1.5:
                # cross direction has significantly higher weighted queue
                current_index = self.phase_sequence.index(current_phase)
                next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
                
                # record response time
                self.response_times.append(time.time() - response_start)
                return next_phase
        
        elif current_phase == "rGry" and phase_duration >= min_green_time:
            if weighted_ns_queue > weighted_ew_queue * 1.5:
                # cross direction has significantly higher weighted queue
                current_index = self.phase_sequence.index(current_phase)
                next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
                
                # record response time
                self.response_times.append(time.time() - response_start)
                return next_phase
        
        # check for no traffic in current direction but vehicles waiting in cross direction
        if current_phase == "GrYr" and phase_duration >= min_green_time:
            if north_south_queue == 0 and east_west_queue > 0:
                # no vehicles in current direction but waiting in cross direction
                current_index = self.phase_sequence.index(current_phase)
                next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
                
                # record response time
                self.response_times.append(time.time() - response_start)
                return next_phase
        
        elif current_phase == "rGry" and phase_duration >= min_green_time:
            if east_west_queue == 0 and north_south_queue > 0:
                # no vehicles in current direction but waiting in cross direction
                current_index = self.phase_sequence.index(current_phase)
                next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
                
                # record response time
                self.response_times.append(time.time() - response_start)
                return next_phase
        
        # check if current queue is being processed efficiently
        if current_phase == "GrYr" and queue_change_ns < 0 and north_south_queue > 0:
            # queue is decreasing, keep processing if cross queue isn't excessive
            if east_west_queue < self.max_queue_threshold and phase_duration < adjusted_max_green:
                self.response_times.append(time.time() - response_start)
                return current_phase
        
        elif current_phase == "rGry" and queue_change_ew < 0 and east_west_queue > 0:
            # queue is decreasing, keep processing if cross queue isn't excessive
            if north_south_queue < self.max_queue_threshold and phase_duration < adjusted_max_green:
                self.response_times.append(time.time() - response_start)
                return current_phase
        
        # follow standard phase durations if no special conditions
        if phase_duration >= self.phase_durations[junction_id][current_phase]:
            current_index = self.phase_sequence.index(current_phase)
            next_phase = self.phase_sequence[(current_index + 1) % len(self.phase_sequence)]
            
            # record response time
            self.response_times.append(time.time() - response_start)
            
            # store this decision parameters for future reference
            if junction_id in self.traffic_state:
                self.last_decision_params[junction_id] = {
                    'time': current_time,
                    'north_south_queue': north_south_queue,
                    'east_west_queue': east_west_queue,
                    'phase_change': current_phase + " -> " + next_phase
                }
            
            return next_phase
        
        # otherwise maintain the current phase
        self.response_times.append(time.time() - response_start)
        return current_phase