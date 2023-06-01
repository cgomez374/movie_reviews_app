from main import app, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Configuration
db = SQLAlchemy()

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"

db.init_app(app)


# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=False, nullable=False)
    email = db.Column(db.String(60), index=True, unique=True, nullable=False)
    hashed_password = db.Column(db.String(100), index=False, unique=False)

    def set_password(self, new_password):
        self.hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)

    def check_password(self, maybe_password):
        return check_password_hash(pwhash=self.hashed_password, password=maybe_password)
