from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash
import random
from models import db, User, Profile, MatchRequest, Conversation, Message, SupportTicket
from models import SupportResponse, Report, VerificationRequest, Statistics
from models import UserType, MaritalStatus, ReligiousLevel, IncomeLevel, RequestStatus

def create_sample_data():
    """إنشاء بيانات تجريبية لاختبار النظام"""
    
    # حذف البيانات الموجودة إن وجدت
    db.session.query(Message).delete()
    db.session.query(Conversation).delete()
    db.session.query(MatchRequest).delete()
    db.session.query(SupportResponse).delete()
    db.session.query(SupportTicket).delete()
    db.session.query(Report).delete()
    db.session.query(VerificationRequest).delete()
    db.session.query(Statistics).delete()
    db.session.query(Profile).delete()
    db.session.query(User).delete()
    db.session.commit()
    
    # إنشاء مستخدم مدير النظام
    admin = User(
        username="admin",
        email="admin@tayseer-zawaj.com",
        phone="+966500000000",
        user_type=UserType.MALE,
        is_admin=True,
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )
    admin.set_password("Admin@123")
    db.session.add(admin)
    
    # إنشاء مستخدمين ذكور
    male_users = []
    male_names = ["أحمد", "محمد", "عبدالله", "سعد", "فهد", "خالد", "عمر", "سلطان", "ناصر", "عبدالرحمن"]
    male_cities = ["الرياض", "جدة", "الدمام", "مكة", "المدينة", "الطائف", "تبوك", "أبها", "حائل", "نجران"]
    
    for i in range(10):
        user = User(
            username=f"male{i+1}",
            email=f"male{i+1}@example.com",
            phone=f"+9665{random.randint(10000000, 99999999)}",
            user_type=UserType.MALE,
            is_admin=False,
            is_active=True,
            is_verified=random.choice([True, False]),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            last_login=datetime.utcnow() - timedelta(days=random.randint(0, 10))
        )
        user.set_password(f"Password{i+1}")
        db.session.add(user)
        male_users.append(user)
        
        # إنشاء ملف شخصي للمستخدم
        profile = Profile(
            user=user,
            first_name=male_names[i],
            birth_date=date(random.randint(1980, 2000), random.randint(1, 12), random.randint(1, 28)),
            nationality="سعودي",
            city=male_cities[i],
            marital_status=random.choice(list(MaritalStatus)),
            children_count=random.randint(0, 3) if random.choice([True, False]) else 0,
            height=random.randint(160, 190),
            weight=random.randint(60, 100),
            skin_color=random.choice(["فاتح", "متوسط", "قمحي", "أسمر"]),
            religious_level=random.choice(list(ReligiousLevel)),
            religious_sect="سني",
            education_level=random.choice(["ثانوي", "بكالوريوس", "ماجستير", "دكتوراه"]),
            specialization=random.choice(["هندسة", "طب", "تعليم", "إدارة أعمال", "تقنية معلومات"]),
            occupation=random.choice(["مهندس", "طبيب", "معلم", "رجل أعمال", "مبرمج"]),
            income_level=random.choice(list(IncomeLevel)),
            preferred_age_min=random.randint(18, 25),
            preferred_age_max=random.randint(26, 40),
            accepts_polygamy=random.choice([True, False]),
            wants_independent_housing=random.choice([True, False]),
            accepts_different_nationality=random.choice([True, False]),
            accepts_misyar=random.choice([True, False]),
            accepts_traditional=True,
            bio=f"أنا {male_names[i]}، أبحث عن شريكة حياة صالحة تشاركني حياتي وتكون عوناً لي على طاعة الله.",
            profile_picture=None,
            has_guardian=False,
            preferred_communication=random.choice(["مباشر عبر المنصة", "عبر وسيط", "بإشراف المنصة"])
        )
        db.session.add(profile)
    
    # إنشاء مستخدمات إناث
    female_users = []
    female_names = ["نورة", "سارة", "هند", "منى", "ريم", "لمياء", "عائشة", "فاطمة", "مريم", "أسماء"]
    female_cities = ["الرياض", "جدة", "الدمام", "مكة", "المدينة", "الطائف", "تبوك", "أبها", "حائل", "نجران"]
    
    for i in range(10):
        user = User(
            username=f"female{i+1}",
            email=f"female{i+1}@example.com",
            phone=f"+9665{random.randint(10000000, 99999999)}",
            user_type=UserType.FEMALE,
            is_admin=False,
            is_active=True,
            is_verified=random.choice([True, False]),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            last_login=datetime.utcnow() - timedelta(days=random.randint(0, 10))
        )
        user.set_password(f"Password{i+1}")
        db.session.add(user)
        female_users.append(user)
        
        # إنشاء ملف شخصي للمستخدمة
        profile = Profile(
            user=user,
            first_name=female_names[i],
            birth_date=date(random.randint(1985, 2002), random.randint(1, 12), random.randint(1, 28)),
            nationality="سعودية",
            city=female_cities[i],
            marital_status=random.choice(list(MaritalStatus)),
            children_count=random.randint(0, 3) if random.choice([True, False]) else 0,
            height=random.randint(150, 175),
            weight=random.randint(45, 75),
            skin_color=random.choice(["فاتح", "متوسط", "قمحي", "أسمر"]),
            religious_level=random.choice(list(ReligiousLevel)),
            religious_sect="سني",
            education_level=random.choice(["ثانوي", "بكالوريوس", "ماجستير", "دكتوراه"]),
            specialization=random.choice(["طب", "تعليم", "إدارة أعمال", "تقنية معلومات", "علوم إنسانية"]),
            occupation=random.choice(["طبيبة", "معلمة", "موظفة", "ربة منزل", "مهندسة"]),
            income_level=random.choice(list(IncomeLevel)),
            preferred_age_min=random.randint(25, 30),
            preferred_age_max=random.randint(31, 45),
            accepts_polygamy=random.choice([True, False]),
            wants_independent_housing=random.choice([True, False]),
            accepts_different_nationality=random.choice([True, False]),
            accepts_misyar=random.choice([True, False]),
            accepts_traditional=True,
            bio=f"أنا {female_names[i]}، أبحث عن زوج صالح يتقي الله فيّ ويكون سنداً لي في الحياة.",
            profile_picture=None,
            has_guardian=True,
            preferred_communication=random.choice(["مباشر عبر المنصة", "عبر وسيط", "بإشراف المنصة"])
        )
        db.session.add(profile)
    
    # إنشاء مستخدمين أولياء أمور
    guardian_users = []
    guardian_names = ["إبراهيم", "عبدالعزيز", "سليمان", "يوسف", "صالح"]
    
    for i in range(5):
        user = User(
            username=f"guardian{i+1}",
            email=f"guardian{i+1}@example.com",
            phone=f"+9665{random.randint(10000000, 99999999)}",
            user_type=UserType.GUARDIAN,
            is_admin=False,
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            last_login=datetime.utcnow() - timedelta(days=random.randint(0, 10))
        )
        user.set_password(f"Password{i+1}")
        db.session.add(user)
        guardian_users.append(user)
        
        # إنشاء ملف شخصي لولي الأمر
        profile = Profile(
            user=user,
            first_name=guardian_names[i],
            birth_date=date(random.randint(1960, 1980), random.randint(1, 12), random.randint(1, 28)),
            nationality="سعودي",
            city=random.choice(male_cities),
            marital_status=MaritalStatus.SINGLE,  # غير مهم لولي الأمر
            bio=f"أنا {guardian_names[i]}، ولي أمر أبحث عن زوج صالح لابنتي/أختي.",
            has_guardian=False,
            preferred_communication="بإشراف المنصة"
        )
        db.session.add(profile)
    
    # إنشاء مستخدمين وسطاء
    mediator_users = []
    mediator_names = ["عبدالمجيد", "راشد", "بندر", "ماجد", "وليد"]
    
    for i in range(5):
        user = User(
            username=f"mediator{i+1}",
            email=f"mediator{i+1}@example.com",
            phone=f"+9665{random.randint(10000000, 99999999)}",
            user_type=UserType.MEDIATOR,
            is_admin=False,
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
            last_login=datetime.utcnow() - timedelta(days=random.randint(0, 10))
        )
        user.set_password(f"Password{i+1}")
        db.session.add(user)
        mediator_users.append(user)
        
        # إنشاء ملف شخصي للوسيط
        profile = Profile(
            user=user,
            first_name=mediator_names[i],
            birth_date=date(random.randint(1960, 1980), random.randint(1, 12), random.randint(1, 28)),
            nationality="سعودي",
            city=random.choice(male_cities),
            marital_status=MaritalStatus.SINGLE,  # غير مهم للوسيط
            bio=f"أنا {mediator_names[i]}، وسيط أساعد في التوفيق بين الراغبين في الزواج.",
            has_guardian=False,
            preferred_communication="بإشراف المنصة"
        )
        db.session.add(profile)
    
    # إنشاء طلبات توافق
    for i in range(15):
        male_user = random.choice(male_users)
        female_user = random.choice(female_users)
        
        match_request = MatchRequest(
            sender=male_user,
            receiver=female_user,
            status=random.choice(list(RequestStatus)),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 10)),
            notes="أتمنى التواصل للتعارف بغرض الزواج"
        )
        db.session.add(match_request)
        
        # إنشاء محادثات للطلبات الموافق عليها
        if match_request.status == RequestStatus.APPROVED:
            conversation = Conversation(
                match_request=match_request,
                created_at=match_request.updated_at,
                is_active=True
            )
            db.session.add(conversation)
            
            # إضافة رسائل للمحادثة
            for j in range(random.randint(3, 10)):
                sender = male_user if j % 2 == 0 else female_user
                message = Message(
                    conversation=conversation,
                    sender=sender,
                    content=f"رسالة تجريبية رقم {j+1} في المحادثة",
                    created_at=conversation.created_at + timedelta(hours=j),
                    is_read=random.choice([True, False])
                )
                db.session.add(message)
    
    # إنشاء طلبات دعم
    for i in range(8):
        user = random.choice(male_users + female_users + guardian_users + mediator_users)
        
        ticket = SupportTicket(
            user=user,
            subject=random.choice([
                "استفسار عن آلية التوثيق",
                "مشكلة في التسجيل",
                "استفسار عن الاشتراكات",
                "اقتراح تحسين للمنصة",
                "مشكلة تقنية",
                "استفسار عام"
            ]),
            content=f"هذا نص تجريبي لطلب الدعم رقم {i+1}. أرجو المساعدة في حل المشكلة.",
            status=random.choice(list(RequestStatus)),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 20)),
            updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 5))
        )
        db.session.add(ticket)
        
        # إضافة ردود للطلبات التي تمت معالجتها
        if ticket.status != RequestStatus.PENDING:
            response = SupportResponse(
                ticket=ticket,
                responder=admin,
                content="شكراً لتواصلك معنا. تم استلام طلبك وسيتم التعامل معه في أقرب وقت.",
                created_at=ticket.created_at + timedelta(days=random.randint(1, 3))
            )
            db.session.add(response)
    
    # إنشاء طلبات توثيق
    for i in range(10):
        user = random.choice(male_users + female_users)
        
        verification = VerificationRequest(
            user=user,
            document_type=random.choice(["هوية وطنية", "جواز سفر", "رخصة قيادة"]),
            document_path=f"/uploads/verification/doc_{user.id}_{i+1}.jpg",
            status=random.choice(list(RequestStatus)),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 15)),
            admin_notes="تم التحقق من الوثائق" if random.choice([True, False]) else None
        )
        db.session.add(verification)
    
    # إنشاء بلاغات
    for i in range(5):
        reporter = random.choice(male_users + female_users)
        reported = random.choice(male_users + female_users)
        
        # تجنب الإبلاغ عن النفس
        while reported.id == reporter.id:
            reported = random.choice(male_users + female_users)
        
        report = Report(
            reporter=reporter,
            reported_user=reported,
            reason=random.choice([
                "معلومات غير صحيحة في الملف الشخصي",
                "سلوك غير لائق في المراسلات",
                "انتحال شخصية",
                "محتوى غير مناسب"
            ]),
            status=random.choice(list(RequestStatus)),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 20)),
            updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 10))
        )
        db.session.add(report)
    
    # إنشاء إحصائيات
    for i in range(30):
        day_date = date.today() - timedelta(days=i)
        stats = Statistics(
            date=day_date,
            new_users_count=random.randint(5, 20),
            active_users_count=random.randint(50, 200),
            successful_matches_count=random.randint(1, 5),
            male_users_count=random.randint(100, 150),
            female_users_count=random.randint(80, 120),
            guardian_users_count=random.randint(10, 30),
            mediator_users_count=random.randint(5, 15),
            reports_count=random.randint(0, 3)
        )
        db.session.add(stats)
    
    # حفظ جميع البيانات في قاعدة البيانات
    db.session.commit()
    
    return {
        'admin': admin,
        'male_users': male_users,
        'female_users': female_users,
        'guardian_users': guardian_users,
        'mediator_users': mediator_users
    }

if __name__ == "__main__":
    # هذا الكود يستخدم فقط عند تشغيل الملف مباشرة
    from app import app, db
    with app.app_context():
        create_sample_data()
        print("تم إنشاء البيانات التجريبية بنجاح!")
