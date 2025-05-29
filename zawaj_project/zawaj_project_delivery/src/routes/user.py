from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from src.routes.auth import login_required
from src.models.models import db, User, Profile, MatchRequest, Conversation, Message, SupportTicket
from src.models.models import UserType, MaritalStatus, ReligiousLevel, IncomeLevel, RequestStatus
from datetime import datetime
from werkzeug.utils import secure_filename
import os

user_bp = Blueprint('user', __name__)

# صفحة الملف الشخصي
@user_bp.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    profile = user.profile
    
    return render_template('user/profile.html', user=user, profile=profile)

# صفحة تعديل الملف الشخصي
@user_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.get(session['user_id'])
    profile = user.profile
    
    if request.method == 'POST':
        try:
            # تحديث بيانات المستخدم
            user.email = request.form.get('email')
            user.phone = request.form.get('phone')
            
            # تحديث بيانات الملف الشخصي
            profile.first_name = request.form.get('first_name')
            
            # البيانات الأساسية
            birth_date_str = request.form.get('birth_date')
            if birth_date_str:
                profile.birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                
            profile.nationality = request.form.get('nationality')
            profile.city = request.form.get('city')
            profile.marital_status = MaritalStatus(request.form.get('marital_status'))
            profile.children_count = int(request.form.get('children_count', 0))
            profile.height = int(request.form.get('height', 0))
            profile.weight = int(request.form.get('weight', 0))
            profile.skin_color = request.form.get('skin_color')
            
            # الجوانب الدينية والقيمية
            profile.religious_level = ReligiousLevel(request.form.get('religious_level'))
            profile.religious_sect = request.form.get('religious_sect')
            
            # التعليم والعمل
            profile.education_level = request.form.get('education_level')
            profile.specialization = request.form.get('specialization')
            profile.occupation = request.form.get('occupation')
            profile.income_level = IncomeLevel(request.form.get('income_level'))
            
            # تفضيلات الزواج
            profile.preferred_age_min = int(request.form.get('preferred_age_min', 18))
            profile.preferred_age_max = int(request.form.get('preferred_age_max', 50))
            profile.accepts_polygamy = 'accepts_polygamy' in request.form
            profile.wants_independent_housing = 'wants_independent_housing' in request.form
            profile.accepts_different_nationality = 'accepts_different_nationality' in request.form
            profile.accepts_misyar = 'accepts_misyar' in request.form
            profile.accepts_traditional = 'accepts_traditional' in request.form
            
            # أخرى
            profile.bio = request.form.get('bio')
            profile.has_guardian = 'has_guardian' in request.form
            profile.preferred_communication = request.form.get('preferred_communication')
            
            # معالجة الصورة الشخصية
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join('static/uploads/profiles', filename)
                    file.save(os.path.join('src', file_path))
                    profile.profile_picture = file_path
            
            db.session.commit()
            flash('تم تحديث الملف الشخصي بنجاح', 'success')
            return redirect(url_for('user.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تحديث الملف الشخصي: {str(e)}', 'danger')
    
    return render_template('user/edit_profile.html', 
                          user=user, 
                          profile=profile,
                          marital_statuses=MaritalStatus,
                          religious_levels=ReligiousLevel,
                          income_levels=IncomeLevel)

# صفحة عرض المستخدمين المتوافقين
@user_bp.route('/matches')
@login_required
def matches():
    user = User.query.get(session['user_id'])
    
    # الحصول على المستخدمين المتوافقين بناءً على التفضيلات
    # هذا مثال بسيط، في التطبيق الحقيقي ستكون هناك خوارزمية أكثر تعقيدًا
    if user.user_type == UserType.MALE:
        potential_matches = User.query.filter_by(user_type=UserType.FEMALE).all()
    elif user.user_type == UserType.FEMALE:
        potential_matches = User.query.filter_by(user_type=UserType.MALE).all()
    else:
        potential_matches = []
    
    # الحصول على طلبات التوافق المرسلة والمستلمة
    sent_requests = MatchRequest.query.filter_by(sender_id=user.id).all()
    received_requests = MatchRequest.query.filter_by(receiver_id=user.id).all()
    
    return render_template('user/matches.html', 
                          user=user,
                          potential_matches=potential_matches,
                          sent_requests=sent_requests,
                          received_requests=received_requests)

# إرسال طلب توافق
@user_bp.route('/matches/send/<int:receiver_id>', methods=['POST'])
@login_required
def send_match_request(receiver_id):
    user_id = session['user_id']
    
    # التحقق من عدم وجود طلب سابق
    existing_request = MatchRequest.query.filter_by(sender_id=user_id, receiver_id=receiver_id).first()
    if existing_request:
        flash('لقد قمت بإرسال طلب توافق لهذا المستخدم من قبل', 'warning')
        return redirect(url_for('user.matches'))
    
    # إنشاء طلب توافق جديد
    notes = request.form.get('notes', '')
    match_request = MatchRequest(
        sender_id=user_id,
        receiver_id=receiver_id,
        status=RequestStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        notes=notes
    )
    
    db.session.add(match_request)
    db.session.commit()
    
    flash('تم إرسال طلب التوافق بنجاح', 'success')
    return redirect(url_for('user.matches'))

# الرد على طلب توافق
@user_bp.route('/matches/respond/<int:request_id>', methods=['POST'])
@login_required
def respond_to_match_request(request_id):
    user_id = session['user_id']
    response = request.form.get('response')
    
    match_request = MatchRequest.query.get(request_id)
    
    # التحقق من أن الطلب موجه للمستخدم الحالي
    if not match_request or match_request.receiver_id != user_id:
        flash('طلب غير صالح', 'danger')
        return redirect(url_for('user.matches'))
    
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

# صفحة المحادثات
@user_bp.route('/conversations')
@login_required
def conversations():
    user_id = session['user_id']
    
    # الحصول على جميع المحادثات التي يشارك فيها المستخدم
    sent_match_requests = MatchRequest.query.filter_by(sender_id=user_id, status=RequestStatus.APPROVED).all()
    received_match_requests = MatchRequest.query.filter_by(receiver_id=user_id, status=RequestStatus.APPROVED).all()
    
    conversations = []
    
    for request in sent_match_requests + received_match_requests:
        conversation = Conversation.query.filter_by(match_request_id=request.id).first()
        if conversation:
            conversations.append(conversation)
    
    return render_template('user/conversations.html', conversations=conversations)

# صفحة المحادثة
@user_bp.route('/conversation/<int:conversation_id>', methods=['GET', 'POST'])
@login_required
def conversation(conversation_id):
    user_id = session['user_id']
    conversation = Conversation.query.get(conversation_id)
    
    # التحقق من أن المستخدم مشارك في المحادثة
    if not conversation or (conversation.match_request.sender_id != user_id and conversation.match_request.receiver_id != user_id):
        flash('محادثة غير صالحة', 'danger')
        return redirect(url_for('user.conversations'))
    
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            message = Message(
                conversation=conversation,
                sender_id=user_id,
                content=content,
                created_at=datetime.utcnow(),
                is_read=False
            )
            db.session.add(message)
            db.session.commit()
            flash('تم إرسال الرسالة بنجاح', 'success')
    
    # تحديث حالة القراءة للرسائل المستلمة
    unread_messages = Message.query.filter_by(
        conversation_id=conversation_id,
        is_read=False
    ).filter(Message.sender_id != user_id).all()
    
    for message in unread_messages:
        message.is_read = True
    
    db.session.commit()
    
    # الحصول على جميع الرسائل في المحادثة
    messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).all()
    
    return render_template('user/conversation.html', 
                          conversation=conversation,
                          messages=messages,
                          current_user_id=user_id)

