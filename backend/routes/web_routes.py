from flask import Blueprint, render_template, abort, current_app
from flask_login import login_required, current_user
from backend.database.models import User, Analysis, Scan
import json

# Define the blueprint
web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    return render_template('index.html')

@web_bp.route('/scanner')
@login_required
def scanner():
    return render_template('scanner.html')

@web_bp.route('/ledger')
@login_required
def ledger():
    """Display all scans for the current user"""
    scans = Scan.query.filter_by(user_id=current_user.id).order_by(Scan.timestamp.desc()).all()
    logs = [scan.to_dict() for scan in scans]
    return render_template('ledger.html', logs=logs)

@web_bp.route('/report/<analysis_id>')
@login_required
def report(analysis_id):
    # Logic to handle the 'Mock' IDs from your workspace JS
    if str(analysis_id).startswith('DV-'):
        mock_data = {
            'id': analysis_id,
            'user_id': current_user.id,
            'result_json': json.dumps({
                'skin_type': 'Combination',
                'overall_score': 82,
                'skin_age': 24,
                'acne_status': 'Mild',
                'circles': 'Minimal',
                'pigment': 'Balanced',
                'moisture': 'Stable',
                'texture': 'Refined',
                'glow': 'Radiant',
                'recommendations': ["Use a gentle cleanser", "Apply SPF 50 daily"],
                'health_score': 82
            }),
            'timestamp': '2026-05-04 10:30:00',
            'image_path': 'demo_face.png' 
        }
        image_url = f'/static/uploads/{mock_data["image_path"]}'
        return render_template('report.html', analysis=mock_data, image_url=image_url, scan_id=analysis_id)
    
    # Try to find by scan_id first (from ledger)
    scan = Scan.query.filter_by(scan_id=analysis_id, user_id=current_user.id).first()
    
    if scan:
        # Found in Scan table - convert to Analysis-like object for template
        try:
            results = json.loads(scan.results)
        except:
            results = {'health_score': 82}
        
        analysis = type('obj', (object,), {
            'id': scan.id,
            'result_json': scan.results,
            'image_path': scan.image_path,
            'timestamp': scan.timestamp.strftime('%Y-%m-%d %H:%M:%S') if scan.timestamp else '',
        })()
        
        image_url = f'/uploads/{scan.image_path}' if scan.image_path else '/static/uploads/default.png'
        return render_template('report.html', analysis=analysis, image_url=image_url, scan_id=scan.id)
    
    # Try to find by Analysis id (integer)
    try:
        analysis = Analysis.query.get_or_404(int(analysis_id))
        
        if analysis.user_id != current_user.id:
            abort(403)
        
        # Construct image URL from image_path
        image_url = f'/uploads/{analysis.image_path}' if analysis.image_path else '/static/uploads/default.png'
        scan_id = analysis.id
        
        return render_template('report.html', analysis=analysis, image_url=image_url, scan_id=scan_id)
    except (ValueError, TypeError):
        # If not an integer and not found in Scan table, return 404
        abort(404)
