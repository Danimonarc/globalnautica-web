// Global Nautica — interacciones básicas (sin dependencias)
(function () {
  "use strict";

  // Cabecera sólida al hacer scroll
  var header = document.querySelector("[data-header]");
  function onScroll() {
    if (header) header.classList.toggle("is-scrolled", window.scrollY > 24);
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  // Menú móvil
  var toggle = document.querySelector("[data-nav-toggle]");
  var nav = document.querySelector("[data-nav]");
  function closeNav() {
    if (!toggle) return;
    toggle.setAttribute("aria-expanded", "false");
    nav.classList.remove("is-open");
  }
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("is-open", !open);
      header.classList.add("is-scrolled");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) closeNav();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeNav();
    });
  }

  // Pestañas de servicios (accesibles con teclado)
  document.querySelectorAll("[data-tabs]").forEach(function (root) {
    var tabs = Array.prototype.slice.call(root.querySelectorAll('[role="tab"]'));
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var selected = t === tab;
        t.setAttribute("aria-selected", String(selected));
        t.tabIndex = selected ? 0 : -1;
        document.getElementById(t.getAttribute("aria-controls")).hidden = !selected;
      });
      if (focus) tab.focus();
    }
    // Tarjetas de la portada que abren directamente una pestaña
    document.querySelectorAll("[data-open-tab]").forEach(function (link) {
      var target = document.getElementById(link.getAttribute("data-open-tab"));
      if (tabs.indexOf(target) === -1) return;
      link.addEventListener("click", function () { select(target); });
    });
    tabs.forEach(function (tab, i) {
      tab.addEventListener("click", function () { select(tab); });
      tab.addEventListener("keydown", function (e) {
        var next = null;
        if (e.key === "ArrowRight" || e.key === "ArrowDown") next = tabs[(i + 1) % tabs.length];
        if (e.key === "ArrowLeft" || e.key === "ArrowUp") next = tabs[(i - 1 + tabs.length) % tabs.length];
        if (e.key === "Home") next = tabs[0];
        if (e.key === "End") next = tabs[tabs.length - 1];
        if (next) { e.preventDefault(); select(next, true); }
      });
    });
  });

  // Animación de entrada
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-visible"); });
  }

  // Resaltar la sección activa en el menú
  var links = document.querySelectorAll('.main-nav ul a[href^="#"]');
  if (links.length && "IntersectionObserver" in window) {
    var byId = {};
    links.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var link = byId[entry.target.id];
        if (link && entry.isIntersecting) {
          links.forEach(function (a) { a.classList.remove("is-active"); });
          link.classList.add("is-active");
        }
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    Object.keys(byId).forEach(function (id) {
      var section = document.getElementById(id);
      if (section) spy.observe(section);
    });
  }

  // Mapa: solo se carga Google Maps cuando el usuario lo pide (sin cookies de terceros por defecto)
  var mapCard = document.querySelector("[data-map]");
  var mapBtn = document.querySelector("[data-map-load]");
  if (mapCard && mapBtn) {
    mapBtn.addEventListener("click", function () {
      var iframe = document.createElement("iframe");
      iframe.src = "https://maps.google.com/maps?q=36.4170574,-5.1562526&z=17&output=embed";
      iframe.title = document.documentElement.lang === "en"
        ? "Global Nautica location in Estepona"
        : "Ubicación de Global Nautica en Estepona";
      iframe.loading = "lazy";
      iframe.referrerPolicy = "no-referrer-when-downgrade";
      mapCard.appendChild(iframe);
      mapCard.classList.add("is-loaded");
    });
  }

  // Sugerir la otra versión de idioma si el navegador está en ese idioma.
  // Nunca redirige: solo muestra un aviso que se puede cerrar (y se recuerda).
  var suggest = document.querySelector("[data-lang-suggest]");
  if (suggest) {
    var target = suggest.getAttribute("data-lang-suggest");
    var key = "gn-lang-suggest-dismissed";
    var prefs = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ""];
    var preferred = String(prefs[0] || "").toLowerCase().slice(0, 2);
    var dismissed = false;
    try { dismissed = localStorage.getItem(key) === "1"; } catch (e) {}
    if (preferred === target && !dismissed) {
      suggest.hidden = false;
      document.body.classList.add("has-lang-suggest");
    }
    function remember() {
      try { localStorage.setItem(key, "1"); } catch (e) {}
    }
    suggest.querySelector("[data-lang-suggest-close]").addEventListener("click", function () {
      suggest.hidden = true;
      document.body.classList.remove("has-lang-suggest");
      remember();
    });
    suggest.querySelector("a").addEventListener("click", remember);
  }

  // Enlaces de email: si el equipo no tiene programa de correo, el navegador no hace
  // nada al pulsar. En ese caso mostramos la dirección con alternativas.
  var mailHelp = null;
  function showMailHelp(href) {
    var en = document.documentElement.lang === "en";
    var address = href.replace(/^mailto:/, "").split("?")[0];
    var subject = (href.split("subject=")[1] || "").split("&")[0];
    if (mailHelp) mailHelp.remove();
    mailHelp = document.createElement("div");
    mailHelp.className = "mail-help";
    mailHelp.setAttribute("role", "status");
    var text = document.createElement("p");
    text.textContent = (en ? "Didn't your email program open? Write to us at " : "¿No se ha abierto su programa de correo? Escríbanos a ") + address;
    var actions = document.createElement("div");
    actions.className = "mail-help-actions";
    var copy = document.createElement("button");
    copy.type = "button";
    copy.textContent = en ? "Copy address" : "Copiar dirección";
    copy.addEventListener("click", function () {
      if (navigator.clipboard) navigator.clipboard.writeText(address).then(function () {
        copy.textContent = en ? "Copied" : "Copiada";
      });
    });
    actions.appendChild(copy);
    [["Gmail", "https://mail.google.com/mail/?view=cm&to=" + address + "&su=" + subject],
     ["Outlook", "https://outlook.live.com/mail/0/deeplink/compose?to=" + address + "&subject=" + subject]].forEach(function (w) {
      var a = document.createElement("a");
      a.href = w[1]; a.target = "_blank"; a.rel = "noopener";
      a.textContent = (en ? "Open in " : "Abrir en ") + w[0];
      actions.appendChild(a);
    });
    var close = document.createElement("button");
    close.type = "button"; close.className = "mail-help-close";
    close.setAttribute("aria-label", en ? "Close" : "Cerrar");
    close.textContent = "×";
    close.addEventListener("click", function () { mailHelp.remove(); mailHelp = null; });
    mailHelp.appendChild(text); mailHelp.appendChild(actions); mailHelp.appendChild(close);
    document.body.appendChild(mailHelp);
  }
  document.addEventListener("click", function (e) {
    var link = e.target.closest && e.target.closest('a[href^="mailto:"]');
    if (!link) return;
    // Si el programa de correo se abre, la página pierde el foco y no se muestra nada
    setTimeout(function () {
      if (!document.hidden && document.hasFocus()) showMailHelp(link.getAttribute("href"));
    }, 1200);
  });

  // Año del copyright
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
