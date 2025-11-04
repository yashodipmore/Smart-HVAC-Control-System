#!/usr/bin/env python3
"""
Visualize HVAC System Performance
Creates performance comparison charts
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from controllers.pid_controller import PIDController
from controllers.fuzzy_controller import FuzzyController
from controllers.onoff_controller import OnOffController
from simulation.thermal_model import ThermalModel

def simulate_controller(controller, controller_name, duration=60):
    """Simulate controller performance"""
    thermal_model = ThermalModel()
    thermal_model.indoor_temp = 18.0
    thermal_model.indoor_humidity = 35.0
    
    controller.reset() if hasattr(controller, 'reset') else None
    
    temps = []
    humidities = []
    energies = []
    times = []
    
    for minute in range(duration):
        current_temp = thermal_model.indoor_temp
        current_humidity = thermal_model.indoor_humidity
        
        temp_output = controller.calculate_temperature_control(22.0, current_temp)
        humidity_output = controller.calculate_humidity_control(45.0, current_humidity)
        
        thermal_model.update(temp_output, humidity_output)
        
        temps.append(thermal_model.indoor_temp)
        humidities.append(thermal_model.indoor_humidity)
        energies.append(thermal_model.history['energy_consumption'][-1])
        times.append(minute)
    
    return times, temps, humidities, energies

def main():
    """Generate performance visualizations"""
    print("Generating HVAC System Performance Visualizations...")
    print("This may take a minute...\n")
    
    # Simulate all controllers
    print("Simulating PID Controller...")
    pid_controller = PIDController(kp=2.0, ki=0.1, kd=0.05)
    pid_data = simulate_controller(pid_controller, "PID", duration=30)
    
    print("Simulating On-Off Controller...")
    onoff_controller = OnOffController(deadband=1.0)
    onoff_data = simulate_controller(onoff_controller, "On-Off", duration=30)
    
    print("Simulating Fuzzy Logic Controller...")
    fuzzy_controller = FuzzyController()
    fuzzy_data = simulate_controller(fuzzy_controller, "Fuzzy", duration=30)
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Smart HVAC Control System - Performance Comparison', 
                 fontsize=16, fontweight='bold')
    
    # Temperature comparison
    ax1.plot(pid_data[0], pid_data[1], 'b-', linewidth=2, label='PID')
    ax1.plot(onoff_data[0], onoff_data[1], 'r--', linewidth=2, label='On-Off')
    ax1.plot(fuzzy_data[0], fuzzy_data[1], 'g-.', linewidth=2, label='Fuzzy')
    ax1.axhline(y=22, color='k', linestyle=':', alpha=0.5, label='Setpoint')
    ax1.set_xlabel('Time (minutes)')
    ax1.set_ylabel('Temperature (°C)')
    ax1.set_title('Temperature Control Performance')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Humidity comparison
    ax2.plot(pid_data[0], pid_data[2], 'b-', linewidth=2, label='PID')
    ax2.plot(onoff_data[0], onoff_data[2], 'r--', linewidth=2, label='On-Off')
    ax2.plot(fuzzy_data[0], fuzzy_data[2], 'g-.', linewidth=2, label='Fuzzy')
    ax2.axhline(y=45, color='k', linestyle=':', alpha=0.5, label='Setpoint')
    ax2.set_xlabel('Time (minutes)')
    ax2.set_ylabel('Humidity (%)')
    ax2.set_title('Humidity Control Performance')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Energy consumption
    ax3.plot(pid_data[0], np.array(pid_data[3])/1000, 'b-', linewidth=2, label='PID')
    ax3.plot(onoff_data[0], np.array(onoff_data[3])/1000, 'r--', linewidth=2, label='On-Off')
    ax3.plot(fuzzy_data[0], np.array(fuzzy_data[3])/1000, 'g-.', linewidth=2, label='Fuzzy')
    ax3.set_xlabel('Time (minutes)')
    ax3.set_ylabel('Power (kW)')
    ax3.set_title('Energy Consumption')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Energy comparison bar chart
    pid_avg = np.mean(pid_data[3])
    onoff_avg = np.mean(onoff_data[3])
    fuzzy_avg = np.mean(fuzzy_data[3])
    
    controllers = ['PID', 'On-Off', 'Fuzzy']
    energies = [pid_avg/1000, onoff_avg/1000, fuzzy_avg/1000]
    colors = ['blue', 'red', 'green']
    
    bars = ax4.bar(controllers, energies, color=colors, alpha=0.7)
    ax4.set_ylabel('Average Power (kW)')
    ax4.set_title('Average Energy Consumption Comparison')
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, energy in zip(bars, energies):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{energy:.1f} kW',
                ha='center', va='bottom', fontweight='bold')
    
    # Calculate savings
    pid_savings = ((onoff_avg - pid_avg) / onoff_avg) * 100
    fuzzy_savings = ((onoff_avg - fuzzy_avg) / onoff_avg) * 100
    
    # Add savings text
    savings_text = f'Energy Savings vs On-Off:\nPID: {pid_savings:.1f}%  |  Fuzzy: {fuzzy_savings:.1f}%'
    fig.text(0.5, 0.02, savings_text, ha='center', fontsize=12, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout(rect=[0, 0.05, 1, 0.96])
    
    # Save figure
    output_file = 'hvac_performance_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Performance visualization saved to: {output_file}")
    
    # Show plot
    plt.show()
    
    # Print summary
    print("\n" + "="*60)
    print("PERFORMANCE SUMMARY")
    print("="*60)
    print(f"\nAverage Energy Consumption:")
    print(f"  PID Controller:        {pid_avg:6.0f}W")
    print(f"  On-Off Controller:     {onoff_avg:6.0f}W")
    print(f"  Fuzzy Logic Controller: {fuzzy_avg:6.0f}W")
    print(f"\nEnergy Savings vs On-Off:")
    print(f"  PID Controller:        {pid_savings:5.1f}%")
    print(f"  Fuzzy Logic Controller: {fuzzy_savings:5.1f}%")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
