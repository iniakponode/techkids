document.addEventListener('DOMContentLoaded', () => {
    // Initialize Bootstrap's navbar collapse functionality
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    if (navbarToggler && navbarCollapse) {
        // Close navbar when clicking outside
        document.addEventListener('click', (event) => {
            const isClickInside = navbarToggler.contains(event.target) || 
                                navbarCollapse.contains(event.target);
            
            if (!isClickInside && navbarCollapse.classList.contains('show')) {
                // Use Bootstrap's collapse API to hide the navbar
                bootstrap.Collapse.getInstance(navbarCollapse).hide();
            }
        });

        // Close navbar when window is resized to desktop size
        window.addEventListener('resize', () => {
            if (window.innerWidth > 992 && navbarCollapse.classList.contains('show')) {
                bootstrap.Collapse.getInstance(navbarCollapse).hide();
            }
        });
    }
});
