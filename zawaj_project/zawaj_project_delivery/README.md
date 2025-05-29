# منصة تيسير الزواج - دليل التثبيت والتشغيل

## نظرة عامة
منصة تيسير الزواج هي منصة إلكترونية آمنة وموثوقة تهدف إلى تيسير الزواج بطريقة شرعية وآمنة عبر الإنترنت، تحت إشراف وإدارة دقيقة. تستهدف المنصة الأفراد، أولياء الأمور، والوسطاء من الأقارب والأصدقاء، بطريقة تحفظ الخصوصية وتعزز الجدية.

## متطلبات النظام
- Python 3.8 أو أحدث
- MySQL أو PostgreSQL
- خادم ويب (مثل Nginx أو Apache)
- وحدات Python المطلوبة (مذكورة في ملف requirements.txt)

## خطوات التثبيت

### 1. إعداد البيئة الافتراضية
```bash
# إنشاء بيئة افتراضية
python -m venv venv

# تفعيل البيئة الافتراضية
# في نظام Linux/Mac
source venv/bin/activate
# في نظام Windows
venv\Scripts\activate
```

### 2. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 3. إعداد قاعدة البيانات
```bash
# تعديل إعدادات قاعدة البيانات في ملف src/main.py
# ثم تشغيل الأمر التالي لإنشاء الجداول
python -c "from src.main import db; db.create_all()"

# لإضافة البيانات التجريبية
python -c "from src.models.sample_data import create_sample_data; create_sample_data()"
```

### 4. تشغيل التطبيق
```bash
# للتطوير المحلي
python -m src.main

# للإنتاج، يفضل استخدام Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "src.main:app"
```

## الاستضافة الدائمة
للاستضافة الدائمة، يوصى باتباع الخطوات التالية:

1. استخدام خادم VPS مع نظام Ubuntu 20.04 أو أحدث
2. تثبيت وإعداد Nginx كخادم وكيل عكسي
3. استخدام Gunicorn لتشغيل تطبيق Flask
4. إعداد قاعدة بيانات MySQL أو PostgreSQL
5. تكوين HTTPS باستخدام Let's Encrypt
6. إعداد Supervisor لإدارة عملية التطبيق

### مثال لإعداد Nginx
```
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### مثال لإعداد Supervisor
```
[program:zawaj]
command=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 "src.main:app"
directory=/path/to/zawaj_project
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/zawaj/zawaj.err.log
stdout_logfile=/var/log/zawaj/zawaj.out.log
```

## بيانات الدخول التجريبية
- **حساب مستخدم عادي**:
  - اسم المستخدم: user1
  - كلمة المرور: password123

- **حساب مشرف (إداري)**:
  - اسم المستخدم: admin
  - كلمة المرور: admin123

## هيكل المشروع
```
zawaj_project/
├── src/                    # مصدر التطبيق
│   ├── models/             # نماذج قاعدة البيانات
│   ├── routes/             # مسارات التطبيق
│   ├── static/             # الملفات الثابتة (CSS، JS، الصور)
│   ├── templates/          # قوالب HTML
│   └── main.py             # نقطة الدخول الرئيسية
├── venv/                   # البيئة الافتراضية (لا يتم تضمينها في الحزمة)
└── requirements.txt        # متطلبات Python
```

## الدعم الفني
للحصول على المساعدة أو الإبلاغ عن المشكلات، يرجى التواصل مع فريق الدعم الفني.

## الترخيص
جميع الحقوق محفوظة © 2025 منصة تيسير الزواج.
