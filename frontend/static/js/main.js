// Copyright year fallback
document.addEventListener('DOMContentLoaded', () => {
    const yearElement = document.getElementById('currentYear');
    if (yearElement && !yearElement.textContent.trim()) {
        yearElement.textContent = new Date().getFullYear();
    }
});