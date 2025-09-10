/**
 * External View DAG Plugin - Professional JavaScript
 * Enhanced interactions for DAG specific functionality
 */

console.log('🚁 External View DAG Plugin loaded successfully');

// Professional DAG plugin initialization
class DAGPlugin {
    constructor() {
        this.button = null;
        this.container = null;
        this.dagId = null;
        this.isAnimating = false;
        this.init();
    }

    init() {
        console.log('🚀 Initializing DAG Plugin...');
        
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
        
        // Extract DAG ID from the page
        this.dagId = document.getElementById('dagId')?.textContent || 'unknown';
        
        if (!this.button || !this.container) {
            console.warn('⚠️ Plugin elements not found');
            return;
        }

        this.bindEvents();
        this.addAccessibility();
        this.addDAGSpecificFeatures();
        console.log('✅ DAG Plugin initialized successfully', {
            dagId: this.dagId
        });
    }

    bindEvents() {
        // Main button click with DAG specific feedback
        this.button.addEventListener('click', (e) => this.handleButtonClick(e));
        
        // Enhanced hover interactions
        this.button.addEventListener('mouseenter', () => this.handleMouseEnter());
        this.button.addEventListener('mouseleave', () => this.handleMouseLeave());
        
        // Keyboard support
        this.button.addEventListener('keydown', (e) => this.handleKeydown(e));
    }

    addAccessibility() {
        // Ensure proper ARIA attributes with DAG context
        this.button.setAttribute('aria-label', `Manage DAG ${this.dagId}`);
        this.button.setAttribute('role', 'button');
        
        // Ensure keyboard focus is visible
        this.button.addEventListener('focus', () => {
            this.button.style.outline = '2px solid var(--emerald-400)';
            this.button.style.outlineOffset = '2px';
        });
        
        this.button.addEventListener('blur', () => {
            this.button.style.outline = 'none';
        });
    }

    addDAGSpecificFeatures() {
        // Add hover effects to DAG info items
        const infoItems = document.querySelectorAll('.info-item');
        infoItems.forEach(item => {
            item.addEventListener('mouseenter', () => {
                item.style.background = 'rgba(11, 205, 147, 0.05)';
                item.style.transform = 'translateX(4px)';
                item.style.transition = 'all 0.2s ease';
            });
            
            item.addEventListener('mouseleave', () => {
                item.style.background = 'transparent';
                item.style.transform = 'translateX(0)';
            });
        });

        // Add copy-to-clipboard functionality for DAG ID
        const values = document.querySelectorAll('.value');
        values.forEach(value => {
            value.style.cursor = 'pointer';
            value.title = 'Click to copy';
            
            value.addEventListener('click', () => {
                this.copyToClipboard(value.textContent);
                this.showCopyNotification(value.textContent);
            });
        });
    }

    handleButtonClick(event) {
        if (this.isAnimating) return;
        
        event.preventDefault();
        this.isAnimating = true;
        
        // DAG specific success feedback
        this.showDAGManagementNotification();
        
        // Button click animation
        this.animateButtonClick();
        
        // Log DAG specific interaction
        console.log('🌿 DAG management triggered', {
            dagId: this.dagId,
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
        this.button.textContent = 'Hello Airflow!';
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

    showDAGManagementNotification() {
        // Create DAG specific notification
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
            max-width: 300px;
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">❤️</span>
                <div>
                    <div style="font-size: 0.9rem;">Hi there! I'm a plugin! 😊</div>
                    <div style="font-size: 0.75rem; opacity: 0.9; margin-top: 0.25rem;">
                    </div>
                </div>
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
        }, 4000);
    }

    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
        }
    }

    showCopyNotification(text) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135div style="display: flex; align-items: center; gap: 0.5rem;">
                <span>📋</span>
                <span>Copied: ${text.length > 15 ? text.substring(0, 15) + '...' : text}</span>
            </div>
        `;

        // Add bounce animation
        if (!document.getElementById('bounce-style')) {
            const style = document.createElement('style');
            style.id = 'bounce-style';
            style.textContent = `
                @keyframes bounceIn {
                    0% { opacity: 0; transform: translateX(-50%) scale(0.3); }
                    50% { opacity: 1; transform: translateX(-50%) scale(1.05); }
                    100% { opacity: 1; transform: translateX(-50%) scale(1); }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(notification);

        // Auto-remove
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.2s ease-in forwards';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 200);
        }, 2000);
    }
}

// Initialize the plugin
const dagPlugin = new DAGPlugin();

// Export for potential external use
window.DAGPlugin = dagPlugin;

// Professional console signature
console.log(
    '%c🌿 DAG Plugin Ready %c| Professional External View Plugin for Airflow 3',
    'background: linear-gradient(135deg, #0BCD93, #AF76FF); color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;',
    'color: #575293; font-weight: normal;'
);
