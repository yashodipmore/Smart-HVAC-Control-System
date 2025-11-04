"""
Configuration Management for HVAC System
Handles system configuration and settings
"""

import os
import json
from typing import Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class HVACConfig:
    """HVAC System Configuration"""
    # Control parameters
    temperature_setpoint: float = 22.0
    humidity_setpoint: float = 45.0
    control_interval: float = 60.0  # seconds
    
    # Controller parameters
    pid_kp: float = 2.0
    pid_ki: float = 0.1
    pid_kd: float = 0.05
    
    # System limits
    min_temperature: float = 18.0
    max_temperature: float = 28.0
    min_humidity: float = 30.0
    max_humidity: float = 70.0
    
    # MQTT settings
    mqtt_broker: str = "localhost"
    mqtt_port: int = 1883
    mqtt_username: str = ""
    mqtt_password: str = ""
    
    # Dashboard settings
    dashboard_port: int = 8050
    dashboard_debug: bool = False
    
    # Logging settings
    log_level: str = "INFO"
    log_file: str = "hvac_system.log"
    
    # Energy optimization
    energy_optimization_enabled: bool = True
    peak_hours_start: int = 9  # 9 AM
    peak_hours_end: int = 17   # 5 PM
    energy_saving_mode: bool = False
    
    # Fault detection
    fault_detection_enabled: bool = True
    sensor_timeout: float = 300.0  # seconds
    max_temp_deviation: float = 5.0  # °C
    max_humidity_deviation: float = 15.0  # %
    
    # Building parameters
    building_thermal_mass: float = 5e6  # J/K
    building_ua_envelope: float = 500   # W/K
    building_floor_area: float = 1000   # m²

class Config:
    """Configuration manager for HVAC system"""
    
    def __init__(self, config_file: str = "config/hvac_config.json"):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = Path(config_file)
        self.config = HVACConfig()
        
        # Create config directory if it doesn't exist
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Update config with loaded data
                for key, value in config_data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                
                print(f"Configuration loaded from {self.config_file}")
                
            except Exception as e:
                print(f"Error loading configuration: {e}")
                print("Using default configuration")
        else:
            # Save default configuration
            self.save_config()
            print(f"Default configuration saved to {self.config_file}")
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            config_dict = asdict(self.config)
            
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=4)
            
            print(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def update_config(self, **kwargs):
        """
        Update configuration parameters
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                print(f"Updated {key} = {value}")
            else:
                print(f"Unknown configuration parameter: {key}")
        
        # Save updated configuration
        self.save_config()
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return asdict(self.config)
    
    def validate_config(self) -> bool:
        """Validate configuration parameters"""
        valid = True
        
        # Temperature validation
        if not (self.config.min_temperature <= self.config.temperature_setpoint <= self.config.max_temperature):
            print(f"Invalid temperature setpoint: {self.config.temperature_setpoint}")
            valid = False
        
        # Humidity validation
        if not (self.config.min_humidity <= self.config.humidity_setpoint <= self.config.max_humidity):
            print(f"Invalid humidity setpoint: {self.config.humidity_setpoint}")
            valid = False
        
        # Control interval validation
        if self.config.control_interval <= 0:
            print(f"Invalid control interval: {self.config.control_interval}")
            valid = False
        
        # PID parameters validation
        if self.config.pid_kp < 0 or self.config.pid_ki < 0 or self.config.pid_kd < 0:
            print("Invalid PID parameters (must be non-negative)")
            valid = False
        
        return valid
    
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.config = HVACConfig()
        self.save_config()
        print("Configuration reset to defaults")
    
    # Property accessors for common parameters
    @property
    def temperature_setpoint(self) -> float:
        return self.config.temperature_setpoint
    
    @temperature_setpoint.setter
    def temperature_setpoint(self, value: float):
        if self.config.min_temperature <= value <= self.config.max_temperature:
            self.config.temperature_setpoint = value
            self.save_config()
        else:
            raise ValueError(f"Temperature setpoint must be between {self.config.min_temperature} and {self.config.max_temperature}")
    
    @property
    def humidity_setpoint(self) -> float:
        return self.config.humidity_setpoint
    
    @humidity_setpoint.setter
    def humidity_setpoint(self, value: float):
        if self.config.min_humidity <= value <= self.config.max_humidity:
            self.config.humidity_setpoint = value
            self.save_config()
        else:
            raise ValueError(f"Humidity setpoint must be between {self.config.min_humidity} and {self.config.max_humidity}")
    
    @property
    def control_interval(self) -> float:
        return self.config.control_interval
    
    @property
    def pid_parameters(self) -> Dict[str, float]:
        return {
            'kp': self.config.pid_kp,
            'ki': self.config.pid_ki,
            'kd': self.config.pid_kd
        }
    
    def update_pid_parameters(self, kp: float = None, ki: float = None, kd: float = None):
        """Update PID controller parameters"""
        if kp is not None and kp >= 0:
            self.config.pid_kp = kp
        if ki is not None and ki >= 0:
            self.config.pid_ki = ki
        if kd is not None and kd >= 0:
            self.config.pid_kd = kd
        
        self.save_config()
    
    def get_energy_schedule(self) -> Dict[str, Any]:
        """Get energy optimization schedule"""
        return {
            'optimization_enabled': self.config.energy_optimization_enabled,
            'peak_hours_start': self.config.peak_hours_start,
            'peak_hours_end': self.config.peak_hours_end,
            'energy_saving_mode': self.config.energy_saving_mode
        }
    
    def is_peak_hours(self, hour: int) -> bool:
        """Check if given hour is during peak hours"""
        return self.config.peak_hours_start <= hour <= self.config.peak_hours_end