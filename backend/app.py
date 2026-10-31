
from flask import Flask, jsonify
from sqlalchemy import text

from config import Config
from models import db

app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Database settings
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)


@app.route("/")
def home():
    return jsonify({
        "platform": "LEARNOVA",
        "tagline": "Learn. Innovate. Connect.",
        "status": "Backend is running!"
    })


@app.route("/api/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))

        return jsonify({
            "status": "success",
            "message": "LEARNOVA API is active",
            "database": "connected"
        }), 200

    except Exception:
        return jsonify({
            "status": "error",
            "message": "Database connection failed"
        }), 503


@app.route("/api/platform")
def platform():
    return jsonify({
        "platform": "LEARNOVA",
        "tagline": "Learn. Innovate. Connect.",
        "target_audience": [
            "High School (Classes 8, 9, 10)",
            "Higher Secondary (Classes 11, 12)"
        ],
        "modules": [
            "Internship Hub",
            "Workshops and Events",
            "Career Opportunities",
            "Practical Learning Zone",
            "Student Skill Development",
            "Syllabus-to-Industry Mapper"
        ]
    })


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
