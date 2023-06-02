from flask import Flask, render_template, url_for, redirect, request, flash, abort
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

# Flask object
app = Flask(__name__)
app.secret_key = 'secret_key'

# Login Manager config
login_manager = LoginManager()
login_manager.init_app(app)

# Import routes
import routes

