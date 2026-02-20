"""
AJAX Blueprint

Internal app API
Each route is a endpoint accessible by JS at 'ajax/[endpoint]'
"""

from typing import cast
from flask import Blueprint, render_template, url_for, send_file, jsonify, request, current_app

from app import AppContext


# Cast app_context typing
app = cast(AppContext, current_app)
# Create blueprint
ajax = Blueprint('ajax', __name__)


# TIPS: Access context service like so:
# app.my_service



