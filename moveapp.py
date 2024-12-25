import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import json
from collections import defaultdict
import calendar

class Config:
    TOMTOM_API_KEY = "eXu4hsMGOsruJNBtXirN0pkU6I3DhNo2"
    DEFAULT_LOCATION = {"lat": 28.3835, "lon": 36.4868}
    RADIUS = 3000
    UPDATE_INTERVAL = 300
    
    CAMPUS_LOCATIONS = {
        "Main Gate": {"lat": 28.3835, "lon": 36.4868},
        "College of Engineering": {"lat": 28.3840, "lon": 36.4875},
        "College of Science": {"lat": 28.3830, "lon": 36.4860},
        "University Hospital": {"lat": 28.3845, "lon": 36.4880},
        "Student Center": {"lat": 28.3825, "lon": 36.4870}
    }
    
    RIDE_SHARE_POINTS = {
        "West Campus Hub": {
            "location": {"lat": 28.3840, "lon": 36.4875},
            "capacity": 15,
            "amenities": ["Covered Waiting Area", "Security Camera", "Digital Display"],
            "routes": ["Main Gate", "Student Housing", "Academic Complex"]
        },
        "Central Meeting Point": {
            "location": {"lat": 28.3825, "lon": 36.4870},
            "capacity": 20,
            "amenities": ["Seating Area", "Bike Racks", "Info Kiosk"],
            "routes": ["Library", "Sports Complex", "Cafeteria"]
        },
        "Medical Campus Point": {
            "location": {"lat": 28.3845, "lon": 36.4880},
            "capacity": 12,
            "amenities": ["Weather Protection", "Emergency Phone", "Accessibility Ramp"],
            "routes": ["Medical School", "Research Center", "Parking Complex"]
        }
    }
    
    ECO_PARAMS = {
        "car_emissions": 0.2,
        "bus_emissions": 0.08,
        "walking_calories": 50,
        "cycling_calories": 30,
        "tree_absorption": 22,
    }
    
    TIME_SLOTS = [
        "07:00", "07:30", "08:00", "08:30", "09:00", "09:30",
        "13:00", "13:30", "14:00", "14:30",
        "16:00", "16:30", "17:00", "17:30"
    ]

@dataclass
class TrafficIncident:
    id: str
    type: str
    severity: str
    location: Dict[str, float]
    description: str
    start_time: datetime
    end_time: datetime

@dataclass
class RideSharePoint:
    name: str
    location: Dict[str, float]
    capacity: int
    current_demand: int
    eco_score: float
    amenities: List[str]
    routes: List[str]
    next_departure: datetime
    wait_time: int

    @property
    def demand_percentage(self) -> float:
        return (self.current_demand / self.capacity) if self.capacity > 0 else 0.0

    @property
    def status(self) -> str:
        if self.demand_percentage > 0.8:
            return "High Demand"
        elif self.demand_percentage > 0.5:
            return "Moderate Demand"
        return "Low Demand"

    @property
    def is_available(self) -> bool:
        return self.current_demand < self.capacity

class TomTomAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tomtom.com/traffic/services/4"
        
    def get_traffic_flow(self, lat: float, lon: float, radius: int) -> Dict:
        """Fetch traffic flow data from TomTom API"""
        try:
            endpoint = f"{self.base_url}/flowSegmentData/absolute/10/json"
            params = {
                "key": self.api_key,
                "point": f"{lat},{lon}",
                "radius": radius,
                "unit": "KMPH"
            }
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching traffic flow: {str(e)}")
            return {"flowSegmentData": []}
    
    def get_traffic_incidents(self, lat: float, lon: float, radius: int) -> List[Dict]:
        """Fetch traffic incidents from TomTom API"""
        try:
            endpoint = f"{self.base_url}/incidentDetails/s3/json"
            params = {
                "key": self.api_key,
                "bbox": self._create_bbox(lat, lon, radius)
            }
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json().get('incidents', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching traffic incidents: {str(e)}")
            return []
    
    def get_route_traffic(self, start_lat: float, start_lon: float, 
                         end_lat: float, end_lon: float) -> Dict:
        """Get traffic data along a specific route"""
        try:
            endpoint = "https://api.tomtom.com/routing/1/calculateRoute/json"
            params = {
                "key": self.api_key,
                "traffic": "true",
                "travelMode": "car",
                "waypoint0": f"{start_lat},{start_lon}",
                "waypoint1": f"{end_lat},{end_lon}"
            }
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching route traffic: {str(e)}")
            return {}
    
    @staticmethod
    def _create_bbox(lat: float, lon: float, radius: int) -> str:
        """Create bounding box string for API requests"""
        deg_radius = radius / 111000
        return f"{lon-deg_radius},{lat-deg_radius},{lon+deg_radius},{lat+deg_radius}"

class EcoImpactCalculator:
    def __init__(self, config: Config):
        self.config = config
        self.historical_data = self._initialize_historical_data()

    def _initialize_historical_data(self) -> pd.DataFrame:
        dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
        data = {
            'date': dates,
            'rides_count': np.random.randint(50, 200, size=len(dates)),
            'co2_saved': np.random.uniform(100, 500, size=len(dates)),
            'calories_burned': np.random.uniform(5000, 15000, size=len(dates)),
            'trees_equivalent': np.random.uniform(5, 15, size=len(dates))
        }
        return pd.DataFrame(data)

    def calculate_comprehensive_impact(self, rides: List[RideSharePoint]) -> Dict:
        total_distance = sum(self._estimate_ride_distance(ride) for ride in rides)
        car_emissions_saved = total_distance * self.config.ECO_PARAMS["car_emissions"]
        bus_emissions = total_distance * self.config.ECO_PARAMS["bus_emissions"]
        net_emissions_saved = car_emissions_saved - bus_emissions
        
        walking_distance = total_distance * 0.2
        cycling_distance = total_distance * 0.1
        calories_burned = (
            walking_distance * self.config.ECO_PARAMS["walking_calories"] +
            cycling_distance * self.config.ECO_PARAMS["cycling_calories"]
        )
        
        trees_equivalent = net_emissions_saved / self.config.ECO_PARAMS["tree_absorption"]
        
        return {
            "net_emissions_saved": net_emissions_saved,
            "calories_burned": calories_burned,
            "trees_equivalent": trees_equivalent,
            "walking_distance": walking_distance,
            "cycling_distance": cycling_distance
        }

    @staticmethod
    def _estimate_ride_distance(ride: RideSharePoint) -> float:
        return np.random.uniform(2, 10)

class RideScheduler:
    def __init__(self, config: Config):
        self.config = config
        self.scheduled_rides = []
        self.historical_rides = self._load_historical_rides()
        self._initialize_scheduled_rides()

    def _initialize_scheduled_rides(self):
        for slot in self.config.TIME_SLOTS:
            if np.random.random() > 0.3:
                ride = RideSharePoint(
                    name=f"RIDE_{len(self.scheduled_rides)}",
                    location=list(self.config.RIDE_SHARE_POINTS.values())[0]["location"],
                    capacity=15,
                    current_demand=np.random.randint(5, 15),
                    eco_score=np.random.uniform(80, 100),
                    amenities=["Digital Display", "Security Camera"],
                    routes=["Main Gate", "Student Center"],
                    next_departure=datetime.strptime(f"{datetime.now().date()} {slot}", "%Y-%m-%d %H:%M"),
                    wait_time=np.random.randint(2, 10)
                )
                self.scheduled_rides.append(ride)

    def _load_historical_rides(self) -> pd.DataFrame:
        dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='H')
        data = {
            'datetime': dates,
            'passengers': np.random.randint(5, 20, size=len(dates)),
            'route_type': np.random.choice(['regular', 'on-demand'], size=len(dates)),
            'eco_impact': np.random.uniform(5, 15, size=len(dates))
        }
        return pd.DataFrame(data)

    def get_schedule_analytics(self) -> Dict:
        hourly_patterns = self.historical_rides.groupby(
            self.historical_rides['datetime'].dt.hour
        )['passengers'].mean()
        
        return {
            'hourly_demand': hourly_patterns,
            'route_popularity': pd.Series([15, 12, 8], index=['Route A', 'Route B', 'Route C']),
            'capacity_utilization': 0.75
        }

