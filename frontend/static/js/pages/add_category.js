document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('addCategoryForm');
  const btn = document.getElementById('addCategoryBtn');
  if(!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    btn.innerHTML = 'Adding... <span class="spinner-border spinner-border-sm" role="status"></span>';
    const formData = new FormData(form);
    try {
      const res = await fetch('/api/categories/', {
        method: 'POST',
        body: JSON.stringify(Object.fromEntries(formData)),
        headers: {'Content-Type': 'application/json'}
      });
      if(!res.ok) throw new Error('Failed');
      form.reset();
      btn.innerHTML = 'Add Category';
      const alert = document.createElement('div');
      alert.className = 'alert alert-success mt-3';
      alert.textContent = 'Category added';
      form.prepend(alert);
    } catch(err) {
      btn.innerHTML = 'Add Category';
      const alert = document.createElement('div');
      alert.className = 'alert alert-danger mt-3';
      alert.textContent = 'Error adding category';
      form.prepend(alert);
    }
  });
});
