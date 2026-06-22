// Service worker.
// - HTML + content.json: network-first (always fresh when online, cache as offline fallback).
// - Static assets (icons, font, manifest): cache-first.
const SHELL = "sanju-shell-v3";
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
  const isHTML = e.request.mode === "navigate"
    || url.pathname.endsWith("/") || url.pathname.endsWith("index.html");
  const isContent = url.pathname.endsWith("content.json");

  if(isHTML || isContent){
    // Network-first: fetch fresh, fall back to cache offline, and refresh the cache.
    e.respondWith(
      fetch(e.request).then(resp=>{
        const copy = resp.clone();
        caches.open(SHELL).then(c=>c.put(e.request, copy)).catch(()=>{});
        return resp;
      }).catch(()=>caches.match(e.request).then(r=>r||caches.match("./index.html")))
    );
    return;
  }
  // Static assets: cache-first.
  e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));
});