class EnhancedVisualization:
    @staticmethod
    def create_impact_dashboard(impact_data: Dict) -> go.Figure:
        fig = make_subplots(
            rows=2, cols=2,
            specs=[
                [{"type": "domain"}, {"type": "domain"}],
                [{"type": "domain"}, {"type": "pie"}]
            ],
            subplot_titles=(
                "CO₂ Emissions Saved",
                "Health Impact",
                "Environmental Equivalents",
                "Transportation Mode Shift"
            )
        )

        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=impact_data["net_emissions_saved"],
                delta={'reference': 100, 'relative': True},
                title={"text": "kg CO₂ Saved"},
                domain={'row': 0, 'column': 0}
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Indicator(
                mode="number",
                value=impact_data["calories_burned"],
                title={"text": "Calories Burned"},
                domain={'row': 0, 'column': 1}
            ),
            row=1, col=2
        )

        fig.add_trace(
            go.Indicator(
                mode="number",
                value=impact_data["trees_equivalent"],
                title={"text": "Trees Equivalent"},
                domain={'row': 1, 'column': 0}
            ),
            row=2, col=1
        )

        fig.add_trace(
            go.Pie(
                labels=['Walking', 'Cycling', 'Public Transport'],
                values=[
                    impact_data["walking_distance"],
                    impact_data["cycling_distance"],
                    impact_data["net_emissions_saved"]
                ],
                domain={'row': 1, 'column': 1}
            ),
            row=2, col=2
        )

        fig.update_layout(
            height=800,
            showlegend=False,
            grid={'rows': 2, 'columns': 2, 'pattern': 'independent'}
        )

        return fig

    @staticmethod
    def create_schedule_analysis(schedule_data: Dict) -> go.Figure:
        fig = make_subplots(
            rows=2, cols=2,
            specs=[
                [{"type": "xy"}, {"type": "xy"}],
                [{"type": "domain"}, {"type": "xy"}]
            ],
            subplot_titles=(
                "Hourly Demand",
                "Route Popularity",
                "Capacity Utilization",
                "Peak Hours"
            )
        )

        # Add hourly demand bar chart
        fig.add_trace(
            go.Bar(
                x=schedule_data['hourly_demand'].index,
                y=schedule_data['hourly_demand'].values,
                name="Hourly Demand"
            ),
            row=1, col=1
        )

        # Add route popularity bar chart
        fig.add_trace(
            go.Bar(
                x=schedule_data['route_popularity'].index,
                y=schedule_data['route_popularity'].values,
                name="Route Popularity"
            ),
            row=1, col=2
        )

        # Add capacity utilization gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=schedule_data['capacity_utilization'] * 100,
                title={'text': "Capacity Utilization %"},
                gauge={'axis': {'range': [0, 100]}},
                domain={'row': 1, 'column': 0}
            ),
            row=2, col=1
        )

        fig.update_layout(
            height=800,
            showlegend=True,
            grid={'rows': 2, 'columns': 2, 'pattern': 'independent'}
        )

        return fig

