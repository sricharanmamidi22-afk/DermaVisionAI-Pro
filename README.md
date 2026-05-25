# DermaVisionAI - Advanced AI Dermatology Assistant

A modern, AI-powered dermatology application that provides instant skin analysis, personalized treatment recommendations, and 24/7 access to an AI dermatologist.

## 🚀 Features

- **Real-time Skin Analysis**: Uses computer vision to analyze skin conditions from photos
- **AI Dermatologist Chatbot**: Get instant responses to dermatology questions
- **User Authentication**: Secure user accounts with analysis history
- **Personalized Reports**: Track your skin health over time
- **Modern UI**: Clean, responsive design with medical aesthetics
- **Real AI Models**: OpenCV-based image processing for accurate analysis

## 🛠️ Technology Stack

- **Backend**: Python Flask with SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript
- **AI/ML**: OpenCV, MediaPipe for computer vision
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Flask-Login

## 📋 Prerequisites

- Python 3.8+
- pip package manager

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/DermaVisionAI.git
   cd DermaVisionAI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   cd backend
   python app.py
   ```

4. **Open your browser**
   ```
   http://127.0.0.1:5000
   ```

## 📖 Usage

1. **Register** a new account or **Login** to existing one
2. **Scan Your Skin** using the AI scanner with camera or upload
3. **Chat** with the AI dermatologist for questions
4. **View Reports** to track your skin health history

## 🤖 AI Features

- **Acne Detection**: Identifies acne severity and affected areas
- **Skin Tone Analysis**: Determines skin type and tone
- **Condition Recognition**: Detects common skin conditions
- **Personalized Recommendations**: Tailored skincare advice

## 🏗️ Project Structure

```
DermaVisionAI/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py             # Configuration settings
│   ├── database/
│   │   └── models.py         # Database models
│   ├── routes/
│   │   ├── api_routes.py     # API endpoints
│   │   └── web_routes.py     # Web routes
│   ├── services/
│   │   ├── skin_analyzer.py  # Skin analysis service
│   │   └── chatbot_service.py # Chatbot service
│   └── ai_models/
│       └── predictor.py      # AI prediction models
├── frontend/
│   ├── static/
│   │   ├── js/
│   │   │   ├── main.js       # Main application JS
│   │   │   └── scanner.js    # Scanner logic
│   │   ├── models/           # Face detection model assets
│   │   └── uploads/          # User upload storage
│   └── templates/            # Jinja2 templates
│       ├── base.html
│       ├── index.html
│       ├── scanner.html
│       ├── ledger.html
│       ├── login.html
│       ├── register.html
│       └── report.html
├── requirements.txt          # Python dependencies
└── README.md
```

## 🔒 Security

- Password hashing with Werkzeug
- User session management
- File upload validation
- CORS protection

## 🚀 Deployment

### Docker Deployment

```bash
# Build the image
docker build -t dermavisionai .

# Run the container
docker run -p 5000:5000 dermavisionai
```

### Production Deployment

1. Set `SECRET_KEY` environment variable
2. Use a production WSGI server (Gunicorn)
3. Configure a production database (PostgreSQL)
4. Enable HTTPS

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This application is for informational purposes only and should not replace professional medical advice. Always consult with a qualified dermatologist for medical concerns.

## 📞 Support

For support, email support@dermavisionai.com or open an issue on GitHub.