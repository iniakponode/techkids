document.addEventListener('DOMContentLoaded', async () => {
  const select = document.getElementById('category');
  if(!select) return;
  try {
    const res = await fetch('/api/categories/');
    const cats = await res.json();
    cats.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.name;
      opt.textContent = c.name;
      if(select.dataset.selected && select.dataset.selected === c.name) {
        opt.selected = true;
      }
      select.appendChild(opt);
    });
  } catch (e) {
    console.error('Failed to load categories', e);
  }
});
