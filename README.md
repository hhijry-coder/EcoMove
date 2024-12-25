![EcoMove Logo](assets/logo.png)

# For online images:
![EcoMove Logo](https://raw.githubusercontent.com/username/repository/branch/assets/logo.png)

# For multiple images:
<div align="center">
  <img src="assets/dashboard.png" alt="Dashboard" width="400"/>
  <img src="assets/heatmap.png" alt="Traffic Heatmap" width="400"/>
</div>

# EcoMove Optimizer - Tabuk University - Smart Transportation Team

Smart transportation solution for optimizing campus traffic and ride-sharing at Tabuk University.

## Features

- Real-time traffic visualization
- Route optimization
- Ride-sharing platform
- Traffic analytics dashboard
- Bilingual support (Arabic/English)

## Installation

```bash
git clone https://github.com/your-repo/ecomove-optimizer.git
cd ecomove-optimizer
pip install -r requirements.txt
```

## Configuration

1. Get a Google Maps API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Create `.env` file:
```
GOOGLE_MAPS_API_KEY=your_api_key_here
```

## Usage

Run the application:
```bash
streamlit run app.py
```

Access at: http://localhost:8501

## Requirements

- Python 3.8+
- Streamlit 1.32.0+
- Folium 0.15.1
- Pandas 2.2.0
- Other dependencies in requirements.txt

## Project Structure

```
ecomove-optimizer/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── .env               # Environment variables
└── README.md
```

## Features Details

### Dashboard
- Traffic heatmap
- Real-time congestion points
- Traffic flow visualization
- Performance metrics

### Route Planner
- Optimal route calculation
- Traffic-aware routing
- Carbon footprint tracking

### Ride Sharing
- Ride matching
- Schedule management
- Real-time availability

### Analytics
- Traffic patterns
- Usage statistics
- Environmental impact metrics

## API Integration

- Google Maps API for real-time traffic data
- Custom traffic simulation for development
- Heatmap visualization using Folium

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create pull request

## License

hhijry-coder/EcoMove is licensed under the
GNU Affero General Public License v3.0
