/**
 * EMERGENCY MODAL FIX
 * This is a nuclear option to force modals to work when everything else fails
 */

class EmergencyModalFix {
    constructor() {
        this.debug = true;
        this.init();
    }

    init() {
        // Wait for DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        this.log('Emergency Modal Fix initializing...');
        
        // Force fix all existing modals
        this.fixAllModals();
        
        // Set up nuclear event handling
        this.setupNuclearEventHandling();
        
        // Monitor for new modals
        this.monitorForNewModals();
        
        this.log('Emergency Modal Fix initialized');
    }

    fixAllModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => this.forceFixModal(modal));
    }

    forceFixModal(modal) {
        this.log(`Force fixing modal: ${modal.id}`);
        
        // Force inline styles to override everything
        modal.style.cssText = `
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            z-index: 2000 !important;
            width: 100% !important;
            height: 100% !important;
            pointer-events: auto !important;
            display: none !important;
        `;

        const dialog = modal.querySelector('.modal-dialog');
        if (dialog) {
            dialog.style.cssText = `
                position: relative !important;
                width: auto !important;
                margin: 1.75rem auto !important;
                max-width: 500px !important;
                pointer-events: auto !important;
                z-index: 2001 !important;
            `;
        }

        const content = modal.querySelector('.modal-content');
        if (content) {
            content.style.cssText = `
                position: relative !important;
                background-color: #fff !important;
                border: 1px solid rgba(0, 0, 0, 0.2) !important;
                border-radius: 0.375rem !important;
                box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
                pointer-events: auto !important;
                z-index: 2002 !important;
            `;
        }

        // Force all interactive elements
        const interactiveElements = modal.querySelectorAll('button, input, textarea, select, a, [onclick], [role="button"]');
        interactiveElements.forEach(element => {
            element.style.cssText += `
                pointer-events: auto !important;
                z-index: 2003 !important;
                cursor: pointer !important;
                position: relative !important;
            `;
        });

        // Add emergency event listeners
        this.addEmergencyEventListeners(modal);
    }

    addEmergencyEventListeners(modal) {
        const modalId = modal.id;
        
        // Close button handlers
        const closeButtons = modal.querySelectorAll('[data-bs-dismiss="modal"], .btn-close');
        closeButtons.forEach(btn => {
            // Remove existing listeners
            btn.onclick = null;
            
            // Add new listener
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.forceCloseModal(modalId);
            }, true);
            
            // Also add as inline onclick as backup
            btn.onclick = (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.forceCloseModal(modalId);
                return false;
            };
        });

        // Backdrop click handler
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                e.preventDefault();
                e.stopPropagation();
                this.forceCloseModal(modalId);
            }
        }, true);

        // Escape key handler
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.style.display === 'block') {
                this.forceCloseModal(modalId);
            }
        });
    }

    forceShowModal(modalId) {
        this.log(`Force showing modal: ${modalId}`);
        
        const modal = document.getElementById(modalId);
        if (!modal) {
            this.log(`Modal ${modalId} not found!`);
            return;
        }

        // Fix the modal first
        this.forceFixModal(modal);

        // Create backdrop
        this.createBackdrop();

        // Show modal
        modal.style.display = 'block';
        modal.classList.add('show');
        modal.setAttribute('aria-hidden', 'false');
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        document.body.classList.add('modal-open');

        // Focus management
        setTimeout(() => {
            const firstFocusable = modal.querySelector('input, textarea, select, button, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) {
                firstFocusable.focus();
            } else {
                modal.focus();
            }
        }, 100);

        this.log(`Modal ${modalId} should now be visible and interactive`);
    }

    forceCloseModal(modalId) {
        this.log(`Force closing modal: ${modalId}`);
        
        const modal = document.getElementById(modalId);
        if (!modal) return;

        // Hide modal
        modal.style.display = 'none';
        modal.classList.remove('show');
        modal.setAttribute('aria-hidden', 'true');

        // Remove backdrop
        this.removeBackdrop();

        // Restore body scroll
        document.body.style.overflow = '';
        document.body.classList.remove('modal-open');

        this.log(`Modal ${modalId} closed`);
    }

    createBackdrop() {
        // Remove existing backdrop
        this.removeBackdrop();

        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show emergency-backdrop';
        backdrop.style.cssText = `
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            z-index: 1999 !important;
            width: 100% !important;
            height: 100% !important;
            background-color: rgba(0, 0, 0, 0.5) !important;
            pointer-events: auto !important;
        `;

        document.body.appendChild(backdrop);
    }

    removeBackdrop() {
        const backdrops = document.querySelectorAll('.modal-backdrop, .emergency-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
    }

    setupNuclearEventHandling() {
        // Override Bootstrap modal methods if they exist
        if (window.bootstrap && window.bootstrap.Modal) {
            const originalShow = window.bootstrap.Modal.prototype.show;
            const originalHide = window.bootstrap.Modal.prototype.hide;
            
            window.bootstrap.Modal.prototype.show = function() {
                window.emergencyModalFix.forceShowModal(this._element.id);
            };
            
            window.bootstrap.Modal.prototype.hide = function() {
                window.emergencyModalFix.forceCloseModal(this._element.id);
            };
        }

        // Global click handler
        document.addEventListener('click', (e) => {
            const target = e.target;
            
            // Handle modal triggers
            if (target.hasAttribute('data-bs-toggle') && target.getAttribute('data-bs-toggle') === 'modal') {
                e.preventDefault();
                e.stopPropagation();
                const modalId = target.getAttribute('data-bs-target')?.replace('#', '');
                if (modalId) {
                    this.forceShowModal(modalId);
                }
                return false;
            }
        }, true);
    }

    monitorForNewModals() {
        // Use MutationObserver to watch for new modals
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        if (node.classList?.contains('modal')) {
                            this.forceFixModal(node);
                        }
                        // Check for modals in added subtree
                        const modals = node.querySelectorAll?.('.modal');
                        modals?.forEach(modal => this.forceFixModal(modal));
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    log(message) {
        if (this.debug) {
            console.log(`[EmergencyModalFix] ${message}`);
        }
    }

    // Public API
    showModal(modalId) {
        this.forceShowModal(modalId);
    }

    hideModal(modalId) {
        this.forceCloseModal(modalId);
    }

    debugModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('modal-debug');
            this.log(`Debug mode enabled for modal ${modalId}`);
        }
    }
}

// Initialize immediately
window.emergencyModalFix = new EmergencyModalFix();

// Provide global functions
window.showModal = (modalId) => window.emergencyModalFix.showModal(modalId);
window.hideModal = (modalId) => window.emergencyModalFix.hideModal(modalId);
window.debugModal = (modalId) => window.emergencyModalFix.debugModal(modalId);