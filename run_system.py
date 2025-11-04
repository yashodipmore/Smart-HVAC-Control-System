#!/usr/bin/env python3
"""
Smart HVAC Control System - Main Runner
Starts the complete HVAC system with all components
"""

import sys
import os
import threading
import time
import signal
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from main import HVACControlSystem
from iot.dashboard import HVACDashboard
from simulation.thermal_model import ThermalModel
from utils.logger import hvac_logger

class SystemRunner:
    def __init__(self):
        """Initialize system runner"""
        self.hvac_system = None
        self.dashboard = None
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.shutdown()
    
    def start_hvac_system(self):
        """Start HVAC control system in separate thread"""
        def run_hvac():
            try:
                self.hvac_system = HVACControlSystem()
                hvac_logger.log_startup(self.hvac_system.config.get_config_dict())
                self.hvac_system.start_system()
            except Exception as e:
                hvac_logger.error(f"HVAC system error: {e}")
        
        hvac_thread = threading.Thread(target=run_hvac, daemon=True)
        hvac_thread.start()
        return hvac_thread
    
    def start_dashboard(self):
        """Start IoT dashboard in separate thread"""
        def run_dashboard():
            try:
                self.dashboard = HVACDashboard()
                self.dashboard.run(debug=False, port=8050)
            except Exception as e:
                hvac_logger.error(f"Dashboard error: {e}")
        
        dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        dashboard_thread.start()
        return dashboard_thread
    
    def run_simulation_demo(self):
        """Run a simulation demonstration"""
        print("\n" + "="*60)
        print("SMART HVAC CONTROL SYSTEM - SIMULATION DEMO")
        print("="*60)
        
        # Create thermal model for demonstration
        thermal_model = ThermalModel()
        
        print("\nRunning 10-minute simulation...")
        print("Temperature setpoint: 22°C")
        print("Humidity setpoint: 45%")
        
        # Simulate 10 minutes of operation
        for i in range(10):  # 10 iterations = 10 minutes
            # Simulate control outputs (simplified)
            temp_error = 22.0 - thermal_model.indoor_temp
            humidity_error = 45.0 - thermal_model.indoor_humidity
            
            # Simple proportional control for demo
            temp_output = temp_error * 5.0
            humidity_output = humidity_error * 2.0
            
            # Update thermal model
            thermal_model.update(temp_output, humidity_output)
            
            # Print status
            print(f"Minute {i+1:2d}: "
                  f"Temp={thermal_model.indoor_temp:.1f}°C, "
                  f"Humidity={thermal_model.indoor_humidity:.0f}%, "
                  f"Energy={thermal_model.history['energy_consumption'][-1]:.0f}W")
            
            time.sleep(1)  # 1 second per minute for demo
        
        print("\nSimulation complete!")
        print(f"Final temperature: {thermal_model.indoor_temp:.1f}°C")
        print(f"Final humidity: {thermal_model.indoor_humidity:.0f}%")
        
        # Calculate average energy consumption
        avg_energy = sum(thermal_model.history['energy_consumption']) / len(thermal_model.history['energy_consumption'])
        print(f"Average energy consumption: {avg_energy:.0f}W")
    
    def run_full_system(self):
        """Run the complete HVAC system"""
        print("\n" + "="*60)
        print("STARTING SMART HVAC CONTROL SYSTEM")
        print("="*60)
        
        self.running = True
        
        print("\n1. Starting HVAC Control System...")
        hvac_thread = self.start_hvac_system()
        time.sleep(2)
        
        print("2. Starting IoT Dashboard...")
        dashboard_thread = self.start_dashboard()
        time.sleep(2)
        
        print("\n" + "="*60)
        print("SYSTEM STARTED SUCCESSFULLY!")
        print("="*60)
        print("\nAccess points:")
        print("- IoT Dashboard: http://localhost:8050")
        print("- System logs: logs/hvac_system.log")
        print("- Configuration: config/hvac_config.json")
        print("\nPress Ctrl+C to stop the system")
        print("="*60)
        
        try:
            # Keep main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown all system components"""
        print("\nShutting down system components...")
        self.running = False
        
        if self.hvac_system:
            self.hvac_system.shutdown()
        
        hvac_logger.log_shutdown("User requested shutdown")
        print("System shutdown complete.")
        sys.exit(0)

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = "full"
    
    runner = SystemRunner()
    
    if mode == "demo":
        runner.run_simulation_demo()
    elif mode == "dashboard":
        print("Starting dashboard only...")
        runner.start_dashboard()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    elif mode == "simulation":
        runner.run_simulation_demo()
    else:
        runner.run_full_system()

if __name__ == "__main__":
    main()