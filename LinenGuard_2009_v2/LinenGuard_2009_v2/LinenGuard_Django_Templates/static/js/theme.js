/**
 * LINOVA / LinenGuard - Universal Dark & Light Theme Controller
 * Single source of truth for global theme switching across all workspaces:
 * - Supervisor Console
 * - Attendant Hub & Field Ops
 * - Laundry Processing Station
 * - Executive Dashboard, Inventory & Reports
 * - Authentication Portal
 */

(function () {
  'use strict';

  // Retrieve stored theme or default to 'dark' for sleek railway instrumentation aesthetics
  function getPreferredTheme() {
    try {
      const stored = localStorage.getItem('linenguard_theme');
      if (stored === 'dark' || stored === 'light') {
        return stored;
      }
    } catch (e) {
      console.warn('LocalStorage access blocked:', e);
    }
    return 'dark';
  }

  function applyTheme(theme) {
    const targetTheme = (theme === 'light') ? 'light' : 'dark';
    
    // Set on both <html> and <body> for maximum CSS compatibility
    document.documentElement.setAttribute('data-theme', targetTheme);
    if (document.body) {
      document.body.setAttribute('data-theme', targetTheme);
      document.body.classList.remove('theme-dark', 'theme-light');
      document.body.classList.add('theme-' + targetTheme);
    }

    try {
      localStorage.setItem('linenguard_theme', targetTheme);
    } catch (e) {
      // Ignore private browsing quota issues
    }

    updateToggleButtons(targetTheme);

    // Dispatch event so charts or widgets can redraw if needed
    try {
      window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: targetTheme } }));
    } catch (e) {}
  }

  function updateToggleButtons(theme) {
    const isDark = theme === 'dark';
    const buttons = document.querySelectorAll('.theme-toggle-btn');
    
    buttons.forEach((btn) => {
      btn.setAttribute('aria-label', isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode');
      btn.setAttribute('title', isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode');
      
      const icon = btn.querySelector('.theme-toggle-icon');
      const text = btn.querySelector('.theme-toggle-text');
      
      if (icon) {
        icon.className = isDark ? 'bi bi-sun-fill text-warning theme-toggle-icon' : 'bi bi-moon-stars-fill text-primary theme-toggle-icon';
      }
      if (text) {
        text.textContent = isDark ? 'Light' : 'Dark';
      }
    });
  }

  window.toggleTheme = function () {
    const current = document.documentElement.getAttribute('data-theme') || getPreferredTheme();
    const next = (current === 'dark') ? 'light' : 'dark';
    applyTheme(next);
    return next;
  };

  window.setTheme = function (theme) {
    if (theme === 'dark' || theme === 'light') {
      applyTheme(theme);
    }
  };

  // Immediate execution to prevent FOUC (Flash of Unstyled Content)
  const initialTheme = getPreferredTheme();
  document.documentElement.setAttribute('data-theme', initialTheme);

  function attachListeners() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || initialTheme;
    if (document.body) {
      document.body.setAttribute('data-theme', currentTheme);
      document.body.classList.add('theme-' + currentTheme);
    }
    updateToggleButtons(currentTheme);

    // Attach click listeners to all toggle buttons for reliable triggering
    document.querySelectorAll('.theme-toggle-btn').forEach((btn) => {
      btn.onclick = function (e) {
        e.preventDefault();
        e.stopPropagation();
        window.toggleTheme();
      };
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attachListeners);
  } else {
    attachListeners();
  }
})();

