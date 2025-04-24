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

# config\maps\traffic_grid_routes.rou.xml

```xml
<?xml version="1.0" encoding="UTF-8"?> <routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd"> <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/> <!-- Routes --> <route id="route0" edges="A0B0 B0B1 B1A1 A1A0"/> <route id="route1" edges="A1B1 B1B0 B0A0 A0A1"/> <route id="route2" edges="A0A1 A1B1 B1B0 B0A0"/> <route id="route3" edges="B0A0 A0A1 A1B1 B1B0"/> <!-- Traffic flows --> <flow id="flow0" type="car" route="route0" begin="0" end="1000" vehsPerHour="300"/> <flow id="flow1" type="car" route="route1" begin="0" end="1000" vehsPerHour="300"/> <flow id="flow2" type="car" route="route2" begin="0" end="1000" vehsPerHour="300"/> <flow id="flow3" type="car" route="route3" begin="0" end="1000" vehsPerHour="300"/> </routes>
```

# config\maps\traffic_grid.edg.xml

```xml
<?xml version="1.0" encoding="UTF-8"?> <edges xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/edges_file.xsd"> <edge id="A0A1" from="A0" to="A1" priority="1" numLanes="2" speed="13.89"/> <edge id="A1A0" from="A1" to="A0" priority="1" numLanes="2" speed="13.89"/> <edge id="A0B0" from="A0" to="B0" priority="1" numLanes="2" speed="13.89"/> <edge id="B0A0" from="B0" to="A0" priority="1" numLanes="2" speed="13.89"/> <edge id="A1B1" from="A1" to="B1" priority="1" numLanes="2" speed="13.89"/> <edge id="B1A1" from="B1" to="A1" priority="1" numLanes="2" speed="13.89"/> <edge id="B0B1" from="B0" to="B1" priority="1" numLanes="2" speed="13.89"/> <edge id="B1B0" from="B1" to="B0" priority="1" numLanes="2" speed="13.89"/> </edges>
```

# config\maps\traffic_grid.net.xml

