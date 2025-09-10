/**
 * External View Navigation Plugin - Professional JavaScript
 * Enhanced interactions and animations for the navigation plugin
 */

console.log('🌟 External View Navigation Plugin loaded successfully');

// Professional plugin initialization
class NavigationPlugin {
    constructor() {
        this.button = null;
        this.container = null;
        this.isAnimating = false;
        this.init();
    }

    init() {
        console.log('🚀 Initializing Navigation Plugin...');
        
        // Wait for DOM to be fully ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupPlugin());
        } else {
            this.setupPlugin();
        }
    }

    setupPlugin() {
        this.button = document.getElementById('helloButton');
        this.container = document.querySelector('.container');
        
        if (!this.button || !this.container) {
            console.warn('⚠️ Plugin elements not found');
            return;
        }

        this.bindEvents();
        this.addAccessibility();
        console.log('✅ Navigation Plugin initialized successfully');
    }

    bindEvents() {
        // Main button click with professional feedback
        this.button.addEventListener('click', (e) => this.handleButtonClick(e));
        
        // Enhanced hover interactions
        this.button.addEventListener('mouseenter', () => this.handleMouseEnter());
        this.button.addEventListener('mouseleave', () => this.handleMouseLeave());
        
        // Keyboard support
        this.button.addEventListener('keydown', (e) => this.handleKeydown(e));
    }

    addAccessibility() {
        // Ensure proper ARIA attributes
        this.button.setAttribute('aria-label', 'Trigger greeting interaction');
        this.button.setAttribute('role', 'button');
        
        // Ensure keyboard focus is visible
        this.button.addEventListener('focus', () => {
            this.button.style.outline = '2px solid var(--sapphire-400)';
            this.button.style.outlineOffset = '2px';
        });
        
        this.button.addEventListener('blur', () => {
            this.button.style.outline = 'none';
        });
    }

    handleButtonClick(event) {
        if (this.isAnimating) return;
        
        event.preventDefault();
        this.isAnimating = true;
        
        // Professional success feedback
        this.showSuccessNotification();
        
        // Button click animation
        this.animateButtonClick();
        
        // Log interaction
        console.log('🎉 Button interaction triggered', {
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent.split(' ')[0]
        });
        
        setTimeout(() => {
            this.isAnimating = false;
        }, 1000);
    }

    handleMouseEnter() {
        if (this.isAnimating) return;
        this.button.textContent = '✨ Say Hello!';
    }

    handleMouseLeave() {
        if (this.isAnimating) return;
        this.button.textContent = '👋 Click Me!';
    }

    handleKeydown(event) {
        // Support Enter and Space keys
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            this.handleButtonClick(event);
        }
    }

    animateButtonClick() {
        // Professional ripple effect
        const ripple = document.createElement('span');
        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
            top: 50%;
            left: 50%;
            width: 100px;
            height: 100px;
            margin-top: -50px;
            margin-left: -50px;
        `;

        // Add ripple animation CSS if not exists
        if (!document.getElementById('ripple-style')) {
            const style = document.createElement('style');
            style.id = 'ripple-style';
            style.textContent = `
                @keyframes ripple {
                    to {
                        transform: scale(2);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        this.button.style.position = 'relative';
        this.button.style.overflow = 'hidden';
        this.button.appendChild(ripple);

        // Clean up ripple after animation
        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.parentNode.removeChild(ripple);
            }
        }, 600);
    }

    showSuccessNotification() {
        // Create professional notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #0BCD93, #0aa87f);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(11, 205, 147, 0.3);
            font-weight: 600;
            z-index: 1000;
            animation: slideInRight 0.3s ease-out forwards;
            transform: translateX(100%);
            opacity: 0;
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">🎉</span>
                <span>Hello from the Navigation Plugin!</span>
            </div>
        `;

        // Add slide animation if not exists
        if (!document.getElementById('notification-style')) {
            const style = document.createElement('style');
            style.id = 'notification-style';
            style.textContent = `
                @keyframes slideInRight {
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                @keyframes slideOutRight {
                    to {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(notification);

        // Auto-remove notification
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in forwards';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize the plugin
const navigationPlugin = new NavigationPlugin();

// Export for potential external use
window.NavigationPlugin = navigationPlugin;

// Professional console signature
console.log(
    '%c🌟 Navigation Plugin Ready %c| Professional External View Plugin for Airflow 3',
    'background: linear-gradient(135deg, #AF76FF, #0AA6FF); color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;',
    'color: #575293; font-weight: normal;'
);