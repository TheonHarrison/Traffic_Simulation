import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.utils.sumo_integration import SumoSimulation

def main():
    # Path to the SUMO configuration file
    config_path = os.path.join(project_root, "config", "maps", "traffic_grid.sumocfg")
    print(f"Looking for config file at: {config_path}")
    print(f"File exists: {os.path.exists(config_path)}")
    
    # Create and start the simulation
    sim = SumoSimulation(config_path, gui=True)
    
    try:
        # Start the simulation
        sim.start()
        
        # Run for 100 steps
        for i in range(100):
            # Step the simulation
            sim.step()
            
            # Get and print simulation data
            vehicle_count = sim.get_vehicle_count()
            
            # Get all traffic lights and their states
            tl_ids = traci.trafficlight.getIDList()
            print(f"Traffic lights: {tl_ids}")
            
            for tl_id in tl_ids[:1]:  # Just show the first traffic light
                try:
                    tl_state = sim.get_traffic_light_state(tl_id)
                    print(f"Step {i}: Vehicles: {vehicle_count}, Traffic Light {tl_id}: {tl_state}")
                except Exception as e:
                    print(f"Error getting traffic light state: {e}")
            
            # Optional: change traffic light state occasionally
            if i % 30 == 0 and i > 0 and tl_ids:
                try:
                    # Just flip the first traffic light to all red
                    sim.set_traffic_light_state(tl_ids[0], "rrrr")
                    print(f"Changed traffic light state at step {i}")
                except Exception as e:
                    print(f"Error changing traffic light state: {e}")
    
    finally:
        # Ensure the simulation is closed properly
        sim.close()

if __name__ == "__main__":
    main()