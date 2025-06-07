document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('editCustomerForm');
    const messageDiv = document.getElementById('editCustomerMessage');
    const customerId = window.location.pathname.split('/').pop();

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const data = {
            email: document.getElementById('email').value,
            role: document.getElementById('role').value,
            password: document.getElementById('password').value
        };
        try {
            const response = await fetch(`/api/admin/customers/${customerId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const resData = await response.json();
            if (response.ok) {
                messageDiv.innerHTML = '<div class="alert alert-success">Customer updated successfully.</div>';
            } else {
                messageDiv.innerHTML = `<div class="alert alert-danger">${resData.detail || 'Failed to update customer.'}</div>`;
            }
        } catch (err) {
            console.error('Error:', err);
            messageDiv.innerHTML = '<div class="alert alert-danger">An error occurred.</div>';
        }
    });
});