```xml
<?xml version="1.0" encoding="UTF-8"?> <!-- generated on 2025-04-24 18:19:10 by Eclipse SUMO netconvert Version 1.22.0 <netconvertConfiguration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/netconvertConfiguration.xsd"> <input> <node-files value="C:\Users\Theon\Downloads\traffic_ai_comparison\config\maps\traffic_grid.nod.xml"/> <edge-files value="C:\Users\Theon\Downloads\traffic_ai_comparison\config\maps\traffic_grid.edg.xml"/> </input> <output> <output-file value="C:\Users\Theon\Downloads\traffic_ai_comparison\config\maps\traffic_grid.net.xml"/> </output> <junctions> <no-turnarounds value="true"/> <junctions.corner-detail value="5"/> <junctions.limit-turn-speed value="5.5"/> </junctions> </netconvertConfiguration> --> <net version="1.20" junctionCornerDetail="5" limitTurnSpeed="5.50" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/net_file.xsd"> <location netOffset="0.00,0.00" convBoundary="0.00,0.00,100.00,100.00" origBoundary="0.00,0.00,100.00,100.00" projParameter="!"/> <edge id=":A0_0" function="internal"> <lane id=":A0_0_0" index="0" speed="8.96" length="18.06" shape="-4.80,6.40 -4.10,1.50 -2.00,-2.00 1.50,-4.10 6.40,-4.80"/> <lane id=":A0_0_1" index="1" speed="7.66" length="12.90" shape="-1.60,6.40 -1.10,2.90 0.40,0.40 2.90,-1.10 6.40,-1.60"/> </edge> <edge id=":A0_2" function="internal"> <lane id=":A0_2_0" index="0" speed="3.90" length="2.58" shape="6.40,4.80 5.70,4.90 5.20,5.20 4.90,5.70 4.80,6.40"/> <lane id=":A0_2_1" index="1" speed="6.08" length="7.74" shape="6.40,1.60 4.30,1.90 2.80,2.80 1.90,4.30 1.60,6.40"/> </edge> <edge id=":A1_0" function="internal"> <lane id=":A1_0_0" index="0" speed="8.96" length="18.06" shape="6.40,104.80 1.50,104.10 -2.00,102.00 -4.10,98.50 -4.80,93.60"/> <lane id=":A1_0_1" index="1" speed="7.66" length="12.90" shape="6.40,101.60 2.90,101.10 0.40,99.60 -1.10,97.10 -1.60,93.60"/> </edge> <edge id=":A1_2" function="internal"> <lane id=":A1_2_0" index="0" speed="3.90" length="2.58" shape="4.80,93.60 4.90,94.30 5.20,94.80 5.70,95.10 6.40,95.20"/> <lane id=":A1_2_1" index="1" speed="6.08" length="7.74" shape="1.60,93.60 1.90,95.70 2.80,97.20 4.30,98.10 6.40,98.40"/> </edge> <edge id=":B0_0" function="internal"> <lane id=":B0_0_0" index="0" speed="3.90" length="2.58" shape="95.20,6.40 95.10,5.70 94.80,5.20 94.30,4.90 93.60,4.80"/> <lane id=":B0_0_1" index="1" speed="6.08" length="7.74" shape="98.40,6.40 98.10,4.30 97.20,2.80 95.70,1.90 93.60,1.60"/> </edge> <edge id=":B0_2" function="internal"> <lane id=":B0_2_0" index="0" speed="8.96" length="18.06" shape="93.60,-4.80 98.50,-4.10 102.00,-2.00 104.10,1.50 104.80,6.40"/> <lane id=":B0_2_1" index="1" speed="7.66" length="12.90" shape="93.60,-1.60 97.10,-1.10 99.60,0.40 101.10,2.90 101.60,6.40"/> </edge> <edge id=":B1_0" function="internal"> <lane id=":B1_0_0" index="0" speed="8.96" length="18.06" shape="104.80,93.60 104.10,98.50 102.00,102.00 98.50,104.10 93.60,104.80"/> <lane id=":B1_0_1" index="1" speed="7.66" length="12.90" shape="101.60,93.60 101.10,97.10 99.60,99.60 97.10,101.10 93.60,101.60"/> </edge> <edge id=":B1_2" function="internal"> <lane id=":B1_2_0" index="0" speed="3.90" length="2.58" shape="93.60,95.20 94.30,95.10 94.80,94.80 95.10,94.30 95.20,93.60"/> <lane id=":B1_2_1" index="1" speed="6.08" length="7.74" shape="93.60,98.40 95.70,98.10 97.20,97.20 98.10,95.70 98.40,93.60"/> </edge> <edge id="A0A1" from="A0" to="A1" priority="1"> <lane id="A0A1_0" index="0" speed="13.89" length="87.20" shape="4.80,6.40 4.80,93.60"/> <lane id="A0A1_1" index="1" speed="13.89" length="87.20" shape="1.60,6.40 1.60,93.60"/> </edge> <edge id="A0B0" from="A0" to="B0" priority="1"> <lane id="A0B0_0" index="0" speed="13.89" length="87.20" shape="6.40,-4.80 93.60,-4.80"/> <lane id="A0B0_1" index="1" speed="13.89" length="87.20" shape="6.40,-1.60 93.60,-1.60"/> </edge> <edge id="A1A0" from="A1" to="A0" priority="1"> <lane id="A1A0_0" index="0" speed="13.89" length="87.20" shape="-4.80,93.60 -4.80,6.40"/> <lane id="A1A0_1" index="1" speed="13.89" length="87.20" shape="-1.60,93.60 -1.60,6.40"/> </edge> <edge id="A1B1" from="A1" to="B1" priority="1"> <lane id="A1B1_0" index="0" speed="13.89" length="87.20" shape="6.40,95.20 93.60,95.20"/> <lane id="A1B1_1" index="1" speed="13.89" length="87.20" shape="6.40,98.40 93.60,98.40"/> </edge> <edge id="B0A0" from="B0" to="A0" priority="1"> <lane id="B0A0_0" index="0" speed="13.89" length="87.20" shape="93.60,4.80 6.40,4.80"/> <lane id="B0A0_1" index="1" speed="13.89" length="87.20" shape="93.60,1.60 6.40,1.60"/> </edge> <edge id="B0B1" from="B0" to="B1" priority="1"> <lane id="B0B1_0" index="0" speed="13.89" length="87.20" shape="104.80,6.40 104.80,93.60"/> <lane id="B0B1_1" index="1" speed="13.89" length="87.20" shape="101.60,6.40 101.60,93.60"/> </edge> <edge id="B1A1" from="B1" to="A1" priority="1"> <lane id="B1A1_0" index="0" speed="13.89" length="87.20" shape="93.60,104.80 6.40,104.80"/> <lane id="B1A1_1" index="1" speed="13.89" length="87.20" shape="93.60,101.60 6.40,101.60"/> </edge> <edge id="B1B0" from="B1" to="B0" priority="1"> <lane id="B1B0_0" index="0" speed="13.89" length="87.20" shape="95.20,93.60 95.20,6.40"/> <lane id="B1B0_1" index="1" speed="13.89" length="87.20" shape="98.40,93.60 98.40,6.40"/> </edge> <tlLogic id="A0" type="static" programID="0" offset="0"> <phase duration="90" state="GGGG"/> </tlLogic> <tlLogic id="A1" type="static" programID="0" offset="0"> <phase duration="90" state="GGGG"/> </tlLogic> <tlLogic id="B0" type="static" programID="0" offset="0"> <phase duration="90" state="GGGG"/> </tlLogic> <tlLogic id="B1" type="static" programID="0" offset="0"> <phase duration="90" state="GGGG"/> </tlLogic> <junction id="A0" type="traffic_light" x="0.00" y="0.00" incLanes="A1A0_0 A1A0_1 B0A0_0 B0A0_1" intLanes=":A0_0_0 :A0_0_1 :A0_2_0 :A0_2_1" shape="-6.40,6.40 6.40,6.40 6.40,-6.40 2.49,-6.04 -0.71,-4.98 -3.20,-3.20 -4.98,-0.71 -6.04,2.49"> <request index="0" response="0000" foes="0000" cont="0"/> <request index="1" response="0000" foes="0000" cont="0"/> <request index="2" response="0000" foes="0000" cont="0"/> <request index="3" response="0000" foes="0000" cont="0"/> </junction> <junction id="A1" type="traffic_light" x="0.00" y="100.00" incLanes="B1A1_0 B1A1_1 A0A1_0 A0A1_1" intLanes=":A1_0_0 :A1_0_1 :A1_2_0 :A1_2_1" shape="6.40,106.40 6.40,93.60 -6.40,93.60 -6.04,97.51 -4.98,100.71 -3.20,103.20 -0.71,104.98 2.49,106.04"> <request index="0" response="0000" foes="0000" cont="0"/> <request index="1" response="0000" foes="0000" cont="0"/> <request index="2" response="0000" foes="0000" cont="0"/> <request index="3" response="0000" foes="0000" cont="0"/> </junction> <junction id="B0" type="traffic_light" x="100.00" y="0.00" incLanes="B1B0_0 B1B0_1 A0B0_0 A0B0_1" intLanes=":B0_0_0 :B0_0_1 :B0_2_0 :B0_2_1" shape="93.60,6.40 106.40,6.40 106.04,2.49 104.98,-0.71 103.20,-3.20 100.71,-4.98 97.51,-6.04 93.60,-6.40"> <request index="0" response="0000" foes="0000" cont="0"/> <request index="1" response="0000" foes="0000" cont="0"/> <request index="2" response="0000" foes="0000" cont="0"/> <request index="3" response="0000" foes="0000" cont="0"/> </junction> <junction id="B1" type="traffic_light" x="100.00" y="100.00" incLanes="B0B1_0 B0B1_1 A1B1_0 A1B1_1" intLanes=":B1_0_0 :B1_0_1 :B1_2_0 :B1_2_1" shape="106.40,93.60 93.60,93.60 93.60,106.40 97.51,106.04 100.71,104.98 103.20,103.20 104.98,100.71 106.04,97.51"> <request index="0" response="0000" foes="0000" cont="0"/> <request index="1" response="0000" foes="0000" cont="0"/> <request index="2" response="0000" foes="0000" cont="0"/> <request index="3" response="0000" foes="0000" cont="0"/> </junction> <connection from="A0A1" to="A1B1" fromLane="0" toLane="0" via=":A1_2_0" tl="A1" linkIndex="2" dir="r" state="O"/> <connection from="A0A1" to="A1B1" fromLane="1" toLane="1" via=":A1_2_1" tl="A1" linkIndex="3" dir="r" state="O"/> <connection from="A0B0" to="B0B1" fromLane="0" toLane="0" via=":B0_2_0" tl="B0" linkIndex="2" dir="l" state="O"/> <connection from="A0B0" to="B0B1" fromLane="1" toLane="1" via=":B0_2_1" tl="B0" linkIndex="3" dir="l" state="O"/> <connection from="A1A0" to="A0B0" fromLane="0" toLane="0" via=":A0_0_0" tl="A0" linkIndex="0" dir="l" state="O"/> <connection from="A1A0" to="A0B0" fromLane="1" toLane="1" via=":A0_0_1" tl="A0" linkIndex="1" dir="l" state="O"/> <connection from="A1B1" to="B1B0" fromLane="0" toLane="0" via=":B1_2_0" tl="B1" linkIndex="2" dir="r" state="O"/> <connection from="A1B1" to="B1B0" fromLane="1" toLane="1" via=":B1_2_1" tl="B1" linkIndex="3" dir="r" state="O"/> <connection from="B0A0" to="A0A1" fromLane="0" toLane="0" via=":A0_2_0" tl="A0" linkIndex="2" dir="r" state="O"/> <connection from="B0A0" to="A0A1" fromLane="1" toLane="1" via=":A0_2_1" tl="A0" linkIndex="3" dir="r" state="O"/> <connection from="B0B1" to="B1A1" fromLane="0" toLane="0" via=":B1_0_0" tl="B1" linkIndex="0" dir="l" state="O"/> <connection from="B0B1" to="B1A1" fromLane="1" toLane="1" via=":B1_0_1" tl="B1" linkIndex="1" dir="l" state="O"/> <connection from="B1A1" to="A1A0" fromLane="0" toLane="0" via=":A1_0_0" tl="A1" linkIndex="0" dir="l" state="O"/> <connection from="B1A1" to="A1A0" fromLane="1" toLane="1" via=":A1_0_1" tl="A1" linkIndex="1" dir="l" state="O"/> <connection from="B1B0" to="B0A0" fromLane="0" toLane="0" via=":B0_0_0" tl="B0" linkIndex="0" dir="r" state="O"/> <connection from="B1B0" to="B0A0" fromLane="1" toLane="1" via=":B0_0_1" tl="B0" linkIndex="1" dir="r" state="O"/> <connection from=":A0_0" to="A0B0" fromLane="0" toLane="0" dir="l" state="M"/> <connection from=":A0_0" to="A0B0" fromLane="1" toLane="1" dir="l" state="M"/> <connection from=":A0_2" to="A0A1" fromLane="0" toLane="0" dir="r" state="M"/> <connection from=":A0_2" to="A0A1" fromLane="1" toLane="1" dir="r" state="M"/> <connection from=":A1_0" to="A1A0" fromLane="0" toLane="0" dir="l" state="M"/> <connection from=":A1_0" to="A1A0" fromLane="1" toLane="1" dir="l" state="M"/> <connection from=":A1_2" to="A1B1" fromLane="0" toLane="0" dir="r" state="M"/> <connection from=":A1_2" to="A1B1" fromLane="1" toLane="1" dir="r" state="M"/> <connection from=":B0_0" to="B0A0" fromLane="0" toLane="0" dir="r" state="M"/> <connection from=":B0_0" to="B0A0" fromLane="1" toLane="1" dir="r" state="M"/> <connection from=":B0_2" to="B0B1" fromLane="0" toLane="0" dir="l" state="M"/> <connection from=":B0_2" to="B0B1" fromLane="1" toLane="1" dir="l" state="M"/> <connection from=":B1_0" to="B1A1" fromLane="0" toLane="0" dir="l" state="M"/> <connection from=":B1_0" to="B1A1" fromLane="1" toLane="1" dir="l" state="M"/> <connection from=":B1_2" to="B1B0" fromLane="0" toLane="0" dir="r" state="M"/> <connection from=":B1_2" to="B1B0" fromLane="1" toLane="1" dir="r" state="M"/> </net>
```

# config\maps\traffic_grid.netccfg

```netccfg
<?xml version="1.0" encoding="UTF-8"?> <configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/netconvertConfiguration.xsd"> <input> <node-files value="traffic_grid.nod.xml"/> <edge-files value="traffic_grid.edg.xml"/> </input> <output> <output-file value="traffic_grid.net.xml"/> </output> <processing> <no-turnarounds value="true"/> <junctions.corner-detail value="5"/> <junctions.limit-turn-speed value="5.5"/> </processing> </configuration>
```

# config\maps\traffic_grid.nod.xml

```xml
<?xml version="1.0" encoding="UTF-8"?> <nodes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/nodes_file.xsd"> <node id="A0" x="0.0" y="0.0" type="traffic_light"/> <node id="A1" x="0.0" y="100.0" type="traffic_light"/> <node id="B0" x="100.0" y="0.0" type="traffic_light"/> <node id="B1" x="100.0" y="100.0" type="traffic_light"/> </nodes>
```

