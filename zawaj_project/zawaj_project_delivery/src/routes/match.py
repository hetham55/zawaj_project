from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from src.routes.auth import login_required
from src.models.models import db, User, Profile, MatchRequest, Conversation, Message
from src.models.models import UserType, MaritalStatus, ReligiousLevel, IncomeLevel, RequestStatus
from datetime import datetime

match_bp = Blueprint('match', __name__)

# صفحة البحث عن توافقات
@match_bp.route('/search')
@login_required
def search():
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # الحصول على معايير البحث من الاستعلام
    age_min = request.args.get('age_min', type=int)
    age_max = request.args.get('age_max', type=int)
    city = request.args.get('city')
    marital_status = request.args.get('marital_status')
    religious_level = request.args.get('religious_level')
    
    # بناء استعلام البحث
    query = User.query.join(Profile)
    
    # تحديد نوع المستخدم المطلوب بناءً على نوع المستخدم الحالي
    if user.user_type == UserType.MALE:
        query = query.filter(User.user_type == UserType.FEMALE)
    elif user.user_type == UserType.FEMALE:
        query = query.filter(User.user_type == UserType.MALE)
    else:
        # للوسطاء وأولياء الأمور، يمكن البحث عن أي نوع
        user_type = request.args.get('user_type')
        if user_type:
            query = query.filter(User.user_type == UserType(user_type))
    
    # تطبيق معايير البحث إذا تم تحديدها
    if age_min:
        query = query.filter(Profile.birth_date <= datetime.now().replace(year=datetime.now().year - age_min))
    
    if age_max:
        query = query.filter(Profile.birth_date >= datetime.now().replace(year=datetime.now().year - age_max))
    
    if city:
        query = query.filter(Profile.city == city)
    
    if marital_status:
        query = query.filter(Profile.marital_status == MaritalStatus(marital_status))
    
    if religious_level:
        query = query.filter(Profile.religious_level == ReligiousLevel(religious_level))
    
    # تنفيذ الاستعلام
    results = query.filter(User.is_active == True).all()
    
    # الحصول على قائمة المدن المتاحة للفلترة
    cities = db.session.query(Profile.city).distinct().all()
    cities = [city[0] for city in cities if city[0]]
    
    return render_template('match/search.html',
                          results=results,
                          cities=cities,
                          marital_statuses=MaritalStatus,
                          religious_levels=ReligiousLevel,
                          user_types=UserType,
                          current_user=user)

# صفحة عرض التوافقات المقترحة
@match_bp.route('/suggestions')
@login_required
def suggestions():
    user_id = session['user_id']
    user = User.query.get(user_id)
    profile = user.profile
    
    # الحصول على المستخدمين المتوافقين بناءً على التفضيلات
    # هذا مثال بسيط، في التطبيق الحقيقي ستكون هناك خوارزمية أكثر تعقيدًا
    query = User.query.join(Profile)
    
    if user.user_type == UserType.MALE:
        query = query.filter(User.user_type == UserType.FEMALE)
    elif user.user_type == UserType.FEMALE:
        query = query.filter(User.user_type == UserType.MALE)
    else:
        # للوسطاء وأولياء الأمور، لا توجد اقتراحات
        return render_template('match/suggestions.html', suggestions=[], current_user=user)
    
    # تطبيق معايير التوافق من الملف الشخصي
    if profile.preferred_age_min:
        query = query.filter(Profile.birth_date <= datetime.now().replace(year=datetime.now().year - profile.preferred_age_min))
    
    if profile.preferred_age_max:
        query = query.filter(Profile.birth_date >= datetime.now().replace(year=datetime.now().year - profile.preferred_age_max))
    
    # تنفيذ الاستعلام
    suggestions = query.filter(User.is_active == True, User.is_verified == True).all()
    
    # استبعاد المستخدمين الذين تم إرسال طلبات لهم بالفعل
    sent_requests = MatchRequest.query.filter_by(sender_id=user_id).all()
    sent_request_ids = [req.receiver_id for req in sent_requests]
    
    filtered_suggestions = [s for s in suggestions if s.id not in sent_request_ids]
    
    return render_template('match/suggestions.html', suggestions=filtered_suggestions, current_user=user)

