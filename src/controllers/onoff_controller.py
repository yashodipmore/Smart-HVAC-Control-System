"""
On-Off (Bang-Bang) Controller for HVAC System
Simple two-position control with deadband
"""

class OnOffController:
    def __init__(self, deadband: float = 1.0):
        """
        Initialize On-Off Controller
        
        Args:
            deadband: Deadband around setpoint to prevent oscillation
        """
        self.deadband = deadband
        
        # State tracking for hysteresis
        self.temp_state = 'off'  # 'heating', 'cooling', 'off'
        self.humidity_state = 'off'  # 'humidifying', 'dehumidifying', 'off'
    
    def calculate_temperature_control(self, setpoint: float, current_value: float) -> float:
        """
        Calculate on-off output for temperature control
        
        Args:
            setpoint: Desired temperature
            current_value: Current temperature
            
        Returns:
            Control output: 100 (heating), -100 (cooling), 0 (off)
        """
        error = setpoint - current_value
        
        # Implement hysteresis to prevent rapid switching
        if self.temp_state == 'off':
            if error > self.deadband:
                self.temp_state = 'heating'
                return 100.0
            elif error < -self.deadband:
                self.temp_state = 'cooling'
                return -100.0
            else:
                return 0.0
        
        elif self.temp_state == 'heating':
            if error < -self.deadband / 2:  # Smaller deadband for switching off
                self.temp_state = 'off'
                return 0.0
            elif error < -self.deadband:
                self.temp_state = 'cooling'
                return -100.0
            else:
                return 100.0
        
        elif self.temp_state == 'cooling':
            if error > self.deadband / 2:  # Smaller deadband for switching off
                self.temp_state = 'off'
                return 0.0
            elif error > self.deadband:
                self.temp_state = 'heating'
                return 100.0
            else:
                return -100.0
        
        return 0.0
    
    def calculate_humidity_control(self, setpoint: float, current_value: float) -> float:
        """
        Calculate on-off output for humidity control
        
        Args:
            setpoint: Desired humidity
            current_value: Current humidity
            
        Returns:
            Control output: 100 (humidifying), -100 (dehumidifying), 0 (off)
        """
        error = setpoint - current_value
        
        # Use larger deadband for humidity (typically less critical)
        humidity_deadband = self.deadband * 2
        
        # Implement hysteresis to prevent rapid switching
        if self.humidity_state == 'off':
            if error > humidity_deadband:
                self.humidity_state = 'humidifying'
                return 100.0
            elif error < -humidity_deadband:
                self.humidity_state = 'dehumidifying'
                return -100.0
            else:
                return 0.0
        
        elif self.humidity_state == 'humidifying':
            if error < -humidity_deadband / 2:
                self.humidity_state = 'off'
                return 0.0
            elif error < -humidity_deadband:
                self.humidity_state = 'dehumidifying'
                return -100.0
            else:
                return 100.0
        
        elif self.humidity_state == 'dehumidifying':
            if error > humidity_deadband / 2:
                self.humidity_state = 'off'
                return 0.0
            elif error > humidity_deadband:
                self.humidity_state = 'humidifying'
                return 100.0
            else:
                return -100.0
        
        return 0.0
    
    def reset(self):
        """Reset controller state"""
        self.temp_state = 'off'
        self.humidity_state = 'off'
    
    def set_deadband(self, deadband: float):
        """Update deadband value"""
        self.deadband = deadband
    
    def get_state(self) -> dict:
        """Get current controller state"""
        return {
            'temp_state': self.temp_state,
            'humidity_state': self.humidity_state,
            'deadband': self.deadband
        }