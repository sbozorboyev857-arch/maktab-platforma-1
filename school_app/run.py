#!/usr/bin/env python3
"""Maktab Platformasi - Lokal test uchun ishga tushirish"""
import os
import sys

def check_flask():
    try:
        import flask
        print(f"✅ Flask topildi (versiya: {flask.__version__})")
        return True
    except ImportError:
        print("❌ Flask topilmadi! O'rnatilmoqda...")
        os.system(f"{sys.executable} -m pip install flask")
        try:
            import flask
            print(f"✅ Flask o'rnatildi (versiya: {flask.__version__})")
            return True
        except:
            print("❌ Flask o'rnatilmadi! Qo'lda o'rnatish:")
            print(f"   {sys.executable} -m pip install flask")
            return False

if __name__ == "__main__":
    print("=" * 50)
    print("🎓 MAKTAB PLATFORMASI")
    print("   Lokal test rejimi")
    print("=" * 50)
    print()

    if not check_flask():
        input("Enter bosib chiqing...")
        sys.exit(1)

    # Hash admin password
    import hashlib
    data_file = os.path.join(os.path.dirname(__file__), 'school_system_data.json')
    if os.path.exists(data_file):
        import json
        with open(data_file, 'r') as f:
            data = json.load(f)
        has_admin = any(u['username'] == 'admin' for u in data.get('users', []))
        if not has_admin:
            print("⚙️ Admin hisobi yaratilmoqda...")
            data['users'].append({
                'username': 'admin',
                'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
                'role': 'teacher',
                'name': 'Administrator',
                'class': '',
                'created_at': '2025-01-01T00:00:00'
            })
            with open(data_file, 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        print("⚙️ Ma'lumotlar fayli yaratilmoqda...")
        import json
        data = {
            'users': [{
                'username': 'admin',
                'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
                'role': 'teacher',
                'name': 'Administrator',
                'class': '',
                'created_at': '2025-01-01T00:00:00'
            }],
            'schedules': {},
            'attendance': [],
            'support_messages': [],
            'teacher_attendance': [],
            'comments': [],
            'test_results': []
        }
        with open(data_file, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    print()
    print("🔐 Kirish ma'lumotlari:")
    print("   Login:  admin")
    print("   Parol:  admin123")
    print()
    print("🌐 Brauzerda oching:")
    print("   http://127.0.0.1:5000")
    print()
    print("⏹️ To'xtatish uchun: Ctrl+C bosing")
    print("=" * 50)
    print()

    from app import app
    app.run(debug=True, host='127.0.0.1', port=5000)
