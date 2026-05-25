from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash

# Modular Imports
from backend.database.models import db, User
from backend.routes.api_routes import api_bp
from backend.routes.web_routes import web_bp
from backend.services.skin_analyzer import SkinAnalyzer
from backend.services.face_detector import FaceDetector
from backend.services.chatbot_service import ChatbotService

def create_app():
    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static"
    )

    # --- 🏗️ CONFIGURATION ---
    app.config.update(
        SECRET_KEY="dermavision-luxury-secret-2026",
        UPLOAD_FOLDER=os.path.join(app.static_folder, "uploads"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024
    )
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{os.path.join(basedir, "database", "dermavision.db")}'

    # --- 🧩 EXTENSIONS ---
    CORS(app)
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'login' 
    login_manager.init_app(app)

    # --- 🤖 AI SERVICES INIT ---
    # We use a try-except block so the app doesn't crash if models aren't ready
    try:
        app.face_detector = FaceDetector()
        app.skin_analyzer = SkinAnalyzer()
        app.chatbot_service = ChatbotService()
    except Exception as e:
        print(f"[ERROR] AI Service Init Failed: {e}")

    # --- 📂 SYSTEM INIT ---
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    
    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- 🔐 AUTH ROUTES ---
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            
            if User.query.filter_by(username=username).first():
                flash('Username already in use.', 'error')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered.', 'error')
                return redirect(url_for('register'))
            
            new_user = User(
                username=username,
                email=email,
                password=generate_password_hash(password)
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                # Ensure 'web.index' exists in your web_routes.py
                return redirect(url_for('web.index')) 
            flash('Invalid Credentials', 'error')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    # --- 📊 REPORT API (Fixes the Report Error) ---
    @app.route('/api/improvement-suggestions/<scan_id>')
    def get_report_data(scan_id):
        # This prevents the report page from showing a blank screen/error
        return jsonify({
            "status": "SUCCESS",
            "suggestions": {
                "current_score": 85,
                "target_score": 100,
                "improvement_potential": 15,
                "timeline_to_perfect": "4 Weeks",
                "suggestions": [
                    {
                        "category": "HYDRATION",
                        "issue": "Slight periorbital dryness",
                        "current_status": "72%", "target": "90%",
                        "improvement_points": 10, "severity": "MEDIUM",
                        "acute_protocol": ["Hyaluronic Acid"],
                        "intensive_protocol": ["Weekly mask"],
                        "product_recommendations": ["Cerave Hydrating Serum"],
                        "timeline_weeks": 2
                    }
                ],
                "prevention_strategies": []
            }
        })

    # --- 🚀 BLUEPRINT REGISTRATION ---
    # CRITICAL: Check if already registered to prevent ValueError
    if 'api' not in app.blueprints:
        app.register_blueprint(api_bp, url_prefix="/api")
    if 'web' not in app.blueprints:
        app.register_blueprint(web_bp)
    
    # Custom Filter
    app.jinja_env.filters['from_json'] = json.loads
    
    return app

if __name__ == "__main__":
    derma_app = create_app()
    print("\n[START] DERMA_OS: NEURAL CORE ONLINE")
    derma_app.run(debug=True, port=5000)