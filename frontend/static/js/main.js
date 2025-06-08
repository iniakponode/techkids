// Copyright year fallback
document.addEventListener('DOMContentLoaded', () => {
    const yearElement = document.getElementById('currentYear');
    if (yearElement && !yearElement.textContent.trim()) {
        yearElement.textContent = new Date().getFullYear();
    }

    // Fade-in sections when they appear
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.fade-section').forEach(sec => observer.observe(sec));
});