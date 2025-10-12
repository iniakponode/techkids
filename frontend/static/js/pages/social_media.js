document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('post-form');
    const platformSelect = document.getElementById('platform');
    const contentTypeSelect = document.getElementById('content_type');
    const imageField = document.getElementById('image-field');
    const videoField = document.getElementById('video-field');
    const postsTableBody = document.getElementById('posts-table-body');
    const credentialsTableBody = document.getElementById('credentials-table-body');
    const credentialForm = document.getElementById('credential-form');

    // Modal initialization with proper error handling
    let previewModal = null;
    let analyticsModal = null;
    
    // Initialize modals after Bootstrap is loaded
    const initializeModals = () => {
        const previewModalElement = document.getElementById('previewModal');
        const analyticsModalElement = document.getElementById('analyticsModal');
        
        if (window.bootstrap && previewModalElement) {
            previewModal = new window.bootstrap.Modal(previewModalElement, {
                backdrop: true,
                keyboard: true,
                focus: true
            });
        }
        
        if (window.bootstrap && analyticsModalElement) {
            analyticsModal = new window.bootstrap.Modal(analyticsModalElement, {
                backdrop: true,
                keyboard: true,
                focus: true
            });
        }
    };
    
    // Initialize modals immediately or wait for Bootstrap
    if (window.bootstrap) {
        initializeModals();
    } else {
        // Wait for Bootstrap to load
        const bootstrapLoadInterval = setInterval(() => {
            if (window.bootstrap) {
                clearInterval(bootstrapLoadInterval);
                initializeModals();
            }
        }, 100);
        
        // Fallback timeout after 5 seconds
        setTimeout(() => {
            clearInterval(bootstrapLoadInterval);
            if (!window.bootstrap) {
                console.warn('Bootstrap not loaded, modals may not work properly');
            }
        }, 5000);
    }

    const previewPlatform = document.getElementById('previewPlatform');
    const previewContentType = document.getElementById('previewContentType');
    const previewTitle = document.getElementById('previewTitle');
    const previewDescription = document.getElementById('previewDescription');
    const previewThumbnail = document.getElementById('previewThumbnail');

    const analyticsStatus = document.getElementById('analyticsStatus');
    const analyticsLastError = document.getElementById('analyticsLastError');
    const analyticsAttempts = document.getElementById('analyticsAttempts');
    const analyticsLastAttempt = document.getElementById('analyticsLastAttempt');
    const analyticsPostedAt = document.getElementById('analyticsPostedAt');
    const analyticsTotals = document.getElementById('analyticsTotals');
    const analyticsLogs = document.getElementById('analyticsLogs');

    const contentOptions = {
        facebook: ['Feed', 'Story'],
        instagram: ['Feed', 'Reel', 'Story'],
        whatsapp: ['Status'],
        x: ['Post'],
        threads: ['Post'],
        telegram: ['Post'],
    };

    function updateContentTypes() {
        const platform = platformSelect.value;
        contentTypeSelect.innerHTML = '';
        const options = contentOptions[platform] || [];
        if (!options.length) {
            const fallback = document.createElement('option');
            fallback.value = 'Post';
            fallback.textContent = 'Post';
            contentTypeSelect.appendChild(fallback);
        } else {
            options.forEach((type) => {
                const opt = document.createElement('option');
                opt.value = type;
                opt.textContent = type;
                contentTypeSelect.appendChild(opt);
            });
        }
        updateMediaFields();
    }

    function updateMediaFields() {
        const type = (contentTypeSelect.value || '').toLowerCase();
        if (type === 'reel' || type === 'story') {
            imageField.style.display = 'none';
            videoField.style.display = 'block';
        } else if (type === 'feed' || type === 'post') {
            imageField.style.display = 'block';
            videoField.style.display = 'none';
        } else {
            imageField.style.display = 'block';
            videoField.style.display = 'block';
        }
    }

    function formatDate(value) {
        if (!value) return '-';
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return value;
        return date.toLocaleString();
    }

    function showAlert(message) {
        window.alert(message);
    }

    async function handleCreatePost(event) {
        event.preventDefault();
        const formData = new FormData(form);
        const response = await fetch('/api/admin/social-posts/', {
            method: 'POST',
            body: formData,
        });
        if (response.ok) {
            window.location.reload();
        } else {
            const error = await response.json().catch(() => ({}));
            showAlert(error.detail || 'Failed to create post');
        }
    }

    async function handleDeletePost(postId) {
        if (!confirm('Delete this post?')) return;
        const response = await fetch(`/api/admin/social-posts/${postId}`, { method: 'DELETE' });
        if (response.ok) {
            window.location.reload();
        } else {
            const error = await response.json().catch(() => ({}));
            showAlert(error.detail || 'Failed to delete post');
        }
    }

    async function handleRetryPost(postId) {
        const response = await fetch(`/api/admin/social-posts/${postId}/retry`, { method: 'POST' });
        if (response.ok) {
            window.location.reload();
        } else {
            const error = await response.json().catch(() => ({}));
            showAlert(error.detail || 'Unable to queue retry');
        }
    }

    async function handlePreview(postId) {
        const response = await fetch(`/api/admin/social-posts/${postId}/preview`);
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            showAlert(error.detail || 'Unable to load preview');
            return;
        }
        const preview = await response.json();
        previewPlatform.textContent = preview.platform;
        previewContentType.textContent = preview.content_type;
        previewTitle.textContent = preview.title;
        previewDescription.textContent = preview.description;
        if (preview.thumbnail_url) {
            previewThumbnail.src = preview.thumbnail_url;
            previewThumbnail.style.display = 'block';
        } else {
            previewThumbnail.style.display = 'none';
        }
        // Use modal manager for reliable modal display
        if (window.modalManager) {
            window.modalManager.show('previewModal');
        } else if (previewModal) {
            try {
                previewModal.show();
            } catch (error) {
                console.error('Error showing preview modal:', error);
            }
        } else {
            console.warn('Modal system not available');
        }
    }

    function renderTotals(totals) {
        analyticsTotals.innerHTML = '';
        const keys = Object.keys(totals || {});
        if (!keys.length) {
            analyticsTotals.innerHTML = '<div class="col-12 text-muted">No engagement metrics recorded yet.</div>';
            return;
        }
        keys.forEach((key) => {
            const value = totals[key];
            const col = document.createElement('div');
            col.className = 'col-6 col-md-3';
            col.innerHTML = `
                <div class="border rounded p-3 h-100 text-center">
                    <div class="text-uppercase small text-muted">${key}</div>
                    <div class="fs-5 fw-semibold">${value}</div>
                </div>
            `;
            analyticsTotals.appendChild(col);
        });
    }

    function renderLogs(logs) {
        analyticsLogs.innerHTML = '';
        if (!logs.length) {
            analyticsLogs.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No dispatch attempts yet.</td></tr>';
            return;
        }
        logs.forEach((log) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${formatDate(log.attempted_at)}</td>
                <td>${log.success ? '<span class="badge bg-success">Success</span>' : '<span class="badge bg-danger">Failed</span>'}</td>
                <td>${log.platform_post_id || '-'}</td>
                <td>${log.diagnostics || log.error_message || '-'}</td>
                <td>${log.impressions}</td>
                <td>${log.clicks}</td>
                <td>${log.comments}</td>
                <td>${log.shares}</td>
            `;
            analyticsLogs.appendChild(row);
        });
    }

    async function handleAnalytics(postId) {
        const response = await fetch(`/api/admin/social-posts/${postId}/analytics`);
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            showAlert(error.detail || 'Unable to load analytics');
            return;
        }
        const analytics = await response.json();
        analyticsStatus.textContent = analytics.status;
        analyticsLastError.textContent = analytics.last_error || 'None';
        analyticsAttempts.textContent = analytics.attempt_count;
        analyticsLastAttempt.textContent = formatDate(analytics.last_attempt_at);
        analyticsPostedAt.textContent = analytics.posted_at ? formatDate(analytics.posted_at) : 'Not yet';
        renderTotals(analytics.totals || {});
        renderLogs(analytics.logs || []);
        // Use modal manager for reliable modal display
        if (window.modalManager) {
            window.modalManager.show('analyticsModal');
        } else if (analyticsModal) {
            try {
                analyticsModal.show();
            } catch (error) {
                console.error('Error showing analytics modal:', error);
            }
        } else {
            console.warn('Modal system not available');
        }
    }

    async function loadCredentials() {
        const response = await fetch('/api/admin/social-posts/credentials');
        if (!response.ok) {
            credentialsTableBody.innerHTML = '<tr><td colspan="2" class="text-danger text-center">Unable to load credentials</td></tr>';
            return;
        }
        const credentials = await response.json();
        credentialsTableBody.innerHTML = '';
        if (!credentials.length) {
            credentialsTableBody.innerHTML = '<tr><td colspan="2" class="text-muted text-center">No credentials stored yet.</td></tr>';
            return;
        }
        credentials.forEach((cred) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="text-capitalize">${cred.platform}</td>
                <td>${formatDate(cred.updated_at)}</td>
            `;
            credentialsTableBody.appendChild(row);
        });
    }

    async function handleCredentialSubmit(event) {
        event.preventDefault();
        const payload = {
            platform: credentialForm.platform.value,
            access_token: credentialForm.access_token.value,
            refresh_token: credentialForm.refresh_token.value || null,
            metadata: credentialForm.metadata.value || null,
        };
        const response = await fetch('/api/admin/social-posts/credentials', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });
        if (response.ok) {
            showAlert('Credentials saved');
            credentialForm.reset();
            loadCredentials();
        } else {
            const error = await response.json().catch(() => ({}));
            showAlert(error.detail || 'Unable to save credentials');
        }
    }

    function delegateTableClicks(event) {
        const button = event.target.closest('button');
        if (!button) return;
        const postId = button.dataset.postId;
        if (!postId) return;
        if (button.classList.contains('delete-post')) {
            handleDeletePost(postId);
        } else if (button.classList.contains('retry-post')) {
            handleRetryPost(postId);
        } else if (button.classList.contains('preview-post')) {
            handlePreview(postId);
        } else if (button.classList.contains('analytics-post')) {
            handleAnalytics(postId);
        }
    }
    
    // Setup modal event listeners (modal manager handles most of this now)
    function setupModalEventListeners() {
        // Additional custom modal event handlers can go here if needed
        console.log('Modal event listeners setup - using global modal manager');
    }

    platformSelect.addEventListener('change', updateContentTypes);
    contentTypeSelect.addEventListener('change', updateMediaFields);
    form.addEventListener('submit', handleCreatePost);
    credentialForm.addEventListener('submit', handleCredentialSubmit);
    postsTableBody?.addEventListener('click', delegateTableClicks);

    // Setup modal event listeners
    setupModalEventListeners();

    updateContentTypes();
    loadCredentials();
});
