"""
Building Thermal Dynamics Simulation
Models heat transfer and thermal behavior of building
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from typing import Dict, List, Tuple
import time

class ThermalModel:
    def __init__(self, building_params: Dict = None):
        """
        Initialize thermal model with building parameters
        
        Args:
            building_params: Dictionary containing building thermal properties
        """
        # Default building parameters (can be overridden)
        self.params = building_params or {
            'thermal_mass': 5e6,      # J/K - Building thermal mass
            'ua_envelope': 500,       # W/K - Overall heat transfer coefficient
            'ua_infiltration': 200,   # W/K - Infiltration heat transfer
            'internal_gains': 2000,   # W - Internal heat gains
            'solar_gains': 1000,      # W - Solar heat gains (variable)
            'floor_area': 1000,       # m² - Floor area
            'volume': 3000,           # m³ - Building volume
        }
        
        # State variables
        self.indoor_temp = 22.0      # °C - Indoor temperature
        self.wall_temp = 20.0        # °C - Wall temperature
        self.indoor_humidity = 45.0   # % - Indoor humidity
        
        # HVAC system parameters
        self.hvac_heating_capacity = 20000  # W
        self.hvac_cooling_capacity = 15000  # W
        self.hvac_efficiency = 0.9
        
        # Environmental conditions
        self.outdoor_temp = 15.0     # °C
        self.outdoor_humidity = 60.0  # %
        
        # Simulation parameters
        self.dt = 60.0  # Time step in seconds
        self.time = 0.0
        
        # Data logging
        self.history = {
            'time': [],
            'indoor_temp': [],
            'wall_temp': [],
            'indoor_humidity': [],
            'outdoor_temp': [],
            'hvac_heating': [],
            'hvac_cooling': [],
            'energy_consumption': []
        }
    
    def update(self, temp_control_output: float, humidity_control_output: float):
        """
        Update thermal model with control outputs
        
        Args:
            temp_control_output: Temperature control output (-100 to 100)
            humidity_control_output: Humidity control output (-100 to 100)
        """
        # Update outdoor conditions (simulate daily variation)
        self._update_outdoor_conditions()
        
        # Calculate HVAC loads
        hvac_heating = max(0, temp_control_output) / 100.0 * self.hvac_heating_capacity
        hvac_cooling = max(0, -temp_control_output) / 100.0 * self.hvac_cooling_capacity
        
        # Solve thermal differential equations
        self._solve_thermal_dynamics(hvac_heating, hvac_cooling)
        
        # Update humidity
        self._update_humidity(humidity_control_output)
        
        # Calculate energy consumption
        energy_consumption = self._calculate_energy_consumption(hvac_heating, hvac_cooling)
        
        # Log data
        self._log_data(hvac_heating, hvac_cooling, energy_consumption)
        
        # Update time
        self.time += self.dt
    
    def _update_outdoor_conditions(self):
        """Update outdoor temperature and humidity with daily variation"""
        # Daily temperature variation
        hour_of_day = (self.time % 86400) / 3600  # Hours since midnight
        daily_temp_variation = 8 * np.sin(2 * np.pi * (hour_of_day - 6) / 24)
        
        # Seasonal variation (simplified)
        day_of_year = (self.time % (365 * 86400)) / 86400
        seasonal_variation = 10 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        self.outdoor_temp = 15.0 + daily_temp_variation + seasonal_variation
        
        # Humidity inversely related to temperature
        self.outdoor_humidity = 70 - 0.5 * (self.outdoor_temp - 15)
        self.outdoor_humidity = np.clip(self.outdoor_humidity, 20, 90)
    
    def _solve_thermal_dynamics(self, hvac_heating: float, hvac_cooling: float):
        """Solve thermal dynamics using differential equations"""
        
        def thermal_ode(state, t):
            """Thermal dynamics ODE system"""
            T_indoor, T_wall = state
            
            # Heat transfer rates
            Q_envelope = self.params['ua_envelope'] * (self.outdoor_temp - T_indoor)
            Q_infiltration = self.params['ua_infiltration'] * (self.outdoor_temp - T_indoor)
            Q_internal = self.params['internal_gains']
            Q_solar = self._calculate_solar_gains()
            Q_hvac = (hvac_heating - hvac_cooling) * self.hvac_efficiency
            
            # Wall thermal dynamics
            Q_wall_storage = 0.3 * self.params['thermal_mass'] * (T_indoor - T_wall) / 3600
            
            # Indoor temperature rate of change
            dT_indoor_dt = (Q_envelope + Q_infiltration + Q_internal + 
                           Q_solar + Q_hvac - Q_wall_storage) / (0.7 * self.params['thermal_mass'])
            
            # Wall temperature rate of change
            dT_wall_dt = Q_wall_storage / (0.3 * self.params['thermal_mass'])
            
            return [dT_indoor_dt, dT_wall_dt]
        
        # Solve ODE for one time step
        t_span = [0, self.dt]
        initial_state = [self.indoor_temp, self.wall_temp]
        
        solution = odeint(thermal_ode, initial_state, t_span)
        
        # Update state variables
        self.indoor_temp = solution[-1, 0]
        self.wall_temp = solution[-1, 1]
    
    def _calculate_solar_gains(self) -> float:
        """Calculate solar heat gains based on time of day"""
        hour_of_day = (self.time % 86400) / 3600
        
        # Solar gains peak at noon, zero at night
        if 6 <= hour_of_day <= 18:
            solar_factor = np.sin(np.pi * (hour_of_day - 6) / 12)
            return self.params['solar_gains'] * solar_factor
        else:
            return 0.0
    
    def _update_humidity(self, humidity_control_output: float):
        """Update indoor humidity based on control output and physics"""
        # Moisture sources and sinks
        moisture_generation = 2.0  # kg/h - Internal moisture generation
        
        # Infiltration moisture exchange
        moisture_infiltration = (self.params['ua_infiltration'] / 1000) * \
                               (self.outdoor_humidity - self.indoor_humidity) * 0.01
        
        # HVAC moisture control
        if humidity_control_output > 0:  # Humidifying
            moisture_hvac = humidity_control_output / 100.0 * 5.0  # kg/h
        else:  # Dehumidifying
            moisture_hvac = humidity_control_output / 100.0 * 3.0  # kg/h
        
        # Update humidity
        total_moisture_change = (moisture_generation + moisture_infiltration + moisture_hvac) * self.dt / 3600
        
        # Convert to humidity change (simplified)
        humidity_change = total_moisture_change * 1000 / self.params['volume']  # Rough conversion
        
        self.indoor_humidity += humidity_change
        self.indoor_humidity = np.clip(self.indoor_humidity, 20, 80)
    
    def _calculate_energy_consumption(self, hvac_heating: float, hvac_cooling: float) -> float:
        """Calculate total energy consumption"""
        # HVAC energy consumption
        heating_energy = hvac_heating / self.hvac_efficiency  # Account for efficiency
        cooling_energy = hvac_cooling / 2.5  # COP of 2.5 for cooling
        
        # Fan energy (simplified)
        fan_energy = 500 if (hvac_heating > 0 or hvac_cooling > 0) else 100
        
        total_energy = heating_energy + cooling_energy + fan_energy  # Watts
        
        return total_energy
    
    def _log_data(self, hvac_heating: float, hvac_cooling: float, energy_consumption: float):
        """Log simulation data"""
        self.history['time'].append(self.time)
        self.history['indoor_temp'].append(self.indoor_temp)
        self.history['wall_temp'].append(self.wall_temp)
        self.history['indoor_humidity'].append(self.indoor_humidity)
        self.history['outdoor_temp'].append(self.outdoor_temp)
        self.history['hvac_heating'].append(hvac_heating)
        self.history['hvac_cooling'].append(hvac_cooling)
        self.history['energy_consumption'].append(energy_consumption)
        
        # Limit history length
        max_history = 1440  # 24 hours at 1-minute intervals
        for key in self.history:
            if len(self.history[key]) > max_history:
                self.history[key].pop(0)
    
    def get_current_state(self) -> Dict:
        """Get current thermal state"""
        return {
            'indoor_temperature': self.indoor_temp,
            'wall_temperature': self.wall_temp,
            'indoor_humidity': self.indoor_humidity,
            'outdoor_temperature': self.outdoor_temp,
            'outdoor_humidity': self.outdoor_humidity,
            'time': self.time
        }
    
    def plot_results(self, hours: int = 24):
        """Plot simulation results"""
        if not self.history['time']:
            print("No data to plot")
            return
        
        # Convert time to hours
        time_hours = np.array(self.history['time']) / 3600
        
        # Limit to recent data
        if len(time_hours) > hours * 60:
            start_idx = -hours * 60
            time_hours = time_hours[start_idx:]
            indoor_temp = self.history['indoor_temp'][start_idx:]
            outdoor_temp = self.history['outdoor_temp'][start_idx:]
            humidity = self.history['indoor_humidity'][start_idx:]
            energy = self.history['energy_consumption'][start_idx:]
        else:
            indoor_temp = self.history['indoor_temp']
            outdoor_temp = self.history['outdoor_temp']
            humidity = self.history['indoor_humidity']
            energy = self.history['energy_consumption']
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # Temperature plot
        ax1.plot(time_hours, indoor_temp, label='Indoor', linewidth=2)
        ax1.plot(time_hours, outdoor_temp, label='Outdoor', linewidth=2)
        ax1.set_ylabel('Temperature (°C)')
        ax1.set_title('Temperature Profile')
        ax1.legend()
        ax1.grid(True)
        
        # Humidity plot
        ax2.plot(time_hours, humidity, 'g-', linewidth=2)
        ax2.set_ylabel('Humidity (%)')
        ax2.set_title('Indoor Humidity')
        ax2.grid(True)
        
        # Energy consumption
        ax3.plot(time_hours, np.array(energy) / 1000, 'r-', linewidth=2)
        ax3.set_ylabel('Energy (kW)')
        ax3.set_xlabel('Time (hours)')
        ax3.set_title('Energy Consumption')
        ax3.grid(True)
        
        # HVAC operation
        heating = np.array(self.history['hvac_heating'][-len(time_hours):]) / 1000
        cooling = np.array(self.history['hvac_cooling'][-len(time_hours):]) / 1000
        ax4.plot(time_hours, heating, 'r-', label='Heating', linewidth=2)
        ax4.plot(time_hours, -cooling, 'b-', label='Cooling', linewidth=2)
        ax4.set_ylabel('HVAC Load (kW)')
        ax4.set_xlabel('Time (hours)')
        ax4.set_title('HVAC Operation')
        ax4.legend()
        ax4.grid(True)
        
        plt.tight_layout()
        plt.show()
    
    def reset(self):
        """Reset simulation to initial conditions"""
        self.indoor_temp = 22.0
        self.wall_temp = 20.0
        self.indoor_humidity = 45.0
        self.time = 0.0
        
        # Clear history
        for key in self.history:
            self.history[key].clear()