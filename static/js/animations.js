// Animation and Visual Effects for USDT Staking Platform

document.addEventListener('DOMContentLoaded', function() {
    // Only initialize animations if no critical errors
    try {
        initializeAnimations();
    } catch (error) {
        console.log('Animation initialization failed, continuing without animations');
    }
});

function initializeAnimations() {
    // Initialize GSAP only if available
    if (typeof gsap !== 'undefined') {
        try {
            initGSAPAnimations();
        } catch (error) {
            console.log('GSAP animations failed, continuing without them');
        }
    }
    
    // Initialize CSS animations
    try {
        initCSSAnimations();
    } catch (error) {
        console.log('CSS animations failed, continuing without them');
    }
    
    // Initialize scroll animations
    try {
        initScrollAnimations();
    } catch (error) {
        console.log('Scroll animations failed, continuing without them');
    }
    
    // Initialize hover effects
    try {
        initHoverEffects();
    } catch (error) {
        console.log('Hover effects failed, continuing without them');
    }
    
    // Initialize particle effects
    try {
        initParticleEffects();
    } catch (error) {
        console.log('Particle effects failed, continuing without them');
    }
}

// GSAP Animations
function initGSAPAnimations() {
    // Hero section animation - only if elements exist
    if (document.querySelector('.hero-title')) {
        gsap.timeline()
            .from('.hero-title', { 
                duration: 1, 
                y: 50, 
                opacity: 0, 
                ease: 'power3.out' 
            })
            .from('.hero-subtitle', { 
                duration: 0.8, 
                y: 30, 
                opacity: 0, 
                ease: 'power3.out' 
            }, '-=0.5')
            .from('.hero-buttons', { 
                duration: 0.8, 
                y: 30, 
                opacity: 0, 
                ease: 'power3.out' 
            }, '-=0.3');
    }
    
    // Stats cards animation - only if elements exist
    if (document.querySelector('.stat-card')) {
        gsap.from('.stat-card', {
            duration: 0.8,
            y: 30,
            opacity: 0,
            stagger: 0.1,
            ease: 'power3.out'
        });
    }
    
    // Feature cards animation - only if elements exist
    if (document.querySelector('.feature-card')) {
        gsap.from('.feature-card', {
            duration: 1,
            scale: 0.8,
            opacity: 0,
            stagger: 0.15,
            ease: 'back.out(1.7)'
        });
    }
    
    // Glass card hover effect
    document.querySelectorAll('.glass-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            gsap.to(card, {
                duration: 0.3,
                scale: 1.02,
                boxShadow: '0 20px 40px rgba(31, 38, 135, 0.4)',
                ease: 'power2.out'
            });
        });
        
        card.addEventListener('mouseleave', () => {
            gsap.to(card, {
                duration: 0.3,
                scale: 1,
                boxShadow: '0 8px 32px rgba(31, 38, 135, 0.37)',
                ease: 'power2.out'
            });
        });
    });
}

// CSS-based animations
function initCSSAnimations() {
    // Fade in animation for elements
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.fade-in-element').forEach(el => {
        observer.observe(el);
    });
    
    // Add CSS for fade-in animation
    if (!document.querySelector('#fade-in-styles')) {
        const style = document.createElement('style');
        style.id = 'fade-in-styles';
        style.textContent = `
            .fade-in-element {
                opacity: 0;
                transform: translateY(30px);
                transition: opacity 0.8s ease, transform 0.8s ease;
            }
            .animate-fade-in {
                opacity: 1;
                transform: translateY(0);
            }
        `;
        document.head.appendChild(style);
    }
}

