# AI Traffic Control Comparison

This project simulates and compares AI-controlled traffic systems operating over wireless and wired networks. The simulation environment uses SUMO (Simulation of Urban MObility) for traffic simulation and Pygame for visualization.

## Project Overview

The goal of this project is to investigate whether AI-driven traffic management using wireless systems can provide a more efficient alternative to traditional wired traffic control. The simulation allows for direct comparison between different control methods:

1. **Wired AI Controller**: Simulates fixed-network communication with consistent latency
2. **Wireless AI Controller**: Simulates wireless communication with dynamic computation delays
3. **Traditional Controller**: Uses fixed timing for traffic lights without adaptive behavior

## Features

- Realistic traffic simulation with multiple vehicle types (cars, trucks, buses, emergency vehicles)
- Enhanced visualization with improved graphics and interactive controls
- Comparative analysis using metrics like waiting time, speed, and throughput
- Various traffic scenarios to test controller performance under different conditions
- Comprehensive reporting and visualization of comparison results

## Installation

### Prerequisites

- Python 3.8 or higher
- SUMO (Simulation of Urban MObility) 1.18.0 or higher
- Pygame 2.5.0 or higher
- Required Python packages (listed in requirements.txt)

### Setup

1. Clone the repository:
git clone <repository-url>
cd traffic_ai_comparison

2. Install the required Python packages:
pip install -r requirements.txt

3. Make sure SUMO is properly installed and accessible in your PATH.

## Usage

### Running Enhanced Visualization

To run the enhanced visualization with a specific scenario and controller:
python src/run_enhanced_visualization.py --scenario light_traffic --controller "Wired AI" --steps 1000 --delay 50

Options:
- `--scenario`: Name of the scenario to run (light_traffic, moderate_traffic, heavy_traffic, peak_hour_morning)
- `--controller`: Controller type ("Wired AI", "Wireless AI", "Traditional")
- `--steps`: Number of simulation steps to run
- `--delay`: Delay in milliseconds between steps

### Running Comprehensive Comparison

To run a comprehensive comparison of all controllers across different scenarios:
python src/run_comprehensive_comparison.py --scenarios light_traffic moderate_traffic --controllers "Wired AI" "Wireless AI" "Traditional" --steps 1000 --runs 3

Options:
- `--scenarios`: List of scenarios to test
- `--controllers`: List of controllers to test
- `--steps`: Number of simulation steps per run
- `--runs`: Number of runs per configuration
- `--gui`: Flag to show visualization during comparison
- `--summary-only`: Only generate summary visualization, not detailed charts
- `--run-id`: Identifier for this comparison run
- `--output`: Directory to save results

### Generating Reports

To generate a comprehensive report from comparison results:
python src/generate_report.py --results data/outputs/comparison_results_20250425-180143.json --output data/outputs/report.md

Options:
- `--results`: Path to the comparison results JSON file
- `--output`: Path to save the generated report

## Controls

During enhanced visualization, you can use the following controls:
- **Mouse Drag**: Pan the view
- **Mouse Wheel**: Zoom in/out
- **I**: Toggle vehicle IDs display
- **S**: Toggle speed display
- **W**: Toggle waiting time display
- **ESC**: Quit

## Project Structure
traffic_ai_comparison/
├── config/
│   ├── maps/               # SUMO network definitions
│   └── scenarios/          # Traffic scenarios
├── data/
│   └── outputs/            # Simulation results and metrics
├── src/
│   ├── ai/                 # AI controller implementations
│   │   ├── controller.py   # Base controller class
│   │   ├── wired_controller.py
│   │   ├── wireless_controller.py
│   │   └── traditional_controller.py
│   ├── comparison_framework.py  # Framework for running comparisons
│   ├── generate_report.py  # Report generation
│   ├── generate_scenarios.py  # Traffic scenario generation
│   ├── run_comprehensive_comparison.py  # Main comparison script
│   ├── run_enhanced_visualization.py  # Main visualization script
│   ├── simulation/         # Simulation components
│   ├── ui/                 # Visualization components
│   │   ├── enhanced_renderer.py  # Enhanced traffic rendering
│   │   └── enhanced_sumo_visualization.py  # Enhanced visualization
│   └── utils/              # Utility functions
├── README.md
└── requirements.txt


## Academic Purpose

This project was developed as part of a BSc Computer Science dissertation to investigate the effectiveness of AI in controlling traffic systems wirelessly compared to traditional wired traffic systems.