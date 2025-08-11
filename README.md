# Face Recognition Attendance System

A comprehensive Django-based attendance system with face recognition capabilities, modern UI, and robust authentication.

## 📋 Features

### Authentication System
- Advanced login/registration with beautiful gradient UI
- Custom user model with roles (Admin, Manager, Employee, Security)
- Profile management with photo upload
- User management for admins
- Settings panel with security and preferences

### Face Recognition
- Face enrollment system with webcam integration
- Multi-angle capture for accuracy
- Real-time face detection simulation
- Face management interface

### Attendance Management
- Dual check-in methods: Face Recognition + Manual Entry
- Real-time attendance tracking
- Comprehensive history view with filters
- Calendar widget for monthly attendance
- Export functionality for reports

### Modern UI/UX
- Responsive design that works on all devices
- Interactive elements with animations
- Professional styling with gradient backgrounds
- Accessibility features

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL (for production)
- Virtual environment tool (venv or virtualenv)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd face_recognition_attendance_system
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   # For production deployment
   pip install -r requirements.txt
   
   # For development
   pip install -r requirements-dev.txt
   ```

4. For face recognition functionality (optional):
   ```bash
   pip install dlib
   pip install face-recognition
   ```

### Running the Application

1. Set up environment variables (see `.env.example`)

2. Run database migrations:
   ```bash
   python manage.py migrate
   ```

3. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

4. Start the development server:
   ```bash
   python manage.py runserver
   ```

   Or use the provided startup script:
   ```bash
   python start_server.py
   ```

## ☁️ Deployment

This application is ready for deployment on various platforms including Heroku, Runway, and other cloud providers.

### Deployment Options

1. **One-Click Deployment**:
   - Use the `app.json` file for one-click deployment to Heroku/Runway
   - Simply click the "Deploy to Heroku" button in the dashboard

2. **Heroku/Runway**: 
   - The `Procfile` and `runtime.txt` are already configured
   - Set environment variables in the dashboard
   - Deploy using automatic deployment from GitHub

3. **Docker**:
   - Use the provided `Dockerfile` and `docker-compose.yml`
   - Build and run with: `docker-compose up --build`

4. **Traditional Server**:
   - Use the provided deployment guide in `DEPLOYMENT.md`

### Environment Variables

For production deployment, set these environment variables:

```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DB_NAME=your-database-name
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_HOST=your-database-host
DB_PORT=5432
```

See `DEPLOYMENT.md` for detailed deployment instructions.

## 📁 Project Structure

```
attendace/
├── face_recognition_system/     # Main Django project settings
├── authentication/              # Authentication app
├── face_recognition/            # Face recognition app
├── attendance/                  # Attendance management app
├── templates/                   # HTML templates
├── static/                      # CSS, JavaScript, images
├── media/                       # User uploaded files
├── requirements.txt             # Python dependencies
├── Procfile                     # For Heroku/Runway deployment
├── runtime.txt                  # Python version specification
├── Dockerfile                   # For Docker deployment
└── docker-compose.yml           # For Docker Compose setup
```

## 🧪 Testing

Run tests with:
```bash
python manage.py test
```

## 🛠️ Technologies Used

- **Backend**: Django 4.2
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Django's built-in auth system
- **API**: Django REST Framework
- **Deployment**: Gunicorn, Docker

## 📚 Documentation

- `DEPLOYMENT.md`: Detailed deployment instructions
- `SYSTEM_COMPLETION_SUMMARY.md`: Project completion overview

## 👥 User Roles

- **Admin**: Full system access
- **Manager**: Manage attendance and users
- **Employee**: Check in/out, view personal attendance
- **Security**: Attendance verification

## 🔐 Security Features

- CSRF protection
- Role-based access control
- Secure password handling
- Session management
- HTTPS support for production

## 🎨 UI Features

- Modern gradient backgrounds
- Glass morphism design elements
- Responsive layout for all devices
- Interactive animations and transitions
- Accessible design patterns

## 🚀 Ready for Production

This system is production-ready with:
- Proper security settings
- Database configuration for PostgreSQL
- Static file handling
- Deployment configurations
- Docker support
- Environment variable management
