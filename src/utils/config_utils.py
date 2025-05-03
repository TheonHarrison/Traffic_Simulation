# src/utils/config_utils.py
import os
from pathlib import Path

# find new model
def find_latest_model(controller_type, project_root=None):
    """
    Find the latest trained model for the specified controller type.
    
    Args:
        controller_type (str): Type of controller ("Wired RL" or "Wireless RL")
        project_root: Project root directory (optional)
    
    Returns:
        str or None: Path to the latest model file, or None if no model is found
    """
    # Determine project root if not provided
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent.parent
    
    # Convert controller type to filename format
    model_prefix = controller_type.replace(' ', '_').lower()
    
    # Define the models directory
    models_dir = os.path.join(project_root, "data", "models")
    
    if not os.path.exists(models_dir):
        print(f"Models directory not found: {models_dir}")
        return None
    
    # Find all model files for this controller type
    import glob
    import re
    model_pattern = os.path.join(models_dir, f"{model_prefix}_episode_*.pkl")
    model_files = glob.glob(model_pattern)
    
    if not model_files:
        print(f"No existing models found for {controller_type}")
        return None
    
    # Extract episode numbers and find the highest one
    episode_numbers = []
    for model_file in model_files:
        match = re.search(r'_episode_(\d+)\.pkl$', model_file)
        if match:
            episode_numbers.append((int(match.group(1)), model_file))
    
    if not episode_numbers:
        print(f"Could not parse episode numbers from model filenames")
        return None
    
    # Sort by episode number and get the latest
    episode_numbers.sort(key=lambda x: x[0], reverse=True)
    latest_episode, latest_model = episode_numbers[0]
    
    print(f"Found latest model for {controller_type}: Episode {latest_episode}")
    print(f"Model path: {latest_model}")
    
    return latest_model

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