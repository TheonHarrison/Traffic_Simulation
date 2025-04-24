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
    config_path = os.path.join(project_root, "config", "maps", "grid_network.sumocfg")
    
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