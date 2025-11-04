#!/usr/bin/env python3
"""
Smart HVAC Control System - Main Application
Implements intelligent HVAC control with multiple strategies
"""

import time
import logging
from datetime import datetime
from controllers.pid_controller import PIDController
from controllers.fuzzy_controller import FuzzyController
from controllers.onoff_controller import OnOffController
from sensors.sensor_manager import SensorManager
from simulation.thermal_model import ThermalModel
from iot.mqtt_client import MQTTClient
from utils.config import Config
from utils.logger import setup_logger

class HVACControlSystem:
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger('hvac_system')
        
        # Initialize components
        self.sensor_manager = SensorManager()
        self.thermal_model = ThermalModel()
        self.mqtt_client = MQTTClient()
        
        # Initialize controllers
        self.controllers = {
            'pid': PIDController(kp=2.0, ki=0.1, kd=0.05),
            'fuzzy': FuzzyController(),
            'onoff': OnOffController(deadband=1.0)
        }
        
        self.current_controller = 'pid'
        self.running = False
        
    def start_system(self):
        """Start the HVAC control system"""
        self.logger.info("Starting Smart HVAC Control System")
        self.running = True
        
        # Connect to MQTT broker
        self.mqtt_client.connect()
        
        try:
            while self.running:
                self.control_loop()
                time.sleep(self.config.control_interval)
                
        except KeyboardInterrupt:
            self.logger.info("System shutdown requested")
        finally:
            self.shutdown()
    
    def control_loop(self):
        """Main control loop"""
        # Read sensor data
        sensor_data = self.sensor_manager.read_all_sensors()
        
        # Get current conditions
        current_temp = sensor_data['temperature']
        current_humidity = sensor_data['humidity']
        setpoint_temp = self.config.temperature_setpoint
        setpoint_humidity = self.config.humidity_setpoint
        
        # Calculate control outputs
        controller = self.controllers[self.current_controller]
        
        # Temperature control
        temp_output = controller.calculate_temperature_control(
            setpoint_temp, current_temp
        )
        
        # Humidity control
        humidity_output = controller.calculate_humidity_control(
            setpoint_humidity, current_humidity
        )
        
        # Apply control outputs
        self.apply_control_outputs(temp_output, humidity_output)
        
        # Update thermal model
        self.thermal_model.update(temp_output, humidity_output)
        
        # Publish data to IoT dashboard
        self.publish_system_data(sensor_data, temp_output, humidity_output)
        
        # Log system status
        self.log_system_status(sensor_data, temp_output, humidity_output)
    
    def apply_control_outputs(self, temp_output, humidity_output):
        """Apply control outputs to HVAC equipment"""
        # Simulate HVAC equipment control
        # In real implementation, this would control actual hardware
        pass
    
    def publish_system_data(self, sensor_data, temp_output, humidity_output):
        """Publish system data to IoT dashboard"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'temperature': sensor_data['temperature'],
            'humidity': sensor_data['humidity'],
            'temp_setpoint': self.config.temperature_setpoint,
            'humidity_setpoint': self.config.humidity_setpoint,
            'temp_output': temp_output,
            'humidity_output': humidity_output,
            'controller': self.current_controller,
            'energy_consumption': self.calculate_energy_consumption(temp_output, humidity_output)
        }
        
        self.mqtt_client.publish('hvac/system_data', data)
    
    def calculate_energy_consumption(self, temp_output, humidity_output):
        """Calculate current energy consumption"""
        # Simplified energy calculation
        base_consumption = 1000  # Watts
        temp_factor = abs(temp_output) * 0.1
        humidity_factor = abs(humidity_output) * 0.05
        
        return base_consumption * (1 + temp_factor + humidity_factor)
    
    def log_system_status(self, sensor_data, temp_output, humidity_output):
        """Log current system status"""
        self.logger.info(
            f"Temp: {sensor_data['temperature']:.1f}°C "
            f"(SP: {self.config.temperature_setpoint}°C), "
            f"Humidity: {sensor_data['humidity']:.1f}% "
            f"(SP: {self.config.humidity_setpoint}%), "
            f"Controller: {self.current_controller}, "
            f"Outputs: T={temp_output:.2f}, H={humidity_output:.2f}"
        )
    
    def switch_controller(self, controller_type):
        """Switch to different control strategy"""
        if controller_type in self.controllers:
            self.current_controller = controller_type
            self.logger.info(f"Switched to {controller_type} controller")
        else:
            self.logger.error(f"Unknown controller type: {controller_type}")
    
    def shutdown(self):
        """Shutdown the system gracefully"""
        self.logger.info("Shutting down HVAC Control System")
        self.running = False
        self.mqtt_client.disconnect()

if __name__ == "__main__":
    hvac_system = HVACControlSystem()
    hvac_system.start_system()