(() => {
  "use strict";

  const root = document.querySelector("[data-luhm-cockpit]");
  if (!root) return;

  const $ = (selector, scope = root) => scope.querySelector(selector);
  const $$ = (selector, scope = root) => Array.from(scope.querySelectorAll(selector));

  const systemLayer = $("[data-luhm-system-layer]");
  const appMenu = $("[data-luhm-menu]");
  const messageStream = $("[data-luhm-message-stream]");
  const composer = $("[data-luhm-composer]");
  const input = $("[data-luhm-input]");
  const clock = $("[data-luhm-clock]");

  const emit = (name, detail = {}) => {
    const event = new CustomEvent(name, { bubbles: true, detail });
    root.dispatchEvent(event);
    return event;
  };

  const setView = (view) => {
    $$("[data-view]").forEach((button) => {
      button.classList.toggle("isActive", button.dataset.view === view);
    });
    emit("luhm:view:change", { view });
    if (appMenu) appMenu.hidden = true;
  };

  const openBackend = () => {
    emit("luhm:backend:open", { source: "frontEnd" });
    if (systemLayer) systemLayer.hidden = false;
    if (appMenu) appMenu.hidden = true;
  };

  const closeBackend = () => {
    if (systemLayer) systemLayer.hidden = true;
    emit("luhm:backend:close", { source: "frontEnd" });
  };

  const appendUserMessage = (text) => {
    const article = document.createElement("article");
    article.className = "message messageUser";
    article.innerHTML = `
      <div class="avatar" aria-hidden="true">Y</div>
      <div>
        <div class="messageMeta"><strong>You</strong><time>${new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}</time></div>
        <p></p>
      </div>`;
    article.querySelector("p").textContent = text;
    messageStream.append(article);
    messageStream.scrollTop = messageStream.scrollHeight;
  };

  $$("[data-view]").forEach((button) => button.addEventListener("click", () => setView(button.dataset.view)));
  $$("[data-luhm-backend-button]").forEach((button) => button.addEventListener("click", openBackend));
  $("[data-luhm-backend-close]")?.addEventListener("click", closeBackend);
  $("[data-luhm-menu-button]")?.addEventListener("click", () => { appMenu.hidden = !appMenu.hidden; });

  composer?.addEventListener("submit", (event) => {
    event.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    appendUserMessage(text);
    input.value = "";
    emit("luhm:chat:submit", { text });
  });

  const updateClock = () => {
    if (clock) clock.textContent = new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  };
  updateClock();
  window.setInterval(updateClock, 30_000);

  // Stable front-end integration surface. jQuery adapters/plugins may bind to
  // these events, but privileged backend behavior does not live here.
  window.LuHmFrontEnd = Object.freeze({
    openBackend,
    closeBackend,
    setView,
    emit,
    version: "0.1.0"
  });

  emit("luhm:frontend:ready", { version: window.LuHmFrontEnd.version });
})();
