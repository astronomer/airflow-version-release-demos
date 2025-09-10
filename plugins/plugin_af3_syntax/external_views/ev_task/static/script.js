/**
 * External View Task Plugin - Professional JavaScript
 * Enhanced interactions for Task specific functionality
 */

console.log('⚡ External View Task Plugin loaded successfully');

// Professional Task plugin initialization
class TaskPlugin {
    constructor() {
        this.button = null;
        this.container = null;
        this.dagId = null;
        this.taskId = null;
        this.isAnimating = false;
        this.init();
    }

    init() {
        console.log('🚀 Initializing Task Plugin...');
        
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
        
        // Extract DAG and Task IDs from the page
        this.dagId = document.getElementById('dagId')?.textContent || 'unknown';
        this.taskId = document.getElementById('taskId')?.textContent || 'unknown';
        
        if (!this.button || !this.container) {
            console.warn('⚠️ Plugin elements not found');
            return;
        }

        this.bindEvents();
        this.addAccessibility();
        this.addTaskSpecificFeatures();
        console.log('✅ Task Plugin initialized successfully', {
            dagId: this.dagId,
            taskId: this.taskId
        });
    }

    bindEvents() {
        // Main button click with Task specific feedback
        this.button.addEventListener('click', (e) => this.handleButtonClick(e));
        
        // Enhanced hover interactions
        this.button.addEventListener('mouseenter', () => this.handleMouseEnter());
        this.button.addEventListener('mouseleave', () => this.handleMouseLeave());
        
        // Keyboard support
        this.button.addEventListener('keydown', (e) => this.handleKeydown(e));
    }

    addAccessibility() {
        // Ensure proper ARIA attributes with Task context
        this.button.setAttribute('aria-label', `Debug task ${this.taskId} in DAG ${this.dagId}`);
        this.button.setAttribute('role', 'button');
        
        // Ensure keyboard focus is visible
        this.button.addEventListener('focus', () => {
            this.button.style.outline = '2px solid var(--amethyst-400)';
            this.button.style.outlineOffset = '2px';
        });
        
        this.button.addEventListener('blur', () => {
            this.button.style.outline = 'none';
        });
    }

    addTaskSpecificFeatures() {
        // Add hover effects to Task info items
        const infoItems = document.querySelectorAll('.info-item');
        infoItems.forEach(item => {
            item.addEventListener('mouseenter', () => {
                item.style.background = 'rgba(175, 118, 255, 0.05)';
                item.style.transform = 'translateX(4px)';
                item.style.transition = 'all 0.2s ease';
            });
            
            item.addEventListener('mouseleave', () => {
                item.style.background = 'transparent';
                item.style.transform = 'translateX(0)';
            });
        });

        // Add copy-to-clipboard functionality for Task/DAG IDs
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
        
        // Task specific success feedback
        this.showTaskDebuggingNotification();
        
        // Button click animation
        this.animateButtonClick();
        
        // Log Task specific interaction
        console.log('⚡ Task debugging triggered', {
            dagId: this.dagId,
            taskId: this.taskId,
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

    showTaskDebuggingNotification() {
        // Create Task specific notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #AF76FF, #9969e6);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(175, 118, 255, 0.3);
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
            background: linear-gradient(135deg, #AF76FF, #9969e6);
            color: white;
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
            box-shadow: 0 4px 16px rgba(175, 118, 255, 0.3);
            font-weight: 600;
            z-index: 1001;
            animation: bounceIn 0.3s ease-out forwards;
            opacity: 0;
            font-size: 0.9rem;
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
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
const taskPlugin = new TaskPlugin();

// Export for potential external use
window.TaskPlugin = taskPlugin;

// Professional console signature
console.log(
    '%c⚡ Task Plugin Ready %c| Professional External View Plugin for Airflow 3',
    'background: linear-gradient(135deg, #AF76FF, #0AA6FF); color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;',
    'color: #575293; font-weight: normal;'
);