# config\maps\traffic_grid.sumocfg

```sumocfg
<?xml version="1.0" encoding="UTF-8"?> <configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd"> <input> <net-file value="traffic_grid.net.xml"/> <route-files value="traffic_grid_routes.rou.xml"/> </input> <time> <begin value="0"/> <end value="1000"/> </time> <processing> <time-to-teleport value="-1"/> </processing> <report> <verbose value="true"/> <no-step-log value="false"/> </report> </configuration>
```

# data\outputs\comparison_results.png

This is a binary file of the type: Image

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

# src\check_network.py

```py
import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

def check_traffic_lights():
    """Check if the network has traffic lights defined"""
    # Path to the SUMO network file
    net_file_path = os.path.join(project_root, "config", "maps", "grid_network.net.xml")
    
    print(f"Checking network file: {net_file_path}")
    print(f"File exists: {os.path.exists(net_file_path)}")
    
    if not os.path.exists(net_file_path):
        return
    
    # Parse the XML
    tree = ET.parse(net_file_path)
    root = tree.getroot()
    
    # Find traffic light junctions
    tl_junctions = root.findall(".//junction[@type='traffic_light']")
    print(f"Found {len(tl_junctions)} traffic light junctions:")
    
    for junction in tl_junctions:
        print(f"  Junction ID: {junction.get('id')}, Type: {junction.get('type')}")
    
    # Find traffic light elements
    traffic_lights = root.findall(".//tlLogic")
    print(f"Found {len(traffic_lights)} traffic light logic definitions:")
    
    for tl in traffic_lights:
        tl_id = tl.get('id')
        tl_type = tl.get('type')
        tl_program = tl.get('programID')
        phases = tl.findall(".//phase")
        
        print(f"  Traffic Light ID: {tl_id}, Type: {tl_type}, Program: {tl_program}")
        print(f"    Number of phases: {len(phases)}")
        
        for i, phase in enumerate(phases):
            duration = phase.get('duration')
            state = phase.get('state')
            print(f"    Phase {i}: Duration={duration}s, State={state}")

def main():
    check_traffic_lights()

if __name__ == "__main__":
    main()
```

# src\generate_network.py

```py
import os
import sys
import subprocess
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

def generate_network():
    """Generate the SUMO network from the configuration files"""
    # Path to the SUMO configuration file
    netccfg_path = os.path.join(project_root, "config", "maps", "traffic_grid.netccfg")
    
    print(f"Generating network from: {netccfg_path}")
    print(f"File exists: {os.path.exists(netccfg_path)}")
    
    if not os.path.exists(netccfg_path):
        print("Network configuration file not found!")
        return False
    
    # Run NETCONVERT to generate the network
    try:
        cmd = ["netconvert", "-c", netccfg_path]
        print(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Network generation successful!")
            print(result.stdout)
            return True
        else:
            print("Network generation failed!")
            print("Error output:")
            print(result.stderr)
            return False
    
    except Exception as e:
        print(f"Error running NETCONVERT: {e}")
        return False

def main():
    if generate_network():
        print("Network generated successfully. You can now run the simulation with traffic lights.")
    else:
        print("Failed to generate the network. Please check the error messages above.")

if __name__ == "__main__":
    main()
```

# src\run_comparison.py

```py
import os
import sys
from pathlib import Path
import time
import subprocess
import matplotlib.pyplot as plt
import numpy as np

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

def run_simulation(mode, steps=500, delay=50, gui=False):
    """Run a simulation with the specified mode and parameters"""
    cmd = [
        sys.executable,
        os.path.join(project_root, "src", "test_visualization.py"),
        "--mode", mode,
        "--steps", str(steps),
        "--delay", str(delay)
    ]
    
    if gui:
        cmd.append("--gui")
    
    print(f"Running {mode} simulation...")
    start_time = time.time()
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    
    elapsed_time = time.time() - start_time
    print(f"{mode} simulation completed in {elapsed_time:.2f} seconds")
    
    # Extract performance metrics from output
    metrics = {
        "avg_wait_time": 0,
        "avg_speed": 0,
        "throughput": 0
    }
    
    for line in stdout.split('\n'):
        if "Average wait time:" in line:
            metrics["avg_wait_time"] = float(line.split(':')[1].strip().split()[0])
        elif "Average speed:" in line:
            metrics["avg_speed"] = float(line.split(':')[1].strip().split()[0])
        elif "Total throughput:" in line:
            metrics["throughput"] = int(line.split(':')[1].strip().split()[0])
    
    return metrics

def plot_comparison(wired_metrics, wireless_metrics):
    """Plot a comparison of the wired and wireless simulation results"""
    # Create the data directory if it doesn't exist
    data_dir = os.path.join(project_root, "data", "outputs")
    os.makedirs(data_dir, exist_ok=True)
    
    # Set up the metrics for comparison
    metrics = ["avg_wait_time", "avg_speed", "throughput"]
    labels = ["Average Wait Time (s)", "Average Speed (m/s)", "Throughput (vehicles)"]
    
    # Create the figure
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    
    for i, (metric, label) in enumerate(zip(metrics, labels)):
        wired_value = wired_metrics[metric]
        wireless_value = wireless_metrics[metric]
        
        # Plot the bars
        bars = axs[i].bar(["Wired AI", "Wireless AI"], [wired_value, wireless_value])
        bars[0].set_color('blue')
        bars[1].set_color('green')
        
        # Add labels and title
        axs[i].set_ylabel(label)
        axs[i].set_title(f"Comparison of {label}")
        
        # Add the values on top of the bars
        for j, v in enumerate([wired_value, wireless_value]):
            axs[i].text(j, v, f"{v:.2f}", ha='center', va='bottom')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(os.path.join(data_dir, "comparison_results.png"))
    plt.close()
    
    print(f"Comparison plot saved to {os.path.join(data_dir, 'comparison_results.png')}")

def main():
    # Run the simulations
    wired_metrics = run_simulation("Wired AI", steps=300, delay=20)
    wireless_metrics = run_simulation("Wireless AI", steps=300, delay=20)
    
    # Print the results
    print("\nResults Summary:")
    print("==================")
    print(f"Wired AI - Wait Time: {wired_metrics['avg_wait_time']:.2f}s, "
          f"Speed: {wired_metrics['avg_speed']:.2f}m/s, "
          f"Throughput: {wired_metrics['throughput']}")
    print(f"Wireless AI - Wait Time: {wireless_metrics['avg_wait_time']:.2f}s, "
          f"Speed: {wireless_metrics['avg_speed']:.2f}m/s, "
          f"Throughput: {wireless_metrics['throughput']}")
    
    # Plot the comparison
    plot_comparison(wired_metrics, wireless_metrics)

if __name__ == "__main__":
    main()
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

# src\test_visualization.py

```py
import os
import sys
from pathlib import Path
import time
import argparse

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.ui.sumo_visualization import SumoVisualization

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run SUMO traffic visualization')
    parser.add_argument('--steps', type=int, default=1000, 
                        help='Number of simulation steps to run')
    parser.add_argument('--delay', type=int, default=50, 
                        help='Delay in milliseconds between steps')
    parser.add_argument('--gui', action='store_true', 
                        help='Use SUMO GUI alongside visualization')
    parser.add_argument('--mode', type=str, default='Wired AI', 
                        choices=['Wired AI', 'Wireless AI', 'Traditional'], 
                        help='Traffic control mode to simulate')
    args = parser.parse_args()
    
    # Path to the SUMO configuration file
    config_path = os.path.join(project_root, "config", "maps", "traffic_grid.sumocfg")  
    
    print(f"Starting visualization with config: {config_path}")
    print(f"Config file exists: {os.path.exists(config_path)}")
    print(f"Mode: {args.mode}, Steps: {args.steps}, Delay: {args.delay}ms")
    
    # Record start time
    start_time = time.time()
    
    # Create the visualization
    visualization = SumoVisualization(config_path, width=1024, height=768, use_gui=args.gui)
    
    # Set the mode
    visualization.set_mode(args.mode)
    
    # Run the visualization
    visualization.run(steps=args.steps, delay_ms=args.delay)
    
    # Calculate and print elapsed time
    elapsed_time = time.time() - start_time
    print(f"Simulation completed in {elapsed_time:.2f} seconds")
    
    # Report performance metrics if the simulation ran long enough
    if args.steps > 100:
        wait_times = visualization.performance_metrics["wait_times"]
        speeds = visualization.performance_metrics["speeds"]
        throughput = visualization.performance_metrics["throughput"]
        
        if wait_times:
            avg_wait = sum(wait_times) / len(wait_times)
            print(f"Average wait time: {avg_wait:.2f} seconds")
        
        if speeds:
            avg_speed = sum(speeds) / len(speeds)
            print(f"Average speed: {avg_speed:.2f} m/s")
        
        if throughput:
            total_throughput = sum(throughput)
            print(f"Total throughput: {total_throughput} vehicles")

