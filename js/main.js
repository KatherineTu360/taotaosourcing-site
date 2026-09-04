// Taotao Trading — site behaviour

// Mobile menu toggle
const navToggle = document.getElementById('navToggle');
const mainNav = document.getElementById('mainNav');
if (navToggle && mainNav) {
  navToggle.addEventListener('click', () => {
    const open = mainNav.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  // Close the menu after tapping a link (mobile)
  mainNav.addEventListener('click', (e) => {
    if (e.target.tagName === 'A') {
      mainNav.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
    }
  });
}

// Inquiry form → WhatsApp with pre-filled message
// (no backend needed; nothing is stored server-side)
const form = document.getElementById('inquiryForm');
if (form) {
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const val = (id) => {
      const el = document.getElementById(id);
      return el ? el.value.trim() : '';
    };
    const parts = [
      'Hi Katherine,',
      '',
      `Name: ${val('name')}`,
      val('company') && `Company: ${val('company')}`,
      val('country') && `Country/Region: ${val('country')}`,
      val('interest') && `Interest: ${val('interest')}`,
      '',
      `Requirement: ${val('message')}`,
    ].filter(Boolean);
    const url = 'https://wa.me/8616626662274?text=' + encodeURIComponent(parts.join('\n'));
    window.open(url, '_blank', 'noopener');
  });
}
