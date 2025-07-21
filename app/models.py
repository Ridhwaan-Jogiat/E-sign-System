from datetime import datetime

import pytz
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.Text)
    role = db.Column(db.String(20))  # 'employee' or 'boss'

    # Relationships
    documents_uploaded = db.relationship(
        'Document',
        backref='uploader',
        lazy='dynamic',
        foreign_keys='Document.uploaded_by'
    )
    signatures = db.relationship('Signature', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_boss(self):
        return self.role == 'boss'


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    original_filename = db.Column(db.String(255))
    file_path = db.Column(db.String(255))
    file_type = db.Column(db.String(10))  # 'pdf' or 'docx'
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    upload_date = db.Column(db.DateTime, default=lambda: datetime.now(pytz.utc))
    status = db.Column(db.String(20), default='pending')  # 'pending', 'signed', 'rejected'
    signed_file_path = db.Column(db.String(255), nullable=True)
    signed_date = db.Column(db.DateTime, nullable=True)

    # New fields for extra document details
    client = db.Column(db.String(120), nullable=True)
    work = db.Column(db.String(120), nullable=True)
    document_type = db.Column(db.String(120), nullable=True)
    comment = db.Column(db.Text, nullable=True)

    # New fields for signature placement
    signature_placement = db.Column(db.Text, nullable=True)  # Store JSON of requested signature positions
    signing_method = db.Column(db.String(20), nullable=True)  # 'auto' or 'manual'

    signed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    signer = db.relationship('User', backref='signed_documents', foreign_keys=[signed_by])

    def __repr__(self):
        return f'<Document {self.original_filename}>'


# In models.py - Update the Signature model
class Signature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    signature_path = db.Column(db.String(255))
    created_date = db.Column(db.DateTime, default=lambda: datetime.now(pytz.utc))
    is_active = db.Column(db.Boolean, default=False)  # Changed from True to False
    signature_type = db.Column(db.String(20), default='signature')  # 'signature', 'initial', or 'company'
    display_name = db.Column(db.String(50))  # Optional name for the signature
    is_default = db.Column(db.Boolean, default=False)  # True if this is the default signature for its type

    def __repr__(self):
        return f'<Signature {self.id} of User {self.user_id}>'


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))