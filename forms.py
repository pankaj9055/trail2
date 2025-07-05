from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, FloatField, SelectField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')
    ])
    referral_code = StringField('Referral Code (Optional)', validators=[Length(max=20)])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')
    
    def validate_phone_number(self, phone_number):
        user = User.query.filter_by(phone_number=phone_number.data).first()
        if user:
            raise ValidationError('Phone number already registered. Please use a different one.')

class StakeForm(FlaskForm):
    coin_id = SelectField('Coin', validators=[DataRequired()], coerce=int)
    plan_id = SelectField('Staking Plan', validators=[DataRequired()], coerce=int)
    amount = FloatField('Amount (USDT)', validators=[DataRequired(), NumberRange(min=1)])

class DepositForm(FlaskForm):
    amount = FloatField('Amount (USDT)', validators=[DataRequired(), NumberRange(min=1)])
    transaction_id = StringField('Transaction ID', validators=[DataRequired(), Length(min=10, max=100)])
    screenshot = FileField('Transaction Screenshot', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])

class WithdrawalForm(FlaskForm):
    amount = FloatField('Amount (USDT)', validators=[DataRequired(), NumberRange(min=1)])
    wallet_address = StringField('Wallet Address', validators=[DataRequired(), Length(min=20, max=200)])
    network = SelectField('Network', choices=[('BEP20', 'BEP20'), ('TRC20', 'TRC20')], validators=[DataRequired()])
    password = PasswordField('Confirm Password', validators=[DataRequired()])

class AdminUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    usdt_balance = FloatField('USDT Balance', validators=[NumberRange(min=0)])
    is_admin = BooleanField('Admin User')
    is_active = BooleanField('Active User')

class AdminCoinForm(FlaskForm):
    symbol = StringField('Symbol', validators=[DataRequired(), Length(max=10)])
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    min_stake = FloatField('Minimum Stake', validators=[DataRequired(), NumberRange(min=0)])
    active = BooleanField('Active')

class AdminStakingPlanForm(FlaskForm):
    duration_days = IntegerField('Duration (Days)', validators=[DataRequired(), NumberRange(min=1)])
    interest_rate = FloatField('Daily Interest Rate (%)', validators=[DataRequired(), NumberRange(min=0)])
    active = BooleanField('Active')

class AdminSettingsForm(FlaskForm):
    platform_name = StringField('Platform Name', validators=[DataRequired()])
    referral_level_1 = FloatField('Level 1 Referral (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    referral_level_2 = FloatField('Level 2 Referral (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    referral_level_3 = FloatField('Level 3 Referral (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    min_referral_activation = FloatField('Min Referral Activation', validators=[DataRequired(), NumberRange(min=0)])
    withdrawal_fee = FloatField('Withdrawal Fee (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])

class AdminPasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), EqualTo('new_password', message='Passwords must match.')
    ])

class AdminPaymentAddressForm(FlaskForm):
    network = SelectField('Network', choices=[('BEP20', 'BEP20'), ('TRC20', 'TRC20')], validators=[DataRequired()])
    address = StringField('Wallet Address', validators=[DataRequired(), Length(min=20, max=200)])
    min_deposit = FloatField('Minimum Deposit (USDT)', validators=[DataRequired(), NumberRange(min=1)], default=10.0)
    is_active = BooleanField('Active', default=True)


class AdminContentForm(FlaskForm):
    page_name = SelectField('Page', choices=[
        ('home', 'Home Page'),
        ('stake', 'Stake Page'),
        ('assets', 'Assets Page'),
        ('profile', 'Profile Page')
    ], validators=[DataRequired()])
    section_name = StringField('Section Name', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Content', validators=[DataRequired()], render_kw={"rows": 6})
    content_type = SelectField('Content Type', choices=[
        ('text', 'Plain Text'),
        ('html', 'HTML')
    ], default='text')
    is_active = BooleanField('Active', default=True)


class SupportMessageForm(FlaskForm):
    problem_type = SelectField('Problem Type', choices=[
        ('account', 'Account & Login Issues'),
        ('staking', 'Staking & Investment Problems'),
        ('deposits', 'Deposit & Withdrawal Issues'),
        ('technical', 'Technical Support'),
        ('general', 'General Questions')
    ], validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Describe your problem in detail', validators=[DataRequired()], render_kw={"rows": 5})
    priority = SelectField('Priority', choices=[
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='normal')


class AdminSupportReplyForm(FlaskForm):
    admin_reply = TextAreaField('Reply', validators=[DataRequired()], render_kw={"rows": 4})
    status = SelectField('Status', choices=[
        ('open', 'Open'),
        ('replied', 'Replied'),
        ('closed', 'Closed')
    ], default='replied')
