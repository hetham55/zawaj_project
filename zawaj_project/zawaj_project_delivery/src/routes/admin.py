from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from src.routes.auth import admin_required
from src.models.models import db, User, Profile, MatchRequest, Conversation, Message, SupportTicket
from src.models.models import SupportResponse, Report, VerificationRequest, Statistics
from src.models.models import UserType, MaritalStatus, ReligiousLevel, IncomeLevel, RequestStatus
from datetime import datetime, date, timedelta
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

# لوحة التحكم الرئيسية
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # إحصائيات عامة
    total_users = User.query.filter_by(is_admin=False).count()
    male_users = User.query.filter_by(user_type=UserType.MALE).count()
    female_users = User.query.filter_by(user_type=UserType.FEMALE).count()
    guardian_users = User.query.filter_by(user_type=UserType.GUARDIAN).count()
    mediator_users = User.query.filter_by(user_type=UserType.MEDIATOR).count()
    
    # طلبات قيد الانتظار
    pending_match_requests = MatchRequest.query.filter_by(status=RequestStatus.PENDING).count()
    pending_verification_requests = VerificationRequest.query.filter_by(status=RequestStatus.PENDING).count()
    pending_support_tickets = SupportTicket.query.filter_by(status=RequestStatus.PENDING).count()
    pending_reports = Report.query.filter_by(status=RequestStatus.PENDING).count()
    
    # إحصائيات النجاح
    successful_matches = MatchRequest.query.filter_by(status=RequestStatus.APPROVED).count()
    
    # إحصائيات آخر 7 أيام
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    new_users_last_week = User.query.filter(
        User.created_at >= week_ago,
        User.is_admin == False
    ).count()
    
    # الحصول على إحصائيات آخر 30 يوم
    month_ago = today - timedelta(days=30)
    daily_stats = Statistics.query.filter(Statistics.date >= month_ago).order_by(Statistics.date).all()
    
    return render_template('admin/dashboard.html',
                          total_users=total_users,
                          male_users=male_users,
                          female_users=female_users,
                          guardian_users=guardian_users,
                          mediator_users=mediator_users,
                          pending_match_requests=pending_match_requests,
                          pending_verification_requests=pending_verification_requests,
                          pending_support_tickets=pending_support_tickets,
                          pending_reports=pending_reports,
                          successful_matches=successful_matches,
                          new_users_last_week=new_users_last_week,
                          daily_stats=daily_stats)

# إدارة المستخدمين
@admin_bp.route('/users')
@admin_required
def users():
    user_type = request.args.get('type', 'all')
    
    if user_type == 'male':
        users = User.query.filter_by(user_type=UserType.MALE).all()
    elif user_type == 'female':
        users = User.query.filter_by(user_type=UserType.FEMALE).all()
    elif user_type == 'guardian':
        users = User.query.filter_by(user_type=UserType.GUARDIAN).all()
    elif user_type == 'mediator':
        users = User.query.filter_by(user_type=UserType.MEDIATOR).all()
    else:
        users = User.query.filter_by(is_admin=False).all()
    
    return render_template('admin/users.html', users=users, user_type=user_type)

# عرض تفاصيل المستخدم
@admin_bp.route('/users/<int:user_id>')
@admin_required
def view_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('المستخدم غير موجود', 'danger')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/view_user.html', user=user)

