from ..utils.db import db
from datetime import datetime

class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer(), primary_key=True)
    username=db.Column(db.String(45), unique=True, nullable=False)
    email=db.Column(db.String(45), unique=True, nullable=False)
    password_hash=db.Column(db.String(255), nullable=False)
    created_at=db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at=db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User: {self.username}>'

    def save(self):
        """
            Saves the user to the database.
        """
        db.session.add(self)
        db.session.commit()
