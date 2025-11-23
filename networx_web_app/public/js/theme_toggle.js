// Theme Toggle Logic
const ThemeManager = {
    init: () => {
        // Check local storage or system preference
        const savedTheme = localStorage.getItem('networx-theme');
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        if (savedTheme === 'dark' || (!savedTheme && systemDark)) {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
        }

        // Add toggle button listener if it exists
        const toggleBtn = document.getElementById('themeToggleBtn');
        if (toggleBtn) {
            ThemeManager.updateIcon(toggleBtn);
            toggleBtn.addEventListener('click', ThemeManager.toggle);
        }
    },

    toggle: () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('networx-theme', newTheme);

        const toggleBtn = document.getElementById('themeToggleBtn');
        if (toggleBtn) {
            ThemeManager.updateIcon(toggleBtn);
        }
    },

    updateIcon: (btn) => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const icon = btn.querySelector('i');
        if (icon) {
            if (currentTheme === 'dark') {
                icon.className = 'ri-sun-line text-xl';
            } else {
                icon.className = 'ri-moon-line text-xl';
            }
        }
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', ThemeManager.init);

// Also run immediately to prevent flash
(function () {
    const savedTheme = localStorage.getItem('networx-theme');
    const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (savedTheme === 'dark' || (!savedTheme && systemDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
})();
