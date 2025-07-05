import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///staking_platform.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models and create tables
    import models
    db.create_all()
    
    # Create admin user if it doesn't exist
    admin_user = models.User.query.filter_by(email='admin@staking.com').first()
    if not admin_user:
        from werkzeug.security import generate_password_hash
        admin = models.User(
            username='admin',
            email='admin@staking.com',
            phone_number='+1234567890',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            usdt_balance=0.0,
            is_active=True
        )
        db.session.add(admin)
        
        # Create default staking coins
        coins = [
            {'symbol': 'BNB', 'name': 'BNB Smart Chain', 'min_stake': 80, 'active': True},
            {'symbol': 'BTC', 'name': 'Bitcoin', 'min_stake': 130, 'active': True},
            {'symbol': 'ETH', 'name': 'Ethereum', 'min_stake': 160, 'active': True},
            {'symbol': 'LTC', 'name': 'Litecoin', 'min_stake': 220, 'active': True},
            {'symbol': 'SOL', 'name': 'Solana', 'min_stake': 100, 'active': True},
            {'symbol': 'TRX', 'name': 'TRON', 'min_stake': 90, 'active': True},
            {'symbol': 'DOT', 'name': 'Polkadot', 'min_stake': 150, 'active': True},
        ]
        
        for coin_data in coins:
            coin = models.Coin(**coin_data)
            db.session.add(coin)
        
        # Create default staking plans
        plans = [
            {'duration_days': 7, 'interest_rate': 1.2},
            {'duration_days': 15, 'interest_rate': 1.5},
            {'duration_days': 30, 'interest_rate': 2.0},
            {'duration_days': 90, 'interest_rate': 3.5},
            {'duration_days': 120, 'interest_rate': 4.8},
        ]
        
        for plan_data in plans:
            plan = models.StakingPlan(**plan_data)
            db.session.add(plan)
        
        # Create platform settings
        settings = [
            {'key': 'referral_level_1', 'value': '5.0'},
            {'key': 'referral_level_2', 'value': '3.0'},
            {'key': 'referral_level_3', 'value': '2.0'},
            {'key': 'min_referral_activation', 'value': '100.0'},
            {'key': 'platform_name', 'value': 'USDT Staking Platform'},
            {'key': 'withdrawal_fee', 'value': '0.0'},
        ]
        
        for setting_data in settings:
            setting = models.PlatformSettings(**setting_data)
            db.session.add(setting)
        
        db.session.commit()
        logging.info("Default data created")
