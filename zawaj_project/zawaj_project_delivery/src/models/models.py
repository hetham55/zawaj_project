from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()

# تعريف الأنواع المختلفة للمستخدمين
class UserType(enum.Enum):
    MALE = "ذكر"
    FEMALE = "أنثى"
    GUARDIAN = "ولي أمر"
    MEDIATOR = "وسيط"

# تعريف الحالة الاجتماعية
class MaritalStatus(enum.Enum):
    SINGLE = "أعزب"
    DIVORCED = "مطلق"
    WIDOWED = "أرمل"

# تعريف مستوى الالتزام الديني
class ReligiousLevel(enum.Enum):
    CONSERVATIVE = "محافظ"
    RELIGIOUS = "متدين"
    COMMITTED = "ملتزم"

# تعريف فئات الدخل
class IncomeLevel(enum.Enum):
    LOW = "أقل من 5 آلاف"
    MEDIUM = "5 إلى 10 آلاف"
    HIGH = "أكثر من 10 آلاف"

# تعريف حالة الطلب
class RequestStatus(enum.Enum):
    PENDING = "قيد المراجعة"
    APPROVED = "تمت الموافقة"
    REJECTED = "مرفوض"
    NEEDS_INFO = "يحتاج معلومات إضافية"

# جدول المستخدمين
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    user_type = db.Column(db.Enum(UserType), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # العلاقات مع الجداول الأخرى
    profile = db.relationship('Profile', backref='user', uselist=False, cascade="all, delete-orphan")
    sent_requests = db.relationship('MatchRequest', foreign_keys='MatchRequest.sender_id', backref='sender', lazy='dynamic')
    received_requests = db.relationship('MatchRequest', foreign_keys='MatchRequest.receiver_id', backref='receiver', lazy='dynamic')
    support_tickets = db.relationship('SupportTicket', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

# جدول الملفات الشخصية
class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # البيانات الأساسية
    first_name = db.Column(db.String(50))
    birth_date = db.Column(db.Date)
    nationality = db.Column(db.String(50))
    city = db.Column(db.String(50))
    marital_status = db.Column(db.Enum(MaritalStatus))
    children_count = db.Column(db.Integer, default=0)
    height = db.Column(db.Integer)  # بالسنتيمتر
    weight = db.Column(db.Integer)  # بالكيلوجرام
    skin_color = db.Column(db.String(30))
    
    # الجوانب الدينية والقيمية
    religious_level = db.Column(db.Enum(ReligiousLevel))
    religious_sect = db.Column(db.String(50))
    
    # التعليم والعمل
    education_level = db.Column(db.String(50))
    specialization = db.Column(db.String(100))
    occupation = db.Column(db.String(100))
    income_level = db.Column(db.Enum(IncomeLevel))
    
    # تفضيلات الزواج
    preferred_age_min = db.Column(db.Integer)
    preferred_age_max = db.Column(db.Integer)
    accepts_polygamy = db.Column(db.Boolean)
    wants_independent_housing = db.Column(db.Boolean)
    accepts_different_nationality = db.Column(db.Boolean)
    accepts_misyar = db.Column(db.Boolean)
    accepts_traditional = db.Column(db.Boolean)
    
    # أخرى
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(255))
    has_guardian = db.Column(db.Boolean, default=False)
    guardian_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    preferred_communication = db.Column(db.String(50))
    
    # العلاقات
    guardian = db.relationship('User', foreign_keys=[guardian_id])
    
    def __repr__(self):
        return f'<Profile {self.first_name}>'

# جدول طلبات التوافق
class MatchRequest(db.Model):
    __tablename__ = 'match_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum(RequestStatus), default=RequestStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # العلاقات
    conversations = db.relationship('Conversation', backref='match_request', lazy='dynamic')
    
    def __repr__(self):
        return f'<MatchRequest {self.id}>'

# جدول المحادثات
class Conversation(db.Model):
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    match_request_id = db.Column(db.Integer, db.ForeignKey('match_requests.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # العلاقات
    messages = db.relationship('Message', backref='conversation', lazy='dynamic')
    
    def __repr__(self):
        return f'<Conversation {self.id}>'

# جدول الرسائل
class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    # العلاقات
    sender = db.relationship('User')
    
    def __repr__(self):
        return f'<Message {self.id}>'

# جدول طلبات الدعم
class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(RequestStatus), default=RequestStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    responses = db.relationship('SupportResponse', backref='ticket', lazy='dynamic')
    
    def __repr__(self):
        return f'<SupportTicket {self.id}>'

# جدول ردود الدعم
class SupportResponse(db.Model):
    __tablename__ = 'support_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.id'), nullable=False)
    responder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    responder = db.relationship('User')
    
    def __repr__(self):
        return f'<SupportResponse {self.id}>'

# جدول البلاغات
class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(RequestStatus), default=RequestStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    reporter = db.relationship('User', foreign_keys=[reporter_id])
    reported_user = db.relationship('User', foreign_keys=[reported_user_id])
    
    def __repr__(self):
        return f'<Report {self.id}>'

# جدول طلبات التوثيق
class VerificationRequest(db.Model):
    __tablename__ = 'verification_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    document_path = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum(RequestStatus), default=RequestStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    admin_notes = db.Column(db.Text)
    
    # العلاقات
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<VerificationRequest {self.id}>'

# جدول الإحصائيات
class Statistics(db.Model):
    __tablename__ = 'statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    new_users_count = db.Column(db.Integer, default=0)
    active_users_count = db.Column(db.Integer, default=0)
    successful_matches_count = db.Column(db.Integer, default=0)
    male_users_count = db.Column(db.Integer, default=0)
    female_users_count = db.Column(db.Integer, default=0)
    guardian_users_count = db.Column(db.Integer, default=0)
    mediator_users_count = db.Column(db.Integer, default=0)
    reports_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Statistics {self.date}>'
