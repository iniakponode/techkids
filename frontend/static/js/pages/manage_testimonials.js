document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.approve-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id = btn.dataset.id;
            const approved = btn.dataset.approved === 'true';
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
});
