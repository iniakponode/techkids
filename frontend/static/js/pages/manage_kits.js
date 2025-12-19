document.addEventListener('DOMContentLoaded', () => {
    const deleteButtons = document.querySelectorAll('.delete-kit');

    deleteButtons.forEach((button) => {
        button.addEventListener('click', async (event) => {
            event.preventDefault();
            const kitId = button.dataset.kitId;
            if (!kitId) {
                return;
            }
            if (confirm('Are you sure you want to delete this kit?')) {
                try {
                    const response = await fetch(`/api/admin/kits/${kitId}`, {
                        method: 'DELETE',
                    });
                    if (response.ok) {
                        window.location.reload();
                    } else {
                        alert('Failed to delete kit.');
                    }
                } catch (error) {
                    console.error('Error deleting kit:', error);
                    alert('An error occurred.');
                }
            }
        });
    });
});
