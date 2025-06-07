document.addEventListener('DOMContentLoaded', () => {
    const banner = document.getElementById('cookie-consent');
    if (!banner) return;
    if (!localStorage.getItem('cookie_consent')) {
        banner.style.display = 'block';
    }
    const btn = document.getElementById('cookie-consent-accept');
    if (btn) {
        btn.addEventListener('click', () => {
            localStorage.setItem('cookie_consent', 'true');
            banner.remove();
        });
    }
});