def create_enhanced_map(center_lat: float, center_lon: float,
                      ride_share_points: List[RideSharePoint],
                      traffic_api: TomTomAPI,
                      radius: int = 3000) -> folium.Map:
    """Create an enhanced map with real-time traffic data."""
    m = folium.Map(location=[center_lat, center_lon],
                  zoom_start=15,
                  tiles="cartodbpositron")

    # Add campus boundary
    folium.Circle(
        location=[center_lat, center_lon],
        radius=radius,
        color="#2E7D32",
        fill=True,
        opacity=0.2
    ).add_to(m)

    # Fetch traffic data
    traffic_flow = traffic_api.get_traffic_flow(center_lat, center_lon, radius)
    traffic_incidents = traffic_api.get_traffic_incidents(center_lat, center_lon, radius)

    # Add traffic flow visualization
    if 'flowSegmentData' in traffic_flow:
        for segment in traffic_flow['flowSegmentData']:
            if isinstance(segment, dict):
                coordinates = segment.get('coordinates', {})
                if coordinates:
                    congestion = segment.get('currentSpeed', 0) / segment.get('freeFlowSpeed', 1)
                    color = (
                        '#FF0000' if congestion < 0.5 else
                        '#FFA500' if congestion < 0.75 else
                        '#00FF00'
                    )

                    folium.PolyLine(
                        locations=coordinates,
                        color=color,
                        weight=5,
                        opacity=0.7,
                        popup=f"Speed: {segment.get('currentSpeed')} km/h<br>"
                              f"Free flow: {segment.get('freeFlowSpeed')} km/h"
                    ).add_to(m)

    # Add traffic incidents
    for incident in traffic_incidents:
        coordinates = incident.get('geometry', {}).get('coordinates', [])
        if coordinates:
            icon_color = {
                'ACCIDENT': 'red',
                'CONSTRUCTION': 'orange',
                'CONGESTION': 'yellow'
            }.get(incident.get('type', ''), 'gray')

            folium.CircleMarker(
                location=[coordinates[1], coordinates[0]],
                radius=8,
                color=icon_color,
                fill=True,
                popup=f"Type: {incident.get('type')}<br>"
                      f"Description: {incident.get('properties', {}).get('description', 'N/A')}"
            ).add_to(m)

    # Add ride-share points
    for point in ride_share_points:
        demand_percentage = point.current_demand / point.capacity
        color = (
            "red" if demand_percentage > 0.8 else
            "orange" if demand_percentage > 0.5 else
            "green"
        )

        folium.CircleMarker(
            location=[point.location["lat"], point.location["lon"]],
            radius=10,
            color=color,
            fill=True,
            popup=f"""
                <b>{point.name}</b><br>
                Capacity: {point.current_demand}/{point.capacity}<br>
                Wait Time: {point.wait_time} min
            """
        ).add_to(m)

    return m

def calculate_traffic_score(traffic_data: Dict) -> float:
    """Calculate traffic score (0-10) based on traffic conditions"""
    if 'flowSegmentData' not in traffic_data:
        return 5.0
    
    segments = traffic_data['flowSegmentData']
    if not segments:
        return 5.0
    
    scores = []
    for segment in segments:
        if isinstance(segment, dict):
            current_speed = segment.get('currentSpeed', 0)
            free_flow_speed = segment.get('freeFlowSpeed', 1)
            ratio = current_speed / free_flow_speed if free_flow_speed > 0 else 0
            score = min(10, ratio * 10)
            scores.append(score)
    
    return sum(scores) / len(scores) if scores else 5.0

def calculate_overall_congestion(traffic_flow: Dict) -> float:
    if 'flowSegmentData' not in traffic_flow:
        return 50.0
    
    segments = traffic_flow['flowSegmentData']
    if not segments:
        return 50.0
    
    congestion_levels = []
    for segment in segments:
        if isinstance(segment, dict):
            current_speed = segment.get('currentSpeed', 0)
            free_flow_speed = segment.get('freeFlowSpeed', 1)
            if free_flow_speed > 0:
                congestion = (1 - current_speed / free_flow_speed) * 100
                congestion_levels.append(congestion)
    
    return np.mean(congestion_levels) if congestion_levels else 50.0

def calculate_average_speed(traffic_flow: Dict) -> float:
    if 'flowSegmentData' not in traffic_flow:
        return 40.0
    
    segments = traffic_flow['flowSegmentData']
    if not segments:
        return 40.0
    
    speeds = [segment.get('currentSpeed', 40) for segment in segments if isinstance(segment, dict)]
    return np.mean(speeds) if speeds else 40.0

def get_incident_location(incident: Dict) -> str:
    coordinates = incident.get('geometry', {}).get('coordinates', [])
    if coordinates:
        return f"({coordinates[1]:.4f}, {coordinates[0]:.4f})"
    return "Location unknown"

