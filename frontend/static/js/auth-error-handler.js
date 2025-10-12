// Global Authentication Error Handler and Session Management
// This file provides centralized authentication error handling and user-friendly messages

class AuthErrorHandler {
    constructor() {
        this.isRedirecting = false;
        this.init();
    }

    init() {
        // Set up global fetch interceptor for authentication errors
        this.setupFetchInterceptor();
        
        // Set up global error event listeners
        this.setupGlobalErrorHandlers();
        
        // Check session validity on page load
        this.checkSessionValidity();
    }

    setupFetchInterceptor() {
        // Store original fetch
        const originalFetch = window.fetch;
        
        // Override fetch globally
        window.fetch = async (...args) => {
            try {
                const response = await originalFetch(...args);
                
                // Check for authentication errors
                if (response.status === 401) {
                    await this.handleAuthenticationError(response, args[0]);
                    return response;
                }
                
                return response;
            } catch (error) {
                console.error('Fetch error:', error);
                throw error;
            }
        };
    }

    setupGlobalErrorHandlers() {
        // Handle unhandled promise rejections that might be auth-related
        window.addEventListener('unhandledrejection', (event) => {
            if (this.isAuthenticationError(event.reason)) {
                event.preventDefault();
                this.handleAuthenticationError(null, null, event.reason);
            }
        });
    }

    async handleAuthenticationError(response = null, requestUrl = null, error = null) {
        if (this.isRedirecting) return;
        
        let errorData = {};
        let errorMessage = "Your session has expired. Please log in again.";
        
        try {
            if (response) {
                errorData = await response.json().catch(() => ({}));
            }
        } catch (e) {
            console.warn('Could not parse auth error response:', e);
        }

        // Determine specific error message
        if (errorData.detail) {
            if (errorData.detail.includes("Session expired")) {
                errorMessage = "Your session has expired. Please log in again to continue.";
            } else if (errorData.detail.includes("Could not validate token")) {
                errorMessage = "Your session is invalid. Please log in again.";
            } else if (errorData.detail.includes("User not found")) {
                errorMessage = "Your account could not be found. Please log in again.";
            } else if (errorData.detail.includes("Invalid token")) {
                errorMessage = "Your session is invalid. Please log in again.";
            } else {
                errorMessage = errorData.detail;
            }
        }

        // Show user-friendly notification
        this.showAuthErrorNotification(errorMessage);
        
        // Clear any sensitive data
        this.clearUserData();
        
        // Redirect to login after a short delay
        this.redirectToLogin(requestUrl);
    }

    showAuthErrorNotification(message) {
        // Remove any existing auth notifications
        this.removeExistingNotifications();
        
        // Create notification
        const notification = document.createElement('div');
        notification.id = 'auth-error-notification';
        notification.className = 'auth-error-notification';
        notification.innerHTML = `
            <div class="auth-error-content">
                <div class="auth-error-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" fill="currentColor"/>
                    </svg>
                </div>
                <div class="auth-error-text">
                    <strong>Session Expired</strong>
                    <p>${message}</p>
                </div>
                <button class="auth-error-close" onclick="window.authErrorHandler.removeExistingNotifications()">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>
            </div>
            <div class="auth-error-progress"></div>
        `;
        
        // Add to DOM
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            this.removeExistingNotifications();
        }, 5000);
    }

    removeExistingNotifications() {
        const existing = document.querySelectorAll('.auth-error-notification');
        existing.forEach(notification => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        });
    }

    clearUserData() {
        // Clear any stored user data (avoid clearing essential cookies here)
        try {
            localStorage.removeItem('user_data');
            localStorage.removeItem('user_preferences');
            sessionStorage.clear();
        } catch (e) {
            console.warn('Could not clear user data:', e);
        }
    }

    redirectToLogin(originalUrl = null) {
        if (this.isRedirecting) return;
        
        this.isRedirecting = true;
        
        // Determine redirect URL
        let loginUrl = '/login';
        
        // Add current page as 'next' parameter if not already on login page
        const currentPath = window.location.pathname;
        if (currentPath !== '/login' && currentPath !== '/') {
            const nextUrl = encodeURIComponent(currentPath + window.location.search);
            loginUrl += `?next=${nextUrl}`;
        }
        
        // If we have the original request URL, use that for context
        if (originalUrl && typeof originalUrl === 'string' && !originalUrl.includes('/api/auth/')) {
            // Extract path from API calls for better context
            const urlPath = originalUrl.replace('/api', '').split('?')[0];
            if (urlPath && urlPath !== currentPath) {
                const nextUrl = encodeURIComponent(urlPath);
                loginUrl = `/login?next=${nextUrl}`;
            }
        }
        
        // Delay redirect slightly to allow user to see the message
        setTimeout(() => {
            window.location.assign(loginUrl);
        }, 2000);
    }

    isAuthenticationError(error) {
        if (!error) return false;
        
        const errorString = error.toString().toLowerCase();
        const authKeywords = [
            'session expired',
            'could not validate token',
            'unauthorized',
            'invalid token',
            'user not found',
            'authentication',
            'please log in'
        ];
        
        return authKeywords.some(keyword => errorString.includes(keyword));
    }

    async checkSessionValidity() {
        try {
            const response = await fetch('/api/auth/check-session', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.status === 401) {
                // Session is invalid, but don't show notification on page load
                // unless user is trying to access a protected page
                const isProtectedPage = this.isProtectedPage();
                if (isProtectedPage) {
                    this.handleAuthenticationError(response);
                }
            }
        } catch (error) {
            // Silently fail - probably network issue or endpoint doesn't exist
            console.debug('Session check failed:', error);
        }
    }

    isProtectedPage() {
        const protectedPaths = [
            '/admin',
            '/student',
            '/teacher',
            '/payment',
            '/dashboard'
        ];
        
        const currentPath = window.location.pathname;
        return protectedPaths.some(path => currentPath.startsWith(path));
    }

    // Utility method for making authenticated API calls
    static async apiCall(url, options = {}) {
        const defaultOptions = {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };
        
        const response = await fetch(url, { ...defaultOptions, ...options });
        
        // Let the global interceptor handle auth errors
        if (!response.ok && response.status !== 401) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Request failed');
        }
        
        return response;
    }

    // Method to manually trigger session check
    async refreshSession() {
        return this.checkSessionValidity();
    }
}

// Initialize global auth error handler
window.authErrorHandler = new AuthErrorHandler();

// Provide global API helper
window.apiCall = AuthErrorHandler.apiCall;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthErrorHandler;
}