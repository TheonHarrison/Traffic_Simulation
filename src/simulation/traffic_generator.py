import os
import math
import random
from pathlib import Path
from lxml import etree

class TrafficGenerator:
    """
    Class for generating SUMO traffic scenarios with different patterns and intensities.
    """
    def __init__(self, template_file=None):
        """
        Initialise the traffic generator.
        """
        self.project_root = Path(__file__).resolve().parent.parent.parent
        
        if template_file is None:
            template_file = os.path.join(self.project_root, "config", "scenarios", "scenario_template.rou.xml")
        
        self.template_file = template_file
        self.output_dir = os.path.join(self.project_root, "config", "scenarios")
        
        # ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # load template if it exists
        self.template_tree = None
        if os.path.exists(template_file):
            self.template_tree = etree.parse(template_file)
        else:
            print(f"Warning: Template file {template_file} not found.")
    
    def generate_constant_traffic(self, output_file, flows, duration=3600):
        """
        Generate a scenario with constant traffic flow.
        
        Args:
            output_file: Name of output file
            flows: Dictionary mapping route IDs to vehicle flow rates (vehicles/hour)
            duration: Duration of the scenario in seconds
        """
        if self.template_tree is None:
            raise ValueError("No template loaded. Cannot generate traffic scenario.")
        
        # create a copy of the template
        tree = etree.ElementTree(self.template_tree.getroot())
        root = tree.getroot()
        
        # add flow definitions
        flow_id = 0
        for route_id, flow_rate in flows.items():
            # basic validation
            if flow_rate < 0:
                print(f"Warning: Negative flow rate for {route_id}. Setting to 0.")
                flow_rate = 0
            
            # add flow element
            flow_element = etree.SubElement(root, "flow")
            flow_element.set("id", f"flow_{flow_id}")
            flow_element.set("type", "car")  # Default to car, can be parameterized
            flow_element.set("route", route_id)
            flow_element.set("begin", "0")
            flow_element.set("end", str(duration))
            flow_element.set("vehsPerHour", str(flow_rate))
            
            flow_id += 1
        
        # add some random individual vehicles of different types
        self._add_random_vehicles(root, ["bus", "truck", "emergency"], 
                                duration, math.ceil(sum(flows.values()) / 100))
        
        # save to file
        output_path = os.path.join(self.output_dir, output_file)
        tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        print(f"Generated constant traffic scenario: {output_path}")
        
        return output_path
    
    def generate_variable_traffic(self, output_file, base_flows, peak_flows, 
                                peak_start, peak_end, duration=3600):
        """
        Generate a scenario with variable traffic flow that peaks at a specific time.
        
        Args:
            output_file: Name of output file
            base_flows: Dictionary mapping route IDs to base flow rates
            peak_flows: Dictionary mapping route IDs to peak flow rates
            peak_start: When the peak period starts (seconds)
            peak_end: When the peak period ends (seconds)
            duration: Total duration of the scenario in seconds
        """
        if self.template_tree is None:
            raise ValueError("No template loaded. Cannot generate traffic scenario.")
        
        # create a copy of the template
        tree = etree.ElementTree(self.template_tree.getroot())
        root = tree.getroot()
        
        # add flow definitions for each time period
        flow_id = 0
        
        # pre-peak period
        if peak_start > 0:
            for route_id, flow_rate in base_flows.items():
                flow_element = etree.SubElement(root, "flow")
                flow_element.set("id", f"flow_pre_peak_{flow_id}")
                flow_element.set("type", "car")
                flow_element.set("route", route_id)
                flow_element.set("begin", "0")
                flow_element.set("end", str(peak_start))
                flow_element.set("vehsPerHour", str(flow_rate))
                flow_id += 1
        
        # peak period
        for route_id, flow_rate in peak_flows.items():
            flow_element = etree.SubElement(root, "flow")
            flow_element.set("id", f"flow_peak_{flow_id}")
            flow_element.set("type", "car")
            flow_element.set("route", route_id)
            flow_element.set("begin", str(peak_start))
            flow_element.set("end", str(peak_end))
            flow_element.set("vehsPerHour", str(flow_rate))
            flow_id += 1
        
        # post-peak period
        if peak_end < duration:
            for route_id, flow_rate in base_flows.items():
                flow_element = etree.SubElement(root, "flow")
                flow_element.set("id", f"flow_post_peak_{flow_id}")
                flow_element.set("type", "car")
                flow_element.set("route", route_id)
                flow_element.set("begin", str(peak_end))
                flow_element.set("end", str(duration))
                flow_element.set("vehsPerHour", str(flow_rate))
                flow_id += 1
        
        # add some random individual vehicles of different types
        max_flow = max(max(base_flows.values()), max(peak_flows.values()))
        self._add_random_vehicles(root, ["bus", "truck", "emergency"], 
                                duration, math.ceil(max_flow / 50))
        
        # Save to file
        output_path = os.path.join(self.output_dir, output_file)
        tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        print(f"Generated variable traffic scenario: {output_path}")
        
        return output_path
    
    def generate_emergency_scenario(self, output_file, base_flows, 
                                    emergency_start, emergency_route, duration=3600):
        """
        Generate a scenario with emergency vehicles that require priority routing.
        
            output_file: Name of output file
            base_flows: Dictionary mapping route IDs to flow rates
            emergency_start: When emergency vehicles start to appear (seconds)
            emergency_route: Route ID for emergency vehicles
            duration: Duration of the scenario in seconds
        """
        if self.template_tree is None:
            raise ValueError("No template loaded. Cannot generate traffic scenario.")
        
        # create a copy of the template
        tree = etree.ElementTree(self.template_tree.getroot())
        root = tree.getroot()
        
        # add base traffic flows
        flow_id = 0
        for route_id, flow_rate in base_flows.items():
            flow_element = etree.SubElement(root, "flow")
            flow_element.set("id", f"flow_{flow_id}")
            flow_element.set("type", "car")
            flow_element.set("route", route_id)
            flow_element.set("begin", "0")
            flow_element.set("end", str(duration))
            flow_element.set("vehsPerHour", str(flow_rate))
            flow_id += 1
        
        # Add emergency vehicles at regular intervals
        emergency_interval = 60  # One emergency vehicle per minute
        for time in range(emergency_start, duration, emergency_interval):
            vehicle_element = etree.SubElement(root, "vehicle")
            vehicle_element.set("id", f"emergency_{time}")
            vehicle_element.set("type", "emergency")
            vehicle_element.set("route", emergency_route)
            vehicle_element.set("depart", str(time))
            vehicle_element.set("departSpeed", "max")
        
        # save to file
        output_path = os.path.join(self.output_dir, output_file)
        tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        print(f"Generated emergency scenario: {output_path}")
        
        return output_path
    
    def generate_congestion_scenario(self, output_file, base_flows, congestion_route, 
                                    congestion_start, congestion_end, congestion_flow, 
                                    duration=3600):
        """
        Generate a scenario with sudden congestion on a specific route.
        """
        if self.template_tree is None:
            raise ValueError("No template loaded. Cannot generate traffic scenario.")
        
        # create a copy of the template
        tree = etree.ElementTree(self.template_tree.getroot())
        root = tree.getroot()
        
        # add base traffic flows for all routes
        flow_id = 0
        for route_id, flow_rate in base_flows.items():
            if route_id != congestion_route:
                # Regular flow for non-congestion routes
                flow_element = etree.SubElement(root, "flow")
                flow_element.set("id", f"flow_regular_{flow_id}")
                flow_element.set("type", "car")
                flow_element.set("route", route_id)
                flow_element.set("begin", "0")
                flow_element.set("end", str(duration))
                flow_element.set("vehsPerHour", str(flow_rate))
                flow_id += 1
        
        # add flows for the congestion route (before, during, after)
        # before congestion
        if congestion_start > 0:
            flow_element = etree.SubElement(root, "flow")
            flow_element.set("id", f"flow_before_congestion")
            flow_element.set("type", "car")
            flow_element.set("route", congestion_route)
            flow_element.set("begin", "0")
            flow_element.set("end", str(congestion_start))
            flow_element.set("vehsPerHour", str(base_flows.get(congestion_route, 300)))
        
        # during congestion
        flow_element = etree.SubElement(root, "flow")
        flow_element.set("id", f"flow_during_congestion")
        flow_element.set("type", "car")
        flow_element.set("route", congestion_route)
        flow_element.set("begin", str(congestion_start))
        flow_element.set("end", str(congestion_end))
        flow_element.set("vehsPerHour", str(congestion_flow))
        
        # after congestion
        if congestion_end < duration:
            flow_element = etree.SubElement(root, "flow")
            flow_element.set("id", f"flow_after_congestion")
            flow_element.set("type", "car")
            flow_element.set("route", congestion_route)
            flow_element.set("begin", str(congestion_end))
            flow_element.set("end", str(duration))
            flow_element.set("vehsPerHour", str(base_flows.get(congestion_route, 300)))
        
        # Save to file
        output_path = os.path.join(self.output_dir, output_file)
        tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        print(f"Generated congestion scenario: {output_path}")
        
        return output_path
    
    def _add_random_vehicles(self, root, vehicle_types, duration, count):
        """
        Add random individual vehicles of specific types.
        """
        # Get all route IDs
        route_ids = []
        for route in root.findall(".//route"):
            route_ids.append(route.get("id"))
        
        if not route_ids:
            return
        
        # add random vehicles
        for i in range(count):
            vehicle_type = random.choice(vehicle_types)
            route_id = random.choice(route_ids)
            depart_time = random.uniform(0, duration)
            
            vehicle_element = etree.SubElement(root, "vehicle")
            vehicle_element.set("id", f"{vehicle_type}_{i}")
            vehicle_element.set("type", vehicle_type)
            vehicle_element.set("route", route_id)
            vehicle_element.set("depart", str(int(depart_time)))