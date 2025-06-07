document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const messageDiv = document.getElementById('loginMessage');

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ // Stringify the data
                    username: username,
                    password: password,
                }),
            });

            const data = await response.json();

            if (response.ok) {
                // Successful login
                if (data.role === 'admin') {
                    // Redirect admin to dashboard
                    messageDiv.innerHTML = `<div class="alert alert-success">${data.detail}</div>`;
                    setTimeout(
                        ()=>{
                            window.location.href='admin/dashboard'
                        }
                    )
                    // window.location.href = '/admin/dashboard';
                } else {
                    // Student, parent, organisation
                    // If there's a pending order, redirect to payment
                    if (pending_order_id) {
                        window.location.href = `/payment?order=${pending_order_id}`;
                    } else {
                        // Redirect other users (e.g., to home page)
                        window.location.href = '/'; // Or wherever you want to redirect
                    }
                    
                }
            } else {
                messageDiv.innerHTML = `<div class="alert alert-danger">${data.detail}</div>`;
                // Login failed
                // alert(data.detail || 'Login failed. Please try again.');
            }
        } catch (error) {
            console.error('Login error:', error);
            alert('An unexpected error occurred.');
        }
    });
});