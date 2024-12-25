import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import json
import random
from PIL import Image
import numpy as np

GOOGLE_MAPS_API_KEY = "AIzaSyAuyGwowFvbkrhbHqewP2PsBPT2o8fXBuU"
TABUK_UNIVERSITY_COORDS = [28.3835, 36.4868]  # Tabuk University coordinates

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
        
    def setup_config(self):
        st.set_page_config(
            page_title="Tabuk University EcoMove",
            page_icon="🚗",
            layout="wide"
        )
        
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
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Campus Traffic Map | خريطة حركة المرور في الحرم الجامعي")
            self.display_traffic_map()
            
        with col2:
            st.subheader("Quick Stats | إحصائيات سريعة")
            self.display_quick_stats()
        
        st.subheader("Notifications | إشعارات")
        self.display_notifications()

    def display_traffic_map(self):
        m = folium.Map(
            location=TABUK_UNIVERSITY_COORDS,
            zoom_start=16
        )
        
        # Add campus locations
        for name, coords in self.campus_locations.items():
            folium.Marker(
                coords,
                popup=name,
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
        
        # Add traffic layer
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=traffic',
            attr='Google Maps Traffic',
            name='Traffic'
        ).add_to(m)
        
        folium_static(m)

    def display_quick_stats(self):
        cols = st.columns(2)
        
        stats = {
            "Active Rides | رحلات نشطة": [random.randint(10, 50), "rides"],
            "CO2 Saved | ثاني أكسيد الكربون الموفر": [random.randint(100, 500), "kg"],
            "Temperature | درجة الحرارة": [random.randint(25, 45), "°C"],
            "Air Quality | جودة الهواء": [random.randint(50, 150), "AQI"]
        }
        
        for i, (label, (value, unit)) in enumerate(stats.items()):
            with cols[i % 2]:
                st.metric(label=label, value=f"{value} {unit}")

    def display_notifications(self):
        notifications = [
            "Heavy traffic at Main Gate | حركة مرور كثيفة عند البوابة الرئيسية",
            "New shuttle service to Student Housing | خدمة نقل جديدة إلى سكن الطلاب",
            "Weather alert: Sandstorm expected | تنبيه الطقس: عاصفة رملية متوقعة"
        ]
        
        for note in notifications:
            st.info(note)

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
            
            # Display route on map
            m = folium.Map(location=TABUK_UNIVERSITY_COORDS, zoom_start=16)
            
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
            
            # Draw line between points
            folium.PolyLine(
                locations=[self.campus_locations[start], self.campus_locations[end]],
                weight=2,
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
        
        self.display_heatmap()
        self.display_usage_stats()

    def display_heatmap(self):
        st.subheader("Campus Traffic Heatmap | خريطة الحرارة لحركة المرور في الحرم الجامعي")
        data = np.random.rand(10, 10)
        st.image(Image.fromarray(np.uint8(data * 255)), caption="Traffic Density | كثافة حركة المرور")

    def display_usage_stats(self):
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

if __name__ == "__main__":
    app = TabukEcoMoveOptimizer()
    app.main()
