from app import create_app, db
from app.models import User, Document, Signature

app = create_app()


# Add context processor for templates
@app.context_processor
def utility_processor():
    return {
        'is_boss': lambda: hasattr(current_user,
                                   'is_authenticated') and current_user.is_authenticated and current_user.role == 'boss'
    }


# Create a CLI command to create users
@app.cli.command('create-user')
def create_user():
    """Create a new user."""
    import click
    from flask.cli import with_appcontext
    from flask_login import current_user

    username = click.prompt('Username')
    email = click.prompt('Email')
    password = click.prompt('Password', hide_input=True, confirmation_prompt=True)
    role = click.prompt('Role (employee/boss)', type=click.Choice(['employee', 'boss']))

    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    click.echo(f'User {username} created successfully.')

@app.cli.command('create-default-users')
def create_default_users():
    """Create default users for testing."""
    from werkzeug.security import generate_password_hash

    boss = User(username='boss', email='boss@example.com', role='boss', password_hash=generate_password_hash('password'))
    employee = User(username='employee', email='employee@example.com', role='employee', password_hash=generate_password_hash('password'))

    db.session.add_all([boss, employee])
    db.session.commit()

    print("Default users created.")

if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()

        # Check if we need to create a default admin user
        if User.query.filter_by(role='boss').first() is None:
            # Create default boss user
            boss = User(username='boss', email='boss@example.com', role='boss')
            boss.set_password('password')
            db.session.add(boss)

            # Create default employee user
            employee = User(username='employee', email='employee@example.com', role='employee')
            employee.set_password('password')
            db.session.add(employee)

            db.session.commit()
            print('Default users created:')
            print('Boss: boss@example.com / password')
            print('Employee: employee@example.com / password')

    # Run the app in debug mode
    app.run(host='0.0.0.0', port=8000, debug=True)
    #app.run(debug=True)
