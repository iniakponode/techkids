document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('editCourseForm');
    const modal = new bootstrap.Modal(document.getElementById('updateCourseModal'));
    const modalBody = document.getElementById('updateCourseModalBody');
    const editCourseBtn = document.getElementById('editCourse');
    const courseId = window.location.pathname.split('/').pop();

    const toolbarOptions = [
        [{ header: [1, 2, 3, false] }],
        ['bold', 'italic', 'underline', 'strike'],
        [{ color: [] }, { background: [] }],
        [{ list: 'ordered' }, { list: 'bullet' }],
        ['blockquote', 'code-block', 'link'],
        ['clean'],
    ];

    const initialiseQuillEditor = (editorSelector, hiddenField) => {
        const editorContainer = document.querySelector(editorSelector);

        if (!editorContainer || !hiddenField || typeof Quill === 'undefined') {
            return null;
        }

        const quill = new Quill(editorContainer, {
            theme: 'snow',
            modules: {
                toolbar: toolbarOptions,
            },
        });

        if (hiddenField.value) {
            quill.clipboard.dangerouslyPasteHTML(hiddenField.value);
        }

        const syncEditorContent = () => {
            const isEmpty = quill.getText().trim().length === 0;
            hiddenField.value = isEmpty ? '' : quill.root.innerHTML;
        };

        quill.on('text-change', syncEditorContent);
        syncEditorContent();

        return quill;
    };

    const summaryField = document.getElementById('summary');
    const descriptionField = document.getElementById('description');

    initialiseQuillEditor('#summaryEditor', summaryField);
    initialiseQuillEditor('#descriptionEditor', descriptionField);

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        if (!descriptionField.value || descriptionField.value.trim().length === 0) {
            descriptionField.setCustomValidity('Please provide a course description.');
            descriptionField.reportValidity();
            return;
        }

        descriptionField.setCustomValidity('');

        editCourseBtn.innerHTML = 'Updating Course Details... <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';

        const formData = new FormData(form);

        try {
            const response = await fetch(`/api/admin/courses/${courseId}`, {
                method: 'PUT',
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                modalBody.innerHTML = '<div class="alert alert-success">Course updated successfully!</div>';
            } else {
                modalBody.innerHTML = `<div class="alert alert-danger">${data.detail || 'Failed to update course.'}</div>`;
            }

            editCourseBtn.innerHTML = 'Update Course';
            modal.show();
        } catch (error) {
            console.error('Error updating course:', error);
            modalBody.innerHTML = '<div class="alert alert-danger">An error occurred.</div>';
            modal.show();
            editCourseBtn.innerHTML = 'Update Course';
        }
    });
});