if __name__ == "__main__":
    main()
```

# src\ui\__init__.py

```py

```

# src\ui\sumo_pygame_mapper.py

```py
import numpy as np
from pathlib import Path
import xml.etree.ElementTree as ET

class SumoNetworkParser:
    """
    Parse SUMO network XML to extract nodes (junctions) and edges (roads).
    """
    def __init__(self, net_file_path):
        """
        Initialize the parser with a SUMO .net.xml file path.
        
        Args:
            net_file_path (str): Path to the SUMO network XML file
        """
        self.net_file_path = Path(net_file_path)
        self.nodes = {}  # id -> (x, y)
        self.edges = {}  # id -> {"from": node_id, "to": node_id, "shape": [(x1, y1), (x2, y2), ...]}
        self.connections = []  # list of (from_edge, to_edge, from_lane, to_lane)
        
        # Parse the network file
        self._parse_network()
        
    def _parse_network(self):
        """Parse the SUMO network XML file."""
        if not self.net_file_path.exists():
            raise FileNotFoundError(f"Network file not found: {self.net_file_path}")

        # Parse the XML
        tree = ET.parse(self.net_file_path)
        root = tree.getroot()
        
        # Parse junctions (nodes)
        for junction in root.findall('.//junction'):
            junction_id = junction.get('id')
            # Skip internal junctions
            if junction.get('type') == 'internal':
                continue
                
            x = float(junction.get('x'))
            y = float(junction.get('y'))
            self.nodes[junction_id] = (x, y)
        
        # Parse edges
        for edge in root.findall('.//edge'):
            edge_id = edge.get('id')
            # Skip internal edges
            if edge.get('function') == 'internal':
                continue
                
            from_node = edge.get('from')
            to_node = edge.get('to')
            
            # Get shape points if available
            shape_points = []
            lanes = edge.findall('.//lane')
            if lanes:
                # Use the first lane's shape
                lane_shape = lanes[0].get('shape')
                if lane_shape:
                    # Shape format: "x1,y1 x2,y2 x3,y3 ..."
                    points = lane_shape.split()
                    for point in points:
                        x, y = map(float, point.split(','))
                        shape_points.append((x, y))
            
            # If no shape points, use from and to node coordinates
            if not shape_points and from_node in self.nodes and to_node in self.nodes:
                shape_points = [self.nodes[from_node], self.nodes[to_node]]
            
            self.edges[edge_id] = {
                "from": from_node,
                "to": to_node,
                "shape": shape_points
            }
        
        # Parse connections
        for connection in root.findall('.//connection'):
            from_edge = connection.get('from')
            to_edge = connection.get('to')
            from_lane = int(connection.get('fromLane'))
            to_lane = int(connection.get('toLane'))
            
            # Skip connections involving internal edges
            if from_edge.startswith(':') or to_edge.startswith(':'):
                continue
                
            self.connections.append((from_edge, to_edge, from_lane, to_lane))
        
        print(f"Parsed SUMO network with {len(self.nodes)} nodes and {len(self.edges)} edges")

class SumoPygameMapper:
    """
    Maps SUMO coordinates to Pygame screen coordinates.
    """
    def __init__(self, net_parser, screen_width, screen_height, margin=50):
        """
        Initialize the coordinate mapper.
        
        Args:
            net_parser (SumoNetworkParser): Parsed SUMO network
            screen_width (int): Width of the Pygame screen
            screen_height (int): Height of the Pygame screen
            margin (int): Margin around the network in pixels
        """
        self.net_parser = net_parser
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.margin = margin
        
        # Calculate network bounds
        self._calculate_bounds()
        
        # Calculate scaling factors
        self._calculate_scaling()
        
    def _calculate_bounds(self):
        """Calculate the bounding box of the SUMO network."""
        # Initialize with extreme values
        self.min_x = float('inf')
        self.max_x = float('-inf')
        self.min_y = float('inf')
        self.max_y = float('-inf')
        
        # Check node coordinates
        for _, (x, y) in self.net_parser.nodes.items():
            self.min_x = min(self.min_x, x)
            self.max_x = max(self.max_x, x)
            self.min_y = min(self.min_y, y)
            self.max_y = max(self.max_y, y)
        
        # Check edge shape points
        for _, edge_data in self.net_parser.edges.items():
            for x, y in edge_data["shape"]:
                self.min_x = min(self.min_x, x)
                self.max_x = max(self.max_x, x)
                self.min_y = min(self.min_y, y)
                self.max_y = max(self.max_y, y)
        
        # If no valid coordinates found, use defaults
        if self.min_x == float('inf'):
            self.min_x, self.max_x = 0, 100
            self.min_y, self.max_y = 0, 100
        
        # Network dimensions
        self.net_width = self.max_x - self.min_x
        self.net_height = self.max_y - self.min_y
        
        print(f"Network bounds: ({self.min_x}, {self.min_y}) to ({self.max_x}, {self.max_y})")
    
    def _calculate_scaling(self):
        """Calculate scaling factors to fit the network in the screen."""
        # Available screen dimensions (accounting for margin)
        available_width = self.screen_width - 2 * self.margin
        available_height = self.screen_height - 2 * self.margin
        
        # Calculate scaling factors
        self.scale_x = available_width / self.net_width if self.net_width > 0 else 1
        self.scale_y = available_height / self.net_height if self.net_height > 0 else 1
        
        # Use the smaller scaling factor to maintain aspect ratio
        self.scale = min(self.scale_x, self.scale_y)
        
        # Recalculate to center the network
        self.offset_x = self.margin + (available_width - self.net_width * self.scale) / 2
        self.offset_y = self.margin + (available_height - self.net_height * self.scale) / 2
        
        print(f"Scaling factor: {self.scale}, Offsets: ({self.offset_x}, {self.offset_y})")
    
    def sumo_to_pygame(self, sumo_x, sumo_y):
        """
        Convert SUMO coordinates to Pygame screen coordinates.
        
        Args:
            sumo_x (float): X coordinate in SUMO
            sumo_y (float): Y coordinate in SUMO
            
        Returns:
            tuple: (pygame_x, pygame_y) coordinates
        """
        # Scale and translate
        pygame_x = self.offset_x + (sumo_x - self.min_x) * self.scale
        # Flip Y-axis (SUMO's Y increases upward, Pygame's Y increases downward)
        pygame_y = self.screen_height - (self.offset_y + (sumo_y - self.min_y) * self.scale)
        
        return int(pygame_x), int(pygame_y)
    
    def get_node_position(self, node_id):
        """
        Get the Pygame screen position of a SUMO node.
        
        Args:
            node_id (str): ID of the SUMO node
            
        Returns:
            tuple or None: (pygame_x, pygame_y) if node exists, None otherwise
        """
        if node_id in self.net_parser.nodes:
            sumo_x, sumo_y = self.net_parser.nodes[node_id]
            return self.sumo_to_pygame(sumo_x, sumo_y)
        return None
    
    def get_edge_shape(self, edge_id):
        """
        Get the Pygame screen coordinates for an edge's shape.
        
        Args:
            edge_id (str): ID of the SUMO edge
            
        Returns:
            list or None: List of (pygame_x, pygame_y) points if edge exists, None otherwise
        """
        if edge_id in self.net_parser.edges:
            shape = self.net_parser.edges[edge_id]["shape"]
            return [self.sumo_to_pygame(x, y) for x, y in shape]
        return None

# Test the mapper
if __name__ == "__main__":
    import os
    import sys
    from pathlib import Path
    
    # Add project root to Python path
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.append(str(project_root))
    
    # Path to the SUMO network file
    net_file_path = os.path.join(project_root, "config", "maps", "grid_network.net.xml")
    
    # Parse the network
    parser = SumoNetworkParser(net_file_path)
    
    # Create a mapper
    mapper = SumoPygameMapper(parser, 800, 600)
    
    # Print some mapped coordinates
    for node_id, (x, y) in list(parser.nodes.items())[:5]:
        pygame_x, pygame_y = mapper.sumo_to_pygame(x, y)
        print(f"Node {node_id}: SUMO ({x}, {y}) -> Pygame ({pygame_x}, {pygame_y})")
    
    # Print some edge shapes
    for edge_id, edge_data in list(parser.edges.items())[:2]:
        print(f"Edge {edge_id} shape:")
        for i, (x, y) in enumerate(edge_data["shape"]):
            pygame_x, pygame_y = mapper.sumo_to_pygame(x, y)
            print(f"  Point {i}: SUMO ({x}, {y}) -> Pygame ({pygame_x}, {pygame_y})")