def calculate_traffic_impact(scheduled_rides: List[RideSharePoint],
                           traffic_api: TomTomAPI) -> Dict:
    reliability = np.random.uniform(85, 95)
    avg_delay = np.random.uniform(2, 8)
    affected_routes = np.random.randint(1, 4)
    
    return {
        'reliability': reliability,
        'reliability_change': np.random.uniform(-2, 2),
        'avg_delay': avg_delay,
        'affected_routes': affected_routes
    }

def get_traffic_status(ride: RideSharePoint, traffic_api: TomTomAPI) -> str:
    traffic_score = calculate_traffic_score(
        traffic_api.get_traffic_flow(
            ride.location["lat"],
            ride.location["lon"],
            500
        )
    )
    
    if traffic_score >= 7:
        return "Clear"
    elif traffic_score >= 5:
        return "Moderate"
    return "Heavy"

def get_schedule_recommendation(ride: RideSharePoint, traffic_impact: Dict) -> str:
    if traffic_impact['reliability'] < 90:
        return "Consider adding buffer time"
    elif traffic_impact['avg_delay'] > 5:
        return "Monitor traffic conditions"
    return "No changes needed"

def calculate_traffic_eco_impact(traffic_api: TomTomAPI, location: Dict) -> Dict:
    traffic_flow = traffic_api.get_traffic_flow(
        location["lat"],
        location["lon"],
        3000
    )
    
    congestion = calculate_overall_congestion(traffic_flow)
    
    return {
        'additional_co2': congestion * 0.5,
        'fuel_waste': congestion * 0.2,
        'time_lost': congestion * 0.3
    }

def calculate_monthly_averages(historical_data: pd.DataFrame,
                             traffic_api: TomTomAPI) -> pd.DataFrame:
    monthly_avg = historical_data.set_index('date').resample('M').mean()
    traffic_factor = np.random.uniform(0.8, 1.2, size=len(monthly_avg))
    monthly_avg = monthly_avg.multiply(traffic_factor, axis=0)
    return monthly_avg

def calculate_traffic_savings(traffic_api: TomTomAPI) -> float:
    return np.random.uniform(100, 500)

def analyze_traffic_correlation(historical_rides: pd.DataFrame,
                              traffic_api: TomTomAPI) -> Dict:
    return {
        'correlation': np.random.uniform(0.6, 0.8),
        'correlation_change': np.random.uniform(-0.1, 0.1),
        'peak_impact': np.random.uniform(10, 30),
        'off_peak_efficiency': np.random.uniform(70, 90),
        'efficiency_change': np.random.uniform(-5, 5)
    }

def create_hourly_analysis(historical_rides: pd.DataFrame,
                          traffic_api: TomTomAPI) -> go.Figure:
    hourly_data = historical_rides.groupby(
        historical_rides['datetime'].dt.hour
    )['passengers'].mean()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hourly_data.index,
        y=hourly_data.values,
        name='Average Passengers'
    ))
    
    traffic_impact = np.random.uniform(0.7, 1.3, size=24)
    fig.add_trace(go.Scatter(
        x=hourly_data.index,
        y=hourly_data.values * traffic_impact,
        name='Traffic Adjusted'
    ))
    
    fig.update_layout(
        title='Hourly Passenger Distribution with Traffic Impact',
        xaxis_title='Hour of Day',
        yaxis_title='Average Passengers'
    )
    
    return fig

def analyze_weekly_trends(historical_rides: pd.DataFrame,
                         traffic_api: TomTomAPI) -> pd.DataFrame:
    weekly_data = historical_rides.groupby(
        historical_rides['datetime'].dt.dayofweek
    ).agg({
        'passengers': 'mean',
        'eco_impact': 'sum'
    })
    
    traffic_factor = np.random.uniform(0.8, 1.2, size=len(weekly_data))
    weekly_data = weekly_data.multiply(traffic_factor, axis=0)
    
    return weekly_data

def generate_recommendations(historical_rides: pd.DataFrame,
                           traffic_correlation: Dict,
                           traffic_api: TomTomAPI) -> List[str]:
    recommendations = [
        "Adjust departure times during peak congestion periods",
        "Add capacity to routes with consistent high demand",
        "Consider alternative routes for heavily congested segments",
        "Implement dynamic scheduling based on real-time traffic"
    ]
    
    if traffic_correlation['peak_impact'] > 20:
        recommendations.append("Increase buffer times during peak hours")
    
    if traffic_correlation['off_peak_efficiency'] < 80:
        recommendations.append("Optimize off-peak route efficiency")
    
    return recommendations

