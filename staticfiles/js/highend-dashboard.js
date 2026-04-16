// High-End IndusVision Dashboard JS Utils
// SSE, GSAP, Theme, Toasts, Utils

// GSAP
gsap.registerPlugin(TextPlugin);

// Theme Toggle
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  const newTheme = current === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  showToast(`Theme switched to ${newTheme}`, 'success');
}

// Init Theme
function initTheme() {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
}

// Toast System
function showToast(message, type = 'info') {
  const colors = { success: 'bg-success', error: 'bg-danger', info: 'bg-info', warning: 'bg-warning' };
  const toastHtml = `
    <div class="toast align-items-center text-white ${colors[type] || 'bg-primary'} border-0" role="alert">
      <div class="d-flex">
        <div class="toast-body">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>
  `;
  const container = document.getElementById('toast-container') || createToastContainer();
  container.insertAdjacentHTML('beforeend', toastHtml);
  const toastEl = container.lastElementChild;
  const toast = new bootstrap.Toast(toastEl);
  toast.show();
  toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

function createToastContainer() {
  const container = document.createElement('div');
  container.id = 'toast-container';
  container.className = 'toast-container position-fixed end-0 p-3';
  document.body.appendChild(container);
  return container;
}

// SSE Client
function connectSSE(url, callback) {
  const eventSource = new EventSource(url);
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    callback(data);
  };
  eventSource.onerror = (err) => {
    console.error('SSE Error:', err);
    showToast('Connection lost, reconnecting...', 'warning');
  };
  return eventSource;
}

// GSAP Animations on Load
function animateOnLoad() {
  gsap.from('.gsap-fade-in', {
    duration: 0.8,
    y: 30,
    opacity: 0,
    stagger: 0.1,
    ease: 'power2.out'
  });
  gsap.from('.gsap-scale-up', {
    duration: 0.6,
    scale: 0.8,
    opacity: 0,
    stagger: 0.05
  });
}

// Skeleton to Content
function replaceSkeleton(containerSelector) {
  gsap.to(`${containerSelector} .skeleton`, {
    duration: 0.5,
    scaleX: 0,
    opacity: 0,
    stagger: 0.1,
    ease: 'power2.out',
    onComplete: () => {
      document.querySelectorAll(`${containerSelector} .skeleton`).forEach(el => el.remove());
    }
  });
}

// Utils
function debounce(fn, ms) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), ms);
  };
}

// Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
  if (e.key === '/') {
    e.preventDefault();
    const search = document.querySelector('input[type="search"], input[placeholder*="search"]');
    if (search) search.focus();
  }
  if (e.key === 't' && e.ctrlKey) toggleTheme();
});

// Init on DOM Load
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  animateOnLoad();
  if (document.querySelector('.theme-toggle')) {
    document.querySelector('.theme-toggle').addEventListener('click', toggleTheme);
  }
});

// Export
window.IndusVisionUtils = {
  toggleTheme,
  showToast,
  connectSSE,
  animateOnLoad,
  replaceSkeleton,
  debounce
};
