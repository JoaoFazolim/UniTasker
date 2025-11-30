from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if current_user.role != 'admin':
        abort(403)
    return render_template('dashboard.html')