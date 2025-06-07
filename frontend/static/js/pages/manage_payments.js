document.addEventListener('DOMContentLoaded', () => {
    const deleteButtons = document.querySelectorAll('.delete-payment');
    deleteButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const paymentId = button.dataset.paymentId;
            if (confirm('Are you sure you want to delete this payment?')) {
                try {
                    const res = await fetch(`/api/admin/payments/delete/${paymentId}`, { method: 'DELETE' });
                    if (res.ok) {
                        window.location.reload();
                    } else {
                        alert('Failed to delete payment.');
                    }
                } catch (err) {
                    console.error('Error:', err);
                    alert('An error occurred.');
                }
            }
        });
    });
});
