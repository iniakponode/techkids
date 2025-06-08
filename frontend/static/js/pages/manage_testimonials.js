document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.approve-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = btn.dataset.id;
            const approved = (btn.dataset.approved || '').toLowerCase() === 'true';
            const res = await fetch(`/api/admin/testimonials/${id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_approved: !approved })
            });
            if (res.ok) {
                location.reload();
            } else {
                alert('Failed to update testimonial');
            }
        });
    });

    document.querySelectorAll('.delete-testimonial').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const id = btn.dataset.id;
            if (confirm('Are you sure you want to delete this testimonial?')) {
                const res = await fetch(`/api/admin/testimonials/${id}`, {
                    method: 'DELETE'
                });
                if (res.ok) {
                    location.reload();
                } else {
                    alert('Failed to delete testimonial');
                }
            }
        });
    });
});
