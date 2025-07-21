from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from app.add_employee import add_employee
from app.email_service import send_email

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/employee-manager')
@login_required
def employee_manager():
    if not current_user.is_boss():
        flash('Only the boss can manage employees.', 'danger')
        return redirect(url_for('documents.dashboard'))
    return render_template('boss/employee_manager.html')

@employees_bp.route('/add-employee', methods=['POST'])
@login_required
def add_employee_route():
    if not current_user.is_boss():
        flash('Only the boss can add employees.', 'danger')
        return redirect(url_for('documents.dashboard'))
    username = request.form.get('username')
    email = request.form.get('email')
    if not username or not email:
        flash('Username and email are required.', 'danger')
        return redirect(url_for('employees.employee_manager'))
    success, message, temp_password = add_employee(username, email)
    if success:
        # Send email to employee
        subject = 'Your E-Signature System Temporary Password'
        with current_app.app_context():
            login_link = url_for('auth.login', _external=True)
        body = f"Hello {username},\n\nYou have been added to the E-Signature System. Your temporary password is: {temp_password}\n\nPlease log in and reset your password immediately.\n\nLogin here: {login_link}\n\nThank you."
        try:
            send_email(subject, email, body)
            flash(f"{message} The temporary password was sent to {email}. The employee must reset it immediately after logging in.", 'success')
        except Exception as e:
            flash(f"{message} However, there was an error sending the email: {str(e)}", 'danger')
    else:
        flash(message, 'danger')
    return redirect(url_for('employees.employee_manager'))

#testing