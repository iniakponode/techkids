document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('teacherApplicationForm');
    if (!form) return;
    const successBox = document.getElementById('teachSuccess');
    const errorBox = document.getElementById('teachError');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        successBox.classList.add('d-none');
        errorBox.classList.add('d-none');

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            const res = await fetch('/api/teacher-applications', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (res.ok) {
                form.reset();
                successBox.classList.remove('d-none');
            } else {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || 'Failed to submit application.');
            }
        } catch (err) {
            errorBox.textContent = err.message || 'Submission failed. Please try again later.';
            errorBox.classList.remove('d-none');
        }
    });
});
