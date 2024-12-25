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

# Enhanced Configuration with all required attributes
class Config:
    TOMTOM_API_KEY = "eXu4hsMGOsruJNBtXirN0pkU6I3DhNo2"
    DEFAULT_LOCATION = {"lat": 28.3835, "lon": 36.4868}  # Tabuk University
    RADIUS = 3000  # meters
    UPDATE_INTERVAL = 300  # seconds
    
    # Campus Locations
    CAMPUS_LOCATIONS = {
        "Main Gate": {"lat": 28.3835, "lon": 36.4868},
        "College of Engineering": {"lat": 28.3840, "lon": 36.4875},
        "College of Science": {"lat": 28.3830, "lon": 36.4860},
        "University Hospital": {"lat": 28.3845, "lon": 36.4880},
        "Student Center": {"lat": 28.3825, "lon": 36.4870}
    }
    
    # Ride-Share Points
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
    
    # Environmental Impact Parameters
    ECO_PARAMS = {
        "car_emissions": 0.2,  # kg CO2 per km
        "bus_emissions": 0.08,  # kg CO2 per km per person
        "walking_calories": 50,  # calories per km
        "cycling_calories": 30,  # calories per km
        "tree_absorption": 22,   # kg CO2 per year per tree
    }
    
    # Time slots for scheduling
    TIME_SLOTS = [
        "07:00", "07:30", "08:00", "08:30", "09:00", "09:30",
        "13:00", "13:30", "14:00", "14:30",
        "16:00", "16:30", "17:00", "17:30"
    ]

@dataclass
class ScheduledRide:
    id: str
    departure_time: datetime
    pickup_point: str
    destination: str
    capacity: int
    current_passengers: int
    route_type: str  # 'regular' or 'on-demand'
    eco_impact: float
    status: str  # 'scheduled', 'in-progress', 'completed'

class EnhancedEcoImpactCalculator:
    def __init__(self, config: Config):
        self.config = config
        self.historical_data = self._initialize_historical_data()

    def _initialize_historical_data(self) -> pd.DataFrame:
        """Initialize historical eco-impact data"""
        dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='D')
        data = {
            'date': dates,
            'rides_count': np.random.randint(50, 200, size=len(dates)),
            'co2_saved': np.random.uniform(100, 500, size=len(dates)),
            'calories_burned': np.random.uniform(5000, 15000, size=len(dates)),
            'trees_equivalent': np.random.uniform(5, 15, size=len(dates))
        }
        return pd.DataFrame(data)

    def calculate_comprehensive_impact(self, rides: List[ScheduledRide]) -> Dict:
        """Calculate comprehensive environmental impact"""
        total_distance = sum(self._estimate_ride_distance(ride) for ride in rides)
        car_emissions_saved = total_distance * self.config.ECO_PARAMS["car_emissions"]
        bus_emissions = total_distance * self.config.ECO_PARAMS["bus_emissions"]
        net_emissions_saved = car_emissions_saved - bus_emissions
        
        # Calculate health impact
        walking_distance = total_distance * 0.2  # Assuming 20% of saved trips convert to walking
        cycling_distance = total_distance * 0.1  # Assuming 10% convert to cycling
        calories_burned = (
            walking_distance * self.config.ECO_PARAMS["walking_calories"] +
            cycling_distance * self.config.ECO_PARAMS["cycling_calories"]
        )
        
        # Calculate environmental equivalents
        trees_equivalent = net_emissions_saved / self.config.ECO_PARAMS["tree_absorption"]
        
        return {
            "net_emissions_saved": net_emissions_saved,
            "calories_burned": calories_burned,
            "trees_equivalent": trees_equivalent,
            "walking_distance": walking_distance,
            "cycling_distance": cycling_distance
        }

    @staticmethod
    def _estimate_ride_distance(ride: ScheduledRide) -> float:
        """Estimate distance for a ride based on pickup and destination"""
        # In real implementation, use actual route distances
        return np.random.uniform(2, 10)  # km

class RideScheduler:
    def __init__(self, config: Config):
        self.config = config
        self.scheduled_rides = self._initialize_scheduled_rides()
        self.historical_rides = self._load_historical_rides()

    def _initialize_scheduled_rides(self) -> List[ScheduledRide]:
        """Initialize scheduled rides for the current day"""
        rides = []
        for slot in self.config.TIME_SLOTS:
            if np.random.random() > 0.3:  # 70% chance of having a ride in each slot
                ride = ScheduledRide(
                    id=f"RIDE_{len(rides)}",
                    departure_time=datetime.strptime(f"{datetime.now().date()} {slot}", "%Y-%m-%d %H:%M"),
                    pickup_point=np.random.choice(list(Config.RIDE_SHARE_POINTS.keys())),
                    destination=np.random.choice(list(Config.CAMPUS_LOCATIONS.keys())),
                    capacity=15,
                    current_passengers=np.random.randint(5, 15),
                    route_type='regular',
                    eco_impact=np.random.uniform(5, 15),
                    status='scheduled'
                )
                rides.append(ride)
        return rides

    def _load_historical_rides(self) -> pd.DataFrame:
        """Load historical ride data"""
        dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='H')
        data = {
            'datetime': dates,
            'passengers': np.random.randint(5, 20, size=len(dates)),
            'route_type': np.random.choice(['regular', 'on-demand'], size=len(dates)),
            'eco_impact': np.random.uniform(5, 15, size=len(dates))
        }
        return pd.DataFrame(data)

    def get_schedule_analytics(self) -> Dict:
        """Analyze scheduling patterns and usage"""
        df = pd.DataFrame([vars(ride) for ride in self.scheduled_rides])
        hourly_demand = df.groupby(df['departure_time'].dt.hour)['current_passengers'].mean()
        route_popularity = df.groupby('destination')['current_passengers'].sum()
        capacity_utilization = df['current_passengers'].sum() / (df['capacity'].sum() or 1)
        
        return {
            'hourly_demand': hourly_demand,
            'route_popularity': route_popularity,
            'capacity_utilization': capacity_utilization
        }

