document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('editCourseForm');
    const modal = new bootstrap.Modal(document.getElementById('updateCourseModal'));
    const modalBody = document.getElementById('updateCourseModalBody');
    const editCourseBtn=document.getElementById("editCourse")
    const courseId = window.location.pathname.split('/').pop();

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Show the spinner and change the button text to "Processing..."
        // loadingSpinner.style.display = "inline-block";
        editCourseBtn.innerHTML = 'Updating Course Details... <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        const formData = new FormData(form);
            try {
            const response = await fetch(`/api/admin/courses/${courseId}`, {
                method: 'PUT',
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                // document.getElementById("updateCourseModalLabel").
                modalBody.innerHTML = '<div class="alert alert-success">Course updated successfully!</div>';
                editCourseBtn.innerHTML = "Update Course";
                
            } else {
                modalBody.innerHTML = `<div class="alert alert-danger">${data.detail || 'Failed to update course.'}</div>`;
                // Hide the spinner and reset button text
                // loadingSpinner.style.display = "none";
                editCourseBtn.innerHTML = "Update Course";
            }
            modal.show();
        } catch (error) {
            console.error('Error updating course:', error);
            modalBody.innerHTML = '<div class="alert alert-danger">An error occurred.</div>';
            modal.show();
        // Hide the spinner and reset button text
            // loadingSpinner.style.display = "none";
            editCourseBtn.innerHTML = "Update Course";
        }
    });
});