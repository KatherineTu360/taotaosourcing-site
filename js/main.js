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

// Inquiry form → structured lead pipeline + WhatsApp/email handoff.
// Journey tracking comes from js/b2b-client.mjs (shared with taotaotrading).
const INQUIRY_ENDPOINT = 'https://www.taotaotrading.com/api/inquiries';
const INQUIRY_CONFIG = 'https://www.taotaotrading.com/api/inquiries/config';

// Load the shared tracker once on every page; it is consent-gated and stores
// nothing until the buyer accepts optional measurement in the privacy panel.
import('./b2b-client.mjs').then(async (m) => {
  window.__ttB2B = m;
  const tracker = m.mountTracking('taotao_sourcing');
  window.__ttTracker = tracker;
  m.mountConsent(tracker);
  const box = document.getElementById('ttTurnstile');
  if (!box) return;
  try {
    const res = await fetch(INQUIRY_CONFIG, { signal: AbortSignal.timeout(8000) });
    const config = await res.json();
    if (config.enabled && config.turnstile_site_key && !config.test_mode) {
      window.__ttChallenge = await m.mountChallenge(config, box);
      window.__ttChallengeRequired = true;
    }
  } catch (e) { /* pipeline offline — forms fall back to direct channels */ }
}).catch(() => { /* tracking unavailable — form keeps working */ });

// Compact human-readable journey for the WhatsApp/email message, so the
// inquiry itself carries context even before the structured record is read.
function journeyText() {
  const tracker = window.__ttTracker;
  if (!tracker) return '';
  let snap;
  try { snap = tracker.snapshot(); } catch (e) { return ''; }
  if (!snap.consent.analytics && !snap.consent.ads) return '';
  const pages = [...new Set(snap.events.map((e) => e.page))].slice(0, 10);
  const ctas = {};
  snap.events.filter((e) => e.type === 'cta_click').forEach((e) => {
    const k = e.cta_name || e.cta_id || 'CTA';
    ctas[k] = (ctas[k] || 0) + 1;
  });
  const src = snap.first || {};
  const source = src.gclid ? 'Google Ads click'
    : src.utm_source ? 'Campaign: ' + src.utm_source
    : src.referrer_host ? 'Referral: ' + src.referrer_host
    : 'Direct visit';
  const mins = snap.events.length > 1
    ? Math.round((Date.parse(snap.events[snap.events.length - 1].at) - Date.parse(snap.events[0].at)) / 60000)
    : 0;
  const lines = [
    '',
    '--- Inquiry journey (auto-attached) ---',
    'First visit: ' + String(src.at || '').slice(0, 10) + (mins ? ' (' + mins + ' min on site)' : ''),
    'Source: ' + source,
    'Landing page: ' + (src.page || 'n/a'),
    'Pages viewed (' + pages.length + '): ' + pages.join(' -> '),
    Object.keys(ctas).length ? 'CTA clicks: ' + Object.entries(ctas).map(([k, v]) => '"' + k + '"' + (v > 1 ? ' x' + v : '')).join('; ') : '',
  ];
  return lines.filter(Boolean).join('\n');
}

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
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const val = (id) => {
      const el = document.getElementById(id);
      return el ? el.value.trim() : '';
    };
    const channel = e.submitter && e.submitter.value;
    const client = window.__ttB2B;
    // Structured receipt through the shared inquiry pipeline. If the pipeline
    // is disabled or unreachable, the WhatsApp/email fallback still carries
    // the full inquiry — nothing is lost.
    if (client && window.__ttTracker) {
      try {
        const fields = {
          name: val('name'),
          company: val('company'),
          contact: val('contact'),
          country: val('country'),
          product: val('interest'),
          message: val('message'),
          ...client.formContext(),
        };
        const token = window.__ttChallenge ? window.__ttChallenge.token() : '';
        await client.sendInquiry(INQUIRY_ENDPOINT, 'taotao_sourcing', 'contact_form', fields, window.__ttTracker, token);
      } catch (err) { /* receipt failed — direct channel below still works */ }
    }
    const parts = [
      'Hi Katherine,',
      '',
      `Name: ${val('name')}`,
      val('company') && `Company: ${val('company')}`,
      val('country') && `Country/Region: ${val('country')}`,
      val('contact') && `Contact: ${val('contact')}`,
      val('interest') && `Interest: ${val('interest')}`,
      '',
      `Requirement: ${val('message')}`,
      journeyText(),
    ].filter(Boolean);
    const message = parts.join('\n');
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
