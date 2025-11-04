"""
Logging utilities for HVAC System
Provides structured logging with different levels and outputs
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

def setup_logger(name: str, log_file: Optional[str] = None, 
                level: str = "INFO", max_bytes: int = 10*1024*1024,
                backup_count: int = 5) -> logging.Logger:
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name
        log_file: Log file path (optional)
        level: Logging level
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file specified)
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

class HVACLogger:
    """Enhanced logger for HVAC system with structured logging"""
    
    def __init__(self, name: str = "hvac_system"):
        """Initialize HVAC logger"""
        self.logger = setup_logger(
            name=name,
            log_file=f"logs/{name}.log",
            level="INFO"
        )
        
        # Performance logger for metrics
        self.perf_logger = setup_logger(
            name=f"{name}_performance",
            log_file=f"logs/{name}_performance.log",
            level="INFO"
        )
        
        # Error logger for critical issues
        self.error_logger = setup_logger(
            name=f"{name}_errors",
            log_file=f"logs/{name}_errors.log",
            level="ERROR"
        )
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context"""
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context"""
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self.logger.warning(message)
    
    def error(self, message: str, **kwargs):
        """Log error message with optional context"""
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self.logger.error(message)
        self.error_logger.error(message)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with optional context"""
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self.logger.critical(message)
        self.error_logger.critical(message)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context"""
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self.logger.debug(message)
    
    def log_system_state(self, temperature: float, humidity: float, 
                        setpoint_temp: float, setpoint_humidity: float,
                        controller: str, energy_consumption: float):
        """Log current system state"""
        self.info(
            "System State",
            temperature=temperature,
            humidity=humidity,
            setpoint_temp=setpoint_temp,
            setpoint_humidity=setpoint_humidity,
            controller=controller,
            energy_consumption=energy_consumption
        )
    
    def log_control_action(self, controller: str, temp_output: float, 
                          humidity_output: float, temp_error: float,
                          humidity_error: float):
        """Log control action"""
        self.info(
            "Control Action",
            controller=controller,
            temp_output=temp_output,
            humidity_output=humidity_output,
            temp_error=temp_error,
            humidity_error=humidity_error
        )
    
    def log_performance_metrics(self, energy_consumption: float,
                               temp_stability: float, humidity_stability: float,
                               response_time: float):
        """Log performance metrics"""
        self.perf_logger.info(
            f"Performance Metrics | "
            f"Energy: {energy_consumption:.1f}W | "
            f"Temp Stability: {temp_stability:.2f}°C | "
            f"Humidity Stability: {humidity_stability:.1f}% | "
            f"Response Time: {response_time:.1f}s"
        )
    
    def log_sensor_fault(self, sensor_id: str, fault_type: str, value: float = None):
        """Log sensor fault"""
        self.error(
            "Sensor Fault Detected",
            sensor_id=sensor_id,
            fault_type=fault_type,
            value=value
        )
    
    def log_controller_switch(self, old_controller: str, new_controller: str, reason: str = None):
        """Log controller switch"""
        self.info(
            "Controller Switch",
            old_controller=old_controller,
            new_controller=new_controller,
            reason=reason
        )
    
    def log_energy_optimization(self, action: str, energy_saved: float = None):
        """Log energy optimization actions"""
        self.info(
            "Energy Optimization",
            action=action,
            energy_saved=energy_saved
        )
    
    def log_alert(self, alert_type: str, message: str, severity: str = "info"):
        """Log system alert"""
        log_method = getattr(self.logger, severity.lower(), self.logger.info)
        log_method(f"ALERT [{alert_type}]: {message}")
    
    def log_startup(self, config: dict):
        """Log system startup"""
        self.info("HVAC System Starting", config=config)
    
    def log_shutdown(self, reason: str = "Normal shutdown"):
        """Log system shutdown"""
        self.info("HVAC System Shutdown", reason=reason)

# Global logger instance
hvac_logger = HVACLogger()

# Convenience functions
def log_info(message: str, **kwargs):
    """Log info message"""
    hvac_logger.info(message, **kwargs)

def log_warning(message: str, **kwargs):
    """Log warning message"""
    hvac_logger.warning(message, **kwargs)

def log_error(message: str, **kwargs):
    """Log error message"""
    hvac_logger.error(message, **kwargs)

def log_debug(message: str, **kwargs):
    """Log debug message"""
    hvac_logger.debug(message, **kwargs)