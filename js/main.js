// Taotao Sourcing — site behaviour

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
  const query = new URLSearchParams(window.location.search);
  const requestedProduct = query.get('product');
  if (requestedProduct) {
    const interest = document.getElementById('interest');
    const message = document.getElementById('message');
    if (interest) interest.value = 'Product catalog item / model';
    if (message && !message.value) {
      message.value = `Product / model: ${requestedProduct}\nTarget market: \nEstimated quantity: \nRequired specifications or documents: `;
    }
  }
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
    const message = parts.join('\n');
    const channel = e.submitter && e.submitter.value;
    if (channel === 'email') {
      const subject = val('interest') ? `Sourcing inquiry: ${val('interest')}` : 'Sourcing inquiry';
      window.location.href = 'mailto:rabieternity@gmail.com?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(message);
      return;
    }
    const url = 'https://wa.me/8616626662274?text=' + encodeURIComponent(message);
    window.open(url, '_blank', 'noopener');
  });
}
