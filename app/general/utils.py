from app import db
from app.models import Contact
from flask_login import current_user


# post message to database
def post_contact_to_db(user_email, user_message):
    # insert message into Contact table
    new_message = Contact(
        username=current_user.username,
        email=user_email,
        message=user_message
        )
    db.session.add(new_message)
    db.session.commit()