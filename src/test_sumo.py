import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.utils.sumo_integration import SumoSimulation

def main():
    # Path to the SUMO configuration file
    config_path = os.path.join(project_root, "config", "maps", "basic_grid.sumocfg")
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
            
            # If there's a traffic light with ID "5", get its state
            try:
                tl_state = sim.get_traffic_light_state("5")
                print(f"Step {i}: Vehicles: {vehicle_count}, Traffic Light: {tl_state}")
            except:
                print(f"Step {i}: Vehicles: {vehicle_count}")
            
            # Optional: change traffic light state occasionally
            if i % 30 == 0 and i > 0:
                try:
                    # Toggle between N-S and E-W green phases
                    if "G" in sim.get_traffic_light_state("5")[:2]:
                        sim.set_traffic_light_state("5", "rrGG")
                    else:
                        sim.set_traffic_light_state("5", "GGrr")
                    print(f"Changed traffic light state at step {i}")
                except:
                    pass
    
    finally:
        # Ensure the simulation is closed properly
        sim.close()

if __name__ == "__main__":
    main()