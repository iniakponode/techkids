document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('post-form');
    const platformSelect = document.getElementById('platform');
    const contentTypeSelect = document.getElementById('content_type');
    const imageField = document.getElementById('image-field');
    const videoField = document.getElementById('video-field');

    const contentOptions = {
        facebook: ['Feed', 'Story'],
        instagram: ['Feed', 'Reel', 'Story'],
        whatsapp: ['Status'],
        x: ['Post'],
        threads: ['Post'],
        telegram: ['Post']
    };

    function updateContentTypes() {
        const platform = platformSelect.value;
        contentTypeSelect.innerHTML = '';
        (contentOptions[platform] || []).forEach(type => {
            const opt = document.createElement('option');
            opt.value = type;
            opt.textContent = type;
            contentTypeSelect.appendChild(opt);
        });
        updateMediaFields();
    }

    function updateMediaFields() {
        const type = contentTypeSelect.value.toLowerCase();
        if (type === 'reel') {
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

    platformSelect.addEventListener('change', updateContentTypes);
    contentTypeSelect.addEventListener('change', updateMediaFields);
    updateContentTypes();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const res = await fetch('/api/admin/social-posts/', {
            method: 'POST',
            body: formData
        });
        if (res.ok) {
            window.location.reload();
        } else {
            alert('Failed to create post');
        }
    });

    document.querySelectorAll('.delete-post').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const id = btn.dataset.postId;
            if (confirm('Delete this post?')) {
                const res = await fetch(`/api/admin/social-posts/${id}`, { method: 'DELETE' });
                if (res.ok) {
                    window.location.reload();
                } else {
                    alert('Failed to delete post');
                }
            }
        });
    });
});

