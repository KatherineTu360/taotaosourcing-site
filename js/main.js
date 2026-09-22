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


// Shared consent-gated inquiry integration. Kept separate from product-page generation.
import('./b2b-client.mjs?v=20260922-b2b3').then(async ({mountTracking,mountConsent,formContext,sendInquiry,mountChallenge})=>{
  const tracker=mountTracking('taotao_sourcing');mountConsent(tracker);
  const preferences=document.createElement('button');preferences.type='button';preferences.textContent='Privacy choices';preferences.className='tt-privacy-settings';preferences.onclick=()=>window.dispatchEvent(new Event('taotao:open-analytics-preferences'));(document.querySelector('footer')||document.body).append(preferences);
  document.querySelectorAll('a[href*="contact.html"]').forEach(link=>{
    const url=new URL(link.href,location.href);if(url.origin!==location.origin)return;
    url.searchParams.set('from',location.pathname);
    if(location.pathname.startsWith('/product-')){const product=document.querySelector('h1')?.textContent.trim();if(product&&!url.searchParams.has('product'))url.searchParams.set('product',product.slice(0,160));const modelRow=Array.from(document.querySelectorAll('.spec-table tr')).find(row=>/Model/.test(row.querySelector('th')?.textContent||''));const model=modelRow?.querySelector('td')?.textContent.trim();if(model)url.searchParams.set('model',model.slice(0,100));}
    link.href=url.href;
  });
  const form=document.getElementById('inquiryForm');if(!form)return;
  const context=formContext(),query=new URLSearchParams(location.search);
  const status=document.getElementById('inquiryStatus'),button=form.querySelector('button[type="submit"]');
  form.elements.product.value=context.product;form.elements.model.value=context.model;
  if(context.product)form.elements.interest.value='Product catalog item / model';
  const endpoint=location.hostname==='localhost'||location.hostname==='127.0.0.1'?'http://localhost:4178/api/inquiries':'https://www.taotaotrading.com/api/inquiries';
  let busy=false,challenge={token:()=>'',reset:()=>{}};
  try{const response=await fetch(endpoint+'/config',{credentials:'omit'});const config=await response.json();button.disabled=!config.enabled;status.textContent=config.enabled?(config.test_mode?'TEST environment — no production conversion uploads.':''):'Online inquiry receipt is not enabled yet. Use the direct contact links.';if(config.enabled)challenge=await mountChallenge(config,document.getElementById('inquiryChallenge'));}catch{status.textContent='Online receipt is unavailable. Use the direct contact links or retry later.';}
  form.addEventListener('submit',async event=>{
    event.preventDefault();if(busy)return;busy=true;button.disabled=true;button.textContent='Sending…';status.textContent='Sending your sourcing request…';
    const fields=Object.fromEntries(new FormData(form));fields.product=fields.product||fields.interest;delete fields.interest;fields.origin_page=query.get('from')||context.page;fields.cta_id=context.cta_id;
    try{const result=await sendInquiry(endpoint,'taotao_sourcing','sourcing_inquiry',fields,tracker,challenge.token());status.textContent='Request received. Reference: '+result.lead_id+'. Katherine can now review your requirements.';}
    catch(error){status.textContent=error.message||'We could not confirm receipt. Retry with the same details.';challenge.reset();}
    finally{busy=false;button.disabled=false;button.textContent='Request a sourcing assessment';}
  });
}).catch(()=>{const status=document.getElementById('inquiryStatus');if(status)status.textContent='Online form could not load. Please use the direct contact links.';});
