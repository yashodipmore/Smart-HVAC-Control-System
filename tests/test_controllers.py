"""
Unit tests for HVAC controllers
"""

import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from controllers.pid_controller import PIDController
from controllers.fuzzy_controller import FuzzyController
from controllers.onoff_controller import OnOffController

class TestPIDController(unittest.TestCase):
    def setUp(self):
        self.controller = PIDController(kp=2.0, ki=0.1, kd=0.05)
    
    def test_initialization(self):
        """Test PID controller initialization"""
        self.assertEqual(self.controller.kp, 2.0)
        self.assertEqual(self.controller.ki, 0.1)
        self.assertEqual(self.controller.kd, 0.05)
    
    def test_temperature_control(self):
        """Test temperature control output"""
        # Test heating scenario
        output = self.controller.calculate_temperature_control(25.0, 20.0)
        self.assertGreater(output, 0)  # Should be positive for heating
        
        # Test cooling scenario
        output = self.controller.calculate_temperature_control(20.0, 25.0)
        self.assertLess(output, 0)  # Should be negative for cooling
        
        # Test at setpoint
        output = self.controller.calculate_temperature_control(22.0, 22.0)
        self.assertEqual(output, 0.0)  # Should be zero at setpoint
    
    def test_humidity_control(self):
        """Test humidity control output"""
        # Test humidifying scenario
        output = self.controller.calculate_humidity_control(50.0, 40.0)
        self.assertGreater(output, 0)  # Should be positive for humidifying
        
        # Test dehumidifying scenario
        output = self.controller.calculate_humidity_control(40.0, 50.0)
        self.assertLess(output, 0)  # Should be negative for dehumidifying
    
    def test_output_limits(self):
        """Test output limits"""
        # Test extreme error
        output = self.controller.calculate_temperature_control(50.0, 0.0)
        self.assertLessEqual(abs(output), 100)  # Should be within limits
    
    def test_reset(self):
        """Test controller reset"""
        # Generate some output first
        self.controller.calculate_temperature_control(25.0, 20.0)
        
        # Reset and test
        self.controller.reset()
        output = self.controller.calculate_temperature_control(22.0, 22.0)
        self.assertEqual(output, 0.0)

class TestOnOffController(unittest.TestCase):
    def setUp(self):
        self.controller = OnOffController(deadband=1.0)
    
    def test_initialization(self):
        """Test On-Off controller initialization"""
        self.assertEqual(self.controller.deadband, 1.0)
        self.assertEqual(self.controller.temp_state, 'off')
        self.assertEqual(self.controller.humidity_state, 'off')
    
    def test_temperature_control(self):
        """Test temperature control with hysteresis"""
        # Test heating activation
        output = self.controller.calculate_temperature_control(25.0, 20.0)
        self.assertEqual(output, 100.0)  # Should be full heating
        self.assertEqual(self.controller.temp_state, 'heating')
        
        # Test cooling activation
        self.controller.reset()
        output = self.controller.calculate_temperature_control(20.0, 25.0)
        self.assertEqual(output, -100.0)  # Should be full cooling
        self.assertEqual(self.controller.temp_state, 'cooling')
    
    def test_deadband_behavior(self):
        """Test deadband prevents oscillation"""
        # Start in off state
        output = self.controller.calculate_temperature_control(22.0, 22.5)
        self.assertEqual(output, 0.0)  # Should stay off within deadband
        
        # Exceed deadband
        output = self.controller.calculate_temperature_control(22.0, 20.5)
        self.assertEqual(output, 100.0)  # Should turn on heating
    
    def test_hysteresis(self):
        """Test hysteresis behavior"""
        # Activate heating
        self.controller.calculate_temperature_control(25.0, 20.0)
        self.assertEqual(self.controller.temp_state, 'heating')
        
        # Small change shouldn't switch off
        output = self.controller.calculate_temperature_control(25.0, 24.0)
        self.assertEqual(output, 100.0)  # Should stay heating
        self.assertEqual(self.controller.temp_state, 'heating')

class TestFuzzyController(unittest.TestCase):
    def setUp(self):
        self.controller = FuzzyController()
    
    def test_initialization(self):
        """Test Fuzzy controller initialization"""
        self.assertIsNotNone(self.controller.temp_simulator)
        self.assertIsNotNone(self.controller.humidity_simulator)
    
    def test_temperature_control(self):
        """Test fuzzy temperature control"""
        # Test heating scenario
        output = self.controller.calculate_temperature_control(25.0, 20.0)
        self.assertGreater(output, 0)  # Should be positive for heating
        
        # Test cooling scenario
        output = self.controller.calculate_temperature_control(20.0, 25.0)
        self.assertLess(output, 0)  # Should be negative for cooling
    
    def test_humidity_control(self):
        """Test fuzzy humidity control"""
        # Test humidifying scenario
        output = self.controller.calculate_humidity_control(50.0, 40.0)
        self.assertGreater(output, 0)  # Should be positive for humidifying
        
        # Test dehumidifying scenario
        output = self.controller.calculate_humidity_control(40.0, 50.0)
        self.assertLess(output, 0)  # Should be negative for dehumidifying
    
    def test_output_bounds(self):
        """Test output is within bounds"""
        output = self.controller.calculate_temperature_control(50.0, 0.0)
        self.assertGreaterEqual(output, -100)
        self.assertLessEqual(output, 100)

if __name__ == '__main__':
    unittest.main()