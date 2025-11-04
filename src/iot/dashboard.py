"""
IoT Dashboard for HVAC System Monitoring
Real-time web dashboard using Dash and Plotly
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import json
from datetime import datetime, timedelta
import numpy as np
from collections import deque
import threading
import time

from iot.mqtt_client import MQTTClient

class HVACDashboard:
    def __init__(self):
        """Initialize HVAC Dashboard"""
        self.app = dash.Dash(__name__)
        self.mqtt_client = MQTTClient()
        
        # Data storage
        self.max_data_points = 1000
        self.system_data = deque(maxlen=self.max_data_points)
        self.alerts = deque(maxlen=50)
        
        # Dashboard state
        self.current_data = {
            'temperature': 22.0,
            'humidity': 45.0,
            'temp_setpoint': 22.0,
            'humidity_setpoint': 45.0,
            'controller': 'pid',
            'energy_consumption': 1000,
            'system_status': 'normal'
        }
        
        self.setup_layout()
        self.setup_callbacks()
        self.start_data_collection()
    
    def setup_layout(self):
        """Setup dashboard layout"""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("Smart HVAC Control System", className="header-title"),
                html.P("Real-time monitoring and control dashboard", className="header-subtitle")
            ], className="header"),
            
            # Status Cards
            html.Div([
                html.Div([
                    html.H3("Temperature", className="card-title"),
                    html.H2(id="temp-display", className="metric-value"),
                    html.P(id="temp-status", className="metric-status")
                ], className="status-card"),
                
                html.Div([
                    html.H3("Humidity", className="card-title"),
                    html.H2(id="humidity-display", className="metric-value"),
                    html.P(id="humidity-status", className="metric-status")
                ], className="status-card"),
                
                html.Div([
                    html.H3("Energy", className="card-title"),
                    html.H2(id="energy-display", className="metric-value"),
                    html.P("Current consumption", className="metric-status")
                ], className="status-card"),
                
                html.Div([
                    html.H3("Controller", className="card-title"),
                    html.H2(id="controller-display", className="metric-value"),
                    html.P(id="system-status", className="metric-status")
                ], className="status-card")
            ], className="status-grid"),
            
            # Charts
            html.Div([
                html.Div([
                    dcc.Graph(id="temperature-chart")
                ], className="chart-container"),
                
                html.Div([
                    dcc.Graph(id="humidity-chart")
                ], className="chart-container")
            ], className="charts-row"),
            
            html.Div([
                html.Div([
                    dcc.Graph(id="energy-chart")
                ], className="chart-container"),
                
                html.Div([
                    dcc.Graph(id="control-output-chart")
                ], className="chart-container")
            ], className="charts-row"),
            
            # Control Panel
            html.Div([
                html.H3("Control Panel"),
                html.Div([
                    html.Label("Temperature Setpoint (°C):"),
                    dcc.Slider(
                        id="temp-setpoint-slider",
                        min=18, max=28, step=0.5, value=22,
                        marks={i: str(i) for i in range(18, 29, 2)}
                    )
                ], className="control-item"),
                
                html.Div([
                    html.Label("Humidity Setpoint (%):"),
                    dcc.Slider(
                        id="humidity-setpoint-slider",
                        min=30, max=70, step=5, value=45,
                        marks={i: str(i) for i in range(30, 71, 10)}
                    )
                ], className="control-item"),
                
                html.Div([
                    html.Label("Controller Type:"),
                    dcc.Dropdown(
                        id="controller-dropdown",
                        options=[
                            {'label': 'PID Controller', 'value': 'pid'},
                            {'label': 'Fuzzy Logic', 'value': 'fuzzy'},
                            {'label': 'On-Off', 'value': 'onoff'}
                        ],
                        value='pid'
                    )
                ], className="control-item")
            ], className="control-panel"),
            
            # Alerts
            html.Div([
                html.H3("System Alerts"),
                html.Div(id="alerts-container")
            ], className="alerts-section"),
            
            # Auto-refresh
            dcc.Interval(
                id='interval-component',
                interval=2000,  # Update every 2 seconds
                n_intervals=0
            )
        ])
    
    def setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        @self.app.callback(
            [Output('temp-display', 'children'),
             Output('humidity-display', 'children'),
             Output('energy-display', 'children'),
             Output('controller-display', 'children'),
             Output('temp-status', 'children'),
             Output('humidity-status', 'children'),
             Output('system-status', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_status_cards(n):
            temp_status = f"Setpoint: {self.current_data['temp_setpoint']:.1f}°C"
            humidity_status = f"Setpoint: {self.current_data['humidity_setpoint']:.0f}%"
            
            return (
                f"{self.current_data['temperature']:.1f}°C",
                f"{self.current_data['humidity']:.0f}%",
                f"{self.current_data['energy_consumption']:.0f}W",
                self.current_data['controller'].upper(),
                temp_status,
                humidity_status,
                self.current_data['system_status'].title()
            )
        
        @self.app.callback(
            Output('temperature-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_temperature_chart(n):
            if not self.system_data:
                return go.Figure()
            
            df = pd.DataFrame(list(self.system_data))
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=df['temperature'],
                mode='lines', name='Temperature',
                line=dict(color='red', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=df['temp_setpoint'],
                mode='lines', name='Setpoint',
                line=dict(color='red', width=1, dash='dash')
            ))
            
            fig.update_layout(
                title="Temperature Trend",
                xaxis_title="Time",
                yaxis_title="Temperature (°C)",
                height=300
            )
            
            return fig
        
        @self.app.callback(
            Output('humidity-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_humidity_chart(n):
            if not self.system_data:
                return go.Figure()
            
            df = pd.DataFrame(list(self.system_data))
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=df['humidity'],
                mode='lines', name='Humidity',
                line=dict(color='blue', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=df['humidity_setpoint'],
                mode='lines', name='Setpoint',
                line=dict(color='blue', width=1, dash='dash')
            ))
            
            fig.update_layout(
                title="Humidity Trend",
                xaxis_title="Time",
                yaxis_title="Humidity (%)",
                height=300
            )
            
            return fig
        
        @self.app.callback(
            Output('energy-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_energy_chart(n):
            if not self.system_data:
                return go.Figure()
            
            df = pd.DataFrame(list(self.system_data))
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=df['energy_consumption'],
                mode='lines', name='Energy Consumption',
                line=dict(color='green', width=2),
                fill='tonexty'
            ))
            
            fig.update_layout(
                title="Energy Consumption",
                xaxis_title="Time",
                yaxis_title="Power (W)",
                height=300
            )
            
            return fig
        
        @self.app.callback(
            Output('control-output-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_control_chart(n):
            if not self.system_data:
                return go.Figure()
            
            df = pd.DataFrame(list(self.system_data))
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=df['temp_output'],
                mode='lines', name='Temperature Output',
                line=dict(color='red', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=df['humidity_output'],
                mode='lines', name='Humidity Output',
                line=dict(color='blue', width=2)
            ))
            
            fig.update_layout(
                title="Control Outputs",
                xaxis_title="Time",
                yaxis_title="Control Output (%)",
                height=300
            )
            
            return fig
        
        @self.app.callback(
            Output('alerts-container', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_alerts(n):
            if not self.alerts:
                return html.P("No active alerts", className="no-alerts")
            
            alert_items = []
            for alert in list(self.alerts)[-10:]:  # Show last 10 alerts
                alert_items.append(
                    html.Div([
                        html.Span(alert['timestamp'], className="alert-time"),
                        html.Span(alert['message'], className=f"alert-message {alert['level']}")
                    ], className="alert-item")
                )
            
            return alert_items
    
    def start_data_collection(self):
        """Start collecting data from MQTT"""
        def data_collector():
            self.mqtt_client.connect()
            
            def on_message(topic, payload):
                try:
                    data = json.loads(payload)
                    self.system_data.append(data)
                    self.current_data.update(data)
                    
                    # Check for alerts
                    self.check_alerts(data)
                    
                except Exception as e:
                    print(f"Error processing MQTT message: {e}")
            
            self.mqtt_client.set_message_callback(on_message)
            self.mqtt_client.subscribe('hvac/system_data')
            
            # Keep the thread alive
            while True:
                time.sleep(1)
        
        # Start data collection in background thread
        thread = threading.Thread(target=data_collector, daemon=True)
        thread.start()
    
    def check_alerts(self, data):
        """Check for system alerts"""
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Temperature alerts
        temp_error = abs(data['temperature'] - data['temp_setpoint'])
        if temp_error > 3:
            self.alerts.append({
                'timestamp': current_time,
                'level': 'warning',
                'message': f"Temperature deviation: {temp_error:.1f}°C"
            })
        
        # Humidity alerts
        humidity_error = abs(data['humidity'] - data['humidity_setpoint'])
        if humidity_error > 10:
            self.alerts.append({
                'timestamp': current_time,
                'level': 'warning',
                'message': f"Humidity deviation: {humidity_error:.0f}%"
            })
        
        # Energy alerts
        if data['energy_consumption'] > 5000:
            self.alerts.append({
                'timestamp': current_time,
                'level': 'info',
                'message': f"High energy consumption: {data['energy_consumption']:.0f}W"
            })
    
    def run(self, debug=False, port=8050):
        """Run the dashboard"""
        print(f"Starting HVAC Dashboard on http://localhost:{port}")
        self.app.run_server(debug=debug, port=port, host='0.0.0.0')

if __name__ == "__main__":
    dashboard = HVACDashboard()
    dashboard.run(debug=True)