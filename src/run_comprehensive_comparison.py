# src/run_comprehensive_comparison.py
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
    parser.add_argument('--scenarios', type=str, nargs='+',
                        help='Specific scenarios to test')
    parser.add_argument('--controllers', type=str, nargs='+',
                        choices=["Traditional", "Wired AI", "Wireless AI"],
                        help='Specific controller types to test')
    parser.add_argument('--steps', type=int, default=1000,
                        help='Number of simulation steps per run')
    parser.add_argument('--runs', type=int, default=3,
                        help='Number of runs per configuration')
    parser.add_argument('--gui', action='store_true',
                        help='Show visualization GUI during simulation')
    parser.add_argument('--output', type=str, default=None,
                        help='Directory to save results')
    parser.add_argument('--summary-only', action='store_true',
                        help='Only generate summary visualization, not detailed charts')
    parser.add_argument('--run-id', type=str, default=None,
                        help='Identifier for this comparison run')
    args = parser.parse_args()
    
    # Generate a unique run ID if not provided
    if args.run_id is None:
        args.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Initialize the comparison framework with specified run ID
    comparison = ComparisonFramework(output_dir=args.output, run_id=args.run_id)
    
    print(f"\n{'='*80}")
    print(f"Running comprehensive comparison with controllers: {args.controllers or comparison.controller_types}")
    print(f"Testing scenarios: {args.scenarios or comparison.scenarios}")
    print(f"Using {args.runs} runs per configuration, {args.steps} steps per run")
    print(f"Results will be stored in folder: Comparison_{args.run_id}")
    print(f"{'='*80}\n")
    
    # Run the comparison
    results = comparison.run_comparison(
        scenarios=args.scenarios,
        controller_types=args.controllers,
        steps=args.steps,
        runs_per_config=args.runs,
        gui=args.gui
    )
    
    # If summary-only flag is set, regenerate visualizations with only summary
    if args.summary_only and results:
        print("\nGenerating summary-only visualization...")
        comparison.visualize_comparison(results, summary_only=True)
    
    # Print overall summary
    if results:
        controllers = list(results["summary"].keys())
        print("\nOverall Performance Summary:")
        print("=" * 80)
        
        for controller in controllers:
            print(f"\n{controller}:")
            for metric, value in results["summary"][controller].items():
                print(f"  {metric}: {value:.4f}")
    else:
        print("No results were generated. Please check for errors above.")

if __name__ == "__main__":
    main()