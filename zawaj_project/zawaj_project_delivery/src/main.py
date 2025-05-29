import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import logging
from datetime import datetime

# إعداد التطبيق
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tayseer_zawaj_secret_key_2025'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# تكوين قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"

# تهيئة قاعدة البيانات
db = SQLAlchemy(app)

# استيراد النماذج
from src.models.models import User, Profile, MatchRequest, Conversation, Message, SupportTicket
from src.models.models import SupportResponse, Report, VerificationRequest, Statistics
from src.models.models import UserType, MaritalStatus, ReligiousLevel, IncomeLevel, RequestStatus

# استيراد المسارات
from src.routes.auth import auth_bp
from src.routes.user import user_bp
from src.routes.admin import admin_bp
from src.routes.match import match_bp
from src.routes.support import support_bp

# تسجيل المسارات
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(match_bp)
app.register_blueprint(support_bp)

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# صفحة الخطأ 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# صفحة الخطأ 500
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# تهيئة قاعدة البيانات وإنشاء البيانات التجريبية
@app.cli.command('init-db')
def init_db_command():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    db.create_all()
    print('تم تهيئة قاعدة البيانات بنجاح!')

@app.cli.command('create-sample-data')
def create_sample_data_command():
    """إنشاء بيانات تجريبية"""
    from models.sample_data import create_sample_data
    create_sample_data()
    print('تم إنشاء البيانات التجريبية بنجاح!')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
