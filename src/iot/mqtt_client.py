"""
MQTT Client for IoT Communication
Handles MQTT messaging for HVAC system data
"""

import json
import time
import logging
from typing import Callable, Dict, Any
import paho.mqtt.client as mqtt
from threading import Lock

class MQTTClient:
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883,
                 client_id: str = "hvac_system"):
        """
        Initialize MQTT Client
        
        Args:
            broker_host: MQTT broker hostname
            broker_port: MQTT broker port
            client_id: Unique client identifier
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        
        # Initialize MQTT client
        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish
        
        # Connection state
        self.connected = False
        self.connection_lock = Lock()
        
        # Message callback
        self.message_callback = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # QoS levels
        self.qos_levels = {
            'system_data': 0,      # At most once
            'alerts': 1,           # At least once
            'commands': 2          # Exactly once
        }
    
    def connect(self, username: str = None, password: str = None) -> bool:
        """
        Connect to MQTT broker
        
        Args:
            username: MQTT username (optional)
            password: MQTT password (optional)
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if username and password:
                self.client.username_pw_set(username, password)
            
            self.logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port, 60)
            
            # Start the network loop
            self.client.loop_start()
            
            # Wait for connection
            timeout = 10  # seconds
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.connected:
                self.logger.info("Successfully connected to MQTT broker")
                return True
            else:
                self.logger.error("Failed to connect to MQTT broker within timeout")
                return False
                
        except Exception as e:
            self.logger.error(f"Error connecting to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            self.logger.info("Disconnected from MQTT broker")
        except Exception as e:
            self.logger.error(f"Error disconnecting from MQTT broker: {e}")
    
    def publish(self, topic: str, payload: Dict[str, Any], qos: int = None) -> bool:
        """
        Publish message to MQTT topic
        
        Args:
            topic: MQTT topic
            payload: Message payload (will be JSON serialized)
            qos: Quality of Service level (optional)
            
        Returns:
            True if publish successful, False otherwise
        """
        if not self.connected:
            self.logger.warning("Not connected to MQTT broker")
            return False
        
        try:
            # Determine QoS level
            if qos is None:
                qos = self._get_qos_for_topic(topic)
            
            # Serialize payload
            json_payload = json.dumps(payload, default=str)
            
            # Publish message
            result = self.client.publish(topic, json_payload, qos=qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"Published to {topic}: {json_payload[:100]}...")
                return True
            else:
                self.logger.error(f"Failed to publish to {topic}: {result.rc}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error publishing to {topic}: {e}")
            return False
    
    def subscribe(self, topic: str, qos: int = None) -> bool:
        """
        Subscribe to MQTT topic
        
        Args:
            topic: MQTT topic to subscribe to
            qos: Quality of Service level (optional)
            
        Returns:
            True if subscription successful, False otherwise
        """
        if not self.connected:
            self.logger.warning("Not connected to MQTT broker")
            return False
        
        try:
            # Determine QoS level
            if qos is None:
                qos = self._get_qos_for_topic(topic)
            
            result = self.client.subscribe(topic, qos=qos)
            
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"Subscribed to {topic} with QoS {qos}")
                return True
            else:
                self.logger.error(f"Failed to subscribe to {topic}: {result[0]}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error subscribing to {topic}: {e}")
            return False
    
    def unsubscribe(self, topic: str) -> bool:
        """
        Unsubscribe from MQTT topic
        
        Args:
            topic: MQTT topic to unsubscribe from
            
        Returns:
            True if unsubscription successful, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            result = self.client.unsubscribe(topic)
            
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"Unsubscribed from {topic}")
                return True
            else:
                self.logger.error(f"Failed to unsubscribe from {topic}: {result[0]}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error unsubscribing from {topic}: {e}")
            return False
    
    def set_message_callback(self, callback: Callable[[str, str], None]):
        """
        Set callback function for received messages
        
        Args:
            callback: Function to call when message received (topic, payload)
        """
        self.message_callback = callback
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection"""
        if rc == 0:
            with self.connection_lock:
                self.connected = True
            self.logger.info("Connected to MQTT broker")
        else:
            self.logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for MQTT disconnection"""
        with self.connection_lock:
            self.connected = False
        
        if rc != 0:
            self.logger.warning("Unexpected disconnection from MQTT broker")
        else:
            self.logger.info("Disconnected from MQTT broker")
    
    def _on_message(self, client, userdata, msg):
        """Callback for received MQTT message"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            self.logger.debug(f"Received message on {topic}: {payload[:100]}...")
            
            if self.message_callback:
                self.message_callback(topic, payload)
                
        except Exception as e:
            self.logger.error(f"Error processing received message: {e}")
    
    def _on_publish(self, client, userdata, mid):
        """Callback for published message"""
        self.logger.debug(f"Message published with ID: {mid}")
    
    def _get_qos_for_topic(self, topic: str) -> int:
        """Get appropriate QoS level for topic"""
        for topic_pattern, qos in self.qos_levels.items():
            if topic_pattern in topic:
                return qos
        return 0  # Default QoS
    
    def publish_system_data(self, data: Dict[str, Any]):
        """Convenience method to publish system data"""
        return self.publish('hvac/system_data', data)
    
    def publish_alert(self, alert: Dict[str, Any]):
        """Convenience method to publish alerts"""
        return self.publish('hvac/alerts', alert, qos=1)
    
    def publish_command(self, command: Dict[str, Any]):
        """Convenience method to publish commands"""
        return self.publish('hvac/commands', command, qos=2)
    
    def is_connected(self) -> bool:
        """Check if client is connected"""
        with self.connection_lock:
            return self.connected