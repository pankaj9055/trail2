import os
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import qrcode
import io
import base64
from app import app, db
from models import User, Coin, StakingPlan, Stake, Deposit, Withdrawal, PlatformSettings, ActivityLog, PaymentAddress, ContentSection, SupportMessage
from forms import LoginForm, RegisterForm, StakeForm, DepositForm, WithdrawalForm, AdminUserForm, AdminCoinForm, AdminStakingPlanForm, AdminSettingsForm, AdminPasswordChangeForm, AdminPaymentAddressForm, AdminContentForm, SupportMessageForm, AdminSupportReplyForm
from utils import log_activity, generate_qr_code, admin_required

# Public routes
@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    settings = PlatformSettings.get_all_settings()
    return render_template('index_simple.html', settings=settings)

@app.route('/home')
@login_required
def home():
    user_stats = {
        'usdt_balance': current_user.usdt_balance,
        'total_staked': current_user.total_staked,
        'total_earned': current_user.total_earned,
        'referral_bonus': current_user.referral_bonus
    }
    
    # Get recent activities
    recent_stakes = Stake.query.filter_by(user_id=current_user.id).order_by(Stake.created_at.desc()).limit(5).all()
    
    return render_template('home.html', user_stats=user_stats, recent_stakes=recent_stakes)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user)
            log_activity(user.id, 'login', f'User {user.username} logged in')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        flash('Invalid email or password', 'error')
    
    return render_template('auth/login_new.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        referrer = None
        if form.referral_code.data:
            referrer = User.query.filter_by(referral_code=form.referral_code.data).first()
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            referred_by=referrer.id if referrer else None
        )
        user.set_password(form.password.data)
        
        # Handle referral bonus and 2-referral milestone
        if referrer:
            # Get current referral count before adding new user
            previous_count = referrer.get_referral_count()
            
            # Add user first
            db.session.add(user)
            db.session.commit()
            
            # Check if referrer just reached 2 referrals
            new_count = referrer.get_referral_count()
            if previous_count < 2 and new_count >= 2:
                referrer.usdt_balance += 20.0
                referrer.referral_bonus += 20.0
                db.session.commit()
                log_activity(referrer.id, 'referral_milestone', f'Received 20 USDT bonus for completing 2 referrals')
        else:
            db.session.add(user)
            db.session.commit()
        
        log_activity(user.id, 'register', f'New user {user.username} registered')
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register_new.html', form=form)

@app.route('/logout')
@login_required
def logout():
    log_activity(current_user.id, 'logout', f'User {current_user.username} logged out')
    logout_user()
    return redirect(url_for('index'))

# Staking routes
@app.route('/stake', methods=['GET', 'POST'])
@login_required
def stake():
    form = StakeForm()
    
    # Populate form choices
    form.coin_id.choices = [(c.id, f"{c.symbol} - {c.name}") for c in Coin.query.filter_by(active=True).all()]
    form.plan_id.choices = [(p.id, f"{p.duration_days} days - {p.interest_rate}% daily") for p in StakingPlan.query.filter_by(active=True).all()]
    
    if form.validate_on_submit():
        coin = Coin.query.get(form.coin_id.data)
        plan = StakingPlan.query.get(form.plan_id.data)
        
        if form.amount.data < coin.min_stake:
            flash(f'Minimum stake for {coin.symbol} is {coin.min_stake} USDT', 'error')
        elif form.amount.data > current_user.usdt_balance:
            flash('Insufficient balance', 'error')
        else:
            # Create stake
            end_date = datetime.utcnow() + timedelta(days=plan.duration_days)
            
            # Apply 2% bonus interest for users with 2+ referrals
            daily_interest = plan.interest_rate
            bonus_applied = False
            if current_user.has_two_referrals():
                daily_interest += 2.0  # Add 2% bonus daily interest
                bonus_applied = True
            
            total_return = form.amount.data * daily_interest * plan.duration_days / 100
            
            stake = Stake(
                user_id=current_user.id,
                coin_id=coin.id,
                plan_id=plan.id,
                amount=form.amount.data,
                daily_interest=daily_interest,
                total_return=total_return,
                end_date=end_date
            )
            
            if bonus_applied:
                flash(f'2% bonus applied! You have {current_user.get_referral_count()} referrals', 'success')
            
            # Update user balance
            current_user.usdt_balance -= form.amount.data
            current_user.total_staked += form.amount.data
            
            db.session.add(stake)
            db.session.commit()
            
            log_activity(current_user.id, 'stake', f'Staked {form.amount.data} USDT in {coin.symbol} for {plan.duration_days} days')
            flash('Stake created successfully!', 'success')
            return redirect(url_for('stake'))
    
    # Get user stakes
    user_stakes = Stake.query.filter_by(user_id=current_user.id).order_by(Stake.created_at.desc()).all()
    
    coins = Coin.query.filter_by(active=True).all()
    plans = StakingPlan.query.filter_by(active=True).all()
    
    return render_template('stake_new.html', form=form, user_stakes=user_stakes, coins=coins, plans=plans)

