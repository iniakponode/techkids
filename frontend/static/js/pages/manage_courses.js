document.addEventListener('DOMContentLoaded', () => {
    const deleteButtons = document.querySelectorAll('.delete-course');

    deleteButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
            event.preventDefault();
            const courseId = button.dataset.courseId;
            if (confirm('Are you sure you want to delete this course?')) {
                try {
                    const response = await fetch(`/api/admin/courses/delete/${courseId}`, {
                        method: 'DELETE',
                    });
                    if (response.ok) {
                        window.location.reload();
                    } else {
                        alert('Failed to delete course.');
                    }
                } catch (error) {
                    console.error('Error deleting course:', error);
                    alert('An error occurred.');
                }
            }
        });
    });
});