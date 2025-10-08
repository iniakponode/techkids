document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('addCourseForm');
  const addCourseBtn = document.getElementById('addCourse');

  if (!form || !addCourseBtn) {
    return;
  }

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

    if (!editorContainer || !hiddenField) {
      return null;
    }

    if (typeof Quill === 'undefined') {
      hiddenField.classList.remove('d-none');
      const wrapper = editorContainer.closest('.quill-wrapper');

      if (wrapper) {
        wrapper.classList.add('d-none');
      }

      return null;
    }

    const quill = new Quill(editorContainer, {
      theme: 'snow',
      modules: {
        toolbar: toolbarOptions,
      },
    });

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

  const summaryEditor = initialiseQuillEditor('#summaryEditor', summaryField);
  const descriptionEditor = initialiseQuillEditor('#descriptionEditor', descriptionField);

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    if (descriptionField && (!descriptionField.value || descriptionField.value.trim().length === 0)) {
      descriptionField.setCustomValidity('Please provide a course description.');
      descriptionField.reportValidity();
      return;
    }

    if (descriptionField) {
      descriptionField.setCustomValidity('');
    }

    document.querySelectorAll('.alert').forEach((alertEl) => alertEl.remove());

    addCourseBtn.innerHTML =
      'Adding Course... <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';

    const formData = new FormData(form);

    try {
      const response = await fetch('/api/admin/courses/add', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'Failed to add course.');
      }

      const data = await response.json();

      const alertDiv = document.createElement('div');
      alertDiv.className = 'alert alert-success';
      alertDiv.innerHTML = `Course "${data.title}" added successfully!`;
      form.prepend(alertDiv);

      form.reset();

      if (summaryField) {
        summaryField.value = '';
      }

      if (descriptionField) {
        descriptionField.value = '';
      }

      if (summaryEditor) {
        summaryEditor.setText('');
      }

      if (descriptionEditor) {
        descriptionEditor.setText('');
      }

      addCourseBtn.innerHTML = 'Add Course';
    } catch (error) {
      console.error('Error adding course:', error);
      const errorAlert = document.createElement('div');
      errorAlert.className = 'alert alert-danger mt-3';
      errorAlert.textContent = error.message || 'Failed to add course. Please try again.';
      form.prepend(errorAlert);
      addCourseBtn.innerHTML = 'Add Course';
    }
  });
});
