# Emergency Response System with Leaflet.js and Google Maps

A Django-based emergency response application with real-time mapping capabilities using Leaflet.js and Google Maps API. The system is designed to manage emergency incidents and coordinate emergency services (Fire, Medical, Police) in the Mombasa Chuda area.

## Features

- **Live Emergency Map**: Real-time incident tracking and visualization using Leaflet.js
- **Emergency Reporting**: Users can report emergencies with GPS location
- **Responder Management**: Track available emergency responders in real-time
- **Department Management**: Manage Fire, Medical, and Police departments
- **Incident Tracking**: Monitor incident status from reported to resolved
- **User Authentication**: Secure login and registration system
- **Responsive Design**: Bootstrap 5 responsive UI
- **Google Maps Integration**: Alternative map provider for detailed information
- **API Endpoints**: JSON APIs for real-time data updates

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup Steps

1. **Navigate to project**
   ```bash
   cd emergencyresponse_pr
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Configure Google Maps API**
   - Get your API key from [Google Cloud Console](https://console.cloud.google.com/)
   - Update in `emergencyresponse_pr/settings.py`:
     ```python
     GOOGLE_MAPS_API_KEY = 'YOUR_API_KEY_HERE'
     ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

Access at: http://localhost:8000

## Quick Start

- Register a new account at `/register/`
- Report an emergency at `/incident/create/`
- View all incidents at `/`
- Access admin at `/admin/`

## Map Features

- **Click to select location**
- **Drag marker to adjust**
- **Use GPS button for auto-location**
- **Real-time responder tracking**
- **Leaflet.js for maps**
- **OpenStreetMap tiles**