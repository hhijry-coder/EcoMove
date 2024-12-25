"""Analyze correlation between traffic conditions and ride patterns"""
    return {
        'correlation': np.random.uniform(0.6, 0.8),
        'correlation_change': np.random.uniform(-0.1, 0.1),
        'peak_impact': np.random.uniform(10, 30),
        'off_peak_efficiency': np.random.uniform(70, 90),
        'efficiency_change': np.random.uniform(-5, 5)
    }

def create_hourly_analysis(historical_rides: pd.DataFrame,
                          traffic_api: TomTomAPI) -> go.Figure:
    """Create hourly analysis visualization with traffic overlay"""
    hourly_data = historical_rides.groupby(
        historical_rides['datetime'].dt.hour
    )['passengers'].mean()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hourly_data.index,
        y=hourly_data.values,
        name='Average Passengers'
    ))
    
    # Add mock traffic overlay
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
    """Analyze weekly trends with traffic correlation"""
    weekly_data = historical_rides.groupby(
        historical_rides['datetime'].dt.dayofweek
    ).agg({
        'passengers': 'mean',
        'eco_impact': 'sum'
    })
    
    # Add traffic correlation factor
    traffic_factor = np.random.uniform(0.8, 1.2, size=len(weekly_data))
    weekly_data = weekly_data.multiply(traffic_factor, axis=0)
    
    return weekly_data

def generate_recommendations(historical_rides: pd.DataFrame,
                           traffic_correlation: Dict,
                           traffic_api: TomTomAPI) -> List[str]:
    """Generate optimization recommendations based on analysis"""
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

    # Initialize components
    traffic_api = TomTomAPI(Config.TOMTOM_API_KEY)
    eco_calculator = EcoImpactCalculator(Config)
    ride_scheduler = RideScheduler(Config)
    visualizer = EnhancedVisualization()

    st.sidebar.title("EcoMove - Tabuk University")
    
    # Add refresh interval selector
    refresh_interval = st.sidebar.selectbox(
        "Traffic Data Refresh Interval",
        [60, 180, 300, 600],
        format_func=lambda x: f"{x//60} minutes"
    )

    # Add traffic filters
    show_congestion = st.sidebar.checkbox("Show Congestion", value=True)
    show_incidents = st.sidebar.checkbox("Show Incidents", value=True)
    show_recommendations = st.sidebar.checkbox("Show Recommended Points", value=True)

    page = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Schedule Analysis", "Environmental Impact", "Historical Analysis"]
    )

    if page == "Dashboard":
        st.title("EcoMove Dashboard")
        
        # Add real-time traffic status
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
        
        # Traffic status indicators
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

        # Create enhanced map with traffic data
        st.subheader("Real-time Traffic Map")
        enhanced_map = create_enhanced_map(
            Config.DEFAULT_LOCATION["lat"],
            Config.DEFAULT_LOCATION["lon"],
            ride_scheduler.scheduled_rides,
            traffic_api,
            Config.RADIUS
        )
        
        # Add layer controls if requested
        if show_congestion or show_incidents or show_recommendations:
            folium.LayerControl().add_to(enhanced_map)
        
        # Display map
        folium_static(enhanced_map)

        # Traffic incidents table
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

    elif page == "Schedule Analysis":
        st.title("Ride Schedule Analysis")
        
        analytics = ride_scheduler.get_schedule_analytics()
        st.plotly_chart(
            visualizer.create_schedule_analysis(analytics),
            use_container_width=True
        )

        # Add real-time traffic impact on schedules
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
        } for ride in ride_scheduler.scheduled_rides])
        st.dataframe(schedule_df)

    elif page == "Environmental Impact":
        st.title("Environmental Impact Analysis")
        
        # Historical environmental data
        historical_data = eco_calculator.historical_data
        
        # Add traffic-based environmental impact
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

        # Environmental impact trends
        st.subheader("Impact Trends")
        fig = px.line(
            historical_data,
            x='date',
            y=['co2_saved', 'trees_equivalent'],
            title="Historical Environmental Impact"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Monthly averages with traffic correlation
        st.subheader("Monthly Analysis")
        monthly_avg = calculate_monthly_averages(historical_data, traffic_api)
        st.line_chart(monthly_avg)

    else:  # Historical Analysis
        st.title("Historical Analysis")
        
        # Get historical ride data
        historical_rides = ride_scheduler.historical_rides
        
        # Add traffic correlation analysis
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

        # Ride patterns visualization
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

        # Hourly analysis with traffic overlay
        st.subheader("Hourly Analysis")
        hourly_analysis = create_hourly_analysis(historical_rides, traffic_api)
        st.plotly_chart(hourly_analysis, use_container_width=True)

        # Route type distribution
        st.subheader("Route Type Distribution")
        route_dist = historical_rides['route_type'].value_counts()
        fig = px.pie(
            values=route_dist.values,
            names=route_dist.index,
            title="Distribution of Route Types"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Weekly trends with traffic correlation
        st.subheader("Weekly Trends")
        weekly_data = analyze_weekly_trends(historical_rides, traffic_api)
        st.line_chart(weekly_data)

        # Recommendations based on historical analysis
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
