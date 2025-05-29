from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from src.routes.auth import login_required
from src.models.models import db, User, Profile, SupportTicket, SupportResponse
from src.models.models import RequestStatus
from datetime import datetime

support_bp = Blueprint('support', __name__)

# صفحة طلبات الدعم
@support_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    
    # الحصول على جميع طلبات الدعم للمستخدم
    tickets = SupportTicket.query.filter_by(user_id=user_id).order_by(SupportTicket.created_at.desc()).all()
    
    return render_template('support/index.html', tickets=tickets)

# إنشاء طلب دعم جديد
@support_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        subject = request.form.get('subject')
        content = request.form.get('content')
        
        if subject and content:
            ticket = SupportTicket(
                user_id=session['user_id'],
                subject=subject,
                content=content,
                status=RequestStatus.PENDING,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(ticket)
            db.session.commit()
            
            flash('تم إرسال طلب الدعم بنجاح', 'success')
            return redirect(url_for('support.index'))
        else:
            flash('يرجى ملء جميع الحقول المطلوبة', 'danger')
    
    return render_template('support/create.html')

# عرض تفاصيل طلب دعم
@support_bp.route('/<int:ticket_id>')
@login_required
def view(ticket_id):
    user_id = session['user_id']
    
    ticket = SupportTicket.query.get(ticket_id)
    
    # التحقق من أن الطلب ينتمي للمستخدم الحالي
    if not ticket or ticket.user_id != user_id:
        flash('طلب دعم غير صالح', 'danger')
        return redirect(url_for('support.index'))
    
    # الحصول على جميع الردود على الطلب
    responses = SupportResponse.query.filter_by(ticket_id=ticket_id).order_by(SupportResponse.created_at).all()
    
    return render_template('support/view.html', ticket=ticket, responses=responses)

# إضافة رد على طلب دعم
@support_bp.route('/<int:ticket_id>/reply', methods=['POST'])
@login_required
def reply(ticket_id):
    user_id = session['user_id']
    
    ticket = SupportTicket.query.get(ticket_id)
    
    # التحقق من أن الطلب ينتمي للمستخدم الحالي
    if not ticket or ticket.user_id != user_id:
        flash('طلب دعم غير صالح', 'danger')
        return redirect(url_for('support.index'))
    
    content = request.form.get('content')
    
    if content:
        response = SupportResponse(
            ticket_id=ticket_id,
            responder_id=user_id,
            content=content,
            created_at=datetime.utcnow()
        )
        
        db.session.add(response)
        
        # تحديث حالة الطلب
        ticket.status = RequestStatus.NEEDS_INFO
        ticket.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('تم إرسال الرد بنجاح', 'success')
    else:
        flash('يرجى إدخال محتوى الرد', 'danger')
    
    return redirect(url_for('support.view', ticket_id=ticket_id))

# إغلاق طلب دعم
@support_bp.route('/<int:ticket_id>/close', methods=['POST'])
@login_required
def close(ticket_id):
    user_id = session['user_id']
    
    ticket = SupportTicket.query.get(ticket_id)
    
    # التحقق من أن الطلب ينتمي للمستخدم الحالي
    if not ticket or ticket.user_id != user_id:
        flash('طلب دعم غير صالح', 'danger')
        return redirect(url_for('support.index'))
    
    # تحديث حالة الطلب
    ticket.status = RequestStatus.APPROVED  # استخدام APPROVED كحالة إغلاق
    ticket.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    flash('تم إغلاق طلب الدعم بنجاح', 'success')
    return redirect(url_for('support.index'))
