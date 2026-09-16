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

// Sourcing video library (index.html #sourcing-video)
const videoFrame = document.getElementById('videoFrame');
const videoPicker = document.getElementById('videoPicker');
if (videoFrame && videoPicker) {
  const facade = document.getElementById('videoFacade');
  const captionTitle = document.getElementById('videoCaptionTitle');
  const captionMeta = document.getElementById('videoCaptionMeta');
  const noteEl = document.getElementById('videoNote');
  const notes = {};
  videoPicker.querySelectorAll('button').forEach((btn) => {
    const note = btn.getAttribute('data-note');
    if (note) notes[btn.getAttribute('data-yt')] = note;
  });

  const embed = (yt) => {
    videoFrame.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + yt +
      '?autoplay=1&rel=0&playsinline=1" title="Katherine Tu sourcing video" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>';
  };

  const select = (btn) => {
    const yt = btn.getAttribute('data-yt');
    const title = btn.getAttribute('data-title');
    const dur = btn.getAttribute('duration');
    videoPicker.querySelectorAll('button').forEach((b) => {
      b.classList.toggle('active', b === btn);
      b.setAttribute('aria-pressed', b === btn ? 'true' : 'false');
    });
    captionTitle.textContent = title;
    captionMeta.innerHTML = dur + ' · <a href="https://www.youtube.com/watch?v=' + yt +
      '" target="_blank" rel="noreferrer">Watch on YouTube ↗</a> · ' +
      '<a href="https://www.youtube.com/@TuKatherine/videos" target="_blank" rel="noreferrer">View all videos ↗</a>';
    noteEl.textContent = notes[yt] || '';
    embed(yt);
  };

  facade.addEventListener('click', () => embed(facade.getAttribute('data-yt')));
  videoPicker.addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-yt]');
    if (btn) select(btn);
  });

  const search = document.getElementById('videoSearch');
  if (search) {
    search.addEventListener('input', () => {
      const q = search.value.trim().toLowerCase();
      videoPicker.querySelectorAll('button').forEach((btn) => {
        btn.hidden = q && !btn.getAttribute('data-title').toLowerCase().includes(q);
      });
    });
  }
}
