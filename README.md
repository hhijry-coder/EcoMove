
# EcoMove - Tabuk University Traffic Analysis System

## Overview
EcoMove is a comprehensive traffic analysis and ride-sharing system developed for Tabuk University. The application provides real-time traffic monitoring, eco-friendly ride-sharing coordination, and environmental impact analysis using Streamlit and the TomTom Traffic API.

## Features
- Real-time traffic pattern analysis and visualization
- Eco-friendly ride-sharing system
- Environmental impact tracking
- Historical data analysis
- Interactive dashboards
- Schedule management
- Route optimization

## Tech Stack
- Python 3.8+
- Streamlit
- TomTom Traffic API
- Plotly
- Folium
- Pandas
- NumPy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ecomove.git
cd ecomove
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export TOMTOM_API_KEY="your_api_key_here"
```

## Configuration
1. Update the Config class in `app.py` with your specific settings:
   - TomTom API key
   - Campus locations
   - Ride-share points
   - Environmental parameters

2. Customize the time slots and peak hours in the configuration to match your university's schedule.

## Usage
1. Run the application:
```bash
streamlit run app.py
```

2. Access the application in your web browser at `http://localhost:8501`

## Features Documentation

### Traffic Analysis
- Real-time traffic flow monitoring
- Congestion level tracking
- Incident reporting
- Historical pattern analysis

### Ride-Share System
- Schedule management
- Capacity tracking
- Route optimization
- Real-time availability updates

### Environmental Impact
- CO₂ emissions tracking
- Health impact calculations
- Environmental equivalents
- Transportation mode analysis

### Analytics
- Usage pattern recognition
- Capacity utilization metrics
- Peak hour analysis
- Route popularity tracking

## Deployment
The application can be deployed to various platforms:

### Heroku Deployment
1. Create a new Heroku app
2. Set up environment variables in Heroku dashboard
3. Deploy using the provided Procfile

### Local Server Deployment
1. Set up environment variables
2. Run setup.sh
3. Start the application using the Procfile

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- TomTom for providing the traffic API
- Streamlit for the web framework
- Tabuk University for the collaboration

---
## Tabuk University - SmartTransportationTeam
