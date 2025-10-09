function formatLessonDuration(minutes) {
  if (!minutes && minutes !== 0) return '';
  if (minutes < 60) {
    return `${minutes} mins`;
  }
  const hours = Math.floor(minutes / 60);
  const remaining = minutes % 60;
  return `${hours} hr${hours > 1 ? 's' : ''}${remaining ? ` ${remaining} mins` : ''}`;
}

async function loadCourseLearningPath() {
  const container = document.getElementById('learningPathContainer');
  if (!container) return;
  const emptyState = document.getElementById('learningPathEmpty');
  const courseId = container.dataset.courseId;
  if (!courseId) return;

  try {
    const response = await fetch(`/api/learning-paths/courses/${courseId}`);
    if (!response.ok) {
      throw new Error('Unable to load the learning path at the moment.');
    }
    const modules = await response.json();

    container.innerHTML = '';

    if (!Array.isArray(modules) || !modules.length) {
      container.classList.add('d-none');
      emptyState?.classList.remove('d-none');
      return;
    }

    modules.forEach((module, index) => {
      const lessons = Array.isArray(module.lessons) ? module.lessons : [];
      const moduleCard = document.createElement('article');
      moduleCard.className = 'card shadow-sm border-0';
      moduleCard.innerHTML = `
        <div class="card-body p-4">
          <div class="d-flex justify-content-between align-items-start flex-wrap gap-2 mb-3">
            <div>
              <h4 class="h5 mb-1">Module ${index + 1}: ${module.title}</h4>
              <p class="text-muted mb-0">${module.description || 'No description available yet.'}</p>
            </div>
            <span class="badge rounded-pill text-bg-primary">${lessons.length} lesson${lessons.length === 1 ? '' : 's'}</span>
          </div>
          <div class="list-group list-group-flush">
            ${lessons.map((lesson, lessonIndex) => `
              <div class="list-group-item px-0 py-3">
                <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
                  <div>
                    <p class="fw-semibold mb-1">${lessonIndex + 1}. ${lesson.title}</p>
                    <p class="text-muted mb-0 small">${lesson.content ? lesson.content.slice(0, 120) + (lesson.content.length > 120 ? '…' : '') : 'Lesson overview coming soon.'}</p>
                  </div>
                  <span class="badge text-bg-light">${formatLessonDuration(lesson.duration_minutes)}</span>
                </div>
              </div>
            `).join('') || '<div class="text-muted">Lessons for this module are coming soon.</div>'}
          </div>
        </div>
      `;
      container.appendChild(moduleCard);
    });
  } catch (error) {
    console.error('Learning path error', error);
    container.innerHTML = `<div class="alert alert-danger" role="alert">${error.message || 'Unable to load the curriculum right now.'}</div>`;
  }
}

document.addEventListener('DOMContentLoaded', loadCourseLearningPath);
