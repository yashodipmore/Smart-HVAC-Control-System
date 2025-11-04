"""
PID Controller Implementation for HVAC System
Provides precise temperature and humidity control
"""

import time
from typing import Optional

class PIDController:
    def __init__(self, kp: float = 1.0, ki: float = 0.0, kd: float = 0.0, 
                 output_limits: tuple = (-100, 100)):
        """
        Initialize PID Controller
        
        Args:
            kp: Proportional gain
            ki: Integral gain  
            kd: Derivative gain
            output_limits: Min and max output values
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_limits = output_limits
        
        # Internal state variables
        self._last_error = 0.0
        self._integral = 0.0
        self._last_time = None
        
        # Separate PID states for temperature and humidity
        self._temp_state = {'last_error': 0.0, 'integral': 0.0, 'last_time': None}
        self._humidity_state = {'last_error': 0.0, 'integral': 0.0, 'last_time': None}
    
    def calculate_temperature_control(self, setpoint: float, current_value: float) -> float:
        """Calculate PID output for temperature control"""
        return self._calculate_pid_output(setpoint, current_value, self._temp_state)
    
    def calculate_humidity_control(self, setpoint: float, current_value: float) -> float:
        """Calculate PID output for humidity control"""
        return self._calculate_pid_output(setpoint, current_value, self._humidity_state)
    
    def _calculate_pid_output(self, setpoint: float, current_value: float, state: dict) -> float:
        """Internal PID calculation method"""
        current_time = time.time()
        
        # Calculate error
        error = setpoint - current_value
        
        # Initialize time if first run
        if state['last_time'] is None:
            state['last_time'] = current_time
            state['last_error'] = error
            return 0.0
        
        # Calculate time delta
        dt = current_time - state['last_time']
        if dt <= 0.0:
            return 0.0
        
        # Proportional term
        proportional = self.kp * error
        
        # Integral term with windup protection
        state['integral'] += error * dt
        # Prevent integral windup
        if state['integral'] > self.output_limits[1] / self.ki if self.ki != 0 else float('inf'):
            state['integral'] = self.output_limits[1] / self.ki if self.ki != 0 else 0
        elif state['integral'] < self.output_limits[0] / self.ki if self.ki != 0 else float('-inf'):
            state['integral'] = self.output_limits[0] / self.ki if self.ki != 0 else 0
        
        integral = self.ki * state['integral']
        
        # Derivative term
        derivative = self.kd * (error - state['last_error']) / dt
        
        # Calculate total output
        output = proportional + integral + derivative
        
        # Apply output limits
        output = max(min(output, self.output_limits[1]), self.output_limits[0])
        
        # Update state for next iteration
        state['last_error'] = error
        state['last_time'] = current_time
        
        return output
    
    def reset(self):
        """Reset PID controller state"""
        self._temp_state = {'last_error': 0.0, 'integral': 0.0, 'last_time': None}
        self._humidity_state = {'last_error': 0.0, 'integral': 0.0, 'last_time': None}
    
    def tune_parameters(self, kp: float, ki: float, kd: float):
        """Update PID parameters"""
        self.kp = kp
        self.ki = ki
        self.kd = kd
    
    def get_parameters(self) -> dict:
        """Get current PID parameters"""
        return {
            'kp': self.kp,
            'ki': self.ki,
            'kd': self.kd,
            'output_limits': self.output_limits
        }