import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.comparison_framework import ComparisonFramework

def main():
    """Run a comprehensive comparison of all controllers across all scenarios."""
    parser = argparse.ArgumentParser(description='Run comprehensive traffic controller comparison')
    parser.add_argument('--include-rl', action='store_true',
                        help='Include reinforcement learning controllers in comparison')
    parser.add_argument('--steps', type=int, default=1000,
                        help='Number of simulation steps per run')
    parser.add_argument('--runs', type=int, default=3,
                        help='Number of runs per configuration')
    parser.add_argument('--gui', action='store_true',
                        help='Show SUMO GUI during simulation')
    parser.add_argument('--wired-model', type=str, default=None,
                        help='Path to trained Wired RL model')
    parser.add_argument('--wireless-model', type=str, default=None,
                        help='Path to trained Wireless RL model')
    parser.add_argument('--exploration-rate', type=float, default=0.05,
                        help='Exploration rate for RL controllers during evaluation')
    parser.add_argument('--summary-only', action='store_true',
                        help='Print only the overall summary results')
    args = parser.parse_args()
    
    # Initialize the comparison framework
    comparison = ComparisonFramework()
    
    # Select controller types
    controller_types = ["Traditional", "Wired AI", "Wireless AI"]
    
    if args.include_rl:
        controller_types.extend(["Wired RL", "Wireless RL"])
        
        # Find RL model paths
        model_paths = {}
        models_dir = os.path.join(project_root, "data", "models")
        
        # Use command-line arguments if provided
        if args.wired_model:
            model_paths["Wired RL"] = args.wired_model
            if not args.summary_only:
                print(f"Using specified Wired RL model: {args.wired_model}")

        if args.wireless_model:
            model_paths["Wireless RL"] = args.wireless_model
            if not args.summary_only:
                print(f"Using specified Wireless RL model: {args.wireless_model}")
        
        # Otherwise, try to automatically find the most recent models
        if (not args.wired_model or not args.wireless_model) and os.path.exists(models_dir):
            # Look for the most recent model for each RL controller type
            for controller_type in ["wired_rl", "wireless_rl"]:
                if (controller_type == "wired_rl" and args.wired_model) or \
                   (controller_type == "wireless_rl" and args.wireless_model):
                    continue  # Skip if model was specified via argument
                    
                model_files = [f for f in os.listdir(models_dir) 
                             if f.startswith(controller_type) and f.endswith('.pkl')]
                if model_files:
                    # Sort by episode number to get the most recent
                    model_files.sort(key=lambda x: int(x.split('_episode_')[1].split('.')[0])
                                      if '_episode_' in x else 0)
                    newest_model = os.path.join(models_dir, model_files[-1])
                    
                    # Map to controller type
                    if controller_type == "wired_rl" and not args.wired_model:
                        model_paths["Wired RL"] = newest_model
                        if not args.summary_only:
                            print(f"Auto-detected latest Wired RL model: {newest_model}")
                    elif controller_type == "wireless_rl" and not args.wireless_model:
                        model_paths["Wireless RL"] = newest_model
                        if not args.summary_only:
                            print(f"Auto-detected latest Wireless RL model: {newest_model}")
        
        # Print debug information about which models will be used
        if not args.summary_only:
            print("\nRL Model information:")
            for controller_type, model_path in model_paths.items():
                print(f"  {controller_type}: {model_path}")
                print(f"    File exists: {os.path.exists(model_path)}")
                
                # Print some basic file stats
                if os.path.exists(model_path):
                    file_size = os.path.getsize(model_path) / 1024  # KB
                    print(f"    File size: {file_size:.2f} KB")
                    print(f"    Last modified: {datetime.fromtimestamp(os.path.getmtime(model_path))}")
        
        # Set a low exploration rate for evaluation to ensure trained policy is used
        for controller_type in ["Wired RL", "Wireless RL"]:
            if controller_type in model_paths:
                model_paths[f"{controller_type}_exploration_rate"] = args.exploration_rate
                if not args.summary_only:
                    print(f"  Using exploration rate of {args.exploration_rate} for {controller_type}")
                
        if not args.summary_only:
            print()
    else:
        model_paths = None
    
    # Define scenarios to test
    scenarios = [
        "light_traffic",
        "moderate_traffic", 
        "heavy_traffic",
        "peak_hour_morning"
    ]
    
    if not args.summary_only:
        print(f"Running comprehensive comparison with controllers: {controller_types}")
        print(f"Testing scenarios: {scenarios}")
        print(f"Using {args.runs} runs per configuration, {args.steps} steps per run")
    
    # Run the comparison
    results = comparison.run_comparison(
        scenarios=scenarios,
        controller_types=controller_types,
        steps=args.steps,
        runs_per_config=args.runs,
        gui=args.gui,
        model_paths=model_paths,
        verbose=not args.summary_only
    )
    
    # Print overall summary
    print("\nOverall Performance Summary:")
    print("=" * 80)
    
    for controller in controller_types:
        if controller in results["summary"]:
            print(f"\n{controller}:")
            for metric, value in results["summary"][controller].items():
                print(f"  {metric}: {value:.4f}")

if __name__ == "__main__":
    main()