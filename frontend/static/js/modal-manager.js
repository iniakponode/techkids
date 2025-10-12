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

    fixModalStructure(modalElement) {
        // Ensure proper modal structure and attributes
        modalElement.setAttribute('tabindex', '-1');
        modalElement.setAttribute('aria-hidden', 'true');
        
        // Ensure modal-dialog exists
        let modalDialog = modalElement.querySelector('.modal-dialog');
        if (!modalDialog) {
            modalDialog = document.createElement('div');
            modalDialog.className = 'modal-dialog';
            while (modalElement.firstChild) {
                modalDialog.appendChild(modalElement.firstChild);
            }
            modalElement.appendChild(modalDialog);
        }
        
        // Ensure modal-content exists
        let modalContent = modalDialog.querySelector('.modal-content');
        if (!modalContent) {
            modalContent = document.createElement('div');
            modalContent.className = 'modal-content';
            while (modalDialog.firstChild && !modalDialog.firstChild.classList?.contains('modal-content')) {
                modalContent.appendChild(modalDialog.firstChild);
            }
            modalDialog.appendChild(modalContent);
        }
        
        // Fix any pointer-events issues
        modalElement.style.pointerEvents = 'none';
        modalDialog.style.pointerEvents = 'none';
        modalContent.style.pointerEvents = 'auto';
        
        // Ensure proper z-index stacking
        modalElement.style.zIndex = '1050';
        modalContent.style.zIndex = '1052';
    }

    initializeModals() {
        // Find all modal elements and initialize them
        document.querySelectorAll('.modal').forEach(modalElement => {
            const modalId = modalElement.id;
            if (modalId && window.bootstrap) {
                try {
                    // Force proper modal structure
                    this.fixModalStructure(modalElement);
                    
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
        // Enhanced close button handlers
        document.addEventListener('click', (e) => {
            // Handle close buttons
            if (e.target.matches('[data-bs-dismiss="modal"]') || 
                e.target.closest('[data-bs-dismiss="modal"]')) {
                e.preventDefault();
                e.stopPropagation();
                const modal = e.target.closest('.modal');
                if (modal) {
                    this.hide(modal.id);
                }
            }
        }, true); // Use capture phase

        // Enhanced backdrop click handler
        document.addEventListener('click', (e) => {
            // Only close if clicking directly on the modal backdrop (not content)
            if (e.target.classList.contains('modal') && 
                e.target.classList.contains('show') &&
                !e.target.closest('.modal-content')) {
                e.preventDefault();
                e.stopPropagation();
                this.hide(e.target.id);
            }
        }, true);

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