```

# src\ui\sumo_visualization.py

```py
import pygame
import os
import sys
import traci
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.ui.visualization import Visualization
from src.ui.traffic_renderer import TrafficRenderer, VehicleType
from src.ui.sumo_pygame_mapper import SumoNetworkParser, SumoPygameMapper
from src.utils.sumo_integration import SumoSimulation

class SumoVisualization:
    """
    Integrates SUMO simulation with Pygame visualization.
    """
    def __init__(self, sumo_config_path, width=1024, height=768, use_gui=False):
        """
        Initialize the SUMO visualization.
        
        Args:
            sumo_config_path (str): Path to the SUMO configuration file
            width (int): Width of the visualization window
            height (int): Height of the visualization window
            use_gui (bool): Whether to use SUMO GUI alongside the visualization
        """
        self.sumo_config_path = sumo_config_path
        self.width = width
        self.height = height
        self.use_gui = use_gui
        
        # Get the SUMO network file path from the config directory
        self.net_file_path = self._get_net_file_path()
        
        # Initialize the SUMO simulation
        self.simulation = SumoSimulation(sumo_config_path, gui=use_gui)
        
        # Initialize the visualization
        self.visualization = Visualization(width, height, "SUMO Traffic Visualization", self.net_file_path)
        
        # Create network parser and mapper
        self.network_parser = SumoNetworkParser(self.net_file_path)
        self.mapper = SumoPygameMapper(self.network_parser, width, height)
        
        # Create traffic renderer
        self.traffic_renderer = TrafficRenderer(self.visualization.screen, self.mapper)
        
        # Traffic light positions (will be filled during simulation)
        self.traffic_light_positions = {}
        
        # Simulation running flag
        self.running = False
        
        # Statistics
        self.stats = {
            "vehicles": 0,
            "avg_speed": 0.0,
            "avg_wait_time": 0.0,
            "throughput": 0,
            "step": 0,
            "mode": "Wired AI"  # Default mode, can be changed
        }
        
        # Performance metrics (to be collected during simulation)
        self.performance_metrics = {
            "wait_times": [],
            "speeds": [],
            "throughput": []
        }
        
        print(f"SUMO Visualization initialized with {width}x{height} window")
    
    def _get_net_file_path(self):
        """Extract the network file path from the SUMO configuration file."""
        import xml.etree.ElementTree as ET
        
        try:
            # Parse the SUMO config file
            tree = ET.parse(self.sumo_config_path)
            root = tree.getroot()
            
            # Find the net-file entry
            net_file = root.find(".//net-file")
            if net_file is not None:
                net_file_value = net_file.get("value")
                
                # If it's a relative path, convert to absolute path
                if not os.path.isabs(net_file_value):
                    config_dir = os.path.dirname(self.sumo_config_path)
                    return os.path.join(config_dir, net_file_value)
                return net_file_value
            
            print("Warning: Could not find net-file in SUMO config. Using default.")
            # Try to find a .net.xml file in the same directory as the config
            config_dir = os.path.dirname(self.sumo_config_path)
            net_files = [f for f in os.listdir(config_dir) if f.endswith(".net.xml")]
            if net_files:
                return os.path.join(config_dir, net_files[0])
            
            raise FileNotFoundError("No .net.xml file found in the config directory.")
        
        except Exception as e:
            print(f"Error getting net file path: {e}")
            return None
    
    def start(self):
        """Start the SUMO simulation and visualization."""
        try:
            # Start the SUMO simulation
            self.simulation.start()
            
            # Initialize traffic light positions
            self._initialize_traffic_light_positions()
            
            self.running = True
            print("SUMO Visualization started")
            return True
        
        except Exception as e:
            print(f"Error starting SUMO visualization: {e}")
            return False
    
def _initialize_traffic_light_positions(self):
    """Initialize traffic light positions based on SUMO network."""
    try:
        # Get all traffic lights
        tl_ids = traci.trafficlight.getIDList()
        print(f"Found traffic lights: {tl_ids}")
        
        for tl_id in tl_ids:
            # First, try to match with a junction directly
            if tl_id in self.network_parser.nodes:
                self.traffic_light_positions[tl_id] = self.network_parser.nodes[tl_id]
                print(f"Positioned traffic light {tl_id} at junction position")
                continue
            
            # If not found, try to find any junction that might control this light
            for junction_id in self.network_parser.nodes:
                if junction_id.startswith(tl_id) or tl_id.startswith(junction_id):
                    self.traffic_light_positions[tl_id] = self.network_parser.nodes[junction_id]
                    print(f"Positioned traffic light {tl_id} at related junction {junction_id}")
                    continue
            
            # As a last resort, get controlled links
            try:
                links = traci.trafficlight.getControlledLinks(tl_id)
                if links and links[0]:
                    # Get the incoming lane
                    incoming_lane = links[0][0][0]
                    
                    # Get the lane shape
                    lane_shape = traci.lane.getShape(incoming_lane)
                    
                    # Use the last point of the lane shape (closest to the junction)
                    if lane_shape:
                        self.traffic_light_positions[tl_id] = lane_shape[-1]
                        print(f"Positioned traffic light {tl_id} at lane endpoint")
                        continue
            except Exception as link_error:
                print(f"Error getting controlled links for {tl_id}: {link_error}")
            
            print(f"Warning: Could not determine position for traffic light {tl_id}")
        
        print(f"Initialized {len(self.traffic_light_positions)} traffic light positions out of {len(tl_ids)} traffic lights")
        
        # If we didn't find any traffic lights but the network has junctions, create traffic lights at junctions
        if not self.traffic_light_positions and self.network_parser.nodes:
            print("No traffic lights were found, creating default ones at junctions")
            for junction_id, position in self.network_parser.nodes.items():
                # Only use main junctions (not internal ones)
                if not junction_id.startswith(':'):
                    self.traffic_light_positions[junction_id] = position
                    print(f"Created default traffic light at junction {junction_id}")
    
    except Exception as e:
        print(f"Error initializing traffic light positions: {e}")
    
    def _update_stats(self):
        """Update simulation statistics."""
        try:
            # Update vehicle count
            vehicles = traci.vehicle.getIDList()
            self.stats["vehicles"] = len(vehicles)
            
            # Update average speed and wait time
            if vehicles:
                total_speed = sum(traci.vehicle.getSpeed(v) for v in vehicles)
                total_wait_time = sum(traci.vehicle.getWaitingTime(v) for v in vehicles)
                
                self.stats["avg_speed"] = total_speed / len(vehicles)
                self.stats["avg_wait_time"] = total_wait_time / len(vehicles)
                
                # Store for performance metrics
                self.performance_metrics["speeds"].append(self.stats["avg_speed"])
                self.performance_metrics["wait_times"].append(self.stats["avg_wait_time"])
            else:
                self.stats["avg_speed"] = 0.0
                self.stats["avg_wait_time"] = 0.0
            
            # Update throughput (vehicles that have arrived at their destination)
            arrived = traci.simulation.getArrivedNumber()
            self.stats["throughput"] += arrived
            self.performance_metrics["throughput"].append(arrived)
            
            # Update step number
            self.stats["step"] = traci.simulation.getTime()
        
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def step(self, delay_ms=100):
        """
        Perform one simulation and visualization step with delay to slow down simulation.
        
        Args:
            delay_ms (int): Delay in milliseconds to slow down the simulation
        """
        if not self.running:
            return False
        
        try:
            # Add delay to slow down simulation
            pygame.time.delay(delay_ms)
            
            # Step the SUMO simulation
            self.simulation.step()
            
            # Update statistics
            self._update_stats()
            
            # Handle visualization events
            running = self.visualization.handle_events()
            if not running:
                self.close()
                return False
            
            # Clear the visualization
            self.visualization.clear()
            
            # Update renderer with current visualization settings
            self.traffic_renderer.update_view_settings(
                self.visualization.offset_x,
                self.visualization.offset_y,
                self.visualization.zoom
            )
            
            # Render the network
            self.traffic_renderer.render_network()
            
            # Render all vehicles
            vehicles = traci.vehicle.getIDList()
            for vehicle_id in vehicles:
                try:
                    # Get vehicle position
                    position = traci.vehicle.getPosition(vehicle_id)
                    
                    # Get vehicle angle (heading)
                    angle = traci.vehicle.getAngle(vehicle_id)
                    
                    # Get vehicle type
                    v_type = traci.vehicle.getTypeID(vehicle_id)
                    vehicle_type = self.traffic_renderer.map_vehicle_type(v_type)
                    
                    # Get speed and waiting time
                    speed = traci.vehicle.getSpeed(vehicle_id)
                    waiting_time = traci.vehicle.getWaitingTime(vehicle_id)
                    
                    # Render the vehicle
                    self.traffic_renderer.render_vehicle(
                        vehicle_id, position, angle, vehicle_type, 
                        speed, waiting_time, None  # Skip label for better performance
                    )
                
                except Exception as e:
                    print(f"Error rendering vehicle {vehicle_id}: {e}")
                    continue
            
            # Render all traffic lights
            for tl_id in traci.trafficlight.getIDList():
                try:
                    # Get traffic light state
                    state = traci.trafficlight.getRedYellowGreenState(tl_id)
                    
                    # Get position
                    if tl_id in self.traffic_light_positions:
                        position = self.traffic_light_positions[tl_id]
                        
                        # Render the traffic light
                        self.traffic_renderer.render_traffic_light(tl_id, position, state)
                
                except Exception as e:
                    print(f"Error rendering traffic light {tl_id}: {e}")
                    continue
            
            # Render junctions
            for junction_id in self.network_parser.nodes:
                self.traffic_renderer.render_junction(junction_id)
            
            # Render statistics
            formatted_stats = {
                "Vehicles": self.stats["vehicles"],
                "Avg Speed": f"{self.stats['avg_speed']:.2f} m/s",
                "Avg Wait Time": f"{self.stats['avg_wait_time']:.2f} s",
                "Throughput": self.stats["throughput"],
                "Simulation Time": f"{self.stats['step']:.1f} s",
                "Mode": self.stats["mode"]
            }
            self.visualization.draw_stats(formatted_stats)
            
            # Draw debug information including traffic light states
            self.draw_debug_info()
            
            # Update the visualization
            self.visualization.update()
            
            return True
        
        except Exception as e:
            print(f"Error in simulation step: {e}")
            return False
    
