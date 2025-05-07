import os
import sys
import json
import time
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from datetime import datetime

# add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.simulation.scenario_runner import ScenarioRunner

class ComparisonFramework:
    """
    Framework for comprehensive comparison of different traffic control strategies.
    """
    def __init__(self, output_dir=None, run_id=None):
        """
        Initialise the comparison framework.
        """
        # Create a unique run ID if not provided
        if run_id is None:
            run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Set up output directory with run-specific subfolder
        if output_dir is None:
            output_dir = os.path.join(project_root, "data", "outputs", "comparison_results")
        
        # Create a separate folder for this run
        self.output_dir = os.path.join(output_dir, f"Comparison_{run_id}")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialise the scenario runner
        self.scenario_runner = ScenarioRunner()
        
        # Define controller types for comparison
        self.controller_types = [
            "Traditional", 
            "Wired AI", 
            "Wireless AI",
            "Wired RL",
            "Wireless RL"
        ]
        
        # Define scenarios to test
        self.scenarios = [
            "light_traffic",
            "moderate_traffic",
            "heavy_traffic",
            "peak_hour_morning"
        ]
        
        # Define metrics to track
        self.metrics = [
            "avg_waiting_time",
            "avg_speed",
            "throughput",
            "avg_response_time",
            "avg_decision_time"
        ]
        
    def run_comparison(self, scenarios=None, controller_types=None, steps=1000, 
                       runs_per_config=3, gui=False, model_paths=None):
        """
        Run a complete comparison across specified scenarios and controllers.
        
        Args:
            scenarios: List of scenarios to test (default: all available)
            controller_types: List of controller types to test (default: all available)
            steps: Number of simulation steps per run
            runs_per_config: Number of runs for each scenario-controller combination
            gui: Whether to show visualisation GUI
            model_paths: Dictionary mapping controller types to model paths
            
        """
        # use defaults if not specified
        if scenarios is None:
            scenarios = self.scenarios
        
        if controller_types is None:
            controller_types = self.controller_types
        
        # validate controller types
        valid_controllers = []
        for controller in controller_types:
            if controller in self.controller_types:
                valid_controllers.append(controller)
            else:
                print(f"Warning: Unknown controller type '{controller}'. Skipping.")
        
        if not valid_controllers:
            print("Error: No valid controller types specified.")
            return {}
        
        # initialise results structure
        comparison_results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "parameters": {
                "steps": steps,
                "runs_per_config": runs_per_config
            },
            "scenarios": {},
            "summary": {}
        }
        
        # run comparison for each scenario
        for scenario in scenarios:
            print(f"\n{'='*80}")
            print(f"Running comparison for scenario: {scenario}")
            print(f"{'='*80}")
            
            scenario_results = {}
            
            for controller_type in valid_controllers:
                print(f"\nTesting {controller_type} on {scenario}...")
                
                # get model path for controllers if available
                model_path = None
                if model_paths and controller_type in model_paths:
                    model_path = model_paths[controller_type]
                    print(f"Using pre-trained model: {model_path}")
                
                # initialise controller results
                controller_results = {
                    "runs": [],
                    "avg_metrics": {metric: 0 for metric in self.metrics}
                }
                
                # run multiple times for statistical significance
                for run in range(runs_per_config):
                    print(f"  Run {run+1}/{runs_per_config}...")
                    
                    # run the scenario
                    run_metrics = self.scenario_runner.run_scenario(
                        scenario_file=os.path.join(project_root, "config", "scenarios", f"{scenario}.rou.xml"),
                        controller_type=controller_type,
                        steps=steps,
                        gui=gui,
                        collect_metrics=True,
                        model_path=model_path
                    )
                    
                    # store run results
                    controller_results["runs"].append(run_metrics)
                    
                    # print run metrics
                    print(f"    Wait Time: {run_metrics['avg_waiting_time']:.2f}s")
                    print(f"    Speed: {run_metrics['avg_speed']:.2f}m/s")
                    print(f"    Throughput: {run_metrics['throughput']} vehicles")
                
                # calculate average metrics across runs
                for metric in self.metrics:
                    values = [run.get(metric, 0) for run in controller_results["runs"]]
                    if values:
                        controller_results["avg_metrics"][metric] = sum(values) / len(values)
                
                # Store controller results
                scenario_results[controller_type] = controller_results
                
                # Print average metrics
                print(f"  Average metrics for {controller_type} on {scenario}:")
                for metric, value in controller_results["avg_metrics"].items():
                    print(f"    {metric}: {value:.4f}")
            
            # store scenario results
            comparison_results["scenarios"][scenario] = scenario_results
        
        # calculate summary metrics across all scenarios
        summary = {}
        for controller_type in valid_controllers:
            controller_summary = {metric: [] for metric in self.metrics}
            
            for scenario in scenarios:
                if scenario in comparison_results["scenarios"] and controller_type in comparison_results["scenarios"][scenario]:
                    for metric in self.metrics:
                        value = comparison_results["scenarios"][scenario][controller_type]["avg_metrics"].get(metric, 0)
                        controller_summary[metric].append(value)
            
            # Calculate average of averages
            summary[controller_type] = {
                metric: sum(values) / len(values) if values else 0
                for metric, values in controller_summary.items()
            }
        
        comparison_results["summary"] = summary
        
        # Save comparison results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(self.output_dir, f"comparison_results_{timestamp}.json")
        
        with open(results_file, 'w') as f:
            json.dump(comparison_results, f, indent=2)
        
        print(f"\nComparison results saved to: {results_file}")
        
        # Generate visualisation
        self.visualise_comparison(comparison_results, timestamp)
        
        return comparison_results
    
    def visualise_comparison(self, results, timestamp=None, summary_only=False):
        """
        Generate visualisations from comparison results.
        """
        if not timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Extract controllers and scenarios
        controllers = list(results["summary"].keys())
        scenarios = list(results["scenarios"].keys())
        
        if not controllers or not scenarios:
            print("No data to visualise.")
            return
        
        # Create directory for visualisations
        vis_dir = os.path.join(self.output_dir, "visualisations")
        os.makedirs(vis_dir, exist_ok=True)
        
        # 1. Summary comparison across all scenarios
        self._plot_summary_comparison(results, controllers, vis_dir, timestamp)
        
        # Only generate detailed visualisations if summary_only is False
        if not summary_only:
            # 2. Detailed comparison by scenario
            self._plot_scenario_comparison(results, controllers, scenarios, vis_dir, timestamp)
            
            # 3. Controller performance profile
            self._plot_controller_profiles(results, controllers, scenarios, vis_dir, timestamp)
    
    def _plot_summary_comparison(self, results, controllers, output_dir, timestamp):
        """Plot summary comparison across all scenarios."""
        # Set up the figure
        fig, axs = plt.subplots(len(self.metrics), 1, figsize=(12, 4 * len(self.metrics)))
        fig.suptitle('Summary Comparison Across All Scenarios', fontsize=16)
        
        # Ensure axs is always a list for consistent indexing
        if len(self.metrics) == 1:
            axs = [axs]
        
        # Colors for controllers
        colours = plt.cm.tab10(np.linspace(0, 1, len(controllers)))
        
        # Plot each metric
        for i, metric in enumerate(self.metrics):
            ax = axs[i]
            
            # Get values for each controller
            values = [results["summary"][controller].get(metric, 0) for controller in controllers]
            
            # Create bar chart
            bars = ax.bar(range(len(controllers)), values, color=colours)
            
            # Add values on top of bars
            for j, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.02 * max(values) if values else 0,
                        f'{values[j]:.2f}', ha='center', va='bottom')
            
            # Set labels and title
            ax.set_xlabel('Controller Type')
            ax.set_ylabel(metric.replace('_', ' ').title())
            ax.set_title(f'Average {metric.replace("_", " ").title()} Across All Scenarios')
            ax.set_xticks(range(len(controllers)))
            ax.set_xticklabels(controllers, rotation=45, ha='right')
            ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(os.path.join(output_dir, f'summary_comparison_{timestamp}.png'), dpi=300)
        plt.close()
    
    def _plot_scenario_comparison(self, results, controllers, scenarios, output_dir, timestamp):
        """Plot detailed comparison by scenario."""
        # For each metric, create a grouped bar chart comparing controllers across scenarios
        for metric in self.metrics:
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Set up the plot
            bar_width = 0.15
            index = np.arange(len(scenarios))
            
            # Colors for controllers
            colours = plt.cm.tab10(np.linspace(0, 1, len(controllers)))
            
            # Plot bars for each controller
            for i, controller in enumerate(controllers):
                values = []
                for scenario in scenarios:
                    if scenario in results["scenarios"] and controller in results["scenarios"][scenario]:
                        values.append(results["scenarios"][scenario][controller]["avg_metrics"].get(metric, 0))
                    else:
                        values.append(0)
                
                # Create bars
                bars = ax.bar(index + i * bar_width, values, bar_width,
                              label=controller, color=colours[i])
                
                # Add values on top of bars
                for j, bar in enumerate(bars):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.02 * max(values) if values else 0,
                            f'{values[j]:.2f}', ha='center', va='bottom', fontsize=8)
            
            # set labels and title
            ax.set_xlabel('Scenario')
            ax.set_ylabel(metric.replace('_', ' ').title())
            ax.set_title(f'Comparison of {metric.replace("_", " ").title()} Across Scenarios and Controllers')
            ax.set_xticks(index + bar_width * (len(controllers) - 1) / 2)
            ax.set_xticklabels([s.replace('_', ' ').title() for s in scenarios])
            ax.legend()
            ax.grid(True, axis='y', linestyle='--', alpha=0.7)
            
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'{metric}_comparison_{timestamp}.png'), dpi=300)
            plt.close()
    
    def _plot_controller_profiles(self, results, controllers, scenarios, output_dir, timestamp):
        """Plot line charts showing each controller's performance across scenarios."""
        # For each controller, create line charts showing performance across scenarios
        for controller in controllers:
            # Create a figure with subplots for each metric
            fig, axs = plt.subplots(len(self.metrics), 1, figsize=(10, 3 * len(self.metrics)))
            
            if len(self.metrics) == 1:
                axs = [axs]
                
            fig.suptitle(f'Performance Profile: {controller}', fontsize=16)
            
            # Process each metric
            for i, metric in enumerate(self.metrics):
                ax = axs[i]
                
                # Get values across scenarios
                values = []
                for scenario in scenarios:
                    if scenario in results["scenarios"] and controller in results["scenarios"][scenario]:
                        values.append(results["scenarios"][scenario][controller]["avg_metrics"].get(metric, 0))
                    else:
                        values.append(0)
                
                # Plot line chart
                ax.plot(range(len(scenarios)), values, 'o-', linewidth=2)
                
                # Add value labels
                for j, value in enumerate(values):
                    ax.text(j, value + 0.02 * max(values) if values else 0, f'{value:.2f}', 
                            ha='center', va='bottom', fontsize=8)
                
                # Set labels and title
                ax.set_xlabel('Scenario')
                ax.set_ylabel(metric.replace('_', ' ').title())
                ax.set_title(f'{metric.replace("_", " ").title()}')
                ax.set_xticks(range(len(scenarios)))
                ax.set_xticklabels([s.replace('_', ' ').title() for s in scenarios], rotation=45, ha='right')
                ax.grid(True, linestyle='--', alpha=0.7)
            
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            plt.savefig(os.path.join(output_dir, f'{controller}_profile_{timestamp}.png'), dpi=300)
            plt.close()