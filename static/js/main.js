// School Badge Website - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Like button animation
    const likeForms = document.querySelectorAll('form[action*="toggle_like"]');
    likeForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const button = this.querySelector('button');
            const originalText = button.innerHTML;
            
            // Visual feedback
            button.disabled = true;
            button.innerHTML = '⏳';
            
            setTimeout(() => {
                button.disabled = false;
            }, 500);
        });
    });

    console.log('校徽网 - School Badge Collection loaded successfully!');
});
