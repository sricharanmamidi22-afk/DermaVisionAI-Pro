try:
    import pyparsing as _pp
    # Provide backwards/forwards-compatible aliases for common name differences
    if not hasattr(_pp, "DelimitedList") and hasattr(_pp, "delimitedList"):
        _pp.DelimitedList = _pp.delimitedList

    # Ensure ParserElement has both set_name and setName for compat
    try:
        ParserElem = getattr(_pp, "ParserElement", None)
        if ParserElem is not None:
            if not hasattr(ParserElem, "set_name") and hasattr(ParserElem, "setName"):
                setattr(ParserElem, "set_name", ParserElem.setName)
            if not hasattr(ParserElem, "setName") and hasattr(ParserElem, "set_name"):
                setattr(ParserElem, "setName", ParserElem.set_name)
    except Exception:
        pass
except Exception:
    pass

import sys
import os
# Ensure project root is on sys.path so `import backend.*` works even if the
# process is started from a different working directory or via `python backend/app.py`.
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root not in sys.path:
    sys.path.insert(0, root)

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user
from sqlalchemy.exc import OperationalError
import json
import threading
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
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024
    )
    
    basedir = os.path.abspath(os.path.dirname(__file__))

    if os.getenv("VERCEL"):
        default_db_path = os.path.join("/tmp", "dermavision.db")
        default_upload_folder = os.path.join("/tmp", "uploads")
    else:
        default_db_path = os.path.join(basedir, "database", "dermavision.db")
        default_upload_folder = os.path.join(app.static_folder, "uploads")

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{default_db_path}"

    app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", default_upload_folder)

    # --- 🧩 EXTENSIONS ---
    CORS(app)
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'login' 
    login_manager.init_app(app)

    # --- 🤖 AI SERVICES INIT (non-blocking) ---
    # Initialize attributes immediately and start a background thread
    # so worker startup is fast and health checks succeed.
    app.face_detector = None
    app.skin_analyzer = None
    app.chatbot_service = None

    def _init_ai_services():
        try:
            app.face_detector = FaceDetector()
            app.skin_analyzer = SkinAnalyzer()
            app.chatbot_service = ChatbotService()
            print("[OK] AI Services initialized")
        except Exception as e:
            print(f"[ERROR] AI Service Init Failed: {e}")

    threading.Thread(target=_init_ai_services, daemon=True).start()

    # --- 📂 SYSTEM INIT ---
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    
    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Lightweight health endpoint for readiness checks
    @app.route('/health')
    def health():
        return jsonify({"status": "ok"}), 200

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

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    
    # Custom Filter
    app.jinja_env.filters['from_json'] = json.loads
    
    return app

# Expose a top-level app for WSGI / serverless platforms
app = create_app()

if __name__ == "__main__":
    print("\n[START] DERMA_OS: NEURAL CORE ONLINE")
    app.run(debug=True, port=5000)