# تفعيل/تعطيل المستخدم
@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('المستخدم غير موجود', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'تفعيل' if user.is_active else 'تعطيل'
    flash(f'تم {status} المستخدم بنجاح', 'success')
    return redirect(url_for('admin.view_user', user_id=user_id))

# توثيق المستخدم
@admin_bp.route('/users/<int:user_id>/verify', methods=['POST'])
@admin_required
def verify_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('المستخدم غير موجود', 'danger')
        return redirect(url_for('admin.users'))
    
    user.is_verified = True
    db.session.commit()
    
    flash('تم توثيق المستخدم بنجاح', 'success')
    return redirect(url_for('admin.view_user', user_id=user_id))

# إدارة طلبات التوافق
@admin_bp.route('/match-requests')
@admin_required
def match_requests():
    status = request.args.get('status', 'all')
    
    if status == 'pending':
        requests = MatchRequest.query.filter_by(status=RequestStatus.PENDING).all()
    elif status == 'approved':
        requests = MatchRequest.query.filter_by(status=RequestStatus.APPROVED).all()
    elif status == 'rejected':
        requests = MatchRequest.query.filter_by(status=RequestStatus.REJECTED).all()
    elif status == 'needs_info':
        requests = MatchRequest.query.filter_by(status=RequestStatus.NEEDS_INFO).all()
    else:
        requests = MatchRequest.query.all()
    
    return render_template('admin/match_requests.html', requests=requests, status=status)

# عرض تفاصيل طلب التوافق
@admin_bp.route('/match-requests/<int:request_id>')
@admin_required
def view_match_request(request_id):
    match_request = MatchRequest.query.get(request_id)
    if not match_request:
        flash('طلب التوافق غير موجود', 'danger')
        return redirect(url_for('admin.match_requests'))
    
    return render_template('admin/view_match_request.html', match_request=match_request)

# تحديث حالة طلب التوافق
@admin_bp.route('/match-requests/<int:request_id>/update', methods=['POST'])
@admin_required
def update_match_request(request_id):
    match_request = MatchRequest.query.get(request_id)
    if not match_request:
        flash('طلب التوافق غير موجود', 'danger')
        return redirect(url_for('admin.match_requests'))
    
    status = request.form.get('status')
    notes = request.form.get('notes')
    
    match_request.status = RequestStatus(status)
    match_request.notes = notes
    match_request.updated_at = datetime.utcnow()
    
    # إذا تم الموافقة على الطلب، إنشاء محادثة جديدة
    if status == RequestStatus.APPROVED.value and not Conversation.query.filter_by(match_request_id=request_id).first():
        conversation = Conversation(
            match_request=match_request,
            created_at=datetime.utcnow(),
            is_active=True
        )
        db.session.add(conversation)
    
    db.session.commit()
    
    flash('تم تحديث حالة طلب التوافق بنجاح', 'success')
    return redirect(url_for('admin.view_match_request', request_id=request_id))

# إدارة طلبات التوثيق
@admin_bp.route('/verification-requests')
@admin_required
def verification_requests():
    status = request.args.get('status', 'all')
    
    if status == 'pending':
        requests = VerificationRequest.query.filter_by(status=RequestStatus.PENDING).all()
    elif status == 'approved':
        requests = VerificationRequest.query.filter_by(status=RequestStatus.APPROVED).all()
    elif status == 'rejected':
        requests = VerificationRequest.query.filter_by(status=RequestStatus.REJECTED).all()
    elif status == 'needs_info':
        requests = VerificationRequest.query.filter_by(status=RequestStatus.NEEDS_INFO).all()
    else:
        requests = VerificationRequest.query.all()
    
    return render_template('admin/verification_requests.html', requests=requests, status=status)

# عرض تفاصيل طلب التوثيق
@admin_bp.route('/verification-requests/<int:request_id>')
@admin_required
def view_verification_request(request_id):
    verification_request = VerificationRequest.query.get(request_id)
    if not verification_request:
        flash('طلب التوثيق غير موجود', 'danger')
        return redirect(url_for('admin.verification_requests'))
    
    return render_template('admin/view_verification_request.html', verification_request=verification_request)

# تحديث حالة طلب التوثيق
@admin_bp.route('/verification-requests/<int:request_id>/update', methods=['POST'])
@admin_required
def update_verification_request(request_id):
    verification_request = VerificationRequest.query.get(request_id)
    if not verification_request:
        flash('طلب التوثيق غير موجود', 'danger')
        return redirect(url_for('admin.verification_requests'))
    
    status = request.form.get('status')
    admin_notes = request.form.get('admin_notes')
    
    verification_request.status = RequestStatus(status)
    verification_request.admin_notes = admin_notes
    verification_request.updated_at = datetime.utcnow()
    
    # إذا تم الموافقة على الطلب، تحديث حالة التوثيق للمستخدم
    if status == RequestStatus.APPROVED.value:
        user = User.query.get(verification_request.user_id)
        if user:
            user.is_verified = True
    
    db.session.commit()
    
    flash('تم تحديث حالة طلب التوثيق بنجاح', 'success')
    return redirect(url_for('admin.view_verification_request', request_id=request_id))

# إدارة طلبات الدعم
@admin_bp.route('/support-tickets')
@admin_required
def support_tickets():
    status = request.args.get('status', 'all')
    
    if status == 'pending':
        tickets = SupportTicket.query.filter_by(status=RequestStatus.PENDING).all()
    elif status == 'approved':
        tickets = SupportTicket.query.filter_by(status=RequestStatus.APPROVED).all()
    elif status == 'rejected':
        tickets = SupportTicket.query.filter_by(status=RequestStatus.REJECTED).all()
    elif status == 'needs_info':
        tickets = SupportTicket.query.filter_by(status=RequestStatus.NEEDS_INFO).all()
    else:
        tickets = SupportTicket.query.all()
    
    return render_template('admin/support_tickets.html', tickets=tickets, status=status)

# عرض تفاصيل طلب الدعم
@admin_bp.route('/support-tickets/<int:ticket_id>')
@admin_required
def view_support_ticket(ticket_id):
    ticket = SupportTicket.query.get(ticket_id)
    if not ticket:
        flash('طلب الدعم غير موجود', 'danger')
        return redirect(url_for('admin.support_tickets'))
    
    responses = ticket.responses.order_by(SupportResponse.created_at).all()
    
    return render_template('admin/view_support_ticket.html', ticket=ticket, responses=responses)

# الرد على طلب الدعم
@admin_bp.route('/support-tickets/<int:ticket_id>/respond', methods=['POST'])
@admin_required
def respond_to_support_ticket(ticket_id):
    ticket = SupportTicket.query.get(ticket_id)
    if not ticket:
        flash('طلب الدعم غير موجود', 'danger')
        return redirect(url_for('admin.support_tickets'))
    
    content = request.form.get('content')
    status = request.form.get('status')
    
    if content:
        response = SupportResponse(
            ticket=ticket,
            responder_id=session['user_id'],
            content=content,
            created_at=datetime.utcnow()
        )
        db.session.add(response)
        
        ticket.status = RequestStatus(status)
        ticket.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('تم الرد على طلب الدعم بنجاح', 'success')
    else:
        flash('يرجى إدخال محتوى الرد', 'danger')
    
    return redirect(url_for('admin.view_support_ticket', ticket_id=ticket_id))

# إدارة البلاغات
@admin_bp.route('/reports')
@admin_required
def reports():
    status = request.args.get('status', 'all')
    
    if status == 'pending':
        reports = Report.query.filter_by(status=RequestStatus.PENDING).all()
    elif status == 'approved':
        reports = Report.query.filter_by(status=RequestStatus.APPROVED).all()
    elif status == 'rejected':
        reports = Report.query.filter_by(status=RequestStatus.REJECTED).all()
    elif status == 'needs_info':
        reports = Report.query.filter_by(status=RequestStatus.NEEDS_INFO).all()
    else:
        reports = Report.query.all()
    
    return render_template('admin/reports.html', reports=reports, status=status)

# عرض تفاصيل البلاغ
@admin_bp.route('/reports/<int:report_id>')
@admin_required
def view_report(report_id):
    report = Report.query.get(report_id)
    if not report:
        flash('البلاغ غير موجود', 'danger')
        return redirect(url_for('admin.reports'))
    
    return render_template('admin/view_report.html', report=report)

# تحديث حالة البلاغ
@admin_bp.route('/reports/<int:report_id>/update', methods=['POST'])
@admin_required
def update_report(report_id):
    report = Report.query.get(report_id)
    if not report:
        flash('البلاغ غير موجود', 'danger')
        return redirect(url_for('admin.reports'))
    
    status = request.form.get('status')
    
    report.status = RequestStatus(status)
    report.updated_at = datetime.utcnow()
    
    # إذا تم الموافقة على البلاغ، يمكن اتخاذ إجراء ضد المستخدم المبلغ عنه
    if status == RequestStatus.APPROVED.value:
        action = request.form.get('action')
        if action == 'disable':
            reported_user = User.query.get(report.reported_user_id)
            if reported_user:
                reported_user.is_active = False
    
    db.session.commit()
    
    flash('تم تحديث حالة البلاغ بنجاح', 'success')
    return redirect(url_for('admin.view_report', report_id=report_id))

# إدارة الإحصائيات
@admin_bp.route('/statistics')
@admin_required
def statistics():
    # إحصائيات عامة
    total_users = User.query.filter_by(is_admin=False).count()
    male_users = User.query.filter_by(user_type=UserType.MALE).count()
    female_users = User.query.filter_by(user_type=UserType.FEMALE).count()
    guardian_users = User.query.filter_by(user_type=UserType.GUARDIAN).count()
    mediator_users = User.query.filter_by(user_type=UserType.MEDIATOR).count()
    
    # إحصائيات المناطق
    cities = db.session.query(Profile.city, func.count(Profile.id)).group_by(Profile.city).all()
    
    # إحصائيات الحالة الاجتماعية
    marital_status = db.session.query(Profile.marital_status, func.count(Profile.id)).group_by(Profile.marital_status).all()
    
    # إحصائيات العمر
    age_ranges = {
        '18-25': 0,
        '26-35': 0,
        '36-45': 0,
        '46+': 0
    }
    
    profiles = Profile.query.filter(Profile.birth_date.isnot(None)).all()
    for profile in profiles:
        age = (date.today() - profile.birth_date).days // 365
        if age <= 25:
            age_ranges['18-25'] += 1
        elif age <= 35:
            age_ranges['26-35'] += 1
        elif age <= 45:
            age_ranges['36-45'] += 1
        else:
            age_ranges['46+'] += 1
    
    # إحصائيات التوافق
    match_stats = {
        'total': MatchRequest.query.count(),
        'approved': MatchRequest.query.filter_by(status=RequestStatus.APPROVED).count(),
        'rejected': MatchRequest.query.filter_by(status=RequestStatus.REJECTED).count(),
        'pending': MatchRequest.query.filter_by(status=RequestStatus.PENDING).count()
    }
    
    # إحصائيات آخر 30 يوم
    today = date.today()
    month_ago = today - timedelta(days=30)
    daily_stats = Statistics.query.filter(Statistics.date >= month_ago).order_by(Statistics.date).all()
    
    return render_template('admin/statistics.html',
                          total_users=total_users,
                          male_users=male_users,
                          female_users=female_users,
                          guardian_users=guardian_users,
                          mediator_users=mediator_users,
                          cities=cities,
                          marital_status=marital_status,
                          age_ranges=age_ranges,
                          match_stats=match_stats,
                          daily_stats=daily_stats)

# تحديث الإحصائيات
@admin_bp.route('/update-statistics')
@admin_required
def update_statistics():
    today = date.today()
    
    # التحقق من وجود إحصائيات لليوم الحالي
    existing_stats = Statistics.query.filter_by(date=today).first()
    if existing_stats:
        # تحديث الإحصائيات الموجودة
        existing_stats.new_users_count = User.query.filter(
            func.date(User.created_at) == today,
            User.is_admin == False
        ).count()
        
        existing_stats.active_users_count = User.query.filter_by(
            is_active=True,
            is_admin=False
        ).count()
        
        existing_stats.successful_matches_count = MatchRequest.query.filter(
            func.date(MatchRequest.updated_at) == today,
            MatchRequest.status == RequestStatus.APPROVED
        ).count()
        
        existing_stats.male_users_count = User.query.filter_by(user_type=UserType.MALE).count()
        existing_stats.female_users_count = User.query.filter_by(user_type=UserType.FEMALE).count()
        existing_stats.guardian_users_count = User.query.filter_by(user_type=UserType.GUARDIAN).count()
        existing_stats.mediator_users_count = User.query.filter_by(user_type=UserType.MEDIATOR).count()
        
        existing_stats.reports_count = Report.query.filter(
            func.date(Report.created_at) == today
        ).count()
    else:
        # إنشاء إحصائيات جديدة لليوم الحالي
        new_stats = Statistics(
            date=today,
            new_users_count=User.query.filter(
                func.date(User.created_at) == today,
                User.is_admin == False
            ).count(),
            active_users_count=User.query.filter_by(
                is_active=True,
                is_admin=False
            ).count(),
            successful_matches_count=MatchRequest.query.filter(
                func.date(MatchRequest.updated_at) == today,
                MatchRequest.status == RequestStatus.APPROVED
            ).count(),
            male_users_count=User.query.filter_by(user_type=UserType.MALE).count(),
            female_users_count=User.query.filter_by(user_type=UserType.FEMALE).count(),
            guardian_users_count=User.query.filter_by(user_type=UserType.GUARDIAN).count(),
            mediator_users_count=User.query.filter_by(user_type=UserType.MEDIATOR).count(),
            reports_count=Report.query.filter(
                func.date(Report.created_at) == today
            ).count()
        )
        db.session.add(new_stats)
    
    db.session.commit()
    
    flash('تم تحديث الإحصائيات بنجاح', 'success')
    return redirect(url_for('admin.statistics'))