def draw_debug_info(self):
    """Draw debug information including traffic light states."""
    y_offset = 100  # Start below the regular stats
    
    # Display traffic light states
    self.visualization.draw_text("Traffic Light States:", 10, y_offset, (0, 0, 0))
    y_offset += 20
    
    tl_ids = traci.trafficlight.getIDList()
    
    if not tl_ids:
        self.visualization.draw_text("No traffic lights found in simulation!", 15, y_offset, (255, 0, 0))
        y_offset += 20
        
        # Show additional debug info about junctions
        self.visualization.draw_text("Junctions in network:", 15, y_offset, (0, 0, 100))
        y_offset += 20
        
        for junction_id in list(self.network_parser.nodes.keys())[:5]:  # Show first 5 junctions
            self.visualization.draw_text(f"  {junction_id}: {self.network_parser.nodes[junction_id]}", 15, y_offset, (0, 0, 100))
            y_offset += 20
    else:
        for tl_id in tl_ids[:5]:  # Show first 5 traffic lights
            try:
                state = traci.trafficlight.getRedYellowGreenState(tl_id)
                phase_duration = traci.trafficlight.getPhaseDuration(tl_id)
                time_to_change = traci.trafficlight.getNextSwitch(tl_id) - traci.simulation.getTime()
                
                text = f"{tl_id}: {state} (next change in {time_to_change:.1f}s)"
                self.visualization.draw_text(text, 15, y_offset, (0, 0, 100))
                y_offset += 20
                
                # Show position information
                if tl_id in self.traffic_light_positions:
                    pos = self.traffic_light_positions[tl_id]
                    self.visualization.draw_text(f"  Position: ({pos[0]:.1f}, {pos[1]:.1f})", 25, y_offset, (100, 100, 100))
                    y_offset += 20
            except Exception as e:
                self.visualization.draw_text(f"{tl_id}: Error getting state - {str(e)}", 15, y_offset, (255, 0, 0))
                y_offset += 20
    
    def run(self, steps=1000, delay_ms=100):
        """
        Run the simulation for a specified number of steps.
        
        Args:
            steps (int): Number of simulation steps to run
            delay_ms (int): Delay in milliseconds between steps
        """
        if not self.start():
            return False
        
        for _ in range(steps):
            if not self.step(delay_ms):
                break
        
        self.close()
        return True
    
    def set_mode(self, mode):
        """Set the simulation mode (e.g., 'Wired AI', 'Wireless AI')."""
        self.stats["mode"] = mode
    
    def close(self):
        """Close the simulation and visualization."""
        if self.running:
            self.simulation.close()
            self.visualization.close()
            self.running = False
            print("SUMO Visualization closed")

# Test the SUMO visualization
if __name__ == "__main__":
    import os
    
    # Path to the SUMO configuration file
    sumo_config_path = os.path.join(project_root, "config", "maps", "grid_network.sumocfg")
    
    # Create and run the visualization
    visualization = SumoVisualization(sumo_config_path, width=1024, height=768, use_gui=False)
    visualization.run(steps=1000, delay_ms=100)  # Run for 1000 steps with 100ms delay
```

# src\ui\traffic_renderer.py

```py
import pygame
import math
import numpy as np
from enum import Enum

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
LIGHT_BLUE = (100, 100, 255)
LIGHT_GREEN = (100, 255, 100)

class VehicleType(Enum):
    """Types of vehicles for visualization."""
    PASSENGER = 0
    TRUCK = 1
    BUS = 2
    MOTORCYCLE = 3
    BICYCLE = 4
    EMERGENCY = 5

