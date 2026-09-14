// Menu mobile: alterna o botão hamburger para X e mostra o painel.
// Sem dependências, só o essencial.

const menuToggle = document.getElementById('menuToggle');
const mobileMenu = document.getElementById('mobileMenu');

function closeMenu() {
  menuToggle.setAttribute('aria-expanded', 'false');
  menuToggle.setAttribute('aria-label', 'Abrir menu');
  mobileMenu.classList.remove('open');
  mobileMenu.hidden = true;
}

function openMenu() {
  menuToggle.setAttribute('aria-expanded', 'true');
  menuToggle.setAttribute('aria-label', 'Fechar menu');
  mobileMenu.hidden = false;
  // pequeno delay pra permitir a transição de exibição
  requestAnimationFrame(() => mobileMenu.classList.add('open'));
}

menuToggle.addEventListener('click', () => {
  const isOpen = menuToggle.getAttribute('aria-expanded') === 'true';
  isOpen ? closeMenu() : openMenu();
});

// Fecha o menu se a pessoa aumentar a janela pro layout de desktop
window.addEventListener('resize', () => {
  if (window.innerWidth > 760) {
    closeMenu();
  }
});

// Fecha com Esc, sem precisar procurar o botão de novo
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && menuToggle.getAttribute('aria-expanded') === 'true') {
    closeMenu();
    menuToggle.focus();
  }
});

// Relógio da folha no hero: sobe mais devagar que a página
// (parallax) enquanto a pessoa rola. O giro do ponteiro e o
// flutuar da folha são só CSS (@keyframes em home.css).

const heroClock = document.getElementById('heroClock');
const clockHand = document.getElementById('clockHand');
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (heroClock && clockHand) {
  let ticking = false;

  function updateClock() {
    const scrollY = window.scrollY;
    const parallaxY = scrollY * 0.25;
    heroClock.style.setProperty('--parallax-y', `${parallaxY}px`);

    ticking = false;
  }

  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(updateClock);
      ticking = true;
    }
  }, { passive: true });

  updateClock();
}

// Palavra digitando no hero: alterna entre os materiais que
// dão pontos, reforçando que não é só embalagem que conta.

const dynamicWordEl = document.getElementById('heroDynamicWord');
const words = ['Sua embalagem', 'Seu caderno', 'Sua latinha', 'Sua garrafa'];

if (dynamicWordEl) {
    const typingSpeed = 60;
    const erasingSpeed = 30;
    const pauseAfterWord = 2200;
    let wordIndex = 0;

    function typeWord() {
      const word = words[wordIndex];

      let charIndex = 0;
      dynamicWordEl.textContent = '';

      function typeChar() {
        if (charIndex < word.length) {
          dynamicWordEl.textContent += word.charAt(charIndex);
          charIndex++;
          setTimeout(typeChar, typingSpeed);
        } else {
          setTimeout(eraseWord, pauseAfterWord);
        }
      }

      function eraseWord() {
        if (charIndex > 0) {
          charIndex--;
          dynamicWordEl.textContent = word.substring(0, charIndex);
          setTimeout(eraseWord, erasingSpeed);
        } else {
          wordIndex = (wordIndex + 1) % words.length;
          setTimeout(typeWord, 300);
        }
      }

      typeChar();
    }

    typeWord();
  }

// Botão de voltar ao topo: só aparece depois que a pessoa já
// rolou um pouco, pra não competir com o resto do hero.

const backToTop = document.getElementById('backToTop');

if (backToTop) {
  let toggling = false;

  function updateBackToTop() {
    backToTop.classList.toggle('visible', window.scrollY > 400);
    toggling = false;
  }

  window.addEventListener('scroll', () => {
    if (!toggling) {
      requestAnimationFrame(updateBackToTop);
      toggling = true;
    }
  }, { passive: true });

  backToTop.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: prefersReducedMotion ? 'auto' : 'smooth',
    });
  });
}
