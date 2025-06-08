document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('testimonialForm');
    const alertBox = document.getElementById('testimonialSuccess');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        const res = await fetch('/api/testimonials', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (res.ok) {
            form.reset();
            alertBox.classList.remove('d-none');
        } else {
            alert('Failed to submit testimonial.');
        }
    });
});
