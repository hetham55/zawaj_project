from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.models import db, User, Profile, UserType, MaritalStatus, ReligiousLevel, IncomeLevel
from datetime import datetime
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# دالة للتحقق من تسجيل الدخول
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# دالة للتحقق من صلاحيات المدير
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('يرجى تسجيل الدخول للوصول إلى هذه الصفحة', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# صفحة تسجيل الدخول
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            session['user_type'] = user.user_type.value
            
            # تحديث آخر تسجيل دخول
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash('تم تسجيل الدخول بنجاح', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.profile'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    
    return render_template('auth/login.html')

# صفحة تسجيل حساب جديد
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user_type = request.form.get('user_type')
        
        # التحقق من تطابق كلمة المرور
        if password != confirm_password:
            flash('كلمة المرور وتأكيدها غير متطابقين', 'danger')
            return render_template('auth/register.html')
        
        # التحقق من عدم وجود حساب بنفس اسم المستخدم أو البريد الإلكتروني أو رقم الهاتف
        existing_user = User.query.filter((User.username == username) | 
                                         (User.email == email) | 
                                         (User.phone == phone)).first()
        if existing_user:
            flash('اسم المستخدم أو البريد الإلكتروني أو رقم الهاتف مستخدم بالفعل', 'danger')
            return render_template('auth/register.html')
        
        # إنشاء حساب جديد
        try:
            new_user = User(
                username=username,
                email=email,
                phone=phone,
                user_type=UserType(user_type),
                is_admin=False,
                is_active=True,
                is_verified=False,
                created_at=datetime.utcnow()
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            # إنشاء ملف شخصي فارغ للمستخدم الجديد
            new_profile = Profile(
                user_id=new_user.id,
                marital_status=MaritalStatus.SINGLE
            )
            
            db.session.add(new_profile)
            db.session.commit()
            
            flash('تم إنشاء الحساب بنجاح، يمكنك الآن تسجيل الدخول', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إنشاء الحساب: {str(e)}', 'danger')
    
    return render_template('auth/register.html', user_types=UserType)

# صفحة تسجيل الخروج
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('index'))

# صفحة استعادة كلمة المرور
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # في التطبيق الحقيقي، هنا سيتم إرسال رابط إعادة تعيين كلمة المرور عبر البريد الإلكتروني
            flash('تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني', 'success')
        else:
            flash('البريد الإلكتروني غير مسجل في النظام', 'danger')
    
    return render_template('auth/forgot_password.html')

# صفحة إعادة تعيين كلمة المرور
@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # في التطبيق الحقيقي، هنا سيتم التحقق من صحة الرمز وإعادة تعيين كلمة المرور
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('كلمة المرور وتأكيدها غير متطابقين', 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        flash('تم إعادة تعيين كلمة المرور بنجاح، يمكنك الآن تسجيل الدخول', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)
