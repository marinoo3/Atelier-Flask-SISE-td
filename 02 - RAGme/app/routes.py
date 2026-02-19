"""
Routes Blueprint

Serve HTML pages to the website
Each route is a URL accessible by the user
"""
from flask import Blueprint, render_template


main = Blueprint('main', __name__)


@main.route('/')
def chat():
    return render_template('chat.html')
