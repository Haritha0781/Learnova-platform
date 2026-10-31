
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(30), nullable=False)

    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.Integer, nullable=True)


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    admin_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(255), nullable=False)
    target_user_id = db.Column(db.Integer, nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