# صفحة عرض تفاصيل مستخدم
@match_bp.route('/user/<int:user_id>')
@login_required
def view_user(user_id):
    current_user_id = session['user_id']
    
    # التحقق من أن المستخدم ليس نفسه
    if current_user_id == user_id:
        flash('لا يمكنك عرض ملفك الشخصي هنا', 'warning')
        return redirect(url_for('user.profile'))
    
    user = User.query.get(user_id)
    if not user:
        flash('المستخدم غير موجود', 'danger')
        return redirect(url_for('match.search'))
    
    # التحقق من وجود طلب توافق سابق
    existing_request = MatchRequest.query.filter_by(
        sender_id=current_user_id,
        receiver_id=user_id
    ).first()
    
    # التحقق من وجود طلب توافق مستلم
    received_request = MatchRequest.query.filter_by(
        sender_id=user_id,
        receiver_id=current_user_id
    ).first()
    
    return render_template('match/view_user.html',
                          user=user,
                          existing_request=existing_request,
                          received_request=received_request)

# إرسال طلب توافق
@match_bp.route('/send-request/<int:receiver_id>', methods=['POST'])
@login_required
def send_request(receiver_id):
    sender_id = session['user_id']
    
    # التحقق من عدم وجود طلب سابق
    existing_request = MatchRequest.query.filter_by(
        sender_id=sender_id,
        receiver_id=receiver_id
    ).first()
    
    if existing_request:
        flash('لقد قمت بإرسال طلب توافق لهذا المستخدم من قبل', 'warning')
        return redirect(url_for('match.view_user', user_id=receiver_id))
    
    # إنشاء طلب توافق جديد
    notes = request.form.get('notes', '')
    
    match_request = MatchRequest(
        sender_id=sender_id,
        receiver_id=receiver_id,
        status=RequestStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        notes=notes
    )
    
    db.session.add(match_request)
    db.session.commit()
    
    flash('تم إرسال طلب التوافق بنجاح', 'success')
    return redirect(url_for('match.view_user', user_id=receiver_id))

# إلغاء طلب توافق
@match_bp.route('/cancel-request/<int:request_id>', methods=['POST'])
@login_required
def cancel_request(request_id):
    user_id = session['user_id']
    
    match_request = MatchRequest.query.get(request_id)
    
    # التحقق من أن الطلب ينتمي للمستخدم الحالي
    if not match_request or match_request.sender_id != user_id:
        flash('طلب غير صالح', 'danger')
        return redirect(url_for('user.matches'))
    
    # حذف الطلب
    db.session.delete(match_request)
    db.session.commit()
    
    flash('تم إلغاء طلب التوافق بنجاح', 'success')
    return redirect(url_for('user.matches'))

# الرد على طلب توافق
@match_bp.route('/respond-request/<int:request_id>', methods=['POST'])
@login_required
def respond_request(request_id):
    user_id = session['user_id']
    
    match_request = MatchRequest.query.get(request_id)
    
    # التحقق من أن الطلب موجه للمستخدم الحالي
    if not match_request or match_request.receiver_id != user_id:
        flash('طلب غير صالح', 'danger')
        return redirect(url_for('user.matches'))
    
    response = request.form.get('response')
    
    if response == 'approve':
        match_request.status = RequestStatus.APPROVED
        
        # إنشاء محادثة جديدة
        conversation = Conversation(
            match_request=match_request,
            created_at=datetime.utcnow(),
            is_active=True
        )
        db.session.add(conversation)
        
        flash('تم قبول طلب التوافق بنجاح', 'success')
    elif response == 'reject':
        match_request.status = RequestStatus.REJECTED
        flash('تم رفض طلب التوافق', 'info')
    elif response == 'more_info':
        match_request.status = RequestStatus.NEEDS_INFO
        flash('تم طلب معلومات إضافية', 'info')
    
    match_request.updated_at = datetime.utcnow()
    db.session.commit()
    
    return redirect(url_for('user.matches'))
