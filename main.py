from flask import Flask, render_template, url_for, redirect, request

# Flask object
app = Flask(__name__)

# Import routes
import routes

