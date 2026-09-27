(function ($, window) {
  'use strict';

  var ROOT = '[data-luhm-cockpit]';
  var CHAT = '[data-luhm-chat]';
  var INPUT = '[data-luhm-input]';
  var STREAM = '[data-luhm-message-stream]';

  var ACTIONS = {
    continue: { label: 'Continue', prompt: 'Continue from the current proven state. Use the next smallest action and preserve existing receipts.', lane: 'direct' },
    audit: { label: 'Audit source', prompt: 'Audit the current source and receipts. Report GREEN, AMBER, RED, or UNKNOWN without mutating anything.', lane: 'audit' },
    verify: { label: 'Verify GREEN', prompt: 'Verify the current candidate against the exact source SHA and required proof gates. Do not promote.', lane: 'verify' },
    build: { label: 'Build / test', prompt: 'Prepare the smallest build or test needed for the current change. Reuse proven architecture only when receipts match.', lane: 'build' },
    fix: { label: 'Fix bug', prompt: 'Trace the current regression to the smallest source-level cause and propose or stage a surgical fix.', lane: 'debug' },
    assets: { label: 'Assets', prompt: 'Audit and organize the relevant LuHm game/media assets, provenance, duplicates, and runtime readiness.', lane: 'assets' },
    proofs: { label: 'Proofs', prompt: 'Show the proof/evidence attached to the current task. Preserve exact source SHA, hashes, provenance, and UNKNOWN states.', lane: 'evidence' },
    research: { label: 'Research', prompt: 'Research the current technical question using authoritative current sources and return only findings that affect the build.', lane: 'research' },
    drive: { label: 'Drive install', prompt: 'Continue the Google Drive install workflow using the newest proven artifact. Do not rebuild unless required.', lane: 'distribution' },
    crown: { label: 'Prepare Crown', prompt: 'Prepare the current candidate for Crown review. Summarize exact SHA, evidence, blockers, and authority required. Do not promote.', lane: 'crown' }
  };

  var state = {
    mode: 'ready',
    currentAction: null,
    context: {
      branch: 'UNKNOWN',
      sourceRef: 'UNKNOWN',
      target: 'local-first'
    }
  };

  function clean(value, max) {
    return String(value == null ? '' : value).replace(/[<>]/g, '').slice(0, max || 4000);
  }

  function stamp() {
    return new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  }

  function $root() { return $(ROOT).first(); }
  function $chat() { return $root().find(CHAT).first(); }
  function $input() { return $root().find(INPUT).first(); }
  function $stream() { return $root().find(STREAM).first(); }

  function resizeInput() {
    var el = $input().get(0);
    if (!el || el.tagName !== 'TEXTAREA') return;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 136) + 'px';
  }

  function setHint(text) {
    $root().find('[data-chat-hint]').text(clean(text, 180));
  }

  function setState(mode, label, level) {
    state.mode = clean(mode || 'ready', 24).toLowerCase();
    $chat().attr('data-chat-state', state.mode);
    var $line = $root().find('[data-chat-state-line]');
    $line.attr('data-level', clean(level || '', 16).toUpperCase());
    $line.find('[data-chat-state-label]').text(clean(label || state.mode, 120));
  }

  function renderContext() {
    var map = {
      branch: state.context.branch || 'UNKNOWN',
      sourceRef: state.context.sourceRef || 'UNKNOWN',
      target: state.context.target || 'local-first'
    };
    Object.keys(map).forEach(function (key) {
      var value = clean(map[key], 120);
      var $node = $root().find('[data-chat-context="' + key + '"]');
      $node.find('strong').text(value);
      $node.toggleClass('isUnknown', value === 'UNKNOWN');
    });
  }

  function applyAction(id) {
    var action = ACTIONS[id];
    if (!action) return;
    state.currentAction = id;
    $input().val(action.prompt).trigger('input').focus();
    setHint(action.label + ' · ' + action.lane + ' lane · review then send');
    $root().trigger('luhm:chat:intent-selected', [{ id: id, lane: action.lane, label: action.label }]);
  }

  function appendAssistant(detail) {
    detail = detail || {};
    var text = clean(detail.text, 12000);
    if (!text) return;
    var $article = $('<article>', { 'class': 'message messageLum' });
    $('<div>', { 'class': 'avatar', 'aria-hidden': 'true', text: 'L' }).appendTo($article);
    var $body = $('<div>').appendTo($article);
    var $meta = $('<div>', { 'class': 'messageMeta' }).appendTo($body);
    $('<strong>', { text: clean(detail.name || 'Lum', 40) }).appendTo($meta);
    $('<time>', { text: stamp() }).appendTo($meta);
    $('<p>', { text: text }).appendTo($body);
    $stream().append($article).scrollTop($stream().prop('scrollHeight'));
  }

  function appendReceipt(detail) {
    detail = detail || {};
    var status = clean(detail.status || 'UNKNOWN', 16).toUpperCase();
    var $card = $('<section>', { 'class': 'chatSystemCard', 'data-status': status });
    var $head = $('<div>', { 'class': 'chatSystemCardHeader' }).appendTo($card);
    $('<strong>', { text: clean(detail.title || 'Receipt', 80) }).appendTo($head);
    $('<span>', { 'class': 'chatSystemBadge', text: status }).appendTo($head);
    if (detail.summary) $('<p>', { text: clean(detail.summary, 500) }).appendTo($card);

    var fields = detail.fields && typeof detail.fields === 'object' ? detail.fields : {};
    var keys = Object.keys(fields).slice(0, 8);
    if (keys.length) {
      var $grid = $('<div>', { 'class': 'chatReceiptGrid' }).appendTo($card);
      keys.forEach(function (key) {
        var $cell = $('<div>', { 'class': 'chatReceiptCell' }).appendTo($grid);
        $('<small>', { text: clean(key, 40) }).appendTo($cell);
        $('<code>', { text: clean(fields[key], 180) }).appendTo($cell);
      });
    }

    if (detail.proof && typeof detail.proof === 'object') {
      var proof = $.extend(true, {}, detail.proof);
      if (!proof.status) proof.status = status;
      if (!proof.sourceRef && fields.sourceRef) proof.sourceRef = fields.sourceRef;
      if (!proof.sha256 && fields.sha256) proof.sha256 = fields.sha256;
      var $button = $('<button>', { 'class':'chatProofButton', type:'button', text:'Open proof', 'data-chat-proof-open':'' });
      $button.data('luhmProofPacket', proof).appendTo($card);
    }

    $stream().append($card).scrollTop($stream().prop('scrollHeight'));
  }

  function submitByKeyboard(event) {
    if (event.key !== 'Enter' || event.shiftKey || event.isComposing) return;
    event.preventDefault();
    $root().find('[data-luhm-composer]').trigger('submit');
  }

  function init() {
    var $r = $root();
    if (!$r.length || $r.data('luhmChatWorkbenchReady')) return;
    $r.data('luhmChatWorkbenchReady', true);

    renderContext();
    setState('ready', 'Ready · Lum routes only after you send', '');

    $r.on('click.luhmChatWorkbench', '[data-chat-action]', function () {
      applyAction(String($(this).data('chat-action') || ''));
    });

    $r.on('click.luhmChatWorkbench', '[data-chat-proof-open]', function () {
      var proof = $(this).data('luhmProofPacket');
      if (!proof || typeof proof !== 'object') return;
      window.dispatchEvent(new CustomEvent('luhm:proof:open', { detail: $.extend(true, {}, proof) }));
    });

    $r.on('input.luhmChatWorkbench', INPUT, function () {
      resizeInput();
      if (!String($(this).val() || '').trim()) {
        state.currentAction = null;
        setHint('Enter sends · Shift+Enter adds a line');
      }
    });

    $r.on('keydown.luhmChatWorkbench', INPUT, submitByKeyboard);

    $r.on('click.luhmChatWorkbench', '[data-chat-voice]', function () {
      $(this).toggleClass('isListening');
      var on = $(this).hasClass('isListening');
      setHint(on ? 'Dictation staging requested · speech does not execute tools' : 'Dictation staging stopped');
      $r.trigger('luhm:chat:voice', [{ requested: on }]);
    });

    $r.on('click.luhmChatWorkbench', '[data-chat-attach]', function () {
      $r.trigger('luhm:chat:attach', [{ source: 'composer' }]);
      setHint('Attachment picker requested');
    });

    $r.on('click.luhmChatWorkbench', '[data-chat-stop]', function () {
      $r.trigger('luhm:chat:stop', [{ source: 'composer' }]);
      setState('waiting', 'Stop requested · waiting for backend acknowledgement', 'AMBER');
    });

    $r.on('luhm:chat:submit.luhmChatWorkbench', function (_event, detail) {
      setState('queued', 'Queued to Lum · no worker assumed yet', 'AMBER');
      setHint('Waiting for observed routing state');
      $r.trigger('luhm:chat:workbench-submit', [{
        text: clean(detail && detail.text, 12000),
        intent: state.currentAction || 'freeform',
        context: $.extend({}, state.context)
      }]);
      state.currentAction = null;
      resizeInput();
    });

    window.addEventListener('luhm:chat:state', function (event) {
      var d = event.detail || {};
      setState(d.mode || 'ready', d.label || d.mode || 'ready', d.level || '');
    });

    window.addEventListener('luhm:chat:assistant', function (event) {
      appendAssistant(event.detail || {});
    });

    window.addEventListener('luhm:chat:receipt', function (event) {
      appendReceipt(event.detail || {});
    });

    window.addEventListener('luhm:chat:context', function (event) {
      var d = event.detail || {};
      if (Object.prototype.hasOwnProperty.call(d, 'branch')) state.context.branch = clean(d.branch || 'UNKNOWN', 120);
      if (Object.prototype.hasOwnProperty.call(d, 'sourceRef')) state.context.sourceRef = clean(d.sourceRef || 'UNKNOWN', 120);
      if (Object.prototype.hasOwnProperty.call(d, 'target')) state.context.target = clean(d.target || 'local-first', 120);
      renderContext();
    });

    window.luhmChatWorkbench = Object.freeze({
      version: '0.2.0-beta',
      actions: Object.freeze(Object.keys(ACTIONS)),
      setContext: function (detail) { window.dispatchEvent(new CustomEvent('luhm:chat:context', { detail: detail || {} })); },
      assistant: function (detail) { window.dispatchEvent(new CustomEvent('luhm:chat:assistant', { detail: detail || {} })); },
      receipt: function (detail) { window.dispatchEvent(new CustomEvent('luhm:chat:receipt', { detail: detail || {} })); },
      state: function (detail) { window.dispatchEvent(new CustomEvent('luhm:chat:state', { detail: detail || {} })); }
    });
  }

  $(init);
})(window.jQuery, window);
