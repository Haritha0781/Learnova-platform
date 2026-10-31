
from getpass import getpass

from argon2 import PasswordHasher
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, User


password_hasher = PasswordHasher()


def create_admin_account(number):

    print(f"\n--- Create Admin {number} of 2 ---")

    email_input = input("Admin email: ").strip().lower()

    try:
        email = validate_email(
            email_input,
            check_deliverability=False
        ).normalized
    except EmailNotValidError:
        print("Invalid email address.")
        return False

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        print("This email is already registered.")
        return False

    password = getpass("Create password (minimum 12 characters): ")
    confirm_password = getpass("Confirm password: ")

    if password != confirm_password:
        print("Passwords do not match.")
        return False

    if len(password) < 12 or len(password) > 128:
        print("Password must be between 12 and 128 characters.")
        return False

    full_name = input("Admin full name: ").strip()

    if not full_name or len(full_name) > 150:
        print("Enter a valid full name.")
        return False

    admin = User(
        full_name=full_name,
        email=email,
        password_hash=password_hasher.hash(password),
        role="admin",
        status="approved"
    )

    try:
        db.session.add(admin)
        db.session.commit()

        print(f"Admin {number} created successfully!")
        return True

    except IntegrityError:
        db.session.rollback()
        print("This email already exists.")
        return False

    except Exception:
        db.session.rollback()
        print("Unable to create this admin account.")
        return False


def setup_admins():

    with app.app_context():

        existing_admins = User.query.filter_by(
            role="admin"
        ).count()

        if existing_admins >= 2:
            print("Two Admin accounts already exist.")
            print("No additional Admin accounts can be created.")
            return

        if existing_admins < 0:
            return

        remaining = 2 - existing_admins

        print("LEARNOVA - Secure Admin Setup")
        print(f"Existing Admin accounts: {existing_admins}")
        print(f"Accounts to create: {remaining}")

        for number in range(existing_admins + 1, 3):

            while True:
                success = create_admin_account(number)

                if success:
                    break

                print("Please try again.")

        print("\nAdmin setup completed.")


if __name__ == "__main__":
    setup_admins()
