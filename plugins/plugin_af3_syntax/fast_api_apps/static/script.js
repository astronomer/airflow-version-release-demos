/**
 * FastAPI App Plugin - Professional JavaScript
 * Interactive API testing and demonstrations
 */

console.log('🚀 FastAPI App Plugin loaded successfully');

// Professional FastAPI App plugin initialization
class FastAPIPlugin {
    constructor() {
        this.button = null;
        this.resultDiv = null;
        this.isLoading = false;
        this.init();
    }

    init() {
        console.log('🚀 Initializing FastAPI Plugin...');
        
        // Wait for DOM to be fully ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupPlugin());
        } else {
            this.setupPlugin();
        }
    }

    setupPlugin() {
        this.button = document.getElementById('testApiButton');
        this.resultDiv = document.getElementById('apiResult');
        
        if (!this.button || !this.resultDiv) {
            console.warn('⚠️ Plugin elements not found');
            return;
        }

        this.bindEvents();
        this.addAccessibility();
        console.log('✅ FastAPI Plugin initialized successfully');
    }

    bindEvents() {
        // Main button click for API testing
        this.button.addEventListener('click', (e) => this.handleApiTest(e));
        
        // Enhanced hover interactions
        this.button.addEventListener('mouseenter', () => this.handleMouseEnter());
        this.button.addEventListener('mouseleave', () => this.handleMouseLeave());
        
        // Keyboard support
        this.button.addEventListener('keydown', (e) => this.handleKeydown(e));
    }

    addAccessibility() {
        // Ensure proper ARIA attributes
        this.button.setAttribute('aria-label', 'Test FastAPI endpoints');
        this.button.setAttribute('role', 'button');
        
        // Ensure keyboard focus is visible
        this.button.addEventListener('focus', () => {
            this.button.style.outline = '2px solid var(--fastapi-green)';
            this.button.style.outlineOffset = '2px';
        });
        
        this.button.addEventListener('blur', () => {
            this.button.style.outline = 'none';
        });
    }

    async handleApiTest(event) {
        if (this.isLoading) return;
        
        event.preventDefault();
        this.isLoading = true;
        
        // Update button state
        const originalText = this.button.textContent;
        this.button.textContent = '⏳ Testing API...';
        this.button.disabled = true;
        
        try {
            // Test multiple endpoints
            const results = await this.runAPITests();
            this.displayResults(results);
            this.showSuccessNotification();
            
        } catch (error) {
            this.displayError(error);
            this.showErrorNotification(error.message);
        } finally {
            // Restore button state
            this.button.textContent = originalText;
            this.button.disabled = false;
            this.isLoading = false;
        }
        
        // Button click animation
        this.animateButtonClick();
        
        console.log('🧪 FastAPI tests completed');
    }

    async runAPITests() {
        const results = [];
        
        // Test 1: Root endpoint
        try {
            const response1 = await fetch('/fastapi-app/');
            const data1 = await response1.json();
            results.push({
                endpoint: 'GET /',
                status: response1.status,
                success: response1.ok,
                data: data1
            });
        } catch (error) {
            results.push({
                endpoint: 'GET /',
                status: 'ERROR',
                success: false,
                error: error.message
            });
        }
        
        // Test 2: Info endpoint
        try {
            const response2 = await fetch('/fastapi-app/info');
            const data2 = await response2.json();
            results.push({
                endpoint: 'GET /info',
                status: response2.status,
                success: response2.ok,
                data: data2
            });
        } catch (error) {
            results.push({
                endpoint: 'GET /info',
                status: 'ERROR',
                success: false,
                error: error.message
            });
        }
        
        // Test 3: Health endpoint
        try {
            const response3 = await fetch('/fastapi-app/health');
            const data3 = await response3.json();
            results.push({
                endpoint: 'GET /health',
                status: response3.status,
                success: response3.ok,
                data: data3
            });
        } catch (error) {
            results.push({
                endpoint: 'GET /health',
                status: 'ERROR',
                success: false,
                error: error.message
            });
        }
        
        // Test 4: POST endpoint
        try {
            const response4 = await fetch('/fastapi-app/api/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: 'Hello from FastAPI test!',
                    user_name: 'Plugin Tester'
                })
            });
            const data4 = await response4.json();
            results.push({
                endpoint: 'POST /api/message',
                status: response4.status,
                success: response4.ok,
                data: data4
            });
        } catch (error) {
            results.push({
                endpoint: 'POST /api/message',
                status: 'ERROR',
                success: false,
                error: error.message
            });
        }
        
        return results;
    }

    displayResults(results) {
        let output = '🧪 FastAPI Endpoint Test Results:\n\n';
        
        results.forEach((result, index) => {
            output += `${index + 1}. ${result.endpoint}\n`;
            output += `   Status: ${result.status} ${result.success ? '✅' : '❌'}\n`;
            
            if (result.success && result.data) {
                output += `   Response: ${JSON.stringify(result.data, null, 2)}\n`;
            } else if (result.error) {
                output += `   Error: ${result.error}\n`;
            }
            output += '\n';
        });
        
        output += '📚 Tip: Visit /fastapi-app/docs for interactive API documentation!';
        
        this.resultDiv.textContent = output;
        this.resultDiv.classList.add('show');
    }

    displayError(error) {
        const output = `❌ API Test Error:\n\n${error.message}\n\nPlease check that the FastAPI app is running correctly.`;
        this.resultDiv.textContent = output;
        this.resultDiv.classList.add('show');
    }

    handleMouseEnter() {
        if (this.isLoading) return;
        this.button.textContent = '🧪 Run Tests!';
    }

    handleMouseLeave() {
        if (this.isLoading) return;
        this.button.textContent = '🔥 Test API Call!';
    }

    handleKeydown(event) {
        // Support Enter and Space keys
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            this.handleApiTest(event);
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
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #009688, #00695C);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 150, 136, 0.3);
            font-weight: 600;
            z-index: 1000;
            animation: slideInRight 0.3s ease-out forwards;
            transform: translateX(100%);
            opacity: 0;
            max-width: 300px;
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">🚀</span>
                <div>
                    <div style="font-size: 0.9rem;">API Tests Completed!</div>
                    <div style="font-size: 0.75rem; opacity: 0.9; margin-top: 0.25rem;">
                        FastAPI endpoints tested successfully
                    </div>
                </div>
            </div>
        `;

        this.addNotificationStyles();
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

    showErrorNotification(message) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #f44336, #d32f2f);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(244, 67, 54, 0.3);
            font-weight: 600;
            z-index: 1000;
            animation: slideInRight 0.3s ease-out forwards;
            transform: translateX(100%);
            opacity: 0;
            max-width: 300px;
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">❌</span>
                <div>
                    <div style="font-size: 0.9rem;">API Test Failed</div>
                    <div style="font-size: 0.75rem; opacity: 0.9; margin-top: 0.25rem;">
                        ${message.substring(0, 30)}...
                    </div>
                </div>
            </div>
        `;

        this.addNotificationStyles();
        document.body.appendChild(notification);

        // Auto-remove notification
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in forwards';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }

    addNotificationStyles() {
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
    }
}

// Initialize the plugin
const fastApiPlugin = new FastAPIPlugin();

// Export for potential external use
window.FastAPIPlugin = fastApiPlugin;

// Professional console signature
console.log(
    '%c🚀 FastAPI Plugin Ready %c| Standalone API Application for Airflow 3',
    'background: linear-gradient(135deg, #009688, #0AA6FF); color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;',
    'color: #575293; font-weight: normal;'
);
