# test_email.py
from app import create_app
from app.email_service import send_email

app = create_app()

with app.app_context():
    # Change this to your email
    test_email = input("Enter your email address to test: ")

    success = send_email(
        subject="Test Email from E-Signature System",
        recipient=test_email,
        body="If you're reading this, email is working!"
    )

    if success:
        print("✅ Email sent successfully! Check your inbox.")
    else:
        print("❌ Failed to send email. Check your .env configuration.")