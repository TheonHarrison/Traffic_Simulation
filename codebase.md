# .gitignore

```
venv/
```

# config\maps\grid_network.net.xml

```xml
<?xml version="1.0" encoding="UTF-8"?> <!-- generated on 2025-04-24 13:15:38 by Eclipse SUMO netgenerate Version 1.22.0 <netgenerateConfiguration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/netgenerateConfiguration.xsd"> <grid_network> <grid value="true"/> <grid.x-number value="2"/> <grid.y-number value="2"/> </grid_network> <output> <output-file value="grid_network.net.xml"/> </output> </netgenerateConfiguration> --> <net version="1.20" junctionCornerDetail="5" limitTurnSpeed="5.50" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/net_file.xsd"> <location netOffset="0.00,0.00" convBoundary="0.00,0.00,100.00,100.00" origBoundary="0.00,0.00,100.00,100.00" projParameter="!"/> <edge id=":A0_0" function="internal"> <lane id=":A0_0_0" index="0" speed="6.08" length="7.74" shape="-1.60,3.20 -1.30,1.10 -0.40,-0.40 1.10,-1.30 3.20,-1.60"/> </edge> <edge id=":A0_1" function="internal"> <lane id=":A0_1_0" index="0" speed="3.90" length="2.58" shape="3.20,1.60 2.50,1.70 2.00,2.00 1.70,2.50 1.60,3.20"/> </edge> <edge id=":A1_0" function="internal"> <lane id=":A1_0_0" index="0" speed="6.08" length="7.74" shape="3.20,101.60 1.10,101.30 -0.40,100.40 -1.30,98.90 -1.60,96.80"/> </edge> <edge id=":A1_1" function="internal"> <lane id=":A1_1_0" index="0" speed="3.90" length="2.58" shape="1.60,96.80 1.70,97.50 2.00,98.00 2.50,98.30 3.20,98.40"/> </edge> <edge id=":B0_0" function="internal"> <lane id=":B0_0_0" index="0" speed="3.90" length="2.58" shape="98.40,3.20 98.30,2.50 98.00,2.00 97.50,1.70 96.80,1.60"/> </edge> <edge id=":B0_1" function="internal"> <lane id=":B0_1_0" index="0" speed="6.08" length="7.74" shape="96.80,-1.60 98.90,-1.30 100.40,-0.40 101.30,1.10 101.60,3.20"/> </edge> <edge id=":B1_0" function="internal"> <lane id=":B1_0_0" index="0" speed="6.08" length="7.74" shape="101.60,96.80 101.30,98.90 100.40,100.40 98.90,101.30 96.80,101.60"/> </edge> <edge id=":B1_1" function="internal"> <lane id=":B1_1_0" index="0" speed="3.90" length="2.58" shape="96.80,98.40 97.50,98.30 98.00,98.00 98.30,97.50 98.40,96.80"/> </edge> <edge id="A0A1" from="A0" to="A1" priority="-1"> <lane id="A0A1_0" index="0" speed="13.89" length="93.60" shape="1.60,3.20 1.60,96.80"/> </edge> <edge id="A0B0" from="A0" to="B0" priority="-1"> <lane id="A0B0_0" index="0" speed="13.89" length="93.60" shape="3.20,-1.60 96.80,-1.60"/> </edge> <edge id="A1A0" from="A1" to="A0" priority="-1"> <lane id="A1A0_0" index="0" speed="13.89" length="93.60" shape="-1.60,96.80 -1.60,3.20"/> </edge> <edge id="A1B1" from="A1" to="B1" priority="-1"> <lane id="A1B1_0" index="0" speed="13.89" length="93.60" shape="3.20,98.40 96.80,98.40"/> </edge> <edge id="B0A0" from="B0" to="A0" priority="-1"> <lane id="B0A0_0" index="0" speed="13.89" length="93.60" shape="96.80,1.60 3.20,1.60"/> </edge> <edge id="B0B1" from="B0" to="B1" priority="-1"> <lane id="B0B1_0" index="0" speed="13.89" length="93.60" shape="101.60,3.20 101.60,96.80"/> </edge> <edge id="B1A1" from="B1" to="A1" priority="-1"> <lane id="B1A1_0" index="0" speed="13.89" length="93.60" shape="96.80,101.60 3.20,101.60"/> </edge> <edge id="B1B0" from="B1" to="B0" priority="-1"> <lane id="B1B0_0" index="0" speed="13.89" length="93.60" shape="98.40,96.80 98.40,3.20"/> </edge> <junction id="A0" type="priority" x="0.00" y="0.00" incLanes="A1A0_0 B0A0_0" intLanes=":A0_0_0 :A0_1_0" shape="-3.20,3.20 3.20,3.20 3.20,-3.20 -0.36,-2.49 -1.60,-1.60 -2.49,-0.36 -3.02,1.24"> <request index="0" response="00" foes="00" cont="0"/> <request index="1" response="00" foes="00" cont="0"/> </junction> <junction id="A1" type="priority" x="0.00" y="100.00" incLanes="B1A1_0 A0A1_0" intLanes=":A1_0_0 :A1_1_0" shape="3.20,103.20 3.20,96.80 -3.20,96.80 -2.49,100.36 -1.60,101.60 -0.36,102.49 1.24,103.02"> <request index="0" response="00" foes="00" cont="0"/> <request index="1" response="00" foes="00" cont="0"/> </junction> <junction id="B0" type="priority" x="100.00" y="0.00" incLanes="B1B0_0 A0B0_0" intLanes=":B0_0_0 :B0_1_0" shape="96.80,3.20 103.20,3.20 102.49,-0.36 101.60,-1.60 100.36,-2.49 98.76,-3.02 96.80,-3.20"> <request index="0" response="00" foes="00" cont="0"/> <request index="1" response="00" foes="00" cont="0"/> </junction> <junction id="B1" type="priority" x="100.00" y="100.00" incLanes="B0B1_0 A1B1_0" intLanes=":B1_0_0 :B1_1_0" shape="103.20,96.80 96.80,96.80 96.80,103.20 100.36,102.49 101.60,101.60 102.49,100.36 103.02,98.76"> <request index="0" response="00" foes="00" cont="0"/> <request index="1" response="00" foes="00" cont="0"/> </junction> <connection from="A0A1" to="A1B1" fromLane="0" toLane="0" via=":A1_1_0" dir="r" state="M"/> <connection from="A0B0" to="B0B1" fromLane="0" toLane="0" via=":B0_1_0" dir="l" state="M"/> <connection from="A1A0" to="A0B0" fromLane="0" toLane="0" via=":A0_0_0" dir="l" state="M"/> <connection from="A1B1" to="B1B0" fromLane="0" toLane="0" via=":B1_1_0" dir="r" state="M"/> <connection from="B0A0" to="A0A1" fromLane="0" toLane="0" via=":A0_1_0" dir="r" state="M"/> <connection from="B0B1" to="B1A1" fromLane="0" toLane="0" via=":B1_0_0" dir="l" state="M"/> <connection from="B1A1" to="A1A0" fromLane="0" toLane="0" via=":A1_0_0" dir="l" state="M"/> <connection from="B1B0" to="B0A0" fromLane="0" toLane="0" via=":B0_0_0" dir="r" state="M"/> <connection from=":A0_0" to="A0B0" fromLane="0" toLane="0" dir="l" state="M"/> <connection from=":A0_1" to="A0A1" fromLane="0" toLane="0" dir="r" state="M"/> <connection from=":A1_0" to="A1A0" fromLane="0" toLane="0" dir="l" state="M"/> <connection from=":A1_1" to="A1B1" fromLane="0" toLane="0" dir="r" state="M"/> <connection from=":B0_0" to="B0A0" fromLane="0" toLane="0" dir="r" state="M"/> <connection from=":B0_1" to="B0B1" fromLane="0" toLane="0" dir="l" state="M"/> <connection from=":B1_0" to="B1A1" fromLane="0" toLane="0" dir="l" state="M"/> <connection from=":B1_1" to="B1B0" fromLane="0" toLane="0" dir="r" state="M"/> </net>
```

