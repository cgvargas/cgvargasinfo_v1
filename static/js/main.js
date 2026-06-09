// ── NAVBAR SCROLL EFFECT ─────────────────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  if (window.scrollY > 40) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
}, { passive: true });

// ── MENU MOBILE ──────────────────────────────────────────
const toggle = document.getElementById('navToggle');
const menu   = document.getElementById('navMenu');

if (toggle && menu) {
  toggle.addEventListener('click', () => {
    const isOpen = menu.classList.toggle('open');
    toggle.setAttribute('aria-expanded', isOpen);
    // Animar as barras do hamburger
    const bars = toggle.querySelectorAll('span');
    if (isOpen) {
      bars[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
      bars[1].style.opacity = '0';
      bars[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
    } else {
      bars.forEach(b => { b.style.transform = ''; b.style.opacity = ''; });
    }
  });

  // Fechar menu ao clicar em um link
  menu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      menu.classList.remove('open');
      const bars = toggle.querySelectorAll('span');
      bars.forEach(b => { b.style.transform = ''; b.style.opacity = ''; });
    });
  });

  // Fechar ao clicar fora
  document.addEventListener('click', (e) => {
    if (!navbar.contains(e.target)) {
      menu.classList.remove('open');
      const bars = toggle.querySelectorAll('span');
      bars.forEach(b => { b.style.transform = ''; b.style.opacity = ''; });
    }
  });
}

// ── ACTIVE NAV LINK ──────────────────────────────────────
(function setActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.navbar-menu a').forEach(link => {
    if (link.getAttribute('href') === path ||
        (path !== '/' && link.getAttribute('href') !== '/' && path.startsWith(link.getAttribute('href')))) {
      link.classList.add('active');
    }
  });
})();

// ── REVEAL ON SCROLL (Intersection Observer) ──────────────
const revealEls = document.querySelectorAll('.reveal');
if (revealEls.length > 0) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.classList.add('visible');
        }, i * 80);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  revealEls.forEach(el => observer.observe(el));
}

// ── TYPEWRITER EFFECT (Hero) ──────────────────────────────
const typeTarget = document.getElementById('typewriter');
if (typeTarget) {
  const words = [
    'Soluções Digitais.',
    'Sistemas com IA.',
    'Aplicações Web.',
    'Experiências Únicas.',
  ];
  let wordIdx = 0;
  let charIdx = 0;
  let deleting = false;
  let pauseCount = 0;

  function type() {
    const current = words[wordIdx];
    if (!deleting) {
      typeTarget.textContent = current.substring(0, charIdx + 1);
      charIdx++;
      if (charIdx === current.length) {
        deleting = true;
        pauseCount = 0;
        setTimeout(type, 1800);
        return;
      }
    } else {
      typeTarget.textContent = current.substring(0, charIdx - 1);
      charIdx--;
      if (charIdx === 0) {
        deleting = false;
        wordIdx = (wordIdx + 1) % words.length;
      }
    }
    setTimeout(type, deleting ? 60 : 100);
  }
  setTimeout(type, 800);
}

// ── GLOSSÁRIO: busca em tempo real ───────────────────────
const glossSearch = document.getElementById('glossSearchInput');
if (glossSearch) {
  glossSearch.addEventListener('input', function () {
    const q = this.value.toLowerCase();
    const groups = document.querySelectorAll('.glossario-group');
    groups.forEach(group => {
      let visible = 0;
      group.querySelectorAll('.glossario-term').forEach(term => {
        const text = term.textContent.toLowerCase();
        if (text.includes(q)) {
          term.style.display = '';
          visible++;
        } else {
          term.style.display = 'none';
        }
      });
      group.style.display = visible > 0 ? '' : 'none';
    });
  });
}

// ── SMOOTH SCROLL para âncoras ────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
