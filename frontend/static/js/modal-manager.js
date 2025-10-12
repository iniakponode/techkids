/**
 * Universal Modal Manager
 * Handles Bootstrap modals with fallback support for better reliability
 */

class ModalManager {
    constructor() {
        this.modals = new Map();
        this.initialized = false;
        this.init();
    }

    init() {
        if (this.initialized) return;
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        // Initialize after Bootstrap is loaded
        if (window.bootstrap) {
            this.initializeModals();
        } else {
            // Poll for Bootstrap availability
            const pollBootstrap = () => {
                if (window.bootstrap) {
                    this.initializeModals();
                } else {
                    setTimeout(pollBootstrap, 100);
                }
            };
            pollBootstrap();
        }

        this.setupGlobalEventListeners();
        this.initialized = true;
    }

    initializeModals() {
        // Find all modal elements and initialize them
        document.querySelectorAll('.modal').forEach(modalElement => {
            const modalId = modalElement.id;
            if (modalId && window.bootstrap) {
                try {
                    const modal = new window.bootstrap.Modal(modalElement, {
                        backdrop: true,
                        keyboard: true,
                        focus: true
                    });
                    this.modals.set(modalId, modal);
                } catch (error) {
                    console.warn(`Failed to initialize modal ${modalId}:`, error);
                }
            }
        });
    }

    setupGlobalEventListeners() {
        // Close button handlers
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-bs-dismiss="modal"]') || 
                e.target.closest('[data-bs-dismiss="modal"]')) {
                e.preventDefault();
                const modal = e.target.closest('.modal');
                if (modal) {
                    this.hide(modal.id);
                }
            }
        });

        // Backdrop click handler
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal') && 
                e.target.classList.contains('show')) {
                this.hide(e.target.id);
            }
        });

        // Escape key handler
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal.show');
                if (openModal) {
                    this.hide(openModal.id);
                }
            }
        });
    }

    show(modalId) {
        const modal = this.modals.get(modalId);
        const modalElement = document.getElementById(modalId);

        if (!modalElement) {
            console.error(`Modal element with id "${modalId}" not found`);
            return false;
        }

        try {
            if (modal && window.bootstrap) {
                // Use Bootstrap modal
                modal.show();
            } else {
                // Fallback implementation
                this.showFallback(modalElement);
            }
            return true;
        } catch (error) {
            console.error(`Error showing modal ${modalId}:`, error);
            // Try fallback
            this.showFallback(modalElement);
            return false;
        }
    }

    hide(modalId) {
        const modal = this.modals.get(modalId);
        const modalElement = document.getElementById(modalId);

        if (!modalElement) {
            return false;
        }

        try {
            if (modal && window.bootstrap) {
                // Use Bootstrap modal
                modal.hide();
            } else {
                // Fallback implementation
                this.hideFallback(modalElement);
            }
            return true;
        } catch (error) {
            console.error(`Error hiding modal ${modalId}:`, error);
            // Try fallback
            this.hideFallback(modalElement);
            return false;
        }
    }

    showFallback(modalElement) {
        // Create backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show';
        backdrop.addEventListener('click', () => {
            this.hide(modalElement.id);
        });
        document.body.appendChild(backdrop);

        // Show modal
        modalElement.classList.add('show');
        modalElement.style.display = 'block';
        modalElement.setAttribute('aria-modal', 'true');
        modalElement.removeAttribute('aria-hidden');

        // Prevent body scrolling
        document.body.classList.add('modal-open');
        document.body.style.paddingRight = '15px';

        // Focus management
        modalElement.focus();
    }

    hideFallback(modalElement) {
        // Remove backdrop
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }

        // Hide modal
        modalElement.classList.remove('show');
        modalElement.style.display = 'none';
        modalElement.setAttribute('aria-hidden', 'true');
        modalElement.removeAttribute('aria-modal');

        // Restore body
        document.body.classList.remove('modal-open');
        document.body.style.paddingRight = '';
        document.body.style.overflow = '';
    }

    toggle(modalId) {
        const modalElement = document.getElementById(modalId);
        if (modalElement && modalElement.classList.contains('show')) {
            return this.hide(modalId);
        } else {
            return this.show(modalId);
        }
    }

    isOpen(modalId) {
        const modalElement = document.getElementById(modalId);
        return modalElement && modalElement.classList.contains('show');
    }

    // Utility method to get modal instance
    getInstance(modalId) {
        return this.modals.get(modalId);
    }
}

// Create global instance
window.modalManager = new ModalManager();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModalManager;
}