@app.route('/cancel_stake/<int:stake_id>')
@login_required
def cancel_stake(stake_id):
    stake = Stake.query.get_or_404(stake_id)
    
    if stake.user_id != current_user.id:
        flash('Unauthorized action', 'error')
        return redirect(url_for('stake'))
    
    if stake.status != 'active':
        flash('Stake cannot be cancelled', 'error')
        return redirect(url_for('stake'))
    
    # Cancel stake and return principal
    stake.status = 'cancelled'
    current_user.usdt_balance += stake.amount
    current_user.total_staked -= stake.amount
    
    db.session.commit()
    
    log_activity(current_user.id, 'cancel_stake', f'Cancelled stake #{stake.id}')
    flash('Stake cancelled successfully. Principal amount returned.', 'success')
    return redirect(url_for('stake'))

@app.route('/withdraw_stake/<int:stake_id>')
@login_required
def withdraw_stake(stake_id):
    stake = Stake.query.get_or_404(stake_id)
    
    if stake.user_id != current_user.id:
        flash('Unauthorized action', 'error')
        return redirect(url_for('stake'))
    
    if not stake.is_mature or stake.withdrawn:
        flash('Stake not ready for withdrawal', 'error')
        return redirect(url_for('stake'))
    
    # Calculate final return
    current_return = stake.calculate_current_return()
    total_amount = stake.amount + current_return
    
    # Update user balance
    current_user.usdt_balance += total_amount
    current_user.total_earned += current_return
    current_user.total_staked -= stake.amount
    
    stake.status = 'completed'
    stake.withdrawn = True
    
    db.session.commit()
    
    log_activity(current_user.id, 'withdraw_stake', f'Withdrew stake #{stake.id} - Principal: {stake.amount}, Earnings: {current_return}')
    flash(f'Stake withdrawn successfully! Total: {total_amount} USDT (Earnings: {current_return} USDT)', 'success')
    return redirect(url_for('stake'))

# Assets routes
@app.route('/assets', methods=['GET', 'POST'])
@login_required
def assets():
    deposit_form = DepositForm()
    withdrawal_form = WithdrawalForm()
    
    if request.method == 'POST':
        if 'deposit' in request.form and deposit_form.validate_on_submit():
            # Handle deposit
            deposit = Deposit(
                user_id=current_user.id,
                amount=deposit_form.amount.data,
                transaction_id=deposit_form.transaction_id.data
            )
            
            # Handle file upload
            if deposit_form.screenshot.data:
                filename = secure_filename(deposit_form.screenshot.data.filename)
                upload_path = os.path.join('static', 'uploads', filename)
                deposit_form.screenshot.data.save(upload_path)
                deposit.screenshot_path = upload_path
            
            db.session.add(deposit)
            db.session.commit()
            
            log_activity(current_user.id, 'deposit_request', f'Deposit request for {deposit_form.amount.data} USDT')
            flash('Deposit request submitted for admin approval', 'success')
            return redirect(url_for('assets'))
        
        elif 'withdrawal' in request.form and withdrawal_form.validate_on_submit():
            # Verify password
            if not current_user.check_password(withdrawal_form.password.data):
                flash('Invalid password', 'error')
                return redirect(url_for('assets'))
            
            # Calculate withdrawal fee
            base_amount = withdrawal_form.amount.data
            fee_percentage = 1.0  # 1% default fee
            
            # Check if user has 2 referrals for no fee
            if current_user.has_two_referrals():
                fee_percentage = 0.0
                flash('No withdrawal fee - You have 2+ referrals!', 'success')
            
            fee_amount = base_amount * (fee_percentage / 100)
            total_deduction = base_amount + fee_amount
            
            # Check balance including fee
            if total_deduction > current_user.usdt_balance:
                flash(f'Insufficient balance. Need {total_deduction:.2f} USDT (including {fee_percentage}% fee)', 'error')
                return redirect(url_for('assets'))
            
            # Handle withdrawal
            withdrawal = Withdrawal(
                user_id=current_user.id,
                amount=base_amount,
                wallet_address=withdrawal_form.wallet_address.data,
                network=withdrawal_form.network.data
            )
            
            db.session.add(withdrawal)
            db.session.commit()
            
            log_activity(current_user.id, 'withdrawal_request', f'Withdrawal request for {withdrawal_form.amount.data} USDT')
            flash('Withdrawal request submitted for admin approval', 'success')
            return redirect(url_for('assets'))
    
    # Get user transaction history
    deposits = Deposit.query.filter_by(user_id=current_user.id).order_by(Deposit.created_at.desc()).all()
    withdrawals = Withdrawal.query.filter_by(user_id=current_user.id).order_by(Withdrawal.created_at.desc()).all()
    
    return render_template('assets.html', 
                         deposit_form=deposit_form, 
                         withdrawal_form=withdrawal_form,
                         deposits=deposits, 
                         withdrawals=withdrawals)

