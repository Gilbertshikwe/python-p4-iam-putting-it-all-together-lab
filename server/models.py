from sqlalchemy.ext.hybrid import hybrid_property  #type:ignore
from sqlalchemy_serializer import SerializerMixin  #type:ignore
from sqlalchemy import ForeignKey  #type:ignore
from sqlalchemy.orm import relationship  #type:ignore
from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128))
    image_url = db.Column(db.String(200))
    bio = db.Column(db.String(200))

    recipes = relationship('Recipe', backref='author', lazy=True)

    @hybrid_property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.String(500), nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"Recipe('{self.title}', '{self.instructions}', '{self.minutes_to_complete}')"
