"""
Sensor Manager for HVAC System
Handles temperature, humidity, and other sensor readings
"""

import random
import time
import numpy as np
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class SensorReading:
    """Data class for sensor readings"""
    timestamp: float
    value: float
    sensor_id: str
    sensor_type: str
    status: str = 'ok'

class SensorManager:
    def __init__(self):
        """Initialize sensor manager"""
        self.sensors = {
            'temp_zone1': {'type': 'temperature', 'location': 'Zone 1', 'calibration': 0.0},
            'temp_zone2': {'type': 'temperature', 'location': 'Zone 2', 'calibration': 0.1},
            'temp_outdoor': {'type': 'temperature', 'location': 'Outdoor', 'calibration': -0.2},
            'humidity_zone1': {'type': 'humidity', 'location': 'Zone 1', 'calibration': 0.0},
            'humidity_zone2': {'type': 'humidity', 'location': 'Zone 2', 'calibration': 1.0},
            'pressure': {'type': 'pressure', 'location': 'Main', 'calibration': 0.0},
            'co2_zone1': {'type': 'co2', 'location': 'Zone 1', 'calibration': 0.0},
        }
        
        # Simulation parameters for realistic sensor data
        self.base_temp = 22.0  # Base temperature in Celsius
        self.base_humidity = 45.0  # Base humidity in %
        self.base_pressure = 1013.25  # Base pressure in hPa
        self.base_co2 = 400.0  # Base CO2 in ppm
        
        # Noise parameters
        self.temp_noise = 0.1
        self.humidity_noise = 1.0
        self.pressure_noise = 0.5
        self.co2_noise = 10.0
        
        # Sensor history for fault detection
        self.sensor_history = {sensor_id: [] for sensor_id in self.sensors.keys()}
        self.max_history_length = 100
        
    def read_all_sensors(self) -> Dict[str, float]:
        """Read all sensors and return averaged values by type"""
        readings = {}
        
        # Read individual sensors
        for sensor_id, sensor_info in self.sensors.items():
            reading = self._read_sensor(sensor_id, sensor_info)
            self._store_reading(sensor_id, reading)
        
        # Calculate averaged values for control
        readings['temperature'] = self._get_average_reading('temperature')
        readings['humidity'] = self._get_average_reading('humidity')
        readings['pressure'] = self._get_average_reading('pressure')
        readings['co2'] = self._get_average_reading('co2')
        readings['outdoor_temp'] = self._get_sensor_reading('temp_outdoor')
        
        return readings
    
    def _read_sensor(self, sensor_id: str, sensor_info: dict) -> SensorReading:
        """Read individual sensor with simulation"""
        current_time = time.time()
        sensor_type = sensor_info['type']
        
        # Simulate sensor readings based on type
        if sensor_type == 'temperature':
            # Add daily temperature variation
            daily_variation = 3 * np.sin(2 * np.pi * (current_time % 86400) / 86400)
            if 'outdoor' in sensor_id:
                base_value = self.base_temp + daily_variation + random.uniform(-5, 5)
            else:
                base_value = self.base_temp + daily_variation * 0.3
            
            noise = random.gauss(0, self.temp_noise)
            value = base_value + sensor_info['calibration'] + noise
            
        elif sensor_type == 'humidity':
            # Humidity inversely related to temperature
            temp_effect = -0.5 * (self._get_current_temp() - self.base_temp)
            base_value = self.base_humidity + temp_effect
            noise = random.gauss(0, self.humidity_noise)
            value = max(0, min(100, base_value + sensor_info['calibration'] + noise))
            
        elif sensor_type == 'pressure':
            # Slight pressure variations
            base_value = self.base_pressure
            noise = random.gauss(0, self.pressure_noise)
            value = base_value + sensor_info['calibration'] + noise
            
        elif sensor_type == 'co2':
            # CO2 variations based on occupancy simulation
            occupancy_factor = 1 + 0.5 * np.sin(2 * np.pi * (current_time % 86400) / 86400)
            base_value = self.base_co2 * occupancy_factor
            noise = random.gauss(0, self.co2_noise)
            value = max(300, base_value + sensor_info['calibration'] + noise)
        
        else:
            value = 0.0
        
        # Simulate occasional sensor faults
        status = 'ok'
        if random.random() < 0.001:  # 0.1% chance of fault
            status = 'fault'
            value = float('nan')
        
        return SensorReading(
            timestamp=current_time,
            value=value,
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            status=status
        )
    
    def _store_reading(self, sensor_id: str, reading: SensorReading):
        """Store sensor reading in history"""
        self.sensor_history[sensor_id].append(reading)
        
        # Limit history length
        if len(self.sensor_history[sensor_id]) > self.max_history_length:
            self.sensor_history[sensor_id].pop(0)
    
    def _get_average_reading(self, sensor_type: str) -> float:
        """Get average reading for sensors of specific type"""
        values = []
        
        for sensor_id, sensor_info in self.sensors.items():
            if sensor_info['type'] == sensor_type and 'outdoor' not in sensor_id:
                if self.sensor_history[sensor_id]:
                    latest_reading = self.sensor_history[sensor_id][-1]
                    if latest_reading.status == 'ok' and not np.isnan(latest_reading.value):
                        values.append(latest_reading.value)
        
        return np.mean(values) if values else 0.0
    
    def _get_sensor_reading(self, sensor_id: str) -> float:
        """Get reading from specific sensor"""
        if sensor_id in self.sensor_history and self.sensor_history[sensor_id]:
            latest_reading = self.sensor_history[sensor_id][-1]
            if latest_reading.status == 'ok' and not np.isnan(latest_reading.value):
                return latest_reading.value
        return 0.0
    
    def _get_current_temp(self) -> float:
        """Get current average temperature for calculations"""
        return self._get_average_reading('temperature')
    
    def get_sensor_status(self) -> Dict[str, str]:
        """Get status of all sensors"""
        status = {}
        for sensor_id in self.sensors.keys():
            if self.sensor_history[sensor_id]:
                latest_reading = self.sensor_history[sensor_id][-1]
                status[sensor_id] = latest_reading.status
            else:
                status[sensor_id] = 'no_data'
        return status
    
    def detect_sensor_faults(self) -> List[str]:
        """Detect faulty sensors"""
        faulty_sensors = []
        
        for sensor_id, readings in self.sensor_history.items():
            if len(readings) >= 5:  # Need at least 5 readings
                recent_readings = readings[-5:]
                
                # Check for consecutive faults
                fault_count = sum(1 for r in recent_readings if r.status != 'ok')
                if fault_count >= 3:
                    faulty_sensors.append(sensor_id)
                
                # Check for stuck values
                values = [r.value for r in recent_readings if r.status == 'ok']
                if len(values) >= 3 and len(set(values)) == 1:
                    faulty_sensors.append(sensor_id)
        
        return faulty_sensors
    
    def calibrate_sensor(self, sensor_id: str, calibration_offset: float):
        """Calibrate sensor with offset"""
        if sensor_id in self.sensors:
            self.sensors[sensor_id]['calibration'] = calibration_offset