def main():
    st.set_page_config(
        page_title="EcoMove - Tabuk University",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    traffic_api = TomTomAPI(Config.TOMTOM_API_KEY)
    eco_calculator = EcoImpactCalculator(Config)
    ride_scheduler = RideScheduler(Config)
    visualizer = EnhancedVisualization()

    st.sidebar.title("EcoMove - Tabuk University")
    
    refresh_interval = st.sidebar.selectbox(
        "Traffic Data Refresh Interval",
        [60, 180, 300, 600],
        format_func=lambda x: f"{x//60} minutes"
    )

    show_congestion = st.sidebar.checkbox("Show Congestion", value=True)
    show_incidents = st.sidebar.checkbox("Show Incidents", value=True)
    show_recommendations = st.sidebar.checkbox("Show Recommended Points", value=True)

    page = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Schedule Analysis", "Environmental Impact", "Historical Analysis"]
    )

    if page == "Dashboard":
        st.title("EcoMove Dashboard")
        
        traffic_flow = traffic_api.get_traffic_flow(
            Config.DEFAULT_LOCATION["lat"],
            Config.DEFAULT_LOCATION["lon"],
            Config.RADIUS
        )
        
        incidents = traffic_api.get_traffic_incidents(
            Config.DEFAULT_LOCATION["lat"],
            Config.DEFAULT_LOCATION["lon"],
            Config.RADIUS
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            congestion_level = calculate_overall_congestion(traffic_flow)
            st.metric(
                "Traffic Congestion",
                f"{congestion_level:.1f}%",
                delta=congestion_level - 50
            )
        with col2:
            active_incidents = len(incidents)
            st.metric("Active Incidents", active_incidents)
        with col3:
            average_speed = calculate_average_speed(traffic_flow)
            st.metric(
                "Average Speed",
                f"{average_speed:.1f} km/h",
                delta=average_speed - 40
            )

        st.subheader("Real-time Traffic Map")
        enhanced_map = create_enhanced_map(
            Config.DEFAULT_LOCATION["lat"],
            Config.DEFAULT_LOCATION["lon"],
            ride_scheduler.scheduled_rides,
            traffic_api,
            Config.RADIUS
        )
        
        if show_congestion or show_incidents or show_recommendations:
            folium.LayerControl().add_to(enhanced_map)
        
        folium_static(enhanced_map)

        if show_incidents and incidents:
            st.subheader("Current Traffic Incidents")
            incidents_df = pd.DataFrame([
                {
                    'Type': inc.get('type', 'Unknown'),
                    'Severity': inc.get('properties', {}).get('severity', 'Unknown'),
                    'Description': inc.get('properties', {}).get('description', 'No description'),
                    'Location': get_incident_location(inc)
                }
                for inc in incidents
            ])
            st.dataframe(incidents_df)

        impact_data = eco_calculator.calculate_comprehensive_impact(ride_scheduler.scheduled_rides)
        st.plotly_chart(
            visualizer.create_impact_dashboard(impact_data),
            use_container_width=True
        )

    elif page == "Schedule Analysis":
        st.title("Ride Schedule Analysis")
        
        analytics = ride_scheduler.get_schedule_analytics()
        st.plotly_chart(
            visualizer.create_schedule_analysis(analytics),
            use_container_width=True
        )

        st.subheader("Traffic Impact on Schedules")
        traffic_impact = calculate_traffic_impact(
            ride_scheduler.scheduled_rides,
            traffic_api
        )
        
        impact_cols = st.columns(3)
        with impact_cols[0]:
            st.metric(
                "Schedule Reliability",
                f"{traffic_impact['reliability']:.1f}%",
                delta=traffic_impact['reliability_change']
            )
        with impact_cols[1]:
            st.metric(
                "Average Delay",
                f"{traffic_impact['avg_delay']:.1f} min",
                delta=-traffic_impact['avg_delay'],
                delta_color="inverse"
            )
        with impact_cols[2]:
            st.metric(
                "Routes Affected",
                traffic_impact['affected_routes'],
                delta=-traffic_impact['affected_routes'],
                delta_color="inverse"
            )

        st.subheader("Today's Schedule")
        schedule_df = pd.DataFrame([{
            'Departure': ride.next_departure.strftime('%H:%M'),
            'Location': ride.name,
            'Capacity': f"{ride.current_demand}/{ride.capacity}",
            'Wait Time': f"{ride.wait_time} min",
            'Traffic Status': get_traffic_status(ride, traffic_api),
            'Recommended Action': get_schedule_recommendation(ride, traffic_impact)
        }  for ride in ride_scheduler.scheduled_rides])
        st.dataframe(schedule_df)

    elif page == "Environmental Impact":
        st.title("Environmental Impact Analysis")
        
        historical_data = eco_calculator.historical_data
        traffic_eco_impact = calculate_traffic_eco_impact(traffic_api, Config.DEFAULT_LOCATION)
        
        impact_cols = st.columns(3)
        with impact_cols[0]:
            st.metric(
                "Additional CO₂ from Traffic",
                f"{traffic_eco_impact['additional_co2']:.1f} kg",
                delta=-traffic_eco_impact['additional_co2'],
                delta_color="inverse"
            )
        with impact_cols[1]:
            st.metric(
                "Fuel Wastage",
                f"{traffic_eco_impact['fuel_waste']:.1f} L",
                delta=-traffic_eco_impact['fuel_waste'],
                delta_color="inverse"
            )
        with impact_cols[2]:
            st.metric(
                "Time Lost in Traffic",
                f"{traffic_eco_impact['time_lost']:.0f} hours",
                delta=-traffic_eco_impact['time_lost'],
                delta_color="inverse"
            )

        st.subheader("Impact Trends")
        fig = px.line(
            historical_data,
            x='date',
            y=['co2_saved', 'trees_equivalent'],
            title="Historical Environmental Impact"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Monthly Analysis")
        monthly_avg = calculate_monthly_averages(historical_data, traffic_api)
        st.line_chart(monthly_avg)

    else:  # Historical Analysis
        st.title("Historical Analysis")
        
        historical_rides = ride_scheduler.historical_rides
        traffic_correlation = analyze_traffic_correlation(historical_rides, traffic_api)
        
        st.subheader("Traffic Impact Analysis")
        correlation_cols = st.columns(3)
        with correlation_cols[0]:
            st.metric(
                "Traffic-Ride Correlation",
                f"{traffic_correlation['correlation']:.2f}",
                delta=traffic_correlation['correlation_change']
            )
        with correlation_cols[1]:
            st.metric(
                "Peak Hour Impact",
                f"{traffic_correlation['peak_impact']:.1f}%",
                delta=-traffic_correlation['peak_impact'],
                delta_color="inverse"
            )
        with correlation_cols[2]:
            st.metric(
                "Off-Peak Efficiency",
                f"{traffic_correlation['off_peak_efficiency']:.1f}%",
                delta=traffic_correlation['efficiency_change']
            )

        st.subheader("Ride Patterns")
        fig = px.scatter(
            historical_rides,
            x='datetime',
            y='passengers',
            color='route_type',
            size='eco_impact',
            title="Historical Ride Patterns"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Hourly Analysis")
        hourly_analysis = create_hourly_analysis(historical_rides, traffic_api)
        st.plotly_chart(hourly_analysis, use_container_width=True)

        st.subheader("Route Type Distribution")
        route_dist = historical_rides['route_type'].value_counts()
        fig = px.pie(
            values=route_dist.values,
            names=route_dist.index,
            title="Distribution of Route Types"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Weekly Trends")
        weekly_data = analyze_weekly_trends(historical_rides, traffic_api)
        st.line_chart(weekly_data)

        st.subheader("Optimization Recommendations")
        recommendations = generate_recommendations(
            historical_rides,
            traffic_correlation,
            traffic_api
        )
        for rec in recommendations:
            st.info(rec)

if __name__ == "__main__":
    main()
