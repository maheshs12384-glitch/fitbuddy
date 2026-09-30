(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  /* ---------- rotating headline word ---------- */
  const swap = $('#swap');
  if (swap) {
    const words = ['stronger', 'leaner', 'faster', 'calmer', 'fitter'];
    let i = 0;
    setInterval(() => {
      swap.classList.add('out');
      setTimeout(() => { i = (i + 1) % words.length; swap.textContent = words[i]; swap.classList.remove('out'); }, 350);
    }, 2200);
  }

  /* ---------- loading overlay on form submit ---------- */
  const loader = $('#loader'), msg = $('#loader-msg');
  $$('form[data-loading]').forEach(form => {
    form.addEventListener('submit', () => {
      if (!form.checkValidity()) return;
      const lines = form.dataset.loading.split('|');
      let n = 0;
      msg.textContent = lines[0];
      loader.hidden = false;
      setInterval(() => { n = (n + 1) % lines.length; msg.textContent = lines[n]; }, 1800);
    });
  });
  window.addEventListener('pageshow', () => { if (loader) loader.hidden = true; });

  /* ---------- feedback quick chips ---------- */
  $$('[data-fill]').forEach(b => b.addEventListener('click', () => {
    const t = $('#fb');
    t.value = t.value ? `${t.value.trim()}. ${b.dataset.fill}` : b.dataset.fill;
    t.focus();
  }));

  /* ---------- confetti ---------- */
  const canvas = $('#confetti'), ctx = canvas.getContext('2d');
  function confetti() {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    canvas.width = innerWidth; canvas.height = innerHeight;
    const colors = ['#FF5C7A', '#C6F432', '#FFC53D', '#2DD4F0', '#7C4DFF', '#FF7AD9'];
    const bits = Array.from({ length: 140 }, () => ({
      x: innerWidth / 2, y: innerHeight * 0.6, vx: (Math.random() - .5) * 16, vy: -Math.random() * 15 - 4,
      s: 5 + Math.random() * 7, r: Math.random() * 6, c: colors[Math.random() * colors.length | 0]
    }));
    let frames = 0;
    (function tick() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      bits.forEach(b => { b.x += b.vx; b.y += b.vy; b.vy += .35; b.r += .2;
        ctx.save(); ctx.translate(b.x, b.y); ctx.rotate(b.r); ctx.fillStyle = b.c; ctx.fillRect(-b.s / 2, -b.s / 2, b.s, b.s * .6); ctx.restore(); });
      if (++frames < 130) requestAnimationFrame(tick); else ctx.clearRect(0, 0, canvas.width, canvas.height);
    })();
  }

  /* ---------- result page: tabs, version switch, progress ---------- */
  const plans = $('#plans');
  if (plans) {
    const store = {
      get: id => { try { return localStorage.getItem('fb:' + id) === '1'; } catch { return false; } },
      set: (id, v) => { try { localStorage.setItem('fb:' + id, v ? '1' : '0'); } catch {} }
    };
    const active = () => $$('.plan', plans).find(p => !p.hidden);

    $$('.plan', plans).forEach(plan => {
      const tabs = $$('.daytab', plan), panels = $$('.daypanel', plan);
      tabs.forEach(t => t.addEventListener('click', () => {
        tabs.forEach(x => x.classList.toggle('on', x === t));
        panels.forEach(p => { p.hidden = p.dataset.day !== t.dataset.day; });
      }));
      $$('input[type=checkbox]', plan).forEach(cb => {
        cb.checked = store.get(cb.dataset.id);
        cb.addEventListener('change', () => { store.set(cb.dataset.id, cb.checked); progress(true); });
      });
    });

    let celebrated = false;
    function progress(fromClick) {
      const boxes = $$('input[type=checkbox]', active());
      const done = boxes.filter(b => b.checked).length;
      $('#pcount').textContent = `${done} / ${boxes.length} done`;
      $('#pbar').style.width = boxes.length ? (done / boxes.length * 100) + '%' : '0';
      if (fromClick && boxes.length && done === boxes.length && !celebrated) { celebrated = true; confetti(); }
      if (done < boxes.length) celebrated = false;
    }

    $$('.switch button').forEach(btn => btn.addEventListener('click', () => {
      $$('.switch button').forEach(b => b.classList.toggle('on', b === btn));
      $$('.plan', plans).forEach(p => { p.hidden = p.dataset.plan !== btn.dataset.version; });
      progress();
    }));
    progress();
    if ($('.toast')) confetti();
  }

  /* ---------- coach view: search, expand, count-up ---------- */
  const search = $('#search');
  if (search) search.addEventListener('input', () => {
    const q = search.value.trim().toLowerCase();
    $$('.member').forEach(m => { m.hidden = q && !m.dataset.search.includes(q); });
  });
  $$('.member .toggle').forEach(b => b.addEventListener('click', () => {
    const box = b.closest('.member').querySelector('.plans2');
    box.hidden = !box.hidden;
    b.textContent = box.hidden ? 'Show plans' : 'Hide plans';
  }));
  $$('[data-count]').forEach(el => {
    const end = +el.dataset.count; let cur = 0;
    const step = () => { cur = Math.min(end, cur + Math.max(1, end / 20)); el.textContent = Math.round(cur); if (cur < end) requestAnimationFrame(step); };
    step();
  });
})();