# Profile routes
@app.route('/profile')
@login_required
def profile():
    referral_tree = current_user.get_referral_tree()
    total_referrals = len([r for r in User.query.filter_by(referred_by=current_user.id).all()])
    
    return render_template('profile.html', 
                         referral_tree=referral_tree, 
                         total_referrals=total_referrals)

@app.route('/generate_referral_qr')
@login_required
def generate_referral_qr():
    referral_link = url_for('register', referral_code=current_user.referral_code, _external=True)
    qr_code = generate_qr_code(referral_link)
    return qr_code

# Direct admin access
@app.route('/adminaccess')
def admin_access():
    """Direct admin login for testing purposes"""
    admin_user = User.query.filter_by(email='admin@staking.com').first()
    if admin_user and admin_user.is_admin:
        login_user(admin_user, remember=True)
        log_activity(admin_user.id, 'admin_direct_login', 'Admin accessed via direct route')
        flash('Logged in as admin', 'success')
        return redirect(url_for('admin_dashboard'))
    return "Admin access failed"

# Admin routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_stakes': Stake.query.count(),
        'total_staked_amount': db.session.query(db.func.sum(Stake.amount)).scalar() or 0,
        'pending_deposits': Deposit.query.filter_by(status='pending').count(),
        'pending_withdrawals': Withdrawal.query.filter_by(status='pending').count(),
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/stakes')
@login_required
@admin_required
def admin_stakes():
    stakes = Stake.query.order_by(Stake.created_at.desc()).all()
    return render_template('admin/stakes.html', stakes=stakes)

@app.route('/admin/transactions')
@login_required
@admin_required
def admin_transactions():
    deposits = Deposit.query.order_by(Deposit.created_at.desc()).all()
    withdrawals = Withdrawal.query.order_by(Withdrawal.created_at.desc()).all()
    return render_template('admin/transactions.html', deposits=deposits, withdrawals=withdrawals)

@app.route('/admin/approve_deposit/<int:deposit_id>')
@login_required
@admin_required
def admin_approve_deposit(deposit_id):
    deposit = Deposit.query.get_or_404(deposit_id)
    
    if deposit.status == 'pending':
        deposit.status = 'approved'
        deposit.processed_at = datetime.utcnow()
        
        # Add balance to user
        user = User.query.get(deposit.user_id)
        user.usdt_balance += deposit.amount
        
        # Process referral bonus if applicable
        if user.referred_by:
            referrer = User.query.get(user.referred_by)
            bonus = user.calculate_referral_bonus(deposit.amount)
            if bonus > 0:
                referrer.referral_bonus += bonus
                referrer.usdt_balance += bonus
        
        db.session.commit()
        
        log_activity(None, 'admin_approve_deposit', f'Approved deposit #{deposit.id} for user {user.username}')
        flash('Deposit approved successfully', 'success')
    
    return redirect(url_for('admin_transactions'))

