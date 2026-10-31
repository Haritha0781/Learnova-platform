
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "platform": "LEARNOVA",
        "tagline": "Learn. Innovate. Connect.",
        "status": "Backend is running!"
    })

@app.route("/api/health")
def health():
    return jsonify({
        "status": "success",
        "message": "LEARNOVA API is active"
    })

if __name__ == "__main__":
    app.run(debug=True)