class TrafficRenderer:
    """
    Renderer for traffic elements such as vehicles and traffic lights.
    """
    def __init__(self, screen, mapper, offset_x=0, offset_y=0, zoom=1.0):
        """
        Initialize the traffic renderer.
        
        Args:
            screen: Pygame screen to draw on
            mapper: SumoPygameMapper for coordinate conversion
            offset_x: X offset for panning the view
            offset_y: Y offset for panning the view
            zoom: Zoom factor for the view
        """
        self.screen = screen
        self.mapper = mapper
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.zoom = zoom
        
        # Load fonts
        self.font = pygame.font.SysFont("Arial", 10)
        
        # Set up vehicle type configurations
        self.vehicle_configs = {
            VehicleType.PASSENGER: {
                "color": BLUE,
                "size": (8, 4),
            },
            VehicleType.TRUCK: {
                "color": DARK_GRAY,
                "size": (10, 5),
            },
            VehicleType.BUS: {
                "color": LIGHT_GREEN,
                "size": (12, 5),
            },
            VehicleType.MOTORCYCLE: {
                "color": MAGENTA,
                "size": (6, 3),
            },
            VehicleType.BICYCLE: {
                "color": CYAN,
                "size": (4, 2),
            },
            VehicleType.EMERGENCY: {
                "color": RED,
                "size": (8, 4),
            }
        }
        
        print("Traffic renderer initialized")
    
    def update_view_settings(self, offset_x, offset_y, zoom):
        """Update the view settings for panning and zooming."""
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.zoom = zoom
    
    def _transform_coordinates(self, x, y):
        """Transform SUMO coordinates to screen coordinates with view settings."""
        pygame_x, pygame_y = self.mapper.sumo_to_pygame(x, y)
        return (pygame_x * self.zoom + self.offset_x, 
                pygame_y * self.zoom + self.offset_y)
    
    def map_vehicle_type(self, sumo_type):
        """Map SUMO vehicle type to our visualization vehicle type."""
        sumo_type = sumo_type.lower()
        if "bus" in sumo_type:
            return VehicleType.BUS
        elif "truck" in sumo_type or "trailer" in sumo_type:
            return VehicleType.TRUCK
        elif "motorcycle" in sumo_type or "moped" in sumo_type:
            return VehicleType.MOTORCYCLE
        elif "bicycle" in sumo_type:
            return VehicleType.BICYCLE
        elif "emergency" in sumo_type or "police" in sumo_type or "ambulance" in sumo_type:
            return VehicleType.EMERGENCY
        else:
            return VehicleType.PASSENGER
    
    def render_vehicle(self, vehicle_id, position, angle, vehicle_type=VehicleType.PASSENGER, 
                      speed=None, waiting_time=None, label=None):
        """
        Render a vehicle with the given properties.
        
        Args:
            vehicle_id: ID of the vehicle
            position: (x, y) position in SUMO coordinates
            angle: Heading angle in degrees (0 = East, 90 = North)
            vehicle_type: VehicleType enum value
            speed: Current speed in m/s (optional)
            waiting_time: Time spent waiting in seconds (optional)
            label: Text label to display (optional)
        """
        # Get the vehicle configuration
        config = self.vehicle_configs.get(vehicle_type, self.vehicle_configs[VehicleType.PASSENGER])
        
        # Transform coordinates
        screen_x, screen_y = self._transform_coordinates(position[0], position[1])
        
        # Adjust the angle for Pygame (SUMO uses different angle convention)
        # In SUMO, 0 = east, 90 = north, while in Pygame we need 0 = east, 90 = south
        pygame_angle = -angle + 90  # This might need adjustment based on your specific SUMO setup
        
        # Calculate vehicle size
        width = config["size"][0] * self.zoom
        height = config["size"][1] * self.zoom
        
        # Create a surface for the vehicle
        vehicle_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Color based on vehicle type, with variations based on speed if provided
        base_color = config["color"]
        vehicle_color = base_color
        
        # If speed is provided, adjust color intensity
        if speed is not None:
            # Normalize speed to 0-1 range (assuming max speed is around 30 m/s)
            speed_factor = min(1.0, speed / 30.0)
            # Make faster vehicles brighter
            vehicle_color = tuple(min(255, int(c * (0.5 + 0.5 * speed_factor))) for c in base_color)
        
        # If waiting time is provided, add red tint to indicate waiting
        if waiting_time is not None and waiting_time > 0:
            # Normalize waiting time (max considerd is 60 seconds)
            wait_factor = min(1.0, waiting_time / 60.0)
            # Blend with red based on waiting time
            vehicle_color = tuple(min(255, int(c * (1 - wait_factor) + RED[i] * wait_factor)) 
                                 for i, c in enumerate(vehicle_color))
        
        # Fill the vehicle surface with the calculated color
        vehicle_surface.fill(vehicle_color)
        
        # Draw a small triangle to indicate direction
        arrow_points = [
            (width * 0.8, height // 2),  # Tip of arrow
            (width * 0.5, height * 0.2),  # Left corner
            (width * 0.5, height * 0.8),  # Right corner
        ]
        pygame.draw.polygon(vehicle_surface, BLACK, arrow_points)
        
        # Rotate the vehicle surface
        rotated_surface = pygame.transform.rotate(vehicle_surface, pygame_angle)
        rotated_rect = rotated_surface.get_rect(center=(screen_x, screen_y))
        
        # Draw the vehicle
        self.screen.blit(rotated_surface, rotated_rect.topleft)
        
        # Draw the label if provided
        if label:
            label_surface = self.font.render(label, True, WHITE, BLACK)
            label_rect = label_surface.get_rect(center=(screen_x, screen_y - 15 * self.zoom))
            self.screen.blit(label_surface, label_rect.topleft)
    
    def render_traffic_light(self, tl_id, position, state):
        """
        Render a traffic light with the given state.
        
        Args:
            tl_id: ID of the traffic light
            position: (x, y) position in SUMO coordinates
            state: Traffic light state string (e.g., 'GrYy')
        """
        # Transform coordinates
        screen_x, screen_y = self._transform_coordinates(position[0], position[1])
        
        # Increase sizes for better visibility
        tl_radius = 10 * self.zoom  # Increased from 6
        tl_spacing = 6 * self.zoom  # Increased from 4
        tl_box_width = tl_radius * 2 + 8 * self.zoom  # Increased padding
        tl_box_height = (tl_radius * 2 + tl_spacing) * len(state) + 8 * self.zoom
        
        # Draw traffic light box with more contrasting colors
        tl_box_rect = pygame.Rect(
            screen_x - tl_box_width / 2,
            screen_y - tl_box_height / 2,
            tl_box_width,
            tl_box_height
        )
        pygame.draw.rect(self.screen, BLACK, tl_box_rect, border_radius=4)
        pygame.draw.rect(self.screen, GRAY, tl_box_rect.inflate(-4, -4), border_radius=3)
        
        # Draw each light
        y_offset = screen_y - (tl_box_height / 2) + (tl_radius + 4 * self.zoom)
        
        for i, light in enumerate(state):
            # Determine color based on the state character
            if light in ('G', 'g'):  # Green
                color = GREEN
            elif light in ('Y', 'y'):  # Yellow
                color = YELLOW
            elif light in ('R', 'r'):  # Red
                color = RED
            else:  # Off or unknown
                color = DARK_GRAY
            
            # Draw the light with a black outline for better visibility
            pygame.draw.circle(
                self.screen, 
                BLACK, 
                (screen_x, y_offset + i * (tl_radius * 2 + tl_spacing)), 
                tl_radius + 2  # Slightly larger for outline
            )
            pygame.draw.circle(
                self.screen, 
                color, 
                (screen_x, y_offset + i * (tl_radius * 2 + tl_spacing)), 
                tl_radius
            )
            
            # Add a text label for the traffic light ID
            if i == 0:  # Only show on the first light
                id_text = self.font.render(tl_id, True, WHITE, BLACK)
                id_rect = id_text.get_rect(center=(screen_x, y_offset - tl_radius - 10 * self.zoom))
                self.screen.blit(id_text, id_rect.topleft)
    
    def render_network(self, roads=None):
        """
        Render the road network.
        
        Args:
            roads: Optional list of road segments to render, each with format:
                  (start_pos, end_pos, width, color)
        """
        # If roads are provided, render them
        if roads:
            for start_pos, end_pos, width, color in roads:
                # Transform coordinates
                start_x, start_y = self._transform_coordinates(start_pos[0], start_pos[1])
                end_x, end_y = self._transform_coordinates(end_pos[0], end_pos[1])
                
                # Scale width by zoom
                scaled_width = width * self.zoom
                
                # Draw the road
                pygame.draw.line(self.screen, color, (start_x, start_y), (end_x, end_y), int(scaled_width))
        
        # Otherwise, render all edges from the network parser
        else:
            for edge_id, edge_data in self.mapper.net_parser.edges.items():
                shape = self.mapper.get_edge_shape(edge_id)
                if shape and len(shape) >= 2:
                    for i in range(len(shape) - 1):
                        start = shape[i]
                        end = shape[i + 1]
                        
                        # Apply view transformations
                        start = (start[0] * self.zoom + self.offset_x, 
                                 start[1] * self.zoom + self.offset_y)
                        end = (end[0] * self.zoom + self.offset_x, 
                               end[1] * self.zoom + self.offset_y)
                        
                        # Draw the road
                        pygame.draw.line(self.screen, DARK_GRAY, start, end, int(10 * self.zoom))

    def render_junction(self, junction_id):
        """
        Render a junction (intersection).
        
        Args:
            junction_id: ID of the junction in the SUMO network
        """
        # Get the junction position
        pos = self.mapper.get_node_position(junction_id)
        if not pos:
            return
        
        # Transform coordinates
        screen_x, screen_y = pos[0] * self.zoom + self.offset_x, pos[1] * self.zoom + self.offset_y
        
        # Draw the junction
        pygame.draw.circle(self.screen, DARK_GRAY, (screen_x, screen_y), 15 * self.zoom)
        pygame.draw.circle(self.screen, BLACK, (screen_x, screen_y), 15 * self.zoom, width=2)

# Simple test to verify the traffic renderer works
if __name__ == "__main__":
    import os
    import sys
    from pathlib import Path
    
    # Add project root to Python path
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.append(str(project_root))
    
    from src.ui.sumo_pygame_mapper import SumoNetworkParser, SumoPygameMapper
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Traffic Renderer Test")
    
    # Path to the SUMO network file
    net_file_path = os.path.join(project_root, "config", "maps", "grid_network.net.xml")
    
    # Parse the network and create mapper
    parser = SumoNetworkParser(net_file_path)
    mapper = SumoPygameMapper(parser, 800, 600)
    
    # Create traffic renderer
    renderer = TrafficRenderer(screen, mapper)
    
    # Main loop
    clock = pygame.time.Clock()
    running = True
    
    # Create some test vehicles at different positions
    test_vehicles = [
        # (id, position, angle, type, speed, waiting_time, label)
        ("v1", (25, 25), 0, VehicleType.PASSENGER, 10, 0, "Car1"),
        ("v2", (75, 25), 90, VehicleType.TRUCK, 5, 10, "Truck"),
        ("v3", (25, 75), 180, VehicleType.BUS, 0, 30, "Bus"),
        ("v4", (75, 75), 270, VehicleType.EMERGENCY, 15, 0, "Ambulance"),
    ]
    
    # Test traffic lights
    test_tls = [
        # (id, position, state)
        ("tl1", (25, 25), "GrYr"),
        ("tl2", (75, 25), "rGry"),
        ("tl3", (25, 75), "rrGG"),
        ("tl4", (75, 75), "YYrr"),
    ]
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Clear the screen
        screen.fill(WHITE)
        
        # Render the network
        renderer.render_network()
        
        # Render test vehicles
        for v_id, pos, angle, v_type, speed, wait, label in test_vehicles:
            renderer.render_vehicle(v_id, pos, angle, v_type, speed, wait, label)
        
        # Render test traffic lights
        for tl_id, pos, state in test_tls:
            renderer.render_traffic_light(tl_id, pos, state)
        
        # Render junctions
        for junction_id in list(parser.nodes.keys())[:4]:  # Just render the first 4 junctions for testing
            renderer.render_junction(junction_id)
        
        # Update the display
        pygame.display.flip()
        
        # Control the frame rate
        clock.tick(30)
    
    pygame.quit()
```

# src\ui\visualization.py

```py
import pygame
import os
from pathlib import Path
from src.ui.sumo_pygame_mapper import SumoNetworkParser, SumoPygameMapper

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

class Visualization:
    """
    Pygame-based visualization for the traffic simulation.
    """
    def __init__(self, width=800, height=600, title="AI Traffic Control Simulation", net_file=None):
        """
        Initialize the visualization window.
        
        Args:
            width (int): Width of the window in pixels
            height (int): Height of the window in pixels
            title (str): Title of the window
            net_file (str): Path to the SUMO network file
        """
        # Initialize pygame
        pygame.init()
        
        # Set up the display
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        self.fps = 30
        
        # Load assets
        self.assets_path = Path(__file__).resolve().parent.parent.parent / "assets"
        self.assets = self._load_assets()
        
        # SUMO Network mapping
        self.net_file = net_file
        self.network_parser = None
        self.mapper = None
        if net_file:
            self._setup_network_mapping()
        
        # Simulation view settings
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 1.0
        
        # Font for displaying information
        self.font = pygame.font.SysFont("Arial", 16)
        
        print(f"Visualization initialized with window size {width}x{height}")
    
    def _load_assets(self):
        """Load image assets for the visualization"""
        assets = {}
        
        # Create the assets directory if it doesn't exist
        os.makedirs(self.assets_path, exist_ok=True)
        
        # For now, return empty assets dictionary
        # We'll add real assets later
        return assets
    
    def _setup_network_mapping(self):
        """Set up the SUMO to Pygame coordinate mapping."""
        if not os.path.exists(self.net_file):
            print(f"Warning: Network file not found: {self.net_file}")
            return
        
        try:
            self.network_parser = SumoNetworkParser(self.net_file)
            self.mapper = SumoPygameMapper(self.network_parser, self.width, self.height)
            print("SUMO network successfully loaded and mapped to Pygame coordinates")
        except Exception as e:
            print(f"Error setting up network mapping: {str(e)}")
    
    def handle_events(self):
        """Handle pygame events and return whether to continue running"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                # Press ESC to quit
                if event.key == pygame.K_ESCAPE:
                    return False
                # Arrow keys to move the view
                elif event.key == pygame.K_LEFT:
                    self.offset_x += 20
                elif event.key == pygame.K_RIGHT:
                    self.offset_x -= 20
                elif event.key == pygame.K_UP:
                    self.offset_y += 20
                elif event.key == pygame.K_DOWN:
                    self.offset_y -= 20
                # Zoom controls
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.zoom *= 1.1
                elif event.key == pygame.K_MINUS:
                    self.zoom /= 1.1
        
        return True
    
    def clear(self):
        """Clear the screen to prepare for drawing"""
        self.screen.fill(WHITE)
    
    def draw_text(self, text, x, y, color=BLACK):
        """Draw text on the screen"""
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
    
    def draw_stats(self, stats):
        """Draw simulation statistics"""
        y_offset = 10
        for key, value in stats.items():
            self.draw_text(f"{key}: {value}", 10, y_offset)
            y_offset += 20
    
    def draw_road(self, start_pos, end_pos, width=10):
        """Draw a road segment"""
        # Transform coordinates based on offset and zoom
        start_x = start_pos[0] * self.zoom + self.offset_x
        start_y = start_pos[1] * self.zoom + self.offset_y
        end_x = end_pos[0] * self.zoom + self.offset_x
        end_y = end_pos[1] * self.zoom + self.offset_y
        
        # Draw the road (gray background)
        pygame.draw.line(self.screen, DARK_GRAY, (start_x, start_y), (end_x, end_y), width)
        
        # Draw lane markings (dashed white line)
        # This is a simplified representation; you might want to improve it later
        length = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
        if length > 0:
            dx = (end_x - start_x) / length
            dy = (end_y - start_y) / length
            
            # Draw dashed line
            dash_length = 5
            gap_length = 5
            distance = 0
            drawing = True
            
            while distance < length:
                if drawing:
                    line_start = (start_x + distance * dx, start_y + distance * dy)
                    line_end = (start_x + min(distance + dash_length, length) * dx, 
                                start_y + min(distance + dash_length, length) * dy)
                    pygame.draw.line(self.screen, WHITE, line_start, line_end, 1)
                distance += dash_length if drawing else gap_length
                drawing = not drawing
    
    def draw_intersection(self, position, size=20):
        """Draw a road intersection"""
        # Transform coordinates based on offset and zoom
        x = position[0] * self.zoom + self.offset_x
        y = position[1] * self.zoom + self.offset_y
        transformed_size = size * self.zoom
        
        # Draw the intersection as a dark gray rectangle
        rect = pygame.Rect(
            x - transformed_size/2, 
            y - transformed_size/2, 
            transformed_size, 
            transformed_size
        )
        pygame.draw.rect(self.screen, DARK_GRAY, rect)
    
    def draw_traffic_light(self, position, state):
        """
        Draw a traffic light with the given state.
        
        Args:
            position (tuple): (x, y) position of the traffic light
            state (str): Traffic light state (e.g., 'G' for green, 'Y' for yellow, 'R' for red)
        """
        # Transform coordinates based on offset and zoom
        x = position[0] * self.zoom + self.offset_x
        y = position[1] * self.zoom + self.offset_y
        radius = 5 * self.zoom
        
        # Determine color based on state
        if state == 'G':
            color = GREEN
        elif state == 'Y':
            color = YELLOW
        else:  # 'R' or any other state
            color = RED
        
        # Draw the traffic light as a colored circle
        pygame.draw.circle(self.screen, color, (int(x), int(y)), int(radius))
    
    def draw_vehicle(self, position, size=(10, 5), color=BLUE, angle=0):
        """
        Draw a vehicle.
        
        Args:
            position (tuple): (x, y) position of the vehicle
            size (tuple): (width, height) of the vehicle
            color (tuple): RGB color of the vehicle
            angle (float): Rotation angle in degrees
        """
        # Transform coordinates based on offset and zoom
        x = position[0] * self.zoom + self.offset_x
        y = position[1] * self.zoom + self.offset_y
        width = size[0] * self.zoom
        height = size[1] * self.zoom
        
        # Create a surface for the vehicle
        vehicle_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        vehicle_surface.fill(color)
        
        # Rotate the vehicle if needed
        if angle != 0:
            vehicle_surface = pygame.transform.rotate(vehicle_surface, angle)
        
        # Get the rect for the rotated surface
        rect = vehicle_surface.get_rect(center=(x, y))
        
        # Draw the vehicle
        self.screen.blit(vehicle_surface, rect.topleft)
    
    def draw_sumo_network(self):
        """Draw the SUMO network on the screen."""
        if not self.mapper:
            return
        
        # Draw all edges (roads)
        for edge_id, edge_data in self.network_parser.edges.items():
            shape = self.mapper.get_edge_shape(edge_id)
            if shape and len(shape) >= 2:
                for i in range(len(shape) - 1):
                    start = shape[i]
                    end = shape[i + 1]
                    # Apply visualization offsets and zoom
                    start = (start[0] * self.zoom + self.offset_x, start[1] * self.zoom + self.offset_y)
                    end = (end[0] * self.zoom + self.offset_x, end[1] * self.zoom + self.offset_y)
                    self.draw_road(start, end)
        
        # Draw all nodes (junctions)
        for node_id, _ in self.network_parser.nodes.items():
            pos = self.mapper.get_node_position(node_id)
            if pos:
                # Apply visualization offsets and zoom
                pos = (pos[0] * self.zoom + self.offset_x, pos[1] * self.zoom + self.offset_y)
                self.draw_intersection(pos)
    
    def update(self):
        """Update the display"""
        pygame.display.flip()
        self.clock.tick(self.fps)
    
    def close(self):
        """Close the visualization"""
        pygame.quit()

# Simple test to verify the visualization works with a SUMO network
if __name__ == "__main__":
    import os
    from pathlib import Path
    
    # Get the path to the SUMO network file
    project_root = Path(__file__).resolve().parent.parent.parent
    net_file_path = os.path.join(project_root, "config", "maps", "grid_network.net.xml")
    
    # Create the visualization with the SUMO network
    viz = Visualization(net_file=net_file_path)
    running = True
    
    while running:
        running = viz.handle_events()
        
        viz.clear()
        
        # Draw the SUMO network
        viz.draw_sumo_network()
        
        # Draw some example vehicles and traffic lights
        # These positions should be derived from the SUMO simulation in the future
        viz.draw_vehicle((400, 300))
        viz.draw_vehicle((450, 300))
        
        # Draw sample statistics
        viz.draw_stats({
            "Vehicles": 2,
            "Average Wait Time": "5.2s",
            "Throughput": "85 veh/h",
            "Mode": "SUMO Network Test"
        })
        
        viz.update()
    
    viz.close()
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