# صفحة طلبات الدعم
@user_bp.route('/support', methods=['GET', 'POST'])
@login_required
def support():
    user_id = session['user_id']
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        content = request.form.get('content')
        
        if subject and content:
            ticket = SupportTicket(
                user_id=user_id,
                subject=subject,
                content=content,
                status=RequestStatus.PENDING,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(ticket)
            db.session.commit()
            flash('تم إرسال طلب الدعم بنجاح', 'success')
        else:
            flash('يرجى ملء جميع الحقول المطلوبة', 'danger')
    
    # الحصول على جميع طلبات الدعم للمستخدم
    tickets = SupportTicket.query.filter_by(user_id=user_id).order_by(SupportTicket.created_at.desc()).all()
    
    return render_template('user/support.html', tickets=tickets)

# صفحة عرض طلب دعم
@user_bp.route('/support/<int:ticket_id>')
@login_required
def view_support_ticket(ticket_id):
    user_id = session['user_id']
    ticket = SupportTicket.query.get(ticket_id)
    
    # التحقق من أن الطلب ينتمي للمستخدم الحالي
    if not ticket or ticket.user_id != user_id:
        flash('طلب دعم غير صالح', 'danger')
        return redirect(url_for('user.support'))
    
    responses = ticket.responses.order_by(SupportTicket.created_at).all()
    
    return render_template('user/view_ticket.html', ticket=ticket, responses=responses)

# صفحة طلب التوثيق
@user_bp.route('/verification', methods=['GET', 'POST'])
@login_required
def verification():
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        document_type = request.form.get('document_type')
        
        if 'document' in request.files:
            file = request.files['document']
            if file and file.filename:
                filename = secure_filename(f"{user_id}_{document_type}_{file.filename}")
                file_path = os.path.join('static/uploads/verification', filename)
                file.save(os.path.join('src', file_path))
                
                verification_request = VerificationRequest(
                    user_id=user_id,
                    document_type=document_type,
                    document_path=file_path,
                    status=RequestStatus.PENDING,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.session.add(verification_request)
                db.session.commit()
                
                flash('تم إرسال طلب التوثيق بنجاح', 'success')
            else:
                flash('يرجى اختيار ملف', 'danger')
        else:
            flash('يرجى اختيار ملف', 'danger')
    
    # الحصول على جميع طلبات التوثيق للمستخدم
    verification_requests = VerificationRequest.query.filter_by(user_id=user_id).order_by(VerificationRequest.created_at.desc()).all()
    
    return render_template('user/verification.html', 
                          user=user,
                          verification_requests=verification_requests)

# صفحة الإبلاغ عن مستخدم
@user_bp.route('/report/<int:reported_user_id>', methods=['GET', 'POST'])
@login_required
def report_user(reported_user_id):
    user_id = session['user_id']
    
    if user_id == reported_user_id:
        flash('لا يمكنك الإبلاغ عن نفسك', 'danger')
        return redirect(url_for('user.matches'))
    
    reported_user = User.query.get(reported_user_id)
    if not reported_user:
        flash('مستخدم غير موجود', 'danger')
        return redirect(url_for('user.matches'))
    
    if request.method == 'POST':
        reason = request.form.get('reason')
        
        if reason:
            report = Report(
                reporter_id=user_id,
                reported_user_id=reported_user_id,
                reason=reason,
                status=RequestStatus.PENDING,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(report)
            db.session.commit()
            
            flash('تم إرسال البلاغ بنجاح', 'success')
            return redirect(url_for('user.matches'))
        else:
            flash('يرجى ذكر سبب الإبلاغ', 'danger')
    
    return render_template('user/report.html', reported_user=reported_user)
