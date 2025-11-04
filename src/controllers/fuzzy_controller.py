"""
Fuzzy Logic Controller for HVAC System
Implements intelligent control using fuzzy logic rules
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class FuzzyController:
    def __init__(self):
        """Initialize Fuzzy Logic Controller"""
        self._setup_fuzzy_system()
    
    def _setup_fuzzy_system(self):
        """Setup fuzzy logic system with rules and membership functions"""
        
        # Define input variables
        self.temp_error = ctrl.Antecedent(np.arange(-10, 11, 1), 'temp_error')
        self.temp_error_rate = ctrl.Antecedent(np.arange(-5, 6, 1), 'temp_error_rate')
        self.humidity_error = ctrl.Antecedent(np.arange(-20, 21, 1), 'humidity_error')
        
        # Define output variables
        self.temp_output = ctrl.Consequent(np.arange(-100, 101, 1), 'temp_output')
        self.humidity_output = ctrl.Consequent(np.arange(-100, 101, 1), 'humidity_output')
        
        # Define membership functions for temperature error
        self.temp_error['negative_large'] = fuzz.trimf(self.temp_error.universe, [-10, -10, -5])
        self.temp_error['negative_small'] = fuzz.trimf(self.temp_error.universe, [-7, -3, 0])
        self.temp_error['zero'] = fuzz.trimf(self.temp_error.universe, [-2, 0, 2])
        self.temp_error['positive_small'] = fuzz.trimf(self.temp_error.universe, [0, 3, 7])
        self.temp_error['positive_large'] = fuzz.trimf(self.temp_error.universe, [5, 10, 10])
        
        # Define membership functions for temperature error rate
        self.temp_error_rate['negative'] = fuzz.trimf(self.temp_error_rate.universe, [-5, -5, 0])
        self.temp_error_rate['zero'] = fuzz.trimf(self.temp_error_rate.universe, [-2, 0, 2])
        self.temp_error_rate['positive'] = fuzz.trimf(self.temp_error_rate.universe, [0, 5, 5])
        
        # Define membership functions for humidity error
        self.humidity_error['negative_large'] = fuzz.trimf(self.humidity_error.universe, [-20, -20, -10])
        self.humidity_error['negative_small'] = fuzz.trimf(self.humidity_error.universe, [-15, -5, 0])
        self.humidity_error['zero'] = fuzz.trimf(self.humidity_error.universe, [-5, 0, 5])
        self.humidity_error['positive_small'] = fuzz.trimf(self.humidity_error.universe, [0, 5, 15])
        self.humidity_error['positive_large'] = fuzz.trimf(self.humidity_error.universe, [10, 20, 20])
        
        # Define membership functions for temperature output
        self.temp_output['cooling_high'] = fuzz.trimf(self.temp_output.universe, [-100, -100, -50])
        self.temp_output['cooling_low'] = fuzz.trimf(self.temp_output.universe, [-70, -30, 0])
        self.temp_output['off'] = fuzz.trimf(self.temp_output.universe, [-20, 0, 20])
        self.temp_output['heating_low'] = fuzz.trimf(self.temp_output.universe, [0, 30, 70])
        self.temp_output['heating_high'] = fuzz.trimf(self.temp_output.universe, [50, 100, 100])
        
        # Define membership functions for humidity output
        self.humidity_output['dehumidify_high'] = fuzz.trimf(self.humidity_output.universe, [-100, -100, -50])
        self.humidity_output['dehumidify_low'] = fuzz.trimf(self.humidity_output.universe, [-70, -30, 0])
        self.humidity_output['off'] = fuzz.trimf(self.humidity_output.universe, [-20, 0, 20])
        self.humidity_output['humidify_low'] = fuzz.trimf(self.humidity_output.universe, [0, 30, 70])
        self.humidity_output['humidify_high'] = fuzz.trimf(self.humidity_output.universe, [50, 100, 100])
        
        # Define fuzzy rules for temperature control
        self.temp_rules = [
            ctrl.Rule(self.temp_error['negative_large'], self.temp_output['heating_high']),
            ctrl.Rule(self.temp_error['negative_small'], self.temp_output['heating_low']),
            ctrl.Rule(self.temp_error['zero'], self.temp_output['off']),
            ctrl.Rule(self.temp_error['positive_small'], self.temp_output['cooling_low']),
            ctrl.Rule(self.temp_error['positive_large'], self.temp_output['cooling_high']),
            
            # Rules considering error rate
            ctrl.Rule(self.temp_error['negative_small'] & self.temp_error_rate['positive'], 
                     self.temp_output['off']),
            ctrl.Rule(self.temp_error['positive_small'] & self.temp_error_rate['negative'], 
                     self.temp_output['off']),
        ]
        
        # Define fuzzy rules for humidity control
        self.humidity_rules = [
            ctrl.Rule(self.humidity_error['negative_large'], self.humidity_output['humidify_high']),
            ctrl.Rule(self.humidity_error['negative_small'], self.humidity_output['humidify_low']),
            ctrl.Rule(self.humidity_error['zero'], self.humidity_output['off']),
            ctrl.Rule(self.humidity_error['positive_small'], self.humidity_output['dehumidify_low']),
            ctrl.Rule(self.humidity_error['positive_large'], self.humidity_output['dehumidify_high']),
        ]
        
        # Create control systems
        self.temp_ctrl_system = ctrl.ControlSystem(self.temp_rules)
        self.humidity_ctrl_system = ctrl.ControlSystem(self.humidity_rules)
        
        # Create simulators
        self.temp_simulator = ctrl.ControlSystemSimulation(self.temp_ctrl_system)
        self.humidity_simulator = ctrl.ControlSystemSimulation(self.humidity_ctrl_system)
        
        # Store previous values for error rate calculation
        self.prev_temp_error = 0.0
        self.prev_humidity_error = 0.0
    
    def calculate_temperature_control(self, setpoint: float, current_value: float) -> float:
        """Calculate fuzzy logic output for temperature control"""
        error = setpoint - current_value
        error_rate = error - self.prev_temp_error
        self.prev_temp_error = error
        
        # Clamp inputs to universe ranges
        error = np.clip(error, -10, 10)
        error_rate = np.clip(error_rate, -5, 5)
        
        # Set inputs
        self.temp_simulator.input['temp_error'] = error
        self.temp_simulator.input['temp_error_rate'] = error_rate
        
        # Compute output
        try:
            self.temp_simulator.compute()
            output = self.temp_simulator.output['temp_output']
        except:
            # Fallback to simple proportional control if fuzzy fails
            output = error * 5.0
        
        return np.clip(output, -100, 100)
    
    def calculate_humidity_control(self, setpoint: float, current_value: float) -> float:
        """Calculate fuzzy logic output for humidity control"""
        error = setpoint - current_value
        self.prev_humidity_error = error
        
        # Clamp input to universe range
        error = np.clip(error, -20, 20)
        
        # Set input
        self.humidity_simulator.input['humidity_error'] = error
        
        # Compute output
        try:
            self.humidity_simulator.compute()
            output = self.humidity_simulator.output['humidity_output']
        except:
            # Fallback to simple proportional control if fuzzy fails
            output = error * 2.0
        
        return np.clip(output, -100, 100)
    
    def reset(self):
        """Reset controller state"""
        self.prev_temp_error = 0.0
        self.prev_humidity_error = 0.0