(function ($, window) {
  'use strict';

  var ROLE = {
    lum: { name: 'Lum', glyph: '♛', motif: 'crown' },
    fumi: { name: 'Fumi', glyph: '▤', motif: 'clipboard' },
    drNao: { name: 'Dr. Nao', glyph: '✚', motif: 'doctor' },
    tetsu: { name: 'Tetsu', glyph: '◆', motif: 'hammer' },
    kaji: { name: 'Kaji', glyph: '♨', motif: 'forge' },
    kiri: { name: 'Kiri', glyph: '⌕', motif: 'context' },
    momo: { name: 'Momo', glyph: '✦', motif: 'research' },
    shiori: { name: 'Shiori', glyph: '!', motif: 'critic' },
    kugi: { name: 'Kugi', glyph: '⌘', motif: 'tool' },
    yume: { name: 'Yume', glyph: '✎', motif: 'art' },
    koe: { name: 'Koe', glyph: '◖', motif: 'voice' },
    sumi: { name: 'Sumi', glyph: '#', motif: 'assets' }
  };

  var STATES = {
    IDLE: true, QUEUED: true, ACTIVE: true, WAITING: true,
    VERIFYING: true, SUCCESS: true, ERROR: true, PARKED: true
  };

  var PHASES = {
    INTAKE: true, RESOLVE: true, ROUTE: true, OBSERVE: true,
    MUTATE: true, VERIFY: true, ADJUDICATE: true, REPORT: true,
    CROWN_STOP: true
  };

  var current = {
    taskId: 'chat-idle',
    sourceRef: 'UNKNOWN',
    phase: 'REPORT',
    workers: [{ id: 'lum', state: 'IDLE', label: 'ready' }]
  };

  function text(value, max) {
    return String(value == null ? '' : value).replace(/[<>]/g, '').slice(0, max || 80);
  }

  function normalize(snapshot) {
    if (!snapshot || typeof snapshot !== 'object') throw new Error('activity snapshot must be an object');
    var taskId = text(snapshot.taskId, 96);
    var phase = text(snapshot.phase, 24).toUpperCase();
    if (!taskId) throw new Error('activity snapshot requires taskId');
    if (!PHASES[phase]) throw new Error('unknown activity phase');

    var raw = Array.isArray(snapshot.workers) ? snapshot.workers : [];
    var seen = Object.create(null);
    var workers = [];

    raw.forEach(function (item) {
      if (!item || !ROLE[item.id]) return;
      if (seen[item.id]) throw new Error('duplicate Oni activity worker');
      seen[item.id] = true;
      var state = text(item.state, 20).toUpperCase();
      if (!STATES[state]) throw new Error('unknown Oni activity state');
      workers.push({
        id: item.id,
        state: state,
        label: text(item.label || '', 54),
        evidenceRef: text(item.evidenceRef || '', 120)
      });
    });

    if (!seen.lum) workers.unshift({ id: 'lum', state: phase === 'CROWN_STOP' ? 'WAITING' : 'ACTIVE', label: 'orchestrating', evidenceRef: '' });
    var support = workers.filter(function (w) { return w.id !== 'lum' && w.state !== 'PARKED'; });
    if (support.length > 3) throw new Error('visible Oni support-worker cap exceeded');

    return {
      taskId: taskId,
      sourceRef: text(snapshot.sourceRef || 'UNKNOWN', 96),
      phase: phase,
      workers: workers
    };
  }

  function spritePath(id) {
    return '../assets/pet/oni/sprites/' + id + '.png';
  }

  function petNode(worker) {
    var role = ROLE[worker.id];
    var state = worker.state.toLowerCase();
    var $pet = $('<div>', {
      'class': 'oniPet oniPet--' + worker.id + ' oniPet--' + state,
      'data-oni-id': worker.id,
      'data-oni-state': worker.state,
      'role': 'group',
      'aria-label': role.name + ' ' + worker.state.toLowerCase() + (worker.label ? ': ' + worker.label : '')
    });

    var $portrait = $('<span>', { 'class': 'oniPetPortrait', 'aria-hidden': 'true' });
    var $img = $('<img>', { src: spritePath(worker.id), alt: '', draggable: false });
    $img.on('error', function () { $(this).remove(); $portrait.addClass('isFallback').text(role.glyph); });
    $portrait.append($img);

    var $copy = $('<span>', { 'class': 'oniPetCopy' });
    $copy.append($('<strong>').text(role.name));
    $copy.append($('<small>').text(worker.label || worker.state.toLowerCase()));

    $pet.append($portrait, $copy, $('<i>', { 'class': 'oniPetStateDot', 'aria-hidden': 'true' }));
    return $pet;
  }

  function render(snapshot) {
    var $dock = $('[data-luhm-oni-dock]');
    if (!$dock.length) return;
    var $pets = $dock.find('[data-luhm-oni-pets]').empty();
    snapshot.workers.forEach(function (worker) {
      if (worker.state !== 'PARKED' || worker.id === 'lum') $pets.append(petNode(worker));
    });
    $dock.attr('data-phase', snapshot.phase);
    $dock.find('[data-luhm-oni-phase]').text(snapshot.phase.replace('_', ' '));
    $dock.find('[data-luhm-oni-status]').text(
      snapshot.phase === 'CROWN_STOP' ? 'Crown decision required' :
      snapshot.workers.filter(function (w) { return w.state === 'ACTIVE' || w.state === 'VERIFYING'; }).length + ' active'
    );
  }

  function set(snapshot) {
    current = normalize(snapshot);
    render(current);
    return JSON.parse(JSON.stringify(current));
  }

  $(function () { render(current); });

  window.addEventListener('luhm:oni-activity', function (event) {
    try { set(event.detail); }
    catch (err) { console.warn('LuHm Oni activity packet rejected:', err.message); }
  });

  window.luhmOniActivity = Object.freeze({
    set: set,
    get: function () { return JSON.parse(JSON.stringify(current)); },
    roles: Object.freeze(Object.keys(ROLE))
  });
})(window.jQuery, window);
