import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import json
import random
from PIL import Image
import numpy as np
from folium import plugins
from streamlit_folium import st_folium

from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
TABUK_UNIVERSITY_COORDS = [28.3835, 36.4868]

class TabukEcoMoveOptimizer:
    def __init__(self):
        self.setup_config()
        self.campus_locations = {
            "Main Gate": [28.3835, 36.4868],
            "College of Engineering": [28.3840, 36.4873],
            "College of Medicine": [28.3830, 36.4863],
            "Student Housing": [28.3845, 36.4878],
            "University Library": [28.3833, 36.4870]
        }
        self.roads = [
            {
                "coordinates": [[28.3835, 36.4868], [28.3840, 36.4873]],
                "intensity": "high",
                "name": "Main Campus Road"
            },
            {
                "coordinates": [[28.3830, 36.4863], [28.3833, 36.4870]],
                "intensity": "medium",
                "name": "Library Avenue"
            },
            {
                "coordinates": [[28.3833, 36.4870], [28.3845, 36.4878]],
                "intensity": "low",
                "name": "Housing Road"
            }
        ]
        self.congestion_points = [
            {
                "location": [28.3835, 36.4868],
                "level": "severe",
                "delay": "15 mins",
                "description": "Main Gate Congestion"
            },
            {
                "location": [28.3840, 36.4873],
                "level": "moderate",
                "delay": "8 mins",
                "description": "Engineering College Junction"
            }
        ]
        
    def setup_config(self):
        st.set_page_config(page_title="Tabuk University EcoMove", page_icon="🚗", layout="wide")
        
    def add_traffic_flow(self, m):
        colors = {
            "low": "#00ff00",
            "medium": "#ffa500",
            "high": "#ff0000"
        }
        
        for road in self.roads:
            folium.PolyLine(
                road["coordinates"],
                weight=5,
                color=colors[road["intensity"]],
                popup=f"{road['name']} - Traffic: {road['intensity'].title()}",
                opacity=0.8,
                dash_array='10'
            ).add_to(m)
    
    def add_congestion_markers(self, m):
        for point in self.congestion_points:
            folium.CircleMarker(
                location=point["location"],
                radius=15,
                color="red" if point["level"] == "severe" else "orange",
                fill=True,
                popup=f"{point['description']}<br>Delay: {point['delay']}"
            ).add_to(m)
    
    def show_traffic_timeline(self):
        hours = list(range(6, 24))
        traffic_data = [random.randint(30, 100) for _ in hours]
        
        chart_data = pd.DataFrame({
            'Hour': hours,
            'Traffic Density': traffic_data
        })
        
        st.line_chart(chart_data.set_index('Hour'))

    def main(self):
        st.title("جامعة تبوك EcoMove Optimizer 🌿")
        st.markdown("Smart Transportation Solution for Tabuk University Community")
        
        page = st.sidebar.selectbox(
            "التنقل | Navigation",
            ["Dashboard | لوحة التحكم", 
             "Route Planner | مخطط الطريق", 
             "Ride Sharing | مشاركة الركوب", 
             "Analytics | التحليلات"]
        )
        
        pages = {
            "Dashboard | لوحة التحكم": self.show_dashboard,
            "Route Planner | مخطط الطريق": self.show_route_planner,
            "Ride Sharing | مشاركة الركوب": self.show_ride_sharing,
            "Analytics | التحليلات": self.show_analytics
        }
        pages[page]()

    def show_dashboard(self):
        st.subheader("Campus Traffic Map | خريطة حركة المرور في الحرم الجامعي")
        
        # Create traffic map with all visualizations
        m = folium.Map(location=TABUK_UNIVERSITY_COORDS, zoom_start=16)
        
        # Add campus locations
        for name, coords in self.campus_locations.items():
            folium.Marker(
                coords,
                popup=name,
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
        
        # Add traffic flow visualization
        self.add_traffic_flow(m)
        
        # Add congestion points
        self.add_congestion_markers(m)
        
        # Add heatmap layer
        heat_data = []
        for loc in self.campus_locations.values():
            for _ in range(20):
                lat = loc[0] + random.uniform(-0.001, 0.001)
                lon = loc[1] + random.uniform(-0.001, 0.001)
                weight = random.uniform(0.2, 1.0)
                heat_data.append([lat, lon, weight])
        
        plugins.HeatMap(heat_data, min_opacity=0.4).add_to(m)
        
        # Display the map
        st_folium(m, width=None, height=500)
        
        # Display traffic timeline
        st.subheader("Traffic Density Timeline | جدول زمني لكثافة المرور")
        self.show_traffic_timeline()
        
        # Display metrics
        st.subheader("Quick Stats | إحصائيات سريعة")
        col1, col2, col3, col4 = st.columns(4)
        
        stats = {
            "Active Rides | رحلات نشطة": [random.randint(10, 50), "rides"],
            "CO2 Saved | ثاني أكسيد الكربون الموفر": [random.randint(100, 500), "kg"],
            "Temperature | درجة الحرارة": [random.randint(25, 45), "°C"],
            "Air Quality | جودة الهواء": [random.randint(50, 150), "AQI"]
        }
        
        for (label, (value, unit)), col in zip(stats.items(), [col1, col2, col3, col4]):
            with col:
                st.metric(label=label, value=f"{value} {unit}")



    def show_route_planner(self):
        st.subheader("Route Planner | مخطط الطريق")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start = st.selectbox("Start Location | موقع البداية", list(self.campus_locations.keys()))
            end = st.selectbox("End Location | موقع النهاية", list(self.campus_locations.keys()))
            
            if st.button("Find Route | ابحث عن الطريق"):
                self.calculate_route(start, end)
        
        with col2:
            st.markdown("### Route Details | تفاصيل الطريق")
            self.display_route_details()

    def calculate_route(self, start, end):
        if start and end and start != end:
            st.success(f"Route calculated from {start} to {end} | تم حساب الطريق")
            
            # Create map for route visualization
            m = folium.Map(location=TABUK_UNIVERSITY_COORDS, zoom_start=16)
            
            # Add traffic flow visualization
            self.add_traffic_flow(m)
            
            # Add congestion markers
            self.add_congestion_markers(m)
            
            # Add markers for start and end
            folium.Marker(
                self.campus_locations[start],
                popup=f"Start: {start}",
                icon=folium.Icon(color='green')
            ).add_to(m)
            
            folium.Marker(
                self.campus_locations[end],
                popup=f"End: {end}",
                icon=folium.Icon(color='red')
            ).add_to(m)
            
            # Draw route line
            folium.PolyLine(
                locations=[self.campus_locations[start], self.campus_locations[end]],
                weight=3,
                color='blue',
                opacity=0.8
            ).add_to(m)
            
            folium_static(m)

    def display_route_details(self):
        route_stats = {
            "Distance | المسافة": "1.2 km",
            "Est. Time | الوقت المقدر": "8 mins",
            "Carbon Footprint | البصمة الكربونية": "0.3 kg CO2",
            "Traffic Level | مستوى حركة المرور": "Low | منخفض"
        }
        
        for key, value in route_stats.items():
            st.metric(label=key, value=value)

    def show_ride_sharing(self):
        st.subheader("Ride Sharing | مشاركة الركوب")
        
        tab1, tab2 = st.tabs(["Find a Ride | ابحث عن رحلة", "Offer a Ride | اعرض رحلة"])
        
        with tab1:
            self.find_ride_form()
        
        with tab2:
            self.offer_ride_form()

    def find_ride_form(self):
        pickup = st.selectbox("Pickup Location | موقع الالتقاط", list(self.campus_locations.keys()))
        destination = st.selectbox("Destination | الوجهة", list(self.campus_locations.keys()))
        date = st.date_input("Date | التاريخ", key="find_ride_date")
        time = st.time_input("Preferred Time | الوقت المفضل", key="find_ride_time")
        
        if st.button("Search Rides | البحث عن الرحلات"):
            self.display_available_rides()

    def offer_ride_form(self):
        start = st.selectbox("Start Location | موقع البداية", list(self.campus_locations.keys()))
        end = st.selectbox("End Location | موقع النهاية", list(self.campus_locations.keys()))
        date = st.date_input("Date | التاريخ", key="offer_ride_date")
        time = st.time_input("Departure Time | وقت المغادرة", key="offer_ride_time")
        seats = st.number_input("Available Seats | المقاعد المتاحة", 1, 4)
        
        if st.button("Offer Ride | عرض الرحلة"):
            st.success("Ride offered successfully! | تم عرض الرحلة بنجاح")

    def display_available_rides(self):
        rides = pd.DataFrame({
            'Driver | السائق': ['Abdullah M.', 'Fatima S.', 'Mohammed K.'],
            'Time | الوقت': ['9:00 AM', '9:30 AM', '10:00 AM'],
            'Price | السعر': ['15 SAR', '20 SAR', '12 SAR'],
            'Rating | التقييم': ['⭐⭐⭐⭐', '⭐⭐⭐⭐⭐', '⭐⭐⭐']
        })
        
        st.dataframe(rides)

    def show_analytics(self):
        st.subheader("Traffic Analytics | تحليلات حركة المرور")
        
        # Display traffic patterns
        st.markdown("### Traffic Patterns | أنماط حركة المرور")
        self.show_traffic_timeline()
        
        # Display detailed analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Weekly Statistics | إحصائيات أسبوعية")
            stats_data = pd.DataFrame({
                'Day | اليوم': ['Sun | الأحد', 'Mon | الاثنين', 'Tue | الثلاثاء', 'Wed | الأربعاء', 'Thu | الخميس'],
                'Rides | الرحلات': [45, 52, 38, 41, 55],
                'CO2 Saved (kg) | ثاني أكسيد الكربون الموفر': [90, 104, 76, 82, 110]
            })
            st.dataframe(stats_data)
            
        with col2:
            st.markdown("### Popular Routes | الطرق الشائعة")
            routes_data = pd.DataFrame({
                'Route | الطريق': ['Main Gate-Engineering | البوابة الرئيسية-الهندسة', 
                                  'Library-Medicine | المكتبة-الطب', 
                                  'Housing-Main Gate | السكن-البوابة الرئيسية'],
                'Usage | الاستخدام': ['35%', '28%', '22%']
            })
            st.dataframe(routes_data)
            
        # Display traffic heatmap
        st.subheader("Traffic Heatmap | خريطة الحرارة لحركة المرور")
        m = folium.Map(location=TABUK_UNIVERSITY_COORDS, zoom_start=16)
        
        # Add base locations
        for name, coords in self.campus_locations.items():
            folium.Marker(
                coords,
                popup=name,
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
        
        # Add traffic flow
        self.add_traffic_flow(m)
        
        # Add congestion markers
        self.add_congestion_markers(m)
        
        # Add heatmap layer
        heat_data = []
        for loc in self.campus_locations.values():
            for _ in range(20):
                lat = loc[0] + random.uniform(-0.001, 0.001)
                lon = loc[1] + random.uniform(-0.001, 0.001)
                weight = random.uniform(0.2, 1.0)
                heat_data.append([lat, lon, weight])
        
        plugins.HeatMap(heat_data).add_to(m)
        
        folium_static(m)

if __name__ == "__main__":
    app = TabukEcoMoveOptimizer()
    app.main()



import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import json
import random
from PIL import Image
import numpy as np
from folium import plugins

from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
TABUK_UNIVERSITY_COORDS = [28.3835, 36.4868]

TABUK_UNIVERSITY_COORDS = [28.3835, 36.4868]

class TabukEcoMoveOptimizer:
    def __init__(self):
        self.setup_config()
        self.setup_initial_state()
        
    def setup_config(self):
        st.set_page_config(page_title="Tabuk University EcoMove", page_icon="🚗", layout="wide")
        
    def setup_initial_state(self):
        if 'campus_locations' not in st.session_state:
            st.session_state.campus_locations = {
                "Main Gate": [28.3835, 36.4868],
                "College of Engineering": [28.3840, 36.4873],
                "College of Medicine": [28.3830, 36.4863],
                "Student Housing": [28.3845, 36.4878],
                "University Library": [28.3833, 36.4870]
            }
        
        if 'roads' not in st.session_state:
            st.session_state.roads = [
                {
                    "coordinates": [[28.3835, 36.4868], [28.3840, 36.4873]],
                    "intensity": "high",
                    "name": "Main Campus Road"
                },
                {
                    "coordinates": [[28.3830, 36.4863], [28.3833, 36.4870]],
                    "intensity": "medium",
                    "name": "Library Avenue"
                },
                {
                    "coordinates": [[28.3833, 36.4870], [28.3845, 36.4878]],
                    "intensity": "low",
                    "name": "Housing Road"
                }
            ]
        
        if 'congestion_points' not in st.session_state:
            st.session_state.congestion_points = [
                {
                    "location": [28.3835, 36.4868],
                    "level": "severe",
                    "delay": "15 mins",
                    "description": "Main Gate Congestion"
                },
                {
                    "location": [28.3840, 36.4873],
                    "level": "moderate",
                    "delay": "8 mins",
                    "description": "Engineering College Junction"
                }
            ]

    @st.cache_data(ttl=1800)  # Cache for 30 minutes
    def generate_traffic_timeline(self):
        hours = list(range(6, 24))
        return [random.randint(30, 100) for _ in hours]

    @st.cache_data(ttl=1800)  # Cache for 30 minutes
    def generate_heat_data(self):
        heat_data = []
        for loc in st.session_state.campus_locations.values():
            for _ in range(20):
                lat = loc[0] + random.uniform(-0.001, 0.001)
                lon = loc[1] + random.uniform(-0.001, 0.001)
                weight = random.uniform(0.2, 1.0)
                heat_data.append([lat, lon, weight])
        return heat_data

    def add_traffic_flow(self, m):
        colors = {
            "low": "#00ff00",
            "medium": "#ffa500",
            "high": "#ff0000"
        }
        
        for road in st.session_state.roads:
            folium.PolyLine(
                road["coordinates"],
                weight=5,
                color=colors[road["intensity"]],
                popup=f"{road['name']} - Traffic: {road['intensity'].title()}",
                opacity=0.8,
                dash_array='10'
            ).add_to(m)
    
    def add_congestion_markers(self, m):
        for point in st.session_state.congestion_points:
            folium.CircleMarker(
                location=point["location"],
                radius=15,
                color="red" if point["level"] == "severe" else "orange",
                fill=True,
                popup=f"{point['description']}<br>Delay: {point['delay']}"
            ).add_to(m)
    
    def show_traffic_timeline(self):
        if 'traffic_data' not in st.session_state:
            st.session_state.traffic_data = self.generate_traffic_timeline()
        
        hours = list(range(6, 24))
        chart_data = pd.DataFrame({
            'Hour': hours,
            'Traffic Density': st.session_state.traffic_data
        })
        
        st.line_chart(chart_data.set_index('Hour'))

    def show_dashboard(self):
        st.subheader("Campus Traffic Map | خريطة حركة المرور في الحرم الجامعي")
        
        # Add manual refresh button with longer interval warning
        if st.button('Refresh Data | تحديث البيانات (Updates every 30 minutes)'):
            st.session_state.clear()  # Clear all cached data
            st.rerun()  # Rerun the app to regenerate data
        
        # Create traffic map with all visualizations
        m = folium.Map(location=TABUK_UNIVERSITY_COORDS, zoom_start=16)
        
        # Add campus locations
        for name, coords in st.session_state.campus_locations.items():
            folium.Marker(
                coords,
                popup=name,
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
        
        # Add traffic flow visualization
        self.add_traffic_flow(m)
        
        # Add congestion points
        self.add_congestion_markers(m)
        
        # Add heatmap layer
        if 'heat_data' not in st.session_state:
            st.session_state.heat_data = self.generate_heat_data()
        
        plugins.HeatMap(st.session_state.heat_data, min_opacity=0.4).add_to(m)
        
        # Display the map
        st_folium(m, width=None, height=500)
        
        # Display traffic timeline
        st.subheader("Traffic Density Timeline | جدول زمني لكثافة المرور")
        self.show_traffic_timeline()
        
        # Display metrics with cached data
        st.subheader("Quick Stats | إحصائيات سريعة")
        if 'metrics' not in st.session_state:
            st.session_state.metrics = {
                "Active Rides | رحلات نشطة": [random.randint(10, 50), "rides"],
                "CO2 Saved | ثاني أكسيد الكربون الموفر": [random.randint(100, 500), "kg"],
                "Temperature | درجة الحرارة": [random.randint(25, 45), "°C"],
                "Air Quality | جودة الهواء": [random.randint(50, 150), "AQI"]
            }
        
        col1, col2, col3, col4 = st.columns(4)
                for (label, (value, unit)), col in zip(st.session_state.metrics.items(), [col1, col2, col3, col4]):
                    with col:
                        st.metric(label=label, value=f"{value} {unit}")
        
            def show_route_planner(self):
                st.subheader("Route Planner | مخطط الطريق")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    start = st.selectbox("Start Location | موقع البداية", list(st.session_state.campus_locations.keys()))
                    end = st.selectbox("End Location | موقع النهاية", list(st.session_state.campus_locations.keys()))
                    
                    if st.button("Find Route | ابحث عن الطريق"):
                        self.calculate_route(start, end)
                
                with col2:
                    st.markdown("### Route Details | تفاصيل الطريق")
                    self.display_route_details()
        
            def calculate_route(self, start, end):
                if start and end and start != end:
                    st.success(f"Route calculated from {start} to {end} | تم حساب الطريق")
                    
                    m = folium.Map(location=TABUK_UNIVERSITY_COORDS, zoom_start=16)
                    
                    self.add_traffic_flow(m)
                    self.add_congestion_markers(m)
                    
                    folium.Marker(
                        st.session_state.campus_locations[start],
                        popup=f"Start: {start}",
                        icon=folium.Icon(color='green')
                    ).add_to(m)
                    
                    folium.Marker(
                        st.session_state.campus_locations[end],
                        popup=f"End: {end}",
                        icon=folium.Icon(color='red')
                    ).add_to(m)
                    
                    folium.PolyLine(
                        locations=[st.session_state.campus_locations[start], st.session_state.campus_locations[end]],
                        weight=3,
                        color='blue',
                        opacity=0.8
                    ).add_to(m)
                    
                    st_folium(m, width=None, height=500)
        
            def display_route_details(self):
                route_stats = {
                    "Distance | المسافة": "1.2 km",
                    "Est. Time | الوقت المقدر": "8 mins",
                    "Carbon Footprint | البصمة الكربونية": "0.3 kg CO2",
                    "Traffic Level | مستوى حركة المرور": "Low | منخفض"
                }
                
                for key, value in route_stats.items():
                    st.metric(label=key, value=value)
        
            def show_ride_sharing(self):
                st.subheader("Ride Sharing | مشاركة الركوب")
                
                tab1, tab2 = st.tabs(["Find a Ride | ابحث عن رحلة", "Offer a Ride | اعرض رحلة"])
                
                with tab1:
                    self.find_ride_form()
                
                with tab2:
                    self.offer_ride_form()
        
            def find_ride_form(self):
                pickup = st.selectbox("Pickup Location | موقع الالتقاط", list(st.session_state.campus_locations.keys()))
                destination = st.selectbox("Destination | الوجهة", list(st.session_state.campus_locations.keys()))
                date = st.date_input("Date | التاريخ", key="find_ride_date")
                time = st.time_input("Preferred Time | الوقت المفضل", key="find_ride_time")
                
                if st.button("Search Rides | البحث عن الرحلات"):
                    self.display_available_rides()
        
            def offer_ride_form(self):
                start = st.selectbox("Start Location | موقع البداية", list(st.session_state.campus_locations.keys()))
                end = st.selectbox("End Location | موقع النهاية", list(st.session_state.campus_locations.keys()))
                date = st.date_input("Date | التاريخ", key="offer_ride_date")
                time = st.time_input("Departure Time | وقت المغادرة", key="offer_ride_time")
                seats = st.number_input("Available Seats | المقاعد المتاحة", 1, 4)
                
                if st.button("Offer Ride | عرض الرحلة"):
                    st.success("Ride offered successfully! | تم عرض الرحلة بنجاح")
        
            def display_available_rides(self):
                if 'available_rides' not in st.session_state:
                    st.session_state.available_rides = pd.DataFrame({
                        'Driver | السائق': ['Abdullah M.', 'Fatima S.', 'Mohammed K.'],
                        'Time | الوقت': ['9:00 AM', '9:30 AM', '10:00 AM'],
                        'Price | السعر': ['15 SAR', '20 SAR', '12 SAR'],
                        'Rating | التقييم': ['⭐⭐⭐⭐', '⭐⭐⭐⭐⭐', '⭐⭐⭐']
                    })
                
                st.dataframe(st.session_state.available_rides)
        
            def show_analytics(self):
                st.subheader("Traffic Analytics | تحليلات حركة المرور")
                
                st.markdown("### Traffic Patterns | أنماط حركة المرور")
                self.show_traffic_timeline()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Weekly Statistics | إحصائيات أسبوعية")
                    if 'weekly_stats' not in st.session_state:
                        st.session_state.weekly_stats = pd.DataFrame({
                            'Day | اليوم': ['Sun | الأحد', 'Mon | الاثنين', 'Tue | الثلاثاء', 'Wed | الأربعاء', 'Thu | الخميس'],
                            'Rides | الرحلات': [45, 52, 38, 41, 55],
                            'CO2 Saved (kg) | ثاني أكسيد الكربون الموفر': [90, 104, 76, 82, 110]
                        })
                    st.dataframe(st.session_state.weekly_stats)
                    
                with col2:
                    st.markdown("### Popular Routes | الطرق الشائعة")
                    if 'popular_routes' not in st.session_state:
                        st.session_state.popular_routes = pd.DataFrame({
                            'Route | الطريق': ['Main Gate-Engineering | البوابة الرئيسية-الهندسة', 
                                              'Library-Medicine | المكتبة-الطب', 
                                              'Housing-Main Gate | السكن-البوابة الرئيسية'],
                            'Usage | الاستخدام': ['35%', '28%', '22%']
                        })
                    st.dataframe(st.session_state.popular_routes)
                    
                st.subheader("Traffic Heatmap | خريطة الحرارة لحركة المرور")
                m = folium.Map(location=TABUK_UNIVERSITY_COORDS, zoom_start=16)
                
                for name, coords in st.session_state.campus_locations.items():
                    folium.Marker(
                        coords,
                        popup=name,
                        icon=folium.Icon(color='red', icon='info-sign')
                    ).add_to(m)
                
                self.add_traffic_flow(m)
                self.add_congestion_markers(m)
                
                if 'analytics_heat_data' not in st.session_state:
                    st.session_state.analytics_heat_data = self.generate_heat_data()
                
                plugins.HeatMap(st.session_state.analytics_heat_data).add_to(m)
                
                st_folium(m, width=None, height=500)

if __name__ == "__main__":
    app = TabukEcoMoveOptimizer()
    app.main()
