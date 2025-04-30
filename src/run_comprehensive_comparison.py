import os
import sys
import argparse
import uuid
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.comparison_framework import ComparisonFramework

def main():
    """Run a comprehensive comparison of all controllers across all scenarios."""
    parser = argparse.ArgumentParser(description='Run comprehensive traffic controller comparison')
    parser.add_argument('--exclude-rl', action='store_true',
                        help='Exclude reinforcement learning controllers from comparison')
    parser.add_argument('--steps', type=int, default=1000,
                        help='Number of simulation steps per run')
    parser.add_argument('--runs', type=int, default=3,
                        help='Number of runs per configuration')
    parser.add_argument('--gui', action='store_true',
                        help='Show Python visualization GUI during simulation')
    parser.add_argument('--summary-only', action='store_true',
                        help='Only generate summary visualization, not detailed charts')
    args = parser.parse_args()
    
    # Generate a unique run ID for folder organization
    run_id = uuid.uuid4().hex[:8]
    
    # Initialize the comparison framework with the run ID
    comparison = ComparisonFramework(run_id=run_id)
    
    # Select controller types (include RL by default)
    controller_types = ["Traditional", "Wired AI", "Wireless AI"]
    
    if not args.exclude_rl:
        controller_types.extend(["Wired RL", "Wireless RL"])
        
        # Find RL model paths
        model_paths = {}
        models_dir = os.path.join(project_root, "data", "models")
        
        if os.path.exists(models_dir):
            # Look for the most recent model for each RL controller type
            for controller_type in ["wired_rl", "wireless_rl"]:
                model_files = [f for f in os.listdir(models_dir) 
                             if f.startswith(controller_type) and f.endswith('.pkl')]
                if model_files:
                    try:
                        # Sort by episode number to get the most recent
                        model_files.sort(key=lambda x: int(x.split('_episode_')[1].split('.')[0]))
                        newest_model = os.path.join(models_dir, model_files[-1])
                        
                        # Map to controller type
                        if controller_type == "wired_rl":
                            model_paths["Wired RL"] = newest_model
                            print(f"Found model for Wired RL: {newest_model}")
                        elif controller_type == "wireless_rl":
                            model_paths["Wireless RL"] = newest_model
                            print(f"Found model for Wireless RL: {newest_model}")
                    except (IndexError, ValueError) as e:
                        print(f"Error parsing model files for {controller_type}: {e}")
                else:
                    print(f"No model files found for {controller_type}")
        else:
            print(f"Models directory not found: {models_dir}")
            model_paths = None
    else:
        model_paths = None
    
    # Define scenarios to test
    scenarios = [
        "light_traffic",
        "moderate_traffic", 
        "heavy_traffic",
        "peak_hour_morning"
    ]
    
    print(f"Running comprehensive comparison with controllers: {controller_types}")
    print(f"Testing scenarios: {scenarios}")
    print(f"Using {args.runs} runs per configuration, {args.steps} steps per run")
    print(f"Results will be stored in folder: Comparison_{run_id}")
    
    if model_paths:
        print(f"Using model paths: {model_paths}")
    
    # Run the comparison
    results = comparison.run_comparison(
        scenarios=scenarios,
        controller_types=controller_types,
        steps=args.steps,
        runs_per_config=args.runs,
        gui=args.gui,  # This now controls Python visualization, not SUMO GUI
        model_paths=model_paths
    )
    
    # If summary-only flag is set, regenerate visualizations with only summary
    if args.summary_only and results:
        print("\nGenerating summary-only visualization...")
        comparison.visualize_comparison(results, summary_only=True)
    
    # Print overall summary
    if results:
        print("\nOverall Performance Summary:")
        print("=" * 80)
        
        for controller in controller_types:
            if controller in results["summary"]:
                print(f"\n{controller}:")
                for metric, value in results["summary"][controller].items():
                    print(f"  {metric}: {value:.4f}")
    else:
        print("No results were generated. Please check for errors above.")

if __name__ == "__main__":
    main()