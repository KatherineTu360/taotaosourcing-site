// Shared by both sites. No form values, URLs with queries, or full referrers enter analytics.
export const VERSION = 2;
const DAY = 86400000;
const PARAMS = ['utm_source','utm_medium','utm_campaign','utm_id','utm_content','utm_term','campaign_id','adgroup_id','creative_id','ad_keyword','matchtype','device','network'];
const CLICK_IDS = ['gclid','gbraid','wbraid'];
const id = () => crypto.randomUUID();
const clean = (v, n = 160) => String(v || '').replace(/[\x00-\x1f\x7f]/g, '').slice(0,n);
export function createTracker(w, siteId, now = Date.now) {
  const key = `tt:b2b:${siteId}:v2`, consentKey = `${key}:consent`;
  let memory = null, lastPath = '', lastClick = '', lastClickAt = 0;
  const read = (k) => { try { return JSON.parse(w.localStorage.getItem(k) || 'null'); } catch { return null; } };
  const write = (k,v) => { try { w.localStorage.setItem(k,JSON.stringify(v)); } catch { /* incomplete journey, form still works */ } };
  function consent() {
    const c = read(consentKey);
    return c && c.expires_at > now() ? c : { analytics:false, ads:false, at:null };
  }
  function changeConsent(analytics, ads) {
    const c = {analytics:!!analytics, ads:!!ads, at:new Date(now()).toISOString(), expires_at:now()+180*DAY, version:VERSION};
    write(consentKey,c);
    if (!analytics && !ads) { try { w.localStorage.removeItem(key); } catch {} memory=null; }
    else if (!ads) {
      const state=read(key);
      if (state) { state.ad_clicks=[]; for (const source of [state.first, state.session?.source]) if(source) for(const p of CLICK_IDS) delete source[p]; write(key,state); }
    }
    lastPath=''; lastClick=''; page();
    w.dispatchEvent(new w.CustomEvent('tt:consent', {detail:c}));
    return c;
  }
  function source() {
    const q=new URLSearchParams(w.location.search), c=consent();
    const s={at:new Date(now()).toISOString(),page:w.location.pathname.slice(0,300),referrer_host:'',kind:'direct_or_unknown'};
    try { const r=new URL(w.document.referrer); if(r.origin!==w.location.origin) {s.referrer_host=r.hostname;s.kind='referral';} } catch {}
    for(const p of PARAMS) if(q.get(p)) s[p]=clean(q.get(p));
    // keyword/keyword_id aliases are never described as actual search terms.
    if(q.get('keyword')) s.ad_keyword=clean(q.get('keyword'));
    if(c.ads) for(const p of CLICK_IDS) if(q.get(p)) s[p]=clean(q.get(p),256);
    if(PARAMS.some(p=>s[p]) || CLICK_IDS.some(p=>s[p])) s.kind='campaign';
    return s;
  }
  function state() {
    const c=consent(); if(!c.analytics && !c.ads) return null;
    let s=read(key)||memory;
    if(!s || s.expires_at<=now() || s.site_id!==siteId) s={version:VERSION,site_id:siteId,visitor_id:id(),first:source(),expires_at:now()+90*DAY,ad_clicks:[],events:[],truncated:false};
    if(!s.session || now()-s.session.last_at>30*60000) s.session={id:id(),source:source(),last_at:now()};
    const src=source(), signature=JSON.stringify([...CLICK_IDS,...PARAMS].map(p=>src[p]||''));
    if(src.kind==='campaign' && signature!==s.session.signature) {
      s.session.source=src;s.session.signature=signature;
      if(c.ads && CLICK_IDS.some(p=>src[p])) s.ad_clicks.push({...src,click_id:id()});
    }
    s.session.last_at=now();
    if(s.ad_clicks.length>20 || s.events.length>60) s.truncated=true;
    s.ad_clicks=s.ad_clicks.filter(v=>now()-Date.parse(v.at)<90*DAY).slice(-20);
    s.events=s.events.filter(v=>now()-Date.parse(v.at)<30*DAY).slice(-60);
    memory=s;return s;
  }
  function event(type, details={}) {
    const s=state();if(!s)return;
    s.events.push({event_id:id(),type,at:new Date(now()).toISOString(),page:w.location.pathname.slice(0,300),session_id:s.session.id,...details});
    if(s.events.length>60){s.events=s.events.slice(-60);s.truncated=true;}
    write(key,s);
  }
  function page() {
    const s=state();if(!s)return;
    if(lastPath!==w.location.pathname){lastPath=w.location.pathname;event('page_view');}else write(key,s);
  }
  function cta(ctaId,name,channel='form') {
    if(lastClick===ctaId && now()-lastClickAt<1000)return;
    lastClick=ctaId;lastClickAt=now();event('cta_click',{cta_id:clean(ctaId,100),cta_name:clean(name,100),channel});
  }
  function snapshot() {
    const c=consent(),s=state();
    if(!s)return {version:VERSION,site_id:siteId,consent:c,completeness:'unknown_consent_or_storage',events:[],ad_clicks:[]};
    write(key,s);
    return {...s,consent:c,session_id:s.session.id,current_session_source:s.session.source,events:s.events.map((e,i)=>({...e,sequence:i+1})),completeness:s.truncated?'bounded_history_truncated':'recorded_browser_only'};
  }
  return {consent,changeConsent,page,cta,event,snapshot};
}
const hash = s => {let h=2166136261;for(const c of s) h=Math.imul(h^c.charCodeAt(0),16777619);return (h>>>0).toString(36);};
export function mountTracking(siteId) {
  if(window.__ttTracker)return window.__ttTracker;
  const t=createTracker(window,siteId);window.__ttTracker=t;
  // Do not migrate the old, non-consented tracking history.
  for(const k of ['tt_lead_first_v1','tt_lead_trace_v1','tt_lead_cta_v1']) {try{localStorage.removeItem(k);sessionStorage.removeItem(k);}catch{}}
  const tag=()=>document.querySelectorAll('a[href],button[type="submit"]').forEach(el=>{
    const href=el.getAttribute('href')||'submit';
    if(!/contact|#quote|#sourcing-request|wa\.me|mailto:|tel:|submit/.test(href))return;
    const section=el.closest('section[id],header,footer,form');
    const slot=section?.id||section?.tagName.toLowerCase()||'page';
    if(!el.dataset.ctaId)el.dataset.ctaId=`${siteId}:${slot}:${hash(href.split('?')[0]+el.textContent.trim())}`;
    el.dataset.ctaName=el.dataset.ctaName||el.textContent.trim().slice(0,100)||el.getAttribute('aria-label')||'Contact';
  });
  document.addEventListener('click',e=>{
    tag();const el=e.target.closest?.('[data-cta-id]');if(!el)return;
    const href=el.getAttribute('href')||'';
    const channel=/wa\.me/.test(href)?'whatsapp':/^mailto:/.test(href)?'email':/^tel:/.test(href)?'phone':'form';
    t.cta(el.dataset.ctaId,el.dataset.ctaName,channel);
    // Only product context is retained as necessary form state. No visitor/ad identifier is linked across domains.
    if(channel==='form') try {sessionStorage.setItem('tt:inquiry-context',JSON.stringify({page:location.pathname,product:el.dataset.product||'',model:el.dataset.model||'',cta_id:el.dataset.ctaId}));}catch{}
  },true);
  for(const method of ['pushState','replaceState']) {
    const original=history[method];history[method]=function(...args){const result=original.apply(this,args);t.page();tag();return result;};
  }
  window.addEventListener('popstate',()=>{t.page();tag();});
  window.addEventListener('storage',e=>{if(e.key?.endsWith(':consent'))window.dispatchEvent(new CustomEvent('tt:consent',{detail:t.consent()}));});
  t.page();tag();return t;
}
export function mountConsent(t) {
  let panel;
  const show=()=>{
    if(panel)return;
    panel=document.createElement('aside');panel.className='tt-consent';panel.setAttribute('role','dialog');panel.setAttribute('aria-label','Privacy choices');
    panel.innerHTML='<strong>Your privacy choices</strong><p>Optional measurement records pages, buttons and campaign sources for up to 90 days. Advertising measurement links an inquiry and sales outcome to an ad click. Your form works with both options off.</p><label><input type="checkbox" name="analytics"> Allow website analytics</label><label><input type="checkbox" name="ads"> Allow advertising measurement</label><div><button type="button" data-choice="deny">Reject optional</button><button type="button" data-choice="save">Save choices</button></div>';
    panel.querySelector('[name="analytics"]').checked=t.consent().analytics;
    panel.querySelector('[name="ads"]').checked=t.consent().ads;
    panel.addEventListener('click',e=>{const choice=e.target.dataset.choice;if(!choice)return;t.changeConsent(choice==='save'&&panel.querySelector('[name="analytics"]').checked,choice==='save'&&panel.querySelector('[name="ads"]').checked);panel.remove();panel=null;});
    document.body.append(panel);
  };
  window.addEventListener('taotao:open-analytics-preferences',show);
  if(!t.consent().at)show();
  return ()=>{window.removeEventListener('taotao:open-analytics-preferences',show);panel?.remove();};
}
export function formContext() {
  let c={};try{c=JSON.parse(sessionStorage.getItem('tt:inquiry-context')||'{}');}catch{}
  const q=new URLSearchParams(location.search);
  return {page:c.page||location.pathname,product:clean(q.get('product')||c.product,160),model:clean(q.get('model')||c.model,100),cta_id:clean(c.cta_id,100)};
}
// One key per unchanged payload, including after an uncertain network result or page reload.
// Only a hash and random key persist in session storage; no customer fields are saved there.
export async function sendInquiry(endpoint,siteId,formId,fields,tracker,turnstileToken='') {
  const fingerprint=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(fields))))).map(x=>x.toString(16).padStart(2,'0')).join('');
  const key=`tt:submission:${siteId}:${formId}`;let prior;
  try{prior=JSON.parse(sessionStorage.getItem(key)||'null');}catch{}
  window.__ttSubmissions ||= {};prior ||= window.__ttSubmissions[key];
  const attempt=prior?.fingerprint===fingerprint?prior:{fingerprint,key:id()};window.__ttSubmissions[key]=attempt;
  try{sessionStorage.setItem(key,JSON.stringify(attempt));}catch{}
  tracker.event('form_submit_attempt',{form_id:formId});
  const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':attempt.key},body:JSON.stringify({site_id:siteId,form_id:formId,page:location.pathname,fields,journey:tracker.snapshot(),turnstile_token:turnstileToken}),signal:AbortSignal.timeout(20000),credentials:'omit'});
  const result=await response.json();
  if(!response.ok||!result.lead_id)throw new Error(result.error||'We could not confirm receipt. Retry using the same details.');
  tracker.event('lead_submitted',{form_id:formId});
  return result;
}
export async function mountChallenge(config,container) {
  if(config.test_mode||!config.turnstile_site_key)return {token:()=>'',reset:()=>{}};
  if(!window.turnstile){
    window.__ttChallengeReady ||= new Promise((resolve,reject)=>{
      const script=document.createElement('script');script.src='https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';script.async=true;script.onload=resolve;script.onerror=()=>reject(new Error('Security check could not load. Reload or use direct contact.'));document.head.append(script);
    });
    await window.__ttChallengeReady;
  }
  let token='';const widget=window.turnstile.render(container,{sitekey:config.turnstile_site_key,action:'inquiry',callback:v=>{token=v;},'expired-callback':()=>{token='';},'error-callback':()=>{token='';}});
  return {token:()=>token,reset:()=>{token='';window.turnstile.reset(widget);},remove:()=>window.turnstile.remove(widget)};
}
