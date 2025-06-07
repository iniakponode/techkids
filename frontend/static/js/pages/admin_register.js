document.addEventListener('DOMContentLoaded', () => {
    console.log("admin_register.js loaded"); // Add this line
    const form = document.getElementById('adminRegisterForm');
    const messageDiv = document.getElementById('registrationMessage');

    form.addEventListener('submit', async (event) => {
        console.log("Form submitted"); // Add this line
        event.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('/api/auth/admin/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password, role: 'admin' }),
                credentials: 'include'
            });

            const data = await response.json();

            if (response.ok) {
                messageDiv.innerHTML = '<div class="alert alert-success">Registration successful!</div>';
                form.reset(); // Clear the form
                setTimeout(
                    ()=>{
                        window.location.href='/login'
                    },
                    1500
                )
            } else {
                messageDiv.innerHTML = `<div class="alert alert-danger">${data.detail}</div>`;
            }
        } catch (error) {
            console.error('Registration error:', error);
            messageDiv.innerHTML = '<div class="alert alert-danger">An unexpected error occurred.</div>';
        }
    });
});