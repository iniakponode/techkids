document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('post-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const data = {
            platform: formData.get('platform'),
            content: formData.get('content'),
            scheduled_at: formData.get('scheduled_at') || null,
        };
        const res = await fetch('/api/admin/social-posts/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
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

