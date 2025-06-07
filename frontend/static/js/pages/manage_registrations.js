document.addEventListener('DOMContentLoaded', () => {
    const deleteButtons = document.querySelectorAll('.delete-registration');
    deleteButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const regId = button.dataset.regId;
            if (confirm('Are you sure you want to delete this registration?')) {
                try {
                    const res = await fetch(`/api/admin/registrations/delete/${regId}`, { method: 'DELETE' });
                    if (res.ok) {
                        window.location.reload();
                    } else {
                        alert('Failed to delete registration.');
                    }
                } catch (err) {
                    console.error('Error:', err);
                    alert('An error occurred.');
                }
            }
        });
    });
});
