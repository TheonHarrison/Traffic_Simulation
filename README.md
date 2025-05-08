AI Traffic Control Comparison

This project simulates and compares AI-controlled traffic systems operating over wireless and wired networks. The simulation environment uses SUMO (Simulation of Urban MObility) for traffic simulation and then Pygame for visualization.

Project Overview

The goal of this project is to investigate whether AI traffic management using wireless systems can provide a more efficient alternative to traditional wired traffic control. My simulation allows for direct comparison between different control methods:

1. Traditional Controller: Uses fixed timing for traffic lights with basic adaptations based on traffic conditions
2. Wired RL Controller: Reinforcement learning controller with wired network characteristics 
3. Wireless RL Controller: Reinforcement learning controller with wireless network characteristics

  Installation

  Prerequisites

- Python 3.8 or higher
- SUMO (Simulation of Urban MObility) 1.18.0 or higher
- Pygame 2.5.0 or higher
- Required Python packages (listed in requirements.txt)

   Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd traffic_ai_comparison
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. Make sure SUMO is properly installed and accessible in your PATH.

   Usage

   Running Enhanced Visualization

To run the enhanced visualization with a specific controller:
```bash
python src/run_enhanced_visualisation.py --controller "Wired AI" --steps 1000 --delay 50
```

Options:
- `--controller`: Controller type ("Traditional", "Wired RL", "Wireless RL")
- `--steps`: Number of simulation steps to run
- `--delay`: Delay in milliseconds between steps

Running Visualization on 3x3 Grid

```bash
python src/visualise_3x3_grid.py --controller "Wired RL" --steps 1000 --delay 50
```

    Running Simulations on 3x3 Grid

```bash
python src/run_3x3_simulation.py --controller "Wired RL" --steps 1000 --gui
```

Options:
- `--controller`: Controller type to use
- `--steps`: Number of simulation steps
- `--gui`: Show SUMO GUI during simulation
- `--delay`: Delay in milliseconds (only used with GUI)

    Running Comprehensive Comparison

To compare multiple controllers across different scenarios:
```bash
python src/run_comprehensive_comparison.py --controllers "Wired RL" "Wireless RL" --scenarios light_traffic moderate_traffic heavy_traffic peak_hour_morning --steps 1000 --runs 3 --run-id RL_comparison_run
```

Options:
- `--controllers`: List of controllers to test
- `--scenarios`: List of scenarios to test (light_traffic, moderate_traffic, heavy_traffic, peak_hour_morning)
- `--steps`: Number of simulation steps per run
- `--runs`: Number of runs per configuration
- `--gui`: Flag to show visualization during comparison
- `--summary-only`: Only generate summary visualization, not detailed charts
- `--run-id`: Identifier for this comparison run
- `--output`: Directory to save results

    Simple Controller Comparison on 3x3 Grid

For a simpler comparison on just the 3x3 grid:
```bash
python src/compare_controllers_3x3.py --controllers "Traditional" "Wired RL" "Wireless RL" --steps 1000 --runs 3
```

   Generating a Report

To generate a comprehensive report from comparison results the code made:
```bash
python src/generate_report.py --results data/outputs/comparison_results/Comparison_run_id/comparison_results_timestamp.json --output data/outputs/report.md
```

Options:
- `--results`: Path to the comparison results JSON file
- `--output`: Path to save the generated report

  Training RL Controllers

To train the reinforcement learning controllers:
```bash
python src/train_rl_on_3x3.py --controller "Wired RL" --episodes 50 --steps 500
```

Options:
- `--controller`: Type of RL controller to train ("Wired RL" or "Wireless RL")
- `--episodes`: Number of training episodes
- `--steps`: Number of steps per episode
- `--lr`: Learning rate
- `--discount`: Discount factor
- `--exploration`: Initial exploration rate
- `--decay`: Exploration decay rate

  Generating Traffic Scenarios

To generate different traffic scenarios:
```bash
python src/generate_scenarios.py
```

  Project Structure

```
traffic_ai_comparison/
├── config/
│   ├── maps/               # SUMO network definitions
│   │   ├── grid_network_3x3.sumocfg
│   │   ├── traffic_grid_3x3.edg.xml
│   │   ├── traffic_grid_3x3.net.xml
│   │   ├── traffic_grid_3x3.netccfg
│   │   └── traffic_grid_3x3.nod.xml
│   └── scenarios/          # Traffic scenarios
│       ├── grid_routes_3x3.rou.xml
│       ├── heavy_traffic.rou.xml
│       ├── light_traffic.rou.xml
│       ├── moderate_traffic.rou.xml
│       ├── peak_hour_morning.rou.xml
│       └── scenario_template.rou.xml
├── data/
│   ├── models/             # Trained RL models
│   └── outputs/            # Simulation results and metrics
├── src/
│   ├── ai/
│   │   ├── controller.py
│   │   ├── controller_factory.py
│   │   ├── traditional_controller.py
│   │   ├── wired_controller.py
│   │   ├── wireless_controller.py
│   │   └── reinforcement_learning/
│   │       ├── q_learning_controller.py
│   │       ├── rl_controller.py
│   │       ├── wired_rl_controller.py
│   │       └── wireless_rl_controller.py
│   ├── simulation/
│   │   ├── scenario_runner.py
│   │   └── traffic_generator.py
│   ├── ui/
│   │   ├── enhanced_renderer.py
│   │   ├── enhanced_sumo_visualisation.py
│   │   ├── enhanced_traffic_visualiser.py
│   │   ├── enhanced_visualisation.py
│   │   └── sumo_pygame_mapper.py
│   ├── utils/
│   │   ├── config_utils.py
│   │   └── sumo_integration.py
│   ├── comparison_framework.py
│   ├── compare_controllers_3x3.py
│   ├── generate_3x3_network.py
│   ├── generate_report.py
│   ├── generate_scenarios.py
│   ├── run_3x3_simulation.py
│   ├── run_comprehensive_comparison.py
│   ├── train_rl_on_3x3.py
│   └── visualise_3x3_grid.py
├── .gitignore
├── README.md
└── requirements.txt