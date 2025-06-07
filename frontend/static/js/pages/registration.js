// /static/js/pages/registration.js

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('registrationForm');
  if (!form) return;

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    // Remove existing alerts
    document.querySelectorAll('.alert').forEach(alertEl => alertEl.remove());

    // Basic validation
    if (!form.checkValidity()) {
      event.stopPropagation();
      form.classList.add('was-validated');
      return;
    }

    // Gather form data
    const formData = new FormData(form);

    // If using checkboxes for multiple courses
    const selectedCourseIds = [];
    form.querySelectorAll('input[name="course_ids"]:checked').forEach(checkbox => {
      selectedCourseIds.push(parseInt(checkbox.value));
    });

    const registrationData = {
      fullName: formData.get('fullName'),
      email: formData.get('email'),
      password: formData.get('password'),
      confirm_password: formData.get('confirm_password'),
      phone: formData.get('phone'),
      course_ids: selectedCourseIds,
      role: formData.get('role') || 'student',
    };

    try {
      const response = await fetch('/api/registrations/public-register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registrationData),
        credentials: 'include'
      });

      if (!response.ok) {
        const errorJson = await response.json();
        if (Array.isArray(errorJson.detail)) {
          const messages = errorJson.detail.map(err => err.msg).join(', ');
          throw new Error(messages);
        } else if (typeof errorJson.detail === 'string') {
          throw new Error(errorJson.detail);
        } else {
          throw new Error('Registration failed');
        }
      }

      const result = await response.json();
      // result = { order_id, total_cost }

      // Show success
      const alertDiv = document.createElement('div');
      alertDiv.className = 'alert alert-success';
      alertDiv.role = 'alert';
      alertDiv.innerHTML = 'Registration successful! Redirecting to payment...';
      form.replaceWith(alertDiv);

      // Go to payment page
      setTimeout(() => {
        window.location.href = `/payment?order=${result.order_id}`;
      }, 1500);

    } catch (error) {
      console.error('Registration error:', error);
      const errorAlert = document.createElement('div');
      errorAlert.className = 'alert alert-danger mt-3';
      errorAlert.role = 'alert';
      errorAlert.textContent = error.message || 'Registration failed. Please try again.';
      form.insertAdjacentElement('beforebegin', errorAlert);
    }
  });
});