@app.route('/admin/reject_deposit/<int:deposit_id>')
@login_required
@admin_required
def admin_reject_deposit(deposit_id):
    deposit = Deposit.query.get_or_404(deposit_id)
    
    if deposit.status == 'pending':
        deposit.status = 'rejected'
        deposit.processed_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(None, 'admin_reject_deposit', f'Rejected deposit #{deposit.id}')
        flash('Deposit rejected', 'success')
    
    return redirect(url_for('admin_transactions'))

@app.route('/admin/approve_withdrawal/<int:withdrawal_id>')
@login_required
@admin_required
def admin_approve_withdrawal(withdrawal_id):
    withdrawal = Withdrawal.query.get_or_404(withdrawal_id)
    
    if withdrawal.status == 'pending':
        withdrawal.status = 'approved'
        withdrawal.processed_at = datetime.utcnow()
        
        # Deduct balance from user
        user = User.query.get(withdrawal.user_id)
        user.usdt_balance -= withdrawal.amount
        
        db.session.commit()
        
        log_activity(None, 'admin_approve_withdrawal', f'Approved withdrawal #{withdrawal.id} for user {user.username}')
        flash('Withdrawal approved successfully', 'success')
    
    return redirect(url_for('admin_transactions'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_settings():
    form = AdminSettingsForm()
    
    if form.validate_on_submit():
        PlatformSettings.set_setting('platform_name', form.platform_name.data)
        PlatformSettings.set_setting('referral_level_1', str(form.referral_level_1.data))
        PlatformSettings.set_setting('referral_level_2', str(form.referral_level_2.data))
        PlatformSettings.set_setting('referral_level_3', str(form.referral_level_3.data))
        PlatformSettings.set_setting('min_referral_activation', str(form.min_referral_activation.data))
        PlatformSettings.set_setting('withdrawal_fee', str(form.withdrawal_fee.data))
        
        flash('Settings updated successfully', 'success')
        return redirect(url_for('admin_settings'))
    
    # Load current settings
    settings = PlatformSettings.get_all_settings()
    form.platform_name.data = settings.get('platform_name', 'USDT Staking Platform')
    form.referral_level_1.data = float(settings.get('referral_level_1', 5))
    form.referral_level_2.data = float(settings.get('referral_level_2', 3))
    form.referral_level_3.data = float(settings.get('referral_level_3', 2))
    form.min_referral_activation.data = float(settings.get('min_referral_activation', 100))
    form.withdrawal_fee.data = float(settings.get('withdrawal_fee', 0))
    
    return render_template('admin/settings.html', form=form, current_settings=settings)

@app.route('/admin/password', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_change_password():
    form = AdminPasswordChangeForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            log_activity(current_user.id, 'admin_password_change', 'Admin password changed')
            flash('Password changed successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Current password is incorrect', 'error')
    
    return render_template('admin/password_change.html', form=form)

@app.route('/admin/coins')
@login_required
@admin_required
def admin_coins():
    coins = Coin.query.all()
    return render_template('admin/coins.html', coins=coins)

@app.route('/admin/coins/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_coin():
    form = AdminCoinForm()
    if form.validate_on_submit():
        coin = Coin(
            symbol=form.symbol.data,
            name=form.name.data,
            min_stake=form.min_stake.data,
            active=form.active.data
        )
        db.session.add(coin)
        db.session.commit()
        log_activity(current_user.id, 'admin_add_coin', f'Added coin {form.symbol.data}')
        flash('Coin added successfully', 'success')
        return redirect(url_for('admin_coins'))
    return render_template('admin/coin_form.html', form=form, title='Add Coin')

@app.route('/admin/coins/edit/<int:coin_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_coin(coin_id):
    coin = Coin.query.get_or_404(coin_id)
    form = AdminCoinForm(obj=coin)
    if form.validate_on_submit():
        coin.symbol = form.symbol.data
        coin.name = form.name.data
        coin.min_stake = form.min_stake.data
        coin.active = form.active.data
        db.session.commit()
        log_activity(current_user.id, 'admin_edit_coin', f'Edited coin {coin.symbol}')
        flash('Coin updated successfully', 'success')
        return redirect(url_for('admin_coins'))
    return render_template('admin/coin_form.html', form=form, title='Edit Coin', coin=coin)

@app.route('/admin/plans')
@login_required
@admin_required
def admin_plans():
    plans = StakingPlan.query.all()
    return render_template('admin/plans.html', plans=plans)

@app.route('/admin/plans/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_plan():
    form = AdminStakingPlanForm()
    if form.validate_on_submit():
        plan = StakingPlan(
            duration_days=form.duration_days.data,
            interest_rate=form.interest_rate.data,
            active=form.active.data
        )
        db.session.add(plan)
        db.session.commit()
        log_activity(current_user.id, 'admin_add_plan', f'Added staking plan {form.duration_days.data} days')
        flash('Staking plan added successfully', 'success')
        return redirect(url_for('admin_plans'))
    return render_template('admin/plan_form.html', form=form, title='Add Staking Plan')

@app.route('/admin/plans/edit/<int:plan_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_plan(plan_id):
    plan = StakingPlan.query.get_or_404(plan_id)
    form = AdminStakingPlanForm(obj=plan)
    if form.validate_on_submit():
        plan.duration_days = form.duration_days.data
        plan.interest_rate = form.interest_rate.data
        plan.active = form.active.data
        db.session.commit()
        log_activity(current_user.id, 'admin_edit_plan', f'Edited staking plan {plan.duration_days} days')
        flash('Staking plan updated successfully', 'success')
        return redirect(url_for('admin_plans'))
    return render_template('admin/plan_form.html', form=form, title='Edit Staking Plan', plan=plan)

@app.route('/admin/activity')
@login_required
@admin_required
def admin_activity():
    page = request.args.get('page', 1, type=int)
    activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template('admin/activity.html', activities=activities)

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminUserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.usdt_balance = form.usdt_balance.data
        user.is_admin = form.is_admin.data
        user.is_active = form.is_active.data
        db.session.commit()
        log_activity(current_user.id, 'admin_edit_user', f'Edited user {user.username}')
        flash('User updated successfully', 'success')
        return redirect(url_for('admin_users'))
    return render_template('admin/user_form.html', form=form, title='Edit User', user=user)

# Admin Payment Address Management
@app.route('/admin/payment-addresses')
@login_required
@admin_required
def admin_payment_addresses():
    addresses = PaymentAddress.query.all()
    return render_template('admin/payment_addresses.html', addresses=addresses)

@app.route('/admin/payment-addresses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_payment_address():
    form = AdminPaymentAddressForm()
    if form.validate_on_submit():
        address = PaymentAddress(
            network=form.network.data,
            address=form.address.data,
            is_active=form.is_active.data
        )
        db.session.add(address)
        db.session.commit()
        log_activity(current_user.id, 'admin_add_address', f'Added {form.network.data} payment address')
        flash('Payment address added successfully', 'success')
        return redirect(url_for('admin_payment_addresses'))
    return render_template('admin/payment_address_form.html', form=form, title='Add Payment Address')

@app.route('/admin/payment-addresses/edit/<int:address_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_payment_address(address_id):
    address = PaymentAddress.query.get_or_404(address_id)
    form = AdminPaymentAddressForm(obj=address)
    if form.validate_on_submit():
        address.network = form.network.data
        address.address = form.address.data
        address.is_active = form.is_active.data
        db.session.commit()
        log_activity(current_user.id, 'admin_edit_address', f'Edited {form.network.data} payment address')
        flash('Payment address updated successfully', 'success')
        return redirect(url_for('admin_payment_addresses'))
    return render_template('admin/payment_address_form.html', form=form, title='Edit Payment Address', address=address)

@app.route('/admin/users/ban/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_ban_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Cannot ban admin users', 'error')
        return redirect(url_for('admin_users'))
    
    user.is_active = False
    db.session.commit()
    log_activity(current_user.id, 'admin_ban_user', f'Banned user {user.username}')
    flash(f'User {user.username} has been banned successfully', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/unban/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_unban_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    log_activity(current_user.id, 'admin_unban_user', f'Unbanned user {user.username}')
    flash(f'User {user.username} has been unbanned successfully', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/limit/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_set_limit(user_id):
    user = User.query.get_or_404(user_id)
    # For now, we'll redirect to edit user page where limits can be set
    return redirect(url_for('admin_edit_user', user_id=user_id))


@app.route('/admin/content')
@login_required
@admin_required
def admin_content():
    contents = ContentSection.query.order_by(ContentSection.page_name, ContentSection.section_name).all()
    return render_template('admin/content.html', contents=contents)


@app.route('/admin/content/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add_content():
    form = AdminContentForm()
    if form.validate_on_submit():
        ContentSection.set_content(
            form.page_name.data,
            form.section_name.data,
            form.content.data,
            form.content_type.data
        )
        
        log_activity(current_user.id, 'add_content', f'Added content section: {form.page_name.data}/{form.section_name.data}', request.remote_addr)
        flash('Content added successfully!', 'success')
        return redirect(url_for('admin_content'))
    
    return render_template('admin/content_form.html', form=form, title='Add Content')


@app.route('/admin/content/<int:content_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_content(content_id):
    content = ContentSection.query.get_or_404(content_id)
    form = AdminContentForm(obj=content)
    
    if form.validate_on_submit():
        content.page_name = form.page_name.data
        content.section_name = form.section_name.data
        content.content = form.content.data
        content.content_type = form.content_type.data
        content.is_active = form.is_active.data
        content.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(current_user.id, 'edit_content', f'Edited content section: {content.page_name}/{content.section_name}', request.remote_addr)
        flash('Content updated successfully!', 'success')
        return redirect(url_for('admin_content'))
    
    return render_template('admin/content_form.html', form=form, content=content, title='Edit Content')


@app.route('/admin/content/<int:content_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_content(content_id):
    content = ContentSection.query.get_or_404(content_id)
    page_section = f'{content.page_name}/{content.section_name}'
    
    db.session.delete(content)
    db.session.commit()
    
    log_activity(current_user.id, 'delete_content', f'Deleted content section: {page_section}', request.remote_addr)
    flash('Content deleted successfully!', 'success')
    return redirect(url_for('admin_content'))


@app.route('/admin/payment-address/<int:address_id>/toggle', methods=['POST'])
@login_required
@admin_required
def admin_toggle_payment_address(address_id):
    address = PaymentAddress.query.get_or_404(address_id)
    data = request.get_json()
    
    if data and 'is_active' in data:
        address.is_active = data['is_active']
        address.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = 'activated' if data['is_active'] else 'deactivated'
        log_activity(current_user.id, 'toggle_payment_address', f'{status.capitalize()} payment address: {address.network}', request.remote_addr)
        
        return jsonify({'success': True, 'message': f'Payment address {status} successfully'})
    
    return jsonify({'success': False, 'message': 'Invalid request'})


@app.route('/support', methods=['GET', 'POST'])
@login_required
def support():
    form = SupportMessageForm()
    if form.validate_on_submit():
        support_msg = SupportMessage(
            user_id=current_user.id,
            problem_type=form.problem_type.data,
            subject=form.subject.data,
            message=form.message.data,
            priority=form.priority.data
        )
        db.session.add(support_msg)
        db.session.commit()
        
        log_activity(current_user.id, 'support_message', f'Sent support message: {form.subject.data}', request.remote_addr)
        flash('Your message has been sent! We will reply shortly.', 'success')
        return redirect(url_for('support'))
    
    # Get user's previous messages
    messages = SupportMessage.query.filter_by(user_id=current_user.id).order_by(SupportMessage.created_at.desc()).all()
    return render_template('support.html', form=form, messages=messages)


@app.route('/admin/support')
@login_required
@admin_required
def admin_support():
    messages = SupportMessage.query.order_by(SupportMessage.created_at.desc()).all()
    
    # Stats
    total_messages = len(messages)
    open_messages = len([m for m in messages if m.status == 'open'])
    urgent_messages = len([m for m in messages if m.priority == 'urgent'])
    
    stats = {
        'total': total_messages,
        'open': open_messages,
        'urgent': urgent_messages,
        'replied': len([m for m in messages if m.status == 'replied'])
    }
    
    return render_template('admin/support.html', messages=messages, stats=stats)


@app.route('/admin/support/<int:message_id>/reply', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_support_reply(message_id):
    message = SupportMessage.query.get_or_404(message_id)
    form = AdminSupportReplyForm(obj=message)
    
    if form.validate_on_submit():
        message.admin_reply = form.admin_reply.data
        message.status = form.status.data
        message.replied_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(current_user.id, 'support_reply', f'Replied to support message: {message.subject}', request.remote_addr)
        flash('Reply sent successfully!', 'success')
        return redirect(url_for('admin_support'))
    
    return render_template('admin/support_reply.html', message=message, form=form)

# Error handlers
@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