# config\maps\grid_network.sumocfg

```sumocfg
<configuration> <input> <net-file value="grid_network.net.xml"/> <route-files value="grid_routes.rou.xml"/> </input> <time> <begin value="0"/> <end value="1000"/> </time> </configuration>
```

# config\maps\grid_routes.rou.xml

```xml
<routes> <vType id="car" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/> <!-- Create routes using your actual edge IDs --> <route id="route0" edges="A0B0 B0B1 B1A1"/> <route id="route1" edges="B1A1 A1A0 A0B0"/> <route id="route2" edges="A1B1 B1B0 B0A0"/> <route id="route3" edges="B0A0 A0A1 A1B1"/> <!-- Add flows for continuous vehicle insertion --> <flow id="flow0" type="car" route="route0" begin="0" end="1000" vehsPerHour="300"/> <flow id="flow1" type="car" route="route1" begin="0" end="1000" vehsPerHour="300"/> <flow id="flow2" type="car" route="route2" begin="0" end="1000" vehsPerHour="300"/> <flow id="flow3" type="car" route="route3" begin="0" end="1000" vehsPerHour="300"/> </routes>
```

# README.md

```md

```

# requirements.txt

```txt
pygame>=2.5.0 numpy>=1.24.0 matplotlib>=3.7.0 traci>=1.18.0 # Python interface for SUMO sumolib>=1.18.0 # SUMO library
```

