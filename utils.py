import os
import qrcode
import io
import base64
from functools import wraps
from flask import abort
from flask_login import current_user
from models import ActivityLog
from app import db

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def log_activity(user_id, action, description, ip_address=None):
    """Log user activity"""
    activity = ActivityLog(
        user_id=user_id,
        action=action,
        description=description,
        ip_address=ip_address
    )
    db.session.add(activity)
    db.session.commit()

def generate_qr_code(data):
    """Generate QR code as base64 image"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def format_currency(amount):
    """Format currency with 2 decimal places"""
    return f"{amount:.2f}"

def calculate_interest(principal, rate, days):
    """Calculate compound interest"""
    return principal * (rate / 100) * days

def get_coin_icon(symbol):
    """Get coin icon based on symbol"""
    icons = {
        'BTC': '₿',
        'ETH': 'Ξ',
        'BNB': 'BNB',
        'LTC': 'Ł',
        'SOL': 'SOL',
        'TRX': 'TRX',
        'DOT': 'DOT',
    }
    return icons.get(symbol.upper(), symbol)

def get_network_info(network):
    """Get network information"""
    networks = {
        'BEP20': {
            'name': 'Binance Smart Chain',
            'explorer': 'https://bscscan.com',
            'address': '0x55d398326f99059ff775485246999027b3197955'  # USDT BSC
        },
        'TRC20': {
            'name': 'TRON Network',
            'explorer': 'https://tronscan.org',
            'address': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'  # USDT TRC20
        }
    }
    return networks.get(network, {})
