# add_employee.py
from app import create_app, db
from app.models import User
import secrets
import string
import sys


def generate_temp_password(length=8):
    """Generate a temporary password"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def add_employee(username, email):
    """Add an employee with a temporary password. Returns (success, message, temp_password)"""
    app = create_app()

    with app.app_context():
        # Check if user already exists by email or username
        if User.query.filter_by(email=email).first():
            return False, f"❌ User with email {email} already exists!", None
        if User.query.filter_by(username=username).first():
            return False, f"❌ User with username {username} already exists!", None

        # Generate temporary password
        temp_password = generate_temp_password()

        # Create new employee
        employee = User(
            username=username,
            email=email,
            role='employee'
        )
        employee.set_password(temp_password)

        db.session.add(employee)
        db.session.commit()

        return True, f"✅ Employee added successfully!", temp_password


def add_employee_cli(username, email):
    success, message, temp_password = add_employee(username, email)
    print(f"\n{message}")
    if success:
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Temporary Password: {temp_password}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"\n⚠️  Please share these credentials securely with the employee.")
        print(f"They should change their password after first login.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_employee.py <username> <email>")
        print("Example: python add_employee.py john john@company.com")
        print("\nThis will generate a temporary password automatically.")
    else:
        username = sys.argv[1]
        email = sys.argv[2]
        add_employee_cli(username, email)