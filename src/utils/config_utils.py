# src/utils/config_utils.py
import os
from pathlib import Path

def create_temp_config(route_file, network_file=None, project_root=None):
    """
    Create a temporary SUMO configuration file.
    
    Args:
        route_file: Path to the route file
        network_file: Path to the network file (optional)
        project_root: Project root directory (optional)
        
    Returns:
        Path to the created config file
    """
    # Determine project root if not provided
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent.parent
    
    # Determine network file if not provided
    if network_file is None:
        network_file = os.path.join(project_root, "config", "maps", "traffic_grid.net.xml")
    
    # Create a unique config file name
    base_name = os.path.basename(route_file).split('.')[0]
    config_name = f"temp_{base_name}.sumocfg"
    config_path = os.path.join(project_root, "config", "scenarios", config_name)
    
    # Write the config file
    with open(config_path, 'w') as f:
        f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">
    <input>
        <net-file value="{network_file}"/>
        <route-files value="{route_file}"/>
    </input>
    <time>
        <begin value="0"/>
        <end value="3600"/>
        <step-length value="1.0"/>
    </time>
    <processing>
        <time-to-teleport value="-1"/>
    </processing>
    <report>
        <verbose value="false"/>
        <no-step-log value="true"/>
    </report>
</configuration>""")
    
    return config_path