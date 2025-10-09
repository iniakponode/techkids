const lessonStatusLabels = {
  not_started: { label: 'Not started', variant: 'outline-secondary' },
  in_progress: { label: 'In progress', variant: 'outline-primary' },
  completed: { label: 'Completed', variant: 'success' }
};

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  });

  if (!response.ok) {
    if (response.status === 401) {
      window.location.assign(`/login?next=${encodeURIComponent(window.location.pathname)}`);
      return null;
    }
    const error = await response.json().catch(() => ({}));
    const detail = error.detail || 'Unable to complete the request.';
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }

  if (response.status === 204) {
    return null;
  }
  return response.json();
}

function formatCurrency(amount, currency = 'NGN') {
  try {
    return new Intl.NumberFormat('en-NG', { style: 'currency', currency }).format(amount);
  } catch (error) {
    return `${currency} ${amount.toFixed(2)}`;
  }
}

function formatDate(value) {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function buildCourseCard(course, registrationId) {
  const progress = course.progress || { completion_percentage: 0, modules: [] };
  const completion = Math.round(progress.completion_percentage || 0);
  const outstandingBadge = course.outstanding_balance > 0
    ? `<span class="badge bg-warning text-dark ms-2">₦${course.outstanding_balance.toLocaleString()} due</span>`
    : '';

  const courseImage = course.course_image_url || '/static/images/hero1.png';
  const courseSummary = course.course_summary || 'Start your learning journey and keep track of each lesson as you go.';

  const modules = Array.isArray(progress.modules) ? progress.modules : [];

  const lessonsMarkup = modules.map((module, moduleIndex) => {
    const moduleLessons = (Array.isArray(module.lessons) ? module.lessons : []).map(lesson => {
      const status = lessonStatusLabels[lesson.status] || lessonStatusLabels.not_started;
      const completedBadge = lesson.completed_at
        ? `<span class="badge bg-success-subtle text-success ms-2">Completed ${formatDate(lesson.completed_at)}</span>`
        : '';

      return `
        <div class="lesson-row d-flex flex-column flex-lg-row gap-3 align-items-lg-center">
          <div class="flex-grow-1">
            <button class="btn btn-link text-start p-0 lesson-content-trigger" data-lesson-title="${lesson.title.replace(/"/g, '&quot;')}" data-lesson-content="${(lesson.content || '').replace(/"/g, '&quot;')}" data-resource-url="${lesson.resource_url || ''}">
              <span class="fw-semibold">${lesson.title}</span>
            </button>
            <div class="small text-muted">${lesson.duration_minutes ? `${lesson.duration_minutes} mins • ` : ''}Lesson ${lesson.position + 1}</div>
            ${completedBadge}
          </div>
          <div class="lesson-controls btn-group btn-group-sm" role="group">
            ${Object.entries(lessonStatusLabels).map(([statusKey, meta]) => `
              <button
                type="button"
                class="btn btn-${meta.variant} ${lesson.status === statusKey ? 'active' : ''}"
                data-registration-id="${registrationId}"
                data-lesson-id="${lesson.id}"
                data-status="${statusKey}"
              >${meta.label}</button>
            `).join('')}
          </div>
        </div>
      `;
    }).join('');

    return `
      <div class="module-item">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <div>
            <h4 class="h5 mb-1">Module ${moduleIndex + 1}: ${module.title}</h4>
            <p class="text-muted mb-0">${module.description || ''}</p>
          </div>
        </div>
        <div class="d-grid gap-3">
          ${moduleLessons}
        </div>
      </div>
    `;
  }).join('');

  return `
    <article class="course-card">
      <div class="course-card-header">
        <div class="d-flex flex-column flex-lg-row gap-3 align-items-lg-center">
          <img src="${courseImage}" alt="${course.course_title}" class="rounded-4 flex-shrink-0" style="width: 96px; height: 96px; object-fit: cover;">
          <div class="flex-grow-1">
            <div class="d-flex align-items-center gap-2 mb-1">
              <h3 class="h4 mb-0">${course.course_title}</h3>
              ${outstandingBadge}
            </div>
            <p class="course-meta mb-2">Registered ${formatDate(course.registered_at)} • ${course.status || 'pending'}</p>
            <p class="mb-0 text-muted">${courseSummary}</p>
          </div>
          <div class="text-lg-end">
            <span class="badge badge-soft rounded-pill px-3 py-2">${completion}% complete</span>
            <div class="progress mt-3" role="progressbar" aria-valuenow="${completion}" aria-valuemin="0" aria-valuemax="100">
              <div class="progress-bar bg-gradient" style="width: ${completion}%;"></div>
            </div>
            ${course.order_id ? `<a class="d-inline-flex align-items-center gap-2 small mt-3" href="/payment?order=${course.order_id}"><i class="bi bi-receipt"></i> View order</a>` : ''}
          </div>
        </div>
      </div>
      <div class="course-card-body">
        ${lessonsMarkup || '<p class="text-muted mb-0">No lessons have been published for this course yet.</p>'}
      </div>
    </article>
  `;
}

function renderCourses(dashboard) {
  const coursesContainer = document.getElementById('coursesContainer');
  const emptyState = document.getElementById('coursesEmptyState');
  if (!coursesContainer || !emptyState) return;

  coursesContainer.innerHTML = '';

  if (!dashboard.courses.length) {
    emptyState.classList.remove('d-none');
    coursesContainer.appendChild(emptyState);
    return;
  }

  emptyState.classList.add('d-none');
  dashboard.courses.forEach(course => {
    const wrapper = document.createElement('div');
    wrapper.innerHTML = buildCourseCard(course, course.registration_id);
    coursesContainer.appendChild(wrapper.firstElementChild);
  });
}

function renderSummary(dashboard) {
  const greetingEl = document.getElementById('dashboardGreeting');
  const subtextEl = document.getElementById('dashboardSubtext');
  const totalEl = document.getElementById('totalCourses');
  const activeEl = document.getElementById('activeCourses');
  const completedEl = document.getElementById('completedCourses');
  const lastActiveEl = document.getElementById('lastActiveText');

  if (greetingEl) {
    const name = dashboard.display_name || dashboard.student_email;
    greetingEl.textContent = `Hi ${name?.split(' ')[0] || 'there'}!`;
  }
  if (subtextEl) {
    subtextEl.textContent = `You're enrolled in ${dashboard.total_courses} ${dashboard.total_courses === 1 ? 'course' : 'courses'}.`;
  }
  if (totalEl) totalEl.textContent = dashboard.total_courses;
  if (activeEl) activeEl.textContent = dashboard.active_courses;
  if (completedEl) completedEl.textContent = dashboard.completed_courses;
  if (lastActiveEl) lastActiveEl.textContent = dashboard.latest_activity_at ? formatDate(dashboard.latest_activity_at) : 'No activity yet';
}

function renderReceipts(receipts) {
  const receiptsBody = document.getElementById('receiptsBody');
  const wrapper = document.getElementById('receiptsWrapper');
  const empty = document.getElementById('receiptsEmptyState');

  if (!receiptsBody || !wrapper || !empty) return;

  receiptsBody.innerHTML = '';

  if (!receipts.length) {
    wrapper.classList.add('d-none');
    empty.classList.remove('d-none');
    return;
  }

  wrapper.classList.remove('d-none');
  empty.classList.add('d-none');

  receipts.forEach(receipt => {
    const coursesList = receipt.line_items.map(item => item.title).join(', ');
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>
        <span class="badge bg-dark-subtle text-dark-emphasis receipt-pill">${receipt.receipt_number}</span>
      </td>
      <td>${formatDate(receipt.payment_date)}</td>
      <td>${coursesList || '—'}</td>
      <td>${formatCurrency(receipt.amount, receipt.currency)}</td>
      <td class="text-end">
        <button class="btn btn-outline-secondary btn-sm" data-receipt-json='${encodeURIComponent(JSON.stringify(receipt))}'>Download</button>
      </td>
    `;
    receiptsBody.appendChild(tr);
  });
}

function downloadReceipt(receipt) {
  const lines = receipt.line_items.map(item => ` - ${item.title}${item.price ? ` (${formatCurrency(item.price, receipt.currency)})` : ''}`).join('\n');
  const blob = new Blob([
    `TechKids Payment Receipt\n\nReceipt: ${receipt.receipt_number}\nDate: ${formatDate(receipt.payment_date)}\nAmount: ${formatCurrency(receipt.amount, receipt.currency)}\nOrder ID: ${receipt.order_id}\nPayment ID: ${receipt.payment_id}\n\nCourses:\n${lines || 'No course lines available.'}\n\nThank you for learning with TechKids!`
  ], { type: 'text/plain;charset=utf-8' });

  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${receipt.receipt_number}.txt`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function attachEventListeners() {
  document.addEventListener('click', async (event) => {
    const target = event.target;

    if (target.matches('[data-receipt-json]')) {
      const encoded = target.getAttribute('data-receipt-json');
      const data = JSON.parse(decodeURIComponent(encoded));
      downloadReceipt(data);
    }

    if (target.matches('.lesson-controls .btn')) {
      const registrationId = target.getAttribute('data-registration-id');
      const lessonId = target.getAttribute('data-lesson-id');
      const status = target.getAttribute('data-status');
      if (!registrationId || !lessonId || !status) return;

      try {
        const updated = await fetchJson(`/api/learning-paths/registrations/${registrationId}/lessons/${lessonId}`, {
          method: 'PATCH',
          body: JSON.stringify({ status })
        });
        if (updated) {
          await loadDashboard();
        }
      } catch (error) {
        console.error('Unable to update lesson status', error);
        alert(error.message || 'Unable to update lesson status.');
      }
    }

    if (target.closest('.lesson-content-trigger')) {
      const trigger = target.closest('.lesson-content-trigger');
      const title = trigger.getAttribute('data-lesson-title') || 'Lesson content';
      const content = trigger.getAttribute('data-lesson-content') || 'No description provided yet.';
      const resource = trigger.getAttribute('data-resource-url');

      const modalBody = document.getElementById('lessonContentBody');
      const modalTitle = document.getElementById('lessonContentLabel');
      if (modalBody && modalTitle) {
        modalTitle.textContent = title;
        modalBody.innerHTML = `
          <div class="d-grid gap-3">
            <div>${content || 'No description provided yet.'}</div>
            ${resource ? `<a href="${resource}" class="btn btn-outline-primary" target="_blank" rel="noopener">Open resource</a>` : ''}
          </div>
        `;
      }

      const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('lessonContentModal'));
      modal.show();
    }
  });
}

async function loadDashboard() {
  try {
    const [dashboard, receipts] = await Promise.all([
      fetchJson('/api/students/dashboard'),
      fetchJson('/api/students/receipts')
    ]);
    if (!dashboard) return;

    renderSummary(dashboard);
    renderCourses(dashboard);
    renderReceipts(receipts || []);
  } catch (error) {
    console.error('Failed to load dashboard', error);
    const container = document.getElementById('coursesContainer');
    if (container) {
      container.innerHTML = `<div class="alert alert-danger" role="alert">${error.message || 'Unable to load your dashboard at the moment.'}</div>`;
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  attachEventListeners();
  loadDashboard();
});
