(function () {
  document.addEventListener('DOMContentLoaded', () => {
    const courseSelect = document.getElementById('courseSelect');
    const modulesContainer = document.getElementById('modulesContainer');
    const modulesEmptyState = document.getElementById('modulesEmptyState');
    const moduleCountBadge = document.getElementById('moduleCountBadge');
    const moduleForm = document.getElementById('moduleForm');
    const moduleFormHeading = document.getElementById('moduleFormHeading');
    const moduleFormAlert = document.getElementById('moduleFormAlert');
    const moduleFormSubmit = document.getElementById('moduleFormSubmit');
    const moduleFormCancel = document.getElementById('moduleFormCancel');
    const moduleIdInput = document.getElementById('moduleId');
    const moduleTitleInput = document.getElementById('moduleTitle');
    const moduleDescriptionInput = document.getElementById('moduleDescription');
    const modulePositionInput = document.getElementById('modulePosition');
    const alertsContainer = document.getElementById('learningPathAlerts');

    const lessonModalElement = document.getElementById('lessonModal');
    const lessonModalLabel = document.getElementById('lessonModalLabel');
    const lessonForm = document.getElementById('lessonForm');
    const lessonFormSubmit = document.getElementById('lessonFormSubmit');
    const lessonFormAlert = document.getElementById('lessonFormAlert');
    const lessonIdInput = document.getElementById('lessonId');
    const lessonModuleIdInput = document.getElementById('lessonModuleId');
    const lessonTitleInput = document.getElementById('lessonTitle');
    const lessonContentInput = document.getElementById('lessonContent');
    const lessonPositionInput = document.getElementById('lessonPosition');
    const lessonDurationInput = document.getElementById('lessonDuration');
    const lessonResourceInput = document.getElementById('lessonResource');

    if (!modulesContainer) {
      return;
    }

    const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
    const csrfToken = (csrfTokenMeta && csrfTokenMeta.getAttribute('content')) || '';

    const state = {
      activeCourseId: null,
      modules: [],
      editingModuleId: null,
      editingLessonId: null,
      modulesRequestToken: null,
    };

    const bootstrapModal = window.bootstrap && window.bootstrap.Modal ? window.bootstrap.Modal : null;
    const lessonModal = lessonModalElement && bootstrapModal ? new bootstrapModal(lessonModalElement) : null;

    const findModuleById = (moduleId) =>
      state.modules.find((module) => Number(module.id) === Number(moduleId));

    const findLesson = (moduleId, lessonId) => {
      const module = findModuleById(moduleId);
      if (!module || !Array.isArray(module.lessons)) {
        return null;
      }
      return module.lessons.find((lesson) => Number(lesson.id) === Number(lessonId)) || null;
    };

    const setButtonLoading = (button, isLoading, loadingText = 'Saving') => {
      if (!button) {
        return;
      }

      if (isLoading) {
        if (!button.dataset.originalContent) {
          button.dataset.originalContent = button.innerHTML;
        }
        button.innerHTML = `${loadingText} <span class="spinner-border spinner-border-sm ms-2" role="status" aria-hidden="true"></span>`;
        button.disabled = true;
      } else {
        if (button.dataset.originalContent) {
          button.innerHTML = button.dataset.originalContent;
          delete button.dataset.originalContent;
        }
        button.disabled = false;
      }
    };

    const showAlert = (message, type = 'success', timeout = 5000) => {
      if (!alertsContainer || !message) {
        return;
      }

      const alert = document.createElement('div');
      alert.className = `alert alert-${type} alert-dismissible fade show`;
      alert.setAttribute('role', 'alert');
      alert.textContent = message;

      const closeBtn = document.createElement('button');
      closeBtn.type = 'button';
      closeBtn.className = 'btn-close';
      closeBtn.setAttribute('data-bs-dismiss', 'alert');
      closeBtn.setAttribute('aria-label', 'Close');
      closeBtn.addEventListener('click', () => {
        alert.remove();
      });

      alert.appendChild(closeBtn);
      alertsContainer.appendChild(alert);

      if (timeout) {
        window.setTimeout(() => {
          alert.classList.remove('show');
          const removeAlert = () => alert.remove();
          alert.addEventListener('transitionend', removeAlert, { once: true });
          window.setTimeout(removeAlert, 200);
        }, timeout);
      }
    };

    const setModuleFormMessage = (message, type = 'danger') => {
      if (!moduleFormAlert) {
        return;
      }
      if (!message) {
        moduleFormAlert.className = 'alert d-none';
        moduleFormAlert.textContent = '';
        return;
      }
      moduleFormAlert.className = `alert alert-${type} mb-3`;
      moduleFormAlert.textContent = message;
    };

    const setLessonFormMessage = (message, type = 'danger') => {
      if (!lessonFormAlert) {
        return;
      }
      if (!message) {
        lessonFormAlert.className = 'alert d-none';
        lessonFormAlert.textContent = '';
        return;
      }
      lessonFormAlert.className = `alert alert-${type}`;
      lessonFormAlert.textContent = message;
    };

    const updateModuleCount = (count) => {
      if (!moduleCountBadge) {
        return;
      }
      const safeCount = Number.isFinite(count) ? count : 0;
      moduleCountBadge.textContent = `${safeCount} module${safeCount === 1 ? '' : 's'}`;
    };

    const updateModuleDefaultPosition = () => {
      if (!modulePositionInput) {
        return;
      }
      modulePositionInput.placeholder = String(state.modules.length || 0);
      if (!state.editingModuleId) {
        if (modulePositionInput.dataset.autofill !== 'false') {
          modulePositionInput.value = state.modules.length || 0;
          modulePositionInput.dataset.autofill = 'true';
        }
      }
    };

    const updateQueryParam = (key, value) => {
      if (!window.history || !window.history.replaceState) {
        return;
      }
      const url = new URL(window.location.href);
      if (value !== null && value !== undefined && value !== '') {
        url.searchParams.set(key, String(value));
      } else {
        url.searchParams.delete(key);
      }
      window.history.replaceState({}, '', url.toString());
    };

    const updateModuleFormState = () => {
      if (!moduleForm) {
        return;
      }
      const hasCourse = Number.isInteger(state.activeCourseId);
      const elements = moduleForm.querySelectorAll('input, textarea, button');
      elements.forEach((element) => {
        if (element.type === 'hidden') {
          return;
        }
        if (element === moduleFormCancel && moduleFormCancel.classList.contains('d-none')) {
          element.disabled = true;
          return;
        }
        element.disabled = !hasCourse;
      });

      if (!hasCourse) {
        setModuleFormMessage('Add a course to start creating modules.', 'info');
      } else if (moduleFormAlert.classList.contains('alert-info')) {
        setModuleFormMessage(null);
      }
    };

    const resetModuleForm = () => {
      if (!moduleForm) {
        return;
      }
      moduleForm.reset();
      moduleForm.classList.remove('was-validated');
      state.editingModuleId = null;
      if (moduleIdInput) {
        moduleIdInput.value = '';
      }
      if (moduleFormHeading) {
        moduleFormHeading.textContent = 'Add module';
      }
      if (moduleFormSubmit) {
        moduleFormSubmit.textContent = 'Add module';
      }
      if (moduleFormCancel) {
        moduleFormCancel.classList.add('d-none');
        moduleFormCancel.disabled = false;
      }
      if (modulePositionInput) {
        modulePositionInput.dataset.autofill = 'true';
      }
      setModuleFormMessage(null);
      updateModuleDefaultPosition();
    };

    const apiRequest = async (url, { method = 'GET', body } = {}) => {
      const headers = { Accept: 'application/json' };
      if (body !== undefined) {
        headers['Content-Type'] = 'application/json';
      }
      if (csrfToken) {
        headers['X-CSRF-Token'] = csrfToken;
      }

      const response = await fetch(url, {
        method,
        headers,
        body: body !== undefined ? JSON.stringify(body) : undefined,
      });

      if (!response.ok) {
        let message = 'Unable to complete the request.';
        const errorText = await response.text();
        if (errorText) {
          try {
            const parsed = JSON.parse(errorText);
            if (parsed) {
              if (typeof parsed === 'string') {
                message = parsed;
              } else if (parsed.detail) {
                message = typeof parsed.detail === 'string' ? parsed.detail : JSON.stringify(parsed.detail);
              }
            }
          } catch (error) {
            message = errorText;
          }
        }
        throw new Error(message);
      }

      if (response.status === 204 || response.status === 205) {
        return null;
      }

      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        return response.json();
      }

      return null;
    };

    const renderModules = () => {
      if (!modulesContainer) {
        return;
      }

      const hasCourse = Number.isInteger(state.activeCourseId);

      if (!hasCourse) {
        modulesContainer.innerHTML = '<div class="text-center text-muted py-5">Select a course to view its learning path.</div>';
        updateModuleCount(0);
        if (modulesEmptyState) {
          modulesEmptyState.classList.add('d-none');
        }
        updateModuleDefaultPosition();
        return;
      }

      modulesContainer.innerHTML = '';

      const modules = Array.isArray(state.modules)
        ? [...state.modules].sort((a, b) => {
            const aPos = Number.isFinite(a.position) ? a.position : 0;
            const bPos = Number.isFinite(b.position) ? b.position : 0;
            if (aPos === bPos) {
              return Number(a.id) - Number(b.id);
            }
            return aPos - bPos;
          })
        : [];

      updateModuleCount(modules.length);

      if (!modules.length) {
        if (modulesEmptyState) {
          modulesEmptyState.classList.remove('d-none');
        }
        updateModuleDefaultPosition();
        return;
      }

      if (modulesEmptyState) {
        modulesEmptyState.classList.add('d-none');
      }

      modules.forEach((module) => {
        const moduleCard = document.createElement('article');
        moduleCard.className = 'card shadow-sm';
        moduleCard.dataset.moduleId = module.id;

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';

        const header = document.createElement('div');
        header.className = 'd-flex justify-content-between align-items-start flex-wrap gap-2 mb-3';

        const headerInfo = document.createElement('div');
        const titleEl = document.createElement('h3');
        titleEl.className = 'h5 mb-1';
        titleEl.textContent = module.title || 'Untitled module';

        const metaEl = document.createElement('p');
        metaEl.className = 'text-muted small mb-0';
        const modulePosition = Number.isFinite(module.position) ? module.position : 0;
        metaEl.textContent = `Position: ${modulePosition}`;

        headerInfo.appendChild(titleEl);
        headerInfo.appendChild(metaEl);
        header.appendChild(headerInfo);

        const headerActions = document.createElement('div');
        headerActions.className = 'btn-group';

        const editModuleBtn = document.createElement('button');
        editModuleBtn.type = 'button';
        editModuleBtn.className = 'btn btn-sm btn-outline-secondary';
        editModuleBtn.dataset.action = 'edit-module';
        editModuleBtn.dataset.moduleId = module.id;
        editModuleBtn.textContent = 'Edit';

        const addLessonBtn = document.createElement('button');
        addLessonBtn.type = 'button';
        addLessonBtn.className = 'btn btn-sm btn-outline-primary';
        addLessonBtn.dataset.action = 'add-lesson';
        addLessonBtn.dataset.moduleId = module.id;
        addLessonBtn.textContent = 'Add lesson';

        const deleteModuleBtn = document.createElement('button');
        deleteModuleBtn.type = 'button';
        deleteModuleBtn.className = 'btn btn-sm btn-outline-danger';
        deleteModuleBtn.dataset.action = 'delete-module';
        deleteModuleBtn.dataset.moduleId = module.id;
        deleteModuleBtn.textContent = 'Delete';

        headerActions.append(editModuleBtn, addLessonBtn, deleteModuleBtn);
        header.appendChild(headerActions);
        cardBody.appendChild(header);

        if (module.description) {
          const descriptionEl = document.createElement('p');
          descriptionEl.className = 'mb-3';
          descriptionEl.textContent = module.description;
          cardBody.appendChild(descriptionEl);
        }

        const lessonsHeading = document.createElement('h4');
        lessonsHeading.className = 'h6 text-uppercase text-muted mb-2';
        lessonsHeading.textContent = 'Lessons';
        cardBody.appendChild(lessonsHeading);

        const lessons = Array.isArray(module.lessons)
          ? [...module.lessons].sort((a, b) => {
              const aPos = Number.isFinite(a.position) ? a.position : 0;
              const bPos = Number.isFinite(b.position) ? b.position : 0;
              if (aPos === bPos) {
                return Number(a.id) - Number(b.id);
              }
              return aPos - bPos;
            })
          : [];

        if (!lessons.length) {
          const emptyLessons = document.createElement('div');
          emptyLessons.className = 'text-muted fst-italic';
          emptyLessons.textContent = 'No lessons yet. Add one to get started.';
          cardBody.appendChild(emptyLessons);
        } else {
          const lessonList = document.createElement('ul');
          lessonList.className = 'list-group list-group-flush border-top';

          lessons.forEach((lesson) => {
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item px-0';
            listItem.dataset.lessonId = lesson.id;

            const row = document.createElement('div');
            row.className = 'd-flex justify-content-between align-items-start flex-wrap gap-2';

            const info = document.createElement('div');

            const lessonTitle = document.createElement('p');
            lessonTitle.className = 'fw-semibold mb-1';
            lessonTitle.textContent = lesson.title || 'Untitled lesson';
            info.appendChild(lessonTitle);

            const lessonDetails = document.createElement('p');
            lessonDetails.className = 'text-muted small mb-1';
            const detailSegments = [];
            const lessonPosition = Number.isFinite(lesson.position) ? lesson.position : 0;
            detailSegments.push(`Position: ${lessonPosition}`);
            if (lesson.duration_minutes !== null && lesson.duration_minutes !== undefined) {
              detailSegments.push(`Duration: ${lesson.duration_minutes} min`);
            }
            lessonDetails.textContent = detailSegments.join(' • ');
            info.appendChild(lessonDetails);

            const lessonSummary = document.createElement('p');
            lessonSummary.className = 'text-muted small mb-0';
            if (lesson.content) {
              lessonSummary.textContent = lesson.content.length > 140
                ? `${lesson.content.slice(0, 140)}…`
                : lesson.content;
            } else {
              lessonSummary.textContent = 'No summary provided yet.';
            }
            info.appendChild(lessonSummary);

            if (lesson.resource_url) {
              const resourceLink = document.createElement('a');
              resourceLink.className = 'small d-block';
              resourceLink.href = lesson.resource_url;
              resourceLink.target = '_blank';
              resourceLink.rel = 'noopener';
              resourceLink.textContent = 'Open resource';
              info.appendChild(resourceLink);
            }

            row.appendChild(info);

            const lessonActions = document.createElement('div');
            lessonActions.className = 'btn-group';

            const editLessonBtn = document.createElement('button');
            editLessonBtn.type = 'button';
            editLessonBtn.className = 'btn btn-sm btn-outline-secondary';
            editLessonBtn.dataset.action = 'edit-lesson';
            editLessonBtn.dataset.moduleId = module.id;
            editLessonBtn.dataset.lessonId = lesson.id;
            editLessonBtn.textContent = 'Edit';

            const deleteLessonBtn = document.createElement('button');
            deleteLessonBtn.type = 'button';
            deleteLessonBtn.className = 'btn btn-sm btn-outline-danger';
            deleteLessonBtn.dataset.action = 'delete-lesson';
            deleteLessonBtn.dataset.moduleId = module.id;
            deleteLessonBtn.dataset.lessonId = lesson.id;
            deleteLessonBtn.textContent = 'Delete';

            lessonActions.append(editLessonBtn, deleteLessonBtn);
            row.appendChild(lessonActions);

            listItem.appendChild(row);
            lessonList.appendChild(listItem);
          });

          cardBody.appendChild(lessonList);
        }

        moduleCard.appendChild(cardBody);
        modulesContainer.appendChild(moduleCard);
      });

      updateModuleDefaultPosition();
    };

    const fetchModules = async (courseId) => {
      if (!modulesContainer) {
        return;
      }

      if (!Number.isInteger(courseId)) {
        renderModules();
        return;
      }

      const requestToken = Symbol('modulesFetch');
      state.modulesRequestToken = requestToken;

      modulesContainer.innerHTML = '<div class="text-center text-muted py-5">Loading learning path…</div>';
      if (modulesEmptyState) {
        modulesEmptyState.classList.add('d-none');
      }

      try {
        const response = await fetch(`/api/learning-paths/courses/${courseId}`);
        if (!response.ok) {
          throw new Error('Unable to load the learning path right now.');
        }
        const data = await response.json();
        if (state.modulesRequestToken !== requestToken || state.activeCourseId !== courseId) {
          return;
        }
        state.modules = Array.isArray(data) ? data : [];
        renderModules();
      } catch (error) {
        if (state.modulesRequestToken !== requestToken || state.activeCourseId !== courseId) {
          return;
        }
        state.modules = [];
        modulesContainer.innerHTML = `<div class="alert alert-danger" role="alert">${
          error && error.message ? error.message : 'Unable to load the learning path right now.'
        }</div>`;
        updateModuleCount(0);
        if (modulesEmptyState) {
          modulesEmptyState.classList.add('d-none');
        }
      } finally {
        if (state.modulesRequestToken === requestToken && state.activeCourseId === courseId) {
          updateModuleFormState();
          updateModuleDefaultPosition();
        }
      }
    };

    const startModuleEdit = (moduleId) => {
      const module = findModuleById(moduleId);
      if (!module) {
        showAlert('Could not find that module.', 'danger');
        return;
      }

      state.editingModuleId = module.id;
      if (moduleIdInput) {
        moduleIdInput.value = module.id;
      }
      if (moduleTitleInput) {
        moduleTitleInput.value = module.title || '';
      }
      if (moduleDescriptionInput) {
        moduleDescriptionInput.value = module.description || '';
      }
      if (modulePositionInput) {
        modulePositionInput.value = Number.isFinite(module.position) ? module.position : 0;
        modulePositionInput.dataset.autofill = 'false';
      }
      if (moduleFormHeading) {
        moduleFormHeading.textContent = 'Edit module';
      }
      if (moduleFormSubmit) {
        moduleFormSubmit.textContent = 'Save changes';
      }
      if (moduleFormCancel) {
        moduleFormCancel.classList.remove('d-none');
        moduleFormCancel.disabled = false;
      }
      setModuleFormMessage(null);
      moduleTitleInput && moduleTitleInput.focus();
    };

    const openLessonModal = (moduleId, lessonId = null) => {
      const module = findModuleById(moduleId);
      if (!module || !lessonForm) {
        showAlert('Unable to open the lesson editor right now.', 'danger');
        return;
      }

      lessonForm.reset();
      setLessonFormMessage(null);
      state.editingLessonId = lessonId ? Number(lessonId) : null;

      if (lessonModuleIdInput) {
        lessonModuleIdInput.value = module.id;
      }

      if (lessonPositionInput) {
        lessonPositionInput.dataset.autofill = lessonId ? 'false' : 'true';
      }

      if (lessonId && lessonIdInput) {
        lessonIdInput.value = lessonId;
      } else if (lessonIdInput) {
        lessonIdInput.value = '';
      }

      if (lessonId) {
        const lesson = findLesson(module.id, lessonId);
        if (!lesson) {
          showAlert('Could not find that lesson.', 'danger');
          return;
        }
        if (lessonModalLabel) {
          lessonModalLabel.textContent = `Edit lesson – ${module.title || 'Module'}`;
        }
        if (lessonFormSubmit) {
          lessonFormSubmit.textContent = 'Save changes';
        }
        if (lessonTitleInput) {
          lessonTitleInput.value = lesson.title || '';
        }
        if (lessonContentInput) {
          lessonContentInput.value = lesson.content || '';
        }
        if (lessonPositionInput) {
          lessonPositionInput.value = Number.isFinite(lesson.position) ? lesson.position : 0;
        }
        if (lessonDurationInput) {
          lessonDurationInput.value =
            lesson.duration_minutes !== null && lesson.duration_minutes !== undefined
              ? lesson.duration_minutes
              : '';
        }
        if (lessonResourceInput) {
          lessonResourceInput.value = lesson.resource_url || '';
        }
      } else {
        if (lessonModalLabel) {
          lessonModalLabel.textContent = `Add lesson to "${module.title || 'Module'}"`;
        }
        if (lessonFormSubmit) {
          lessonFormSubmit.textContent = 'Add lesson';
        }
        if (lessonPositionInput) {
          const lessonCount = Array.isArray(module.lessons) ? module.lessons.length : 0;
          lessonPositionInput.value = lessonCount;
        }
        if (lessonDurationInput) {
          lessonDurationInput.value = '';
        }
        if (lessonResourceInput) {
          lessonResourceInput.value = '';
        }
      }

      if (lessonModal) {
        lessonModal.show();
      } else {
        showAlert('Lesson modal is unavailable. Please refresh the page.', 'danger');
      }
    };

    const handleModuleDelete = async (moduleId) => {
      const module = findModuleById(moduleId);
      if (!module) {
        showAlert('Could not find that module.', 'danger');
        return;
      }
      const confirmed = window.confirm(`Delete the module "${module.title}" and all of its lessons?`);
      if (!confirmed) {
        return;
      }
      try {
        await apiRequest(`/api/learning-paths/modules/${moduleId}`, { method: 'DELETE' });
        showAlert('Module deleted successfully.', 'success');
        await fetchModules(state.activeCourseId);
        resetModuleForm();
      } catch (error) {
        showAlert(error && error.message ? error.message : 'Unable to delete the module.', 'danger');
      }
    };

    const handleLessonDelete = async (moduleId, lessonId) => {
      const lesson = findLesson(moduleId, lessonId);
      if (!lesson) {
        showAlert('Could not find that lesson.', 'danger');
        return;
      }
      const confirmed = window.confirm(`Delete the lesson "${lesson.title}"?`);
      if (!confirmed) {
        return;
      }
      try {
        await apiRequest(`/api/learning-paths/lessons/${lessonId}`, { method: 'DELETE' });
        showAlert('Lesson deleted successfully.', 'success');
        await fetchModules(state.activeCourseId);
      } catch (error) {
        showAlert(error && error.message ? error.message : 'Unable to delete the lesson.', 'danger');
      }
    };

    if (modulePositionInput) {
      modulePositionInput.addEventListener('input', () => {
        modulePositionInput.dataset.autofill = 'false';
      });
    }

    if (lessonPositionInput) {
      lessonPositionInput.addEventListener('input', () => {
        lessonPositionInput.dataset.autofill = 'false';
      });
    }

    if (courseSelect) {
      courseSelect.addEventListener('change', (event) => {
        const value = event.target.value;
        const numericId = Number.parseInt(value, 10);
        if (Number.isNaN(numericId)) {
          state.activeCourseId = null;
          state.modules = [];
          updateQueryParam('course_id', null);
          resetModuleForm();
          renderModules();
          updateModuleFormState();
          return;
        }
        state.activeCourseId = numericId;
        modulesContainer.dataset.courseId = String(numericId);
        state.modules = [];
        renderModules();
        resetModuleForm();
        updateModuleFormState();
        updateQueryParam('course_id', numericId);
        fetchModules(numericId);
      });
    }

    if (moduleForm) {
      moduleForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        event.stopPropagation();

        if (!moduleForm.checkValidity()) {
          moduleForm.classList.add('was-validated');
          return;
        }

        moduleForm.classList.remove('was-validated');

        if (!Number.isInteger(state.activeCourseId)) {
          showAlert('Select a course before adding modules.', 'warning');
          return;
        }

        const title = moduleTitleInput ? moduleTitleInput.value.trim() : '';
        if (!title) {
          setModuleFormMessage('Please provide a module title.');
          moduleTitleInput && moduleTitleInput.focus();
          return;
        }

        const description = moduleDescriptionInput ? moduleDescriptionInput.value.trim() : '';
        const positionRaw = modulePositionInput ? Number.parseInt(modulePositionInput.value, 10) : 0;
        const position = Number.isNaN(positionRaw) ? 0 : positionRaw;

        const payload = {
          title,
          description: description || null,
          position,
        };

        let succeeded = false;
        try {
          setModuleFormMessage(null);
          moduleFormCancel && (moduleFormCancel.disabled = true);
          setButtonLoading(moduleFormSubmit, true, state.editingModuleId ? 'Saving' : 'Creating');

          if (state.editingModuleId) {
            await apiRequest(`/api/learning-paths/modules/${state.editingModuleId}`, {
              method: 'PATCH',
              body: payload,
            });
            showAlert('Module updated successfully.', 'success');
          } else {
            await apiRequest(`/api/learning-paths/courses/${state.activeCourseId}/modules`, {
              method: 'POST',
              body: payload,
            });
            showAlert('Module created successfully.', 'success');
          }

          succeeded = true;
        } catch (error) {
          const message = error && error.message ? error.message : 'Unable to save the module.';
          setModuleFormMessage(message);
        } finally {
          setButtonLoading(moduleFormSubmit, false);
          moduleFormCancel && (moduleFormCancel.disabled = false);
        }

        if (succeeded) {
          await fetchModules(state.activeCourseId);
          resetModuleForm();
        }
      });
    }

    if (moduleFormCancel) {
      moduleFormCancel.addEventListener('click', () => {
        resetModuleForm();
      });
    }

    modulesContainer.addEventListener('click', (event) => {
      const actionButton = event.target.closest('button[data-action]');
      if (!actionButton) {
        return;
      }
      const action = actionButton.dataset.action;
      const moduleId = Number.parseInt(actionButton.dataset.moduleId || '', 10);
      const lessonId = actionButton.dataset.lessonId
        ? Number.parseInt(actionButton.dataset.lessonId, 10)
        : null;

      if (!Number.isInteger(moduleId)) {
        return;
      }

      switch (action) {
        case 'edit-module':
          startModuleEdit(moduleId);
          break;
        case 'delete-module':
          handleModuleDelete(moduleId);
          break;
        case 'add-lesson':
          openLessonModal(moduleId);
          break;
        case 'edit-lesson':
          if (Number.isInteger(lessonId)) {
            openLessonModal(moduleId, lessonId);
          }
          break;
        case 'delete-lesson':
          if (Number.isInteger(lessonId)) {
            handleLessonDelete(moduleId, lessonId);
          }
          break;
        default:
          break;
      }
    });

    if (lessonModalElement) {
      lessonModalElement.addEventListener('hidden.bs.modal', () => {
        state.editingLessonId = null;
        lessonForm && lessonForm.reset();
        setLessonFormMessage(null);
      });
    }

    if (lessonForm) {
      lessonForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        event.stopPropagation();

        if (!lessonForm.checkValidity()) {
          lessonForm.classList.add('was-validated');
          return;
        }

        lessonForm.classList.remove('was-validated');

        if (!Number.isInteger(state.activeCourseId)) {
          showAlert('Select a course before managing lessons.', 'warning');
          return;
        }

        const moduleId = lessonModuleIdInput ? Number.parseInt(lessonModuleIdInput.value, 10) : null;
        if (!Number.isInteger(moduleId)) {
          setLessonFormMessage('Missing module reference for this lesson.');
          return;
        }

        const title = lessonTitleInput ? lessonTitleInput.value.trim() : '';
        if (!title) {
          setLessonFormMessage('Please provide a lesson title.');
          lessonTitleInput && lessonTitleInput.focus();
          return;
        }

        const content = lessonContentInput ? lessonContentInput.value.trim() : '';
        const positionRaw = lessonPositionInput ? Number.parseInt(lessonPositionInput.value, 10) : 0;
        const durationRaw = lessonDurationInput ? Number.parseInt(lessonDurationInput.value, 10) : NaN;
        const resource = lessonResourceInput ? lessonResourceInput.value.trim() : '';

        const payload = {
          title,
          content: content || null,
          position: Number.isNaN(positionRaw) ? 0 : positionRaw,
          duration_minutes: Number.isNaN(durationRaw) ? null : durationRaw,
          resource_url: resource || null,
        };

        try {
          setLessonFormMessage(null);
          setButtonLoading(lessonFormSubmit, true, state.editingLessonId ? 'Saving' : 'Creating');

          if (state.editingLessonId) {
            await apiRequest(`/api/learning-paths/lessons/${state.editingLessonId}`, {
              method: 'PATCH',
              body: payload,
            });
            showAlert('Lesson updated successfully.', 'success');
          } else {
            await apiRequest(`/api/learning-paths/modules/${moduleId}/lessons`, {
              method: 'POST',
              body: payload,
            });
            showAlert('Lesson added successfully.', 'success');
          }

          if (lessonModal) {
            lessonModal.hide();
          }

          await fetchModules(state.activeCourseId);
        } catch (error) {
          const message = error && error.message ? error.message : 'Unable to save the lesson.';
          setLessonFormMessage(message);
        } finally {
          setButtonLoading(lessonFormSubmit, false);
        }
      });
    }

    const initialCourseId = modulesContainer.dataset.courseId
      ? Number.parseInt(modulesContainer.dataset.courseId, 10)
      : courseSelect && courseSelect.value
      ? Number.parseInt(courseSelect.value, 10)
      : null;

    if (Number.isInteger(initialCourseId)) {
      state.activeCourseId = initialCourseId;
      if (courseSelect) {
        courseSelect.value = String(initialCourseId);
      }
      fetchModules(initialCourseId);
    } else {
      state.activeCourseId = null;
      renderModules();
      updateModuleFormState();
    }

    updateModuleFormState();
  });
})();