// Scroll animations
function initScrollAnimations() {
    let ticking = false;
    
    function updateScrollAnimations() {
        const scrollY = window.pageYOffset;
        
        // Parallax effect for hero background
        const heroSection = document.querySelector('.hero-section');
        if (heroSection) {
            heroSection.style.transform = `translateY(${scrollY * 0.5}px)`;
        }
        
        // Update navigation transparency based on scroll
        const navigation = document.querySelector('nav');
        if (navigation) {
            if (scrollY > 100) {
                navigation.classList.add('nav-scrolled');
            } else {
                navigation.classList.remove('nav-scrolled');
            }
        }
        
        ticking = false;
    }
    
    function requestScrollUpdate() {
        if (!ticking) {
            requestAnimationFrame(updateScrollAnimations);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', requestScrollUpdate);
}

// Hover effects
function initHoverEffects() {
    // Button glow effect
    document.querySelectorAll('.gradient-button').forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 0 30px rgba(102, 126, 234, 0.8)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)';
        });
    });
    
    // Card tilt effect
    document.querySelectorAll('.tilt-card').forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;
            
            this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.05, 1.05, 1.05)`;
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
        });
    });
}

// Particle effects
function initParticleEffects() {
    createFloatingParticles();
}

function createFloatingParticles() {
    const particleContainer = document.createElement('div');
    particleContainer.className = 'particle-container fixed inset-0 pointer-events-none z-0';
    document.body.appendChild(particleContainer);
    
    // Create particles
    for (let i = 0; i < 50; i++) {
        createParticle(particleContainer);
    }
}

function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle absolute rounded-full opacity-30';
    
    // Random size and position
    const size = Math.random() * 4 + 1;
    const x = Math.random() * window.innerWidth;
    const y = Math.random() * window.innerHeight;
    
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;
    particle.style.left = `${x}px`;
    particle.style.top = `${y}px`;
    particle.style.background = `linear-gradient(45deg, rgba(102, 126, 234, 0.5), rgba(118, 75, 162, 0.5))`;
    
    container.appendChild(particle);
    
    // Animate particle
    animateParticle(particle);
}

function animateParticle(particle) {
    const duration = Math.random() * 10000 + 10000; // 10-20 seconds
    const startY = parseFloat(particle.style.top);
    const endY = startY - window.innerHeight - 100;
    
    particle.animate([
        { transform: `translateY(0px) translateX(0px)`, opacity: 0.3 },
        { transform: `translateY(${endY}px) translateX(${Math.random() * 100 - 50}px)`, opacity: 0 }
    ], {
        duration: duration,
        easing: 'linear'
    }).onfinish = () => {
        // Reset particle position
        particle.style.top = `${window.innerHeight + 100}px`;
        particle.style.left = `${Math.random() * window.innerWidth}px`;
        animateParticle(particle);
    };
}

// Typing effect
function createTypingEffect(element, text, speed = 100) {
    let i = 0;
    element.textContent = '';
    
    function typeChar() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(typeChar, speed);
        }
    }
    
    typeChar();
}

// Number counting animation
function animateNumber(element, start, end, duration = 2000) {
    const startTime = Date.now();
    const range = end - start;
    
    function updateNumber() {
        const now = Date.now();
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = start + (range * easeOut);
        
        element.textContent = Math.round(current);
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    updateNumber();
}

// Glitch effect
function createGlitchEffect(element, duration = 500) {
    const originalText = element.textContent;
    const chars = '!@#$%^&*()_+-=[]{}|;:,.<>?';
    let interval;
    
    function glitch() {
        let glitchedText = '';
        for (let i = 0; i < originalText.length; i++) {
            if (Math.random() < 0.1) {
                glitchedText += chars[Math.floor(Math.random() * chars.length)];
            } else {
                glitchedText += originalText[i];
            }
        }
        element.textContent = glitchedText;
    }
    
    interval = setInterval(glitch, 50);
    
    setTimeout(() => {
        clearInterval(interval);
        element.textContent = originalText;
    }, duration);
}

// Ripple effect
function createRippleEffect(event) {
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    const ripple = document.createElement('span');
    ripple.className = 'ripple absolute rounded-full bg-white opacity-30 pointer-events-none';
    ripple.style.left = `${x}px`;
    ripple.style.top = `${y}px`;
    ripple.style.width = '0px';
    ripple.style.height = '0px';
    ripple.style.transform = 'translate(-50%, -50%)';
    
    button.appendChild(ripple);
    
    // Animate ripple
    ripple.animate([
        { width: '0px', height: '0px', opacity: 0.3 },
        { width: '200px', height: '200px', opacity: 0 }
    ], {
        duration: 600,
        easing: 'ease-out'
    }).onfinish = () => {
        ripple.remove();
    };
}

// Add ripple effect to buttons
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('gradient-button') || e.target.classList.contains('glass-button')) {
        createRippleEffect(e);
    }
});

// Smooth page transitions
function createPageTransition() {
    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.className = 'page-transition fixed inset-0 bg-gradient-to-br from-purple-900 to-pink-900 z-50 opacity-0';
        document.body.appendChild(overlay);
        
        overlay.animate([
            { opacity: 0 },
            { opacity: 1 }
        ], {
            duration: 300,
            easing: 'ease-in-out'
        }).onfinish = () => {
            setTimeout(() => {
                overlay.animate([
                    { opacity: 1 },
                    { opacity: 0 }
                ], {
                    duration: 300,
                    easing: 'ease-in-out'
                }).onfinish = () => {
                    overlay.remove();
                    resolve();
                };
            }, 100);
        };
    });
}

// Loading animations
function createLoadingSpinner(container) {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner flex items-center justify-center p-8';
    spinner.innerHTML = `
        <div class="relative w-16 h-16">
            <div class="absolute top-0 left-0 w-full h-full border-4 border-purple-200 rounded-full"></div>
            <div class="absolute top-0 left-0 w-full h-full border-4 border-purple-600 rounded-full border-t-transparent animate-spin"></div>
        </div>
    `;
    
    container.appendChild(spinner);
    return spinner;
}

// Export animation functions
window.AnimationUtils = {
    createTypingEffect,
    animateNumber,
    createGlitchEffect,
    createRippleEffect,
    createPageTransition,
    createLoadingSpinner
};

// Initialize additional animations when elements are added dynamically
const mutationObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) { // Element node
                // Re-initialize animations for new elements
                if (node.classList && node.classList.contains('glass-card')) {
                    initHoverEffects();
                }
                
                if (node.classList && node.classList.contains('fade-in-element')) {
                    const observer = new IntersectionObserver((entries) => {
                        entries.forEach(entry => {
                            if (entry.isIntersecting) {
                                entry.target.classList.add('animate-fade-in');
                            }
                        });
                    });
                    observer.observe(node);
                }
            }
        });
    });
});

// Start observing
mutationObserver.observe(document.body, {
    childList: true,
    subtree: true
});
