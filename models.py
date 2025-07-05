from datetime import datetime, timedelta
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    usdt_balance = db.Column(db.Float, default=0.0)
    total_staked = db.Column(db.Float, default=0.0)
    total_earned = db.Column(db.Float, default=0.0)
    referral_code = db.Column(db.String(20), unique=True, nullable=False)
    referred_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    referral_bonus = db.Column(db.Float, default=0.0)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stakes = db.relationship('Stake', backref='user', lazy=True)
    deposits = db.relationship('Deposit', backref='user', lazy=True)
    withdrawals = db.relationship('Withdrawal', backref='user', lazy=True)
    referrals = db.relationship('User', backref=db.backref('referrer', remote_side=[id]))
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
    
    def generate_referral_code(self):
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_referral_tree(self, level=1, max_level=3):
        if level > max_level:
            return []
        
        referrals = []
        direct_referrals = User.query.filter_by(referred_by=self.id).all()
        
        for referral in direct_referrals:
            referral_data = {
                'user': referral,
                'level': level,
                'children': referral.get_referral_tree(level + 1, max_level)
            }
            referrals.append(referral_data)
        
        return referrals
    
    def get_referral_count(self):
        """Get total number of users referred by this user"""
        return User.query.filter_by(referred_by=self.id).count()
    
    def has_two_referrals(self):
        """Check if user has completed 2 referrals for bonus benefits"""
        return self.get_referral_count() >= 2
    
    def calculate_referral_bonus(self, amount):
        settings = PlatformSettings.get_all_settings()
        if amount < float(settings.get('min_referral_activation', 100)):
            return 0
        
        level_1_rate = float(settings.get('referral_level_1', 5)) / 100
        return amount * level_1_rate

class Coin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    min_stake = db.Column(db.Float, nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    stakes = db.relationship('Stake', backref='coin', lazy=True)

class StakingPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    duration_days = db.Column(db.Integer, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)  # Daily interest rate
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    stakes = db.relationship('Stake', backref='plan', lazy=True)

class Stake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    coin_id = db.Column(db.Integer, db.ForeignKey('coin.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('staking_plan.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    daily_interest = db.Column(db.Float, nullable=False)
    total_return = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    withdrawn = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def is_mature(self):
        return datetime.utcnow() >= self.end_date
    
    @property
    def days_remaining(self):
        if self.is_mature:
            return 0
        return (self.end_date - datetime.utcnow()).days
    
    def calculate_current_return(self):
        if self.status == 'cancelled':
            return 0
        
        days_passed = (datetime.utcnow() - self.start_date).days
        if days_passed > self.plan.duration_days:
            days_passed = self.plan.duration_days
        
        return self.amount * self.daily_interest * days_passed / 100

class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.String(100), nullable=False)
    screenshot_path = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)

class Withdrawal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    wallet_address = db.Column(db.String(200), nullable=False)
    network = db.Column(db.String(20), nullable=False)  # BEP20, TRC20
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)

class PlatformSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_setting(key, default=None):
        setting = PlatformSettings.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def get_all_settings():
        settings = PlatformSettings.query.all()
        return {setting.key: setting.value for setting in settings}
    
    @staticmethod
    def set_setting(key, value, description=None):
        setting = PlatformSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = PlatformSettings(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PaymentAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    network = db.Column(db.String(20), nullable=False)  # BEP20, TRC20
    address = db.Column(db.String(200), nullable=False)
    qr_code_path = db.Column(db.String(200), nullable=True)
    min_deposit = db.Column(db.Float, default=10.0)  # Minimum deposit amount
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ContentSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(50), nullable=False)  # home, stake, assets, profile
    section_name = db.Column(db.String(100), nullable=False)  # hero_title, benefits_text, etc.
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(20), default='text')  # text, html
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get_content(page_name, section_name, default_content=""):
        """Get content for a specific page section"""
        content = ContentSection.query.filter_by(
            page_name=page_name, 
            section_name=section_name, 
            is_active=True
        ).first()
        return content.content if content else default_content

    @staticmethod
    def set_content(page_name, section_name, content, content_type='text'):
        """Set or update content for a specific page section"""
        existing = ContentSection.query.filter_by(
            page_name=page_name, 
            section_name=section_name
        ).first()
        
        if existing:
            existing.content = content
            existing.content_type = content_type
            existing.updated_at = datetime.utcnow()
        else:
            new_content = ContentSection(
                page_name=page_name,
                section_name=section_name,
                content=content,
                content_type=content_type
            )
            db.session.add(new_content)
        
        db.session.commit()


class SupportMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    problem_type = db.Column(db.String(50), default='general')  # account, staking, deposits, technical, general
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    admin_reply = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='open')  # open, replied, closed
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    replied_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    user = db.relationship('User', backref='support_messages')
    
    def __repr__(self):
        return f'<SupportMessage {self.id}: {self.subject}>'
