#!/bin/bash
echo "================================================"
echo "  MAKTAB PLATFORMASI - Lokal test"
echo "================================================"
echo ""
echo "Flask o'rnatilmoqda..."
pip3 install flask 2>/dev/null || pip install flask 2>/dev/null
echo ""
echo "Login: admin"
echo "Parol: admin123"
echo ""
echo "Brauzerda oching: http://127.0.0.1:5000"
echo ""
echo "To'xtatish: Ctrl+C"
echo "================================================"
echo ""
python3 run.py || python run.py