class EnhancedVisualization:
    @staticmethod
    def create_impact_dashboard(impact_data: Dict) -> go.Figure:
        """Create comprehensive impact dashboard"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "CO₂ Emissions Saved",
                "Health Impact",
                "Environmental Equivalents",
                "Transportation Mode Shift"
            )
        )

        # CO₂ Emissions
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=impact_data["net_emissions_saved"],
                delta={'reference': 100, 'relative': True},
                title="kg CO₂ Saved",
                domain={'row': 0, 'column': 0}
            ),
            row=1, col=1
        )

        # Health Impact
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=impact_data["calories_burned"],
                title="Calories Burned",
                domain={'row': 0, 'column': 1}
            ),
            row=1, col=2
        )

        # Environmental Equivalents
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=impact_data["trees_equivalent"],
                title="Trees Equivalent",
                domain={'row': 1, 'column': 0}
            ),
            row=2, col=1
        )

        # Transportation Mode Shift
        labels = ['Walking', 'Cycling', 'Public Transport']
        values = [
            impact_data["walking_distance"],
            impact_data["cycling_distance"],
            impact_data["net_emissions_saved"]
        ]
        fig.add_trace(
            go.Pie(labels=labels, values=values),
            row=2, col=2
        )

        fig.update_layout(height=800, showlegend=False)
        return fig

    @staticmethod
    def create_schedule_analysis(schedule_data: Dict) -> go.Figure:
        """Create schedule analysis visualization"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Hourly Demand",
                "Route Popularity",
                "Capacity Utilization",
                "Peak Hours"
            )
        )

        # Hourly Demand
        fig.add_trace(
            go.Bar(
                x=schedule_data['hourly_demand'].index,
                y=schedule_data['hourly_demand'].values,
                name="Hourly Demand"
            ),
            row=1, col=1
        )

        # Route Popularity
        fig.add_trace(
            go.Bar(
                x=schedule_data['route_popularity'].index,
                y=schedule_data['route_popularity'].values,
                name="Route Popularity"
            ),
            row=1, col=2
        )

        # Capacity Utilization
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=schedule_data['capacity_utilization'] * 100,
                title={'text': "Capacity Utilization %"},
                gauge={'axis': {'range': [0, 100]}}
            ),
            row=2, col=1
        )

        fig.update_layout(height=800, showlegend=True)
        return fig

def main():
    st.set_page_config(
        page_title="EcoMove - Enhanced Analytics",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize components
    eco_calculator = EnhancedEcoImpactCalculator(Config)
    ride_scheduler = RideScheduler(Config)
    visualizer = EnhancedVisualization()

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Schedule Analysis", "Environmental Impact", "Historical Analysis"]
    )

    if page == "Dashboard":
        st.title("EcoMove Dashboard")
        
        # Summary metrics
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

        # Impact dashboard
        st.plotly_chart(
            visualizer.create_impact_dashboard(impact_data),
            use_container_width=True
        )

    elif page == "Schedule Analysis":
        st.title("Ride Schedule Analysis")
        
        # Schedule analytics
        analytics = ride_scheduler.get_schedule_analytics()
        st.plotly_chart(
            visualizer.create_schedule_analysis(analytics),
            use_container_width=True
        )

        # Scheduled rides table
        st.subheader("Today's Schedule")
        rides_df = pd.DataFrame([vars(ride) for ride in ride_scheduler.scheduled_rides])
        st.dataframe(rides_df)

    elif page == "Environmental Impact":
        st.title("Environmental Impact Analysis")
        
        # Historical impact trends
        historical_data = eco_calculator.historical_data
        fig = px.line(historical_data, x='date', y=['co2_saved', 'trees_equivalent'],
                     title="Historical Environmental Impact")
        st.plotly_chart(fig, use_container_width=True)

        # Monthly averages
        monthly_avg = historical_data.set_index('date').resample('M').mean()
        st.subheader("Monthly Averages")
        st.line_chart(monthly_avg)

    else:  # Historical Analysis
        st.title("Historical Analysis")
        
        # Time series analysis
        historical_rides = ride_scheduler.historical_rides
        fig = px.scatter(historical_rides, x='datetime', y='passengers',
                        color='route_type', size='eco_impact',
                        title="Historical Ride Patterns")
        st.plotly_chart(fig, use_container_width=True)

        # Pattern analysis
        st.subheader("Usage Patterns")
        hourly_patterns = historical_rides.groupby(
            historical_rides['datetime'].dt.hour
        )['passengers'].mean()
        st.bar_chart(hourly_patterns)

if __name__ == "__main__":
    main()
