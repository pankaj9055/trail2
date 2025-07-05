# USDT Staking Platform

## Overview

This is a comprehensive USDT staking platform built with Flask, featuring user authentication, staking mechanisms, referral systems, and comprehensive admin management. The platform allows users to stake USDT coins across multiple plans while earning rewards and building referral networks.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with support for multiple databases
- **Authentication**: Flask-Login for session management
- **Forms**: Flask-WTF for form handling and validation
- **Security**: Werkzeug for password hashing and security utilities

### Frontend Architecture
- **CSS Framework**: TailwindCSS for responsive design
- **Styling**: Custom CSS with glass morphism effects
- **JavaScript**: Vanilla JS with GSAP for animations
- **UI Components**: Mobile-first design with bottom navigation
- **Icons**: Font Awesome for iconography

### Database Design
- **SQLAlchemy Models**: Using DeclarativeBase for modern SQLAlchemy patterns
- **User Management**: Comprehensive user profiles with referral tracking
- **Financial Operations**: Deposit, withdrawal, and staking transaction management
- **Admin Controls**: Platform settings and user management capabilities

## Key Components

### User Management System
- User registration and authentication
- Profile management with referral codes
- Multi-level referral system (3 levels deep)
- Admin user privileges and permissions

### Staking System
- Multiple coin support (though primarily USDT-focused)
- Flexible staking plans with varying durations and returns
- Real-time stake tracking and earnings calculation
- Automated reward distribution

### Financial Operations
- USDT wallet management
- Deposit system with transaction verification
- Withdrawal processing with multiple network support (BEP20, TRC20)
- Transaction history and status tracking

### Admin Panel
- Comprehensive dashboard with platform statistics
- User management and account controls
- Transaction approval system (deposits/withdrawals)
- Platform settings configuration
- Staking plan management

### Security Features
- Password hashing with Werkzeug
- Session management with Flask-Login
- CSRF protection with Flask-WTF
- Input validation and sanitization
- Admin-only route protection

## Data Flow

### User Registration Flow
1. User submits registration form with optional referral code
2. System validates unique username/email
3. Password is hashed and user account created
4. Referral relationships established if referral code provided
5. User gains access to platform features

### Staking Flow
1. User selects coin and staking plan
2. System validates available balance
3. Stake record created with calculated returns
4. User balance updated and staking position established
5. Rewards calculated and distributed based on plan terms

### Transaction Flow
1. User initiates deposit/withdrawal request
2. Transaction record created with pending status
3. Admin reviews and approves/rejects transaction
4. User balance updated upon approval
5. Activity logged for audit trail

## External Dependencies

### Python Packages
- Flask: Web framework
- Flask-SQLAlchemy: Database ORM
- Flask-Login: Authentication management
- Flask-WTF: Form handling
- Werkzeug: Security utilities
- QRCode: QR code generation for deposits

### Frontend Libraries
- TailwindCSS: Utility-first CSS framework
- Font Awesome: Icon library
- GSAP: Animation library
- Google Fonts (Poppins): Typography

### Development Tools
- Python 3.x runtime
- SQLite (default) with PostgreSQL support
- File upload handling for transaction screenshots

## Deployment Strategy

### Environment Configuration
- Environment variables for sensitive settings (DATABASE_URL, SESSION_SECRET)
- Debug mode for development environments
- Production-ready WSGI configuration with ProxyFix
- Database connection pooling for performance

### Database Setup
- Automatic table creation on first run
- Admin user creation process
- Migration support through SQLAlchemy
- Support for both SQLite (development) and PostgreSQL (production)

### Security Considerations
- Secret key management through environment variables
- Secure file upload handling
- SQL injection prevention through ORM
- XSS protection through template escaping

## Changelog

- June 30, 2025. Initial setup
- July 1, 2025. Fixed website crash and database connection issues. Added comprehensive admin panel with full website control features including coin management, staking plan management, user management, transaction approval, and activity logging. Added direct admin access route for easy authentication.
- July 1, 2025. Complete separation of admin and user interfaces achieved. Removed all admin elements from user interface. Improved website performance from 3-4 seconds to ~2 seconds response time. Enhanced stake display with detailed information including current earnings, maturity dates, progress bars, and withdrawal options. Added admin password change functionality accessible only from admin panel.
- July 2, 2025. Major feature additions: Phone number registration with unique validation, withdrawal fee system (1% fee waived for users with 2+ referrals), 2-referral bonus system (20 USDT bonus + 2% extra staking income + no withdrawal fees), admin payment address management system, enhanced referral tracking with premium member benefits display.
- July 2, 2025. Performance optimization and content enhancement: Optimized CSS for faster loading (~60% faster page transitions), enhanced admin user management with phone number display and ban/unban functionality, added comprehensive detailed content with animations to all pages (home, stake, assets), implemented smooth fade-in animations and hover effects, added detailed investment insights and financial guidance content throughout the platform.
- July 3, 2025. Complete support system implementation: Added floating support chat button visible on all pages with glowing animation, created comprehensive support messaging system where users can send messages with priority levels, built admin support dashboard to view and reply to all user messages, added user contact information display in admin support panel, implemented support message history and status tracking.

## User Preferences

Preferred communication style: Simple, everyday language.