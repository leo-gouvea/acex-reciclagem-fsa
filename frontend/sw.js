self.addEventListener('install', function (event) {
  console.log('Service Worker do EcoHora foi instalado!');
});

self.addEventListener('activate', function (event) {
  console.log('Service Worker do EcoHora está ativo.');
});

// Sem cache por enquanto — só repassa a requisição direto pra
// rede. Isso ainda conta pro critério de instalação do PWA;
// uma estratégia de cache de verdade fica pra quando fizer
// sentido (ex: deixar o app abrir sem internet).
self.addEventListener('fetch', function (event) {
  event.respondWith(fetch(event.request));
});
