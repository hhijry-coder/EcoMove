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

    def _initialize_scheduled_rides(self) -> None:
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

        fig.add_trace(
            go.Bar(
                x=schedule_data['hourly_demand'].index,
                y=schedule_data['hourly_demand'].values,
                name="Hourly Demand"
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Bar(
                x=schedule_data['route_popularity'].index,
                y=schedule_data['route_popularity'].values,
                name="Route Popularity"
            ),
            row=1, col=2
        )

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

def create_map(center_lat: float, center_lon: float, 
               ride_share_points: List[RideSharePoint]) -> folium.Map:
    m = folium.Map(location=[center_lat, center_lon],
                   zoom_start=15,
                   tiles="cartodbpositron")
    
    folium.Circle(
        location=[Config.DEFAULT_LOCATION["lat"], Config.DEFAULT_LOCATION["lon"]],
        radius=Config.RADIUS,
        color="#2E7D32",
        fill=True,
        opacity=0.2
    ).add_to(m)
    
    for point in ride_share_points:
        demand_percentage = point.current_demand / point.capacity
        color = "red" if demand_percentage > 0.8 else "orange" if demand_percentage > 0.5 else "green"
        
        folium.CircleMarker(
            location=[point.location["lat"], point.location["lon"]],
            radius=10,
            color=color,
            popup=f"""
                <b>{point.name}</b><br>
                Capacity: {point.current_demand}/{point.capacity}<br>
                Eco Score: {point.eco_score:.1f}%<br>
                Wait Time: {point.wait_time} min
            """
        ).add_to(m)
    
    return m

def main():
    st.set_page_config(
        page_title="EcoMove - Tabuk University",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    eco_calculator = EcoImpactCalculator(Config)
    ride_scheduler = RideScheduler(Config)
    visualizer = EnhancedVisualization()

    st.sidebar.title("EcoMove - Tabuk University")
    page = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Schedule Analysis", "Environmental Impact", "Historical Analysis"]
    )

    if page == "Dashboard":
        st.title("EcoMove Dashboard")
        
        impact_data = eco_calculator.calculate_comprehensive_impact(ride_scheduler.scheduled_rides)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("CO₂ Saved", f"{impact_data['net_emissions_saved']:.1f} kg")
        with col2:
            st.metric("Calories Burned", f"{impact_data['calories_burned']:.0f}")
        with col3:
            st.metric("Trees Equivalent", f"{impact_data['trees_equivalent']:.1f}")
        with col4:
            st.metric("Active Rides", len(ride_scheduler.scheduled_rides))

        st.plotly_chart(
            visualizer.create_impact_dashboard(impact_data),
            use_container_width=True
        )

        st.subheader("Campus Map")
        m = create_map(
            Config.DEFAULT_LOCATION["lat"],
            Config.DEFAULT_LOCATION["lon"],
            ride_scheduler.scheduled_rides
        )
        folium_static(m)

    elif page == "Schedule Analysis":
        st.title("Ride Schedule Analysis")
        
        analytics = ride_scheduler.get_schedule_analytics()
        st.plotly_chart(
            visualizer.create_schedule_analysis(analytics),
            use_container_width=True
        )

        st.subheader("Today's Schedule")
        schedule_df = pd.DataFrame([{
            'Departure': ride.next_departure.strftime('%H:%M'),
            'Location': ride.name,
            'Capacity': f"{ride.current_demand}/{ride.capacity}",
            'Wait Time': f"{ride.wait_time} min"
        } for ride in ride_scheduler.scheduled_rides])
        st.dataframe(schedule_df)

    elif page == "Environmental Impact":
        st.title("Environmental Impact Analysis")
        
        historical_data = eco_calculator.historical_data
        fig = px.line(
            historical_data,
            x='date',
            y=['co2_saved', 'trees_equivalent'],
            title="Historical Environmental Impact"
        )
        st.plotly_chart(fig, use_container_width=True)

        monthly_avg = historical_data.set_index('date').resample('M').mean()
        st.subheader("Monthly Averages")
        st.line_chart(monthly_avg)

        st.subheader("Impact Breakdown")
        metrics_df = pd.DataFrame({
            'Metric': ['Total CO₂ Saved', 'Trees Equivalent', 'Calories Burned'],
            'Value': [
                f"{historical_data['co2_saved'].sum():.1f} kg",
                f"{historical_data['trees_equivalent'].sum():.1f} trees",
                f"{historical_data['calories_burned'].sum():.0f} calories"
            ]
        })
        st.table(metrics_df)

    else:  # Historical Analysis
        st.title("Historical Analysis")
        
        historical_rides = ride_scheduler.historical_rides
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

        st.subheader("Hourly Usage Patterns")
        hourly_patterns = historical_rides.groupby(
            historical_rides['datetime'].dt.hour
        )['passengers'].mean()
        st.bar_chart(hourly_patterns)

        st.subheader("Route Type Distribution")
        route_dist = historical_rides['route_type'].value_counts()
        fig = px.pie(
            values=route_dist.values,
            names=route_dist.index,
            title="Distribution of Route Types"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Weekly Trends")
        weekly_data = historical_rides.set_index('datetime').resample('W')['passengers'].mean()
        st.line_chart(weekly_data)

if __name__ == "__main__":
    main()
