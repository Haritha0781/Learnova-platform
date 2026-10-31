
from functools import wraps
from datetime import datetime

from flask import Blueprint, jsonify, session

from models import db, User, AuditLog

admin_bp = Blueprint("admin", __name__)


# Check whether the logged-in user is an approved admin
def admin_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):

        user_id = session.get("user_id")

        if not user_id:
            return jsonify({
                "status": "error",
                "message": "Admin login required."
            }), 401

        admin = db.session.get(User, user_id)

        if (
            not admin
            or admin.role != "admin"
            or admin.status != "approved"
        ):
            return jsonify({
                "status": "error",
                "message": "Admin access denied."
            }), 403

        return function(*args, **kwargs)

    return decorated_function


# Admin dashboard overview
@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():

    total_users = User.query.filter(
        User.role != "admin"
    ).count()

    pending_users = User.query.filter_by(
        status="pending"
    ).count()

    approved_users = User.query.filter_by(
        status="approved"
    ).count()

    return jsonify({
        "status": "success",
        "dashboard": {
            "total_users": total_users,
            "pending_users": pending_users,
            "approved_users": approved_users
        }
    }), 200


# View pending registrations
@admin_bp.route("/pending-users", methods=["GET"])
@admin_required
def pending_users():

    users = User.query.filter_by(
        status="pending"
    ).order_by(User.created_at.desc()).all()

    return jsonify({
        "status": "success",
        "users": [
            {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "created_at": (
                    user.created_at.isoformat()
                    if user.created_at else None
                )
            }
            for user in users
        ]
    }), 200


# Approve a user account
@admin_bp.route("/users/<int:user_id>/approve", methods=["POST"])
@admin_required
def approve_user(user_id):

    admin = db.session.get(User, session["user_id"])
    user = db.session.get(User, user_id)

    if not user or user.role == "admin":
        return jsonify({
            "status": "error",
            "message": "User not found."
        }), 404

    if user.status != "pending":
        return jsonify({
            "status": "error",
            "message": "This account is not awaiting approval."
        }), 409

    user.status = "approved"
    user.approved_at = datetime.utcnow()
    user.approved_by = admin.id

    log = AuditLog(
        admin_id=admin.id,
        action=f"Approved user account: {user.email}",
        target_user_id=user.id
    )

    try:
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Unable to approve this account."
        }), 500

    return jsonify({
        "status": "success",
        "message": "User account approved."
    }), 200


# Suspend a user account
@admin_bp.route("/users/<int:user_id>/suspend", methods=["POST"])
@admin_required
def suspend_user(user_id):

    admin = db.session.get(User, session["user_id"])
    user = db.session.get(User, user_id)

    if not user or user.role == "admin":
        return jsonify({
            "status": "error",
            "message": "User not found."
        }), 404

    user.status = "suspended"

    log = AuditLog(
        admin_id=admin.id,
        action=f"Suspended user account: {user.email}",
        target_user_id=user.id
    )

    try:
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Unable to suspend this account."
        }), 500

    return jsonify({
        "status": "success",
        "message": "User account suspended."
    }), 200
