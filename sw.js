// Service worker: app shell offline, content fetched fresh (network-first).
const SHELL = "sanju-shell-v2";
const SHELL_FILES = ["./", "./index.html", "./manifest.json",
  "./icon-180.png", "./icon-192.png", "./icon-512.png",
  "./NotoSansMongolian-Regular.ttf"];

self.addEventListener("install", e=>{
  e.waitUntil(caches.open(SHELL).then(c=>c.addAll(SHELL_FILES)).catch(()=>{}));
  self.skipWaiting();
});
self.addEventListener("activate", e=>{
  e.waitUntil(caches.keys().then(keys=>
    Promise.all(keys.filter(k=>k!==SHELL).map(k=>caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", e=>{
  const url = new URL(e.request.url);
  // content.json: always try network first so daily content stays fresh.
  if(url.pathname.endsWith("content.json")){
    e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)));
    return;
  }
  // shell: cache first.
  e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));
});
