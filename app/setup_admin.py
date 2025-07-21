# setup_admin.py
import os
import sys
from getpass import getpass
from app import create_app, db
from app.models import User


def safe_getpass(prompt):
    try:
        return getpass(prompt)
    except Exception:
        print("[Warning] Secure password input not available. Your password will be visible.")
        return input(prompt)


def setup_admin():
    """One-time setup for the boss/admin account"""
    app = create_app()

    with app.app_context():
        # Check if boss already exists
        existing_boss = User.query.filter_by(role='boss').first()
        if existing_boss:
            print("⚠️  A boss account already exists!")
            print(f"   Username: {existing_boss.username}")
            print(f"   Email: {existing_boss.email}")
            response = input("\nDo you want to reset the boss password? (y/n): ")
            if response.lower() != 'y':
                print("Setup cancelled.")
                return

            # Reset password
            password = safe_getpass("Enter new password for boss: ")
            confirm = safe_getpass("Confirm password: ")

            if password != confirm:
                print("❌ Passwords don't match!")
                return

            if len(password) < 6:
                print("❌ Password must be at least 6 characters!")
                return

            existing_boss.set_password(password)
            db.session.commit()
            print("✅ Boss password updated successfully!")
            return

        print("=== E-Signature System - Boss Account Setup ===")
        print("Creating the boss/admin account...\n")

        # Get boss details
        username = input("Enter boss username: ").strip()
        email = input("Enter boss email: ").strip()
        password = safe_getpass("Enter password: ")
        confirm = safe_getpass("Confirm password: ")

        if password != confirm:
            print("❌ Passwords don't match!")
            return

        if len(password) < 6:
            print("❌ Password must be at least 6 characters!")
            return

        # Create boss account
        boss = User(
            username=username,
            email=email,
            role='boss'
        )
        boss.set_password(password)

        db.session.add(boss)
        db.session.commit()

        print("\n✅ Boss account created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print("\n⚠️  Keep these credentials secure!")


if __name__ == "__main__":
    setup_admin()

##python -m app.setup_admin

##pip install -r requirements.txt
