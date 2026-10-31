
import os

class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "learnova-development-key-change-before-deployment"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///learnova.db"
    ).replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
