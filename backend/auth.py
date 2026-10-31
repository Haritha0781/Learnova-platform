
from flask import Blueprint, request, jsonify, session
from argon2 import PasswordHasher
from argon2.exceptions import (
    VerifyMismatchError,
    VerificationError,
    InvalidHashError
)
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.exc import IntegrityError

from models import db, User

auth_bp = Blueprint("auth", __name__)
password_hasher = PasswordHasher()

ALLOWED_ROLES = {
    "student",
    "teacher",
    "school",
    "industry_partner"
}


def public_user_data(user):
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "status": user.status
    }


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    full_name = data.get("full_name", "")
    email = data.get("email", "")
    password = data.get("password", "")
    role = data.get("role", "student")

    if not all(isinstance(value, str) for value in
               [full_name, email, password, role]):
        return jsonify({
            "status": "error",
            "message": "All fields must be valid text."
        }), 400

    full_name = full_name.strip()
    email = email.strip().lower()
    role = role.strip().lower()

    if not full_name or len(full_name) > 150:
        return jsonify({
            "status": "error",
            "message": "Enter a valid full name."
        }), 400

    if role not in ALLOWED_ROLES:
        return jsonify({
            "status": "error",
            "message": "Invalid account role."
        }), 400

    if len(password) < 8 or len(password) > 128:
        return jsonify({
            "status": "error",
            "message": "Password must be 8 to 128 characters long."
        }), 400

    try:
        email = validate_email(
            email,
            check_deliverability=False
        ).normalized
    except EmailNotValidError:
        return jsonify({
            "status": "error",
            "message": "Enter a valid email address."
        }), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            "status": "error",
            "message": "An account with this email already exists."
        }), 409

    new_user = User(
        full_name=full_name,
        email=email,
        password_hash=password_hasher.hash(password),
        role=role,
        status="pending"
    )

    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "An account with this email already exists."
        }), 409
    except Exception:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Registration failed. Please try again."
        }), 500

    return jsonify({
        "status": "success",
        "message": "Registration submitted. Your account is awaiting approval.",
        "user": public_user_data(new_user)
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "")
    password = data.get("password", "")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "status": "error",
            "message": "Email and password are required."
        }), 400

    email = email.strip().lower()

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid email or password."
        }), 401

    try:
        password_hasher.verify(user.password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return jsonify({
            "status": "error",
            "message": "Invalid email or password."
        }), 401

    if user.status != "approved":
        return jsonify({
            "status": "error",
            "message": "Your account is awaiting admin approval."
        }), 403

    session.clear()
    session["user_id"] = user.id

    return jsonify({
        "status": "success",
        "message": "Login successful.",
        "user": public_user_data(user)
    }), 200


@auth_bp.route("/me", methods=["GET"])
def current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "status": "error",
            "message": "Please log in first."
        }), 401

    user = db.session.get(User, user_id)

    if not user or user.status != "approved":
        session.clear()
        return jsonify({
            "status": "error",
            "message": "Your session is invalid or your account is not approved."
        }), 401

    return jsonify({
        "status": "success",
        "user": public_user_data(user)
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "status": "success",
        "message": "Logged out successfully."
    }), 200