# src\__init__.py

```py

```

# src\ai\__init__.py

```py

```

# src\simulation\__init__.py

```py

```

# src\test_sumo.py

```py
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
```

# src\ui\__init__.py

```py

```

# src\utils\__init__.py

```py

```

# src\utils\sumo_integration.py

```py
import os
import sys
import traci
import traci.constants as tc
from pathlib import Path

class SumoSimulation:
    def __init__(self, config_path, gui=False):
        """
        Initialize the SUMO simulation.
        
        Args:
            config_path (str): Path to the SUMO configuration file
            gui (bool): Whether to use the SUMO GUI
        """
        self.config_path = config_path
        self.gui = gui
        self.sumo_binary = "sumo-gui" if gui else "sumo"
        self.running = False
        
    def start(self):
        """Start the SUMO simulation"""
        # Check if the configuration file exists
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"SUMO configuration file not found: {self.config_path}")
        
        # Start the SUMO simulation
        sumo_cmd = [self.sumo_binary, "-c", self.config_path]
        traci.start(sumo_cmd)
        self.running = True
        print(f"Started SUMO simulation with configuration: {self.config_path}")
        
    def step(self):
        """Execute a single simulation step"""
        if not self.running:
            raise RuntimeError("Simulation not running. Call start() first.")
        
        traci.simulationStep()
        
    def get_vehicle_count(self):
        """Get the current number of vehicles in the simulation"""
        if not self.running:
            raise RuntimeError("Simulation not running. Call start() first.")
        
        return len(traci.vehicle.getIDList())
    
    def get_traffic_light_state(self, tl_id):
        """Get the state of a traffic light"""
        if not self.running:
            raise RuntimeError("Simulation not running. Call start() first.")
        
        return traci.trafficlight.getRedYellowGreenState(tl_id)
    
    def set_traffic_light_state(self, tl_id, state):
        """Set the state of a traffic light"""
        if not self.running:
            raise RuntimeError("Simulation not running. Call start() first.")
        
        traci.trafficlight.setRedYellowGreenState(tl_id, state)
    
    def close(self):
        """Close the SUMO simulation"""
        if self.running:
            traci.close()
            self.running = False
            print("Closed SUMO simulation")

    def get_average_waiting_time(self):
        """Calculate the average waiting time for all vehicles"""
        if not self.running:
            raise RuntimeError("Simulation not running. Call start() first.")
        
        vehicles = traci.vehicle.getIDList()
        if not vehicles:
            return 0
        
        total_waiting_time = sum(traci.vehicle.getWaitingTime(vehicle) for vehicle in vehicles)
        return total_waiting_time / len(vehicles)

    def get_traffic_throughput(self, edge_id):
        """Get the number of vehicles that have passed a specific edge"""
        if not self.running:
            raise RuntimeError("Simulation not running. Call start() first.")
        
        return traci.edge.getLastStepVehicleNumber(edge_id)
```

