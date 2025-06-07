document.addEventListener('DOMContentLoaded', () => {
    const deleteButtons = document.querySelectorAll('.delete-customer');

    deleteButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
            event.preventDefault();
            const userId = button.dataset.customerId;
            if (confirm('Are you sure you want to delete this customer?')) {
                try {
                    const response = await fetch(`/api/admin/customers/delete/${userId}`, {
                        method: 'DELETE',
                    });
                    if (response.ok) {
                        window.location.reload();
                    } else {
                        alert('Failed to delete customer.');
                    }
                } catch (error) {
                    console.error('Error deleting customer:', error);
                    alert('An error occurred.');
                }
            }
        });
    });
});
