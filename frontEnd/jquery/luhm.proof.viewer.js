(function ($, window) {
  'use strict';

  var ROOT = '[data-luhm-cockpit]';
  var VIEWER = '[data-luhm-proof-viewer]';
  var TYPES = { pdf:true, docx:true, website:true, image:true, asset:true, json:true, text:true };
  var STATUSES = { GREEN:true, AMBER:true, RED:true, UNKNOWN:true };
  var current = null;

  function clean(value, max) {
    return String(value == null ? '' : value).replace(/[<>]/g, '').slice(0, max || 4000);
  }

  function safeUrl(value, options) {
    options = options || {};
    if (!value) return '';
    try {
      var url = new URL(String(value), window.location.href);
      var protocol = url.protocol.toLowerCase();
      if (protocol === 'blob:' && options.allowBlob !== false) return url.href;
      if (protocol === 'https:') return url.href;
      if (protocol === 'http:' && url.origin === window.location.origin) return url.href;
      if ((protocol === 'file:' || protocol === 'content:') && options.allowLocal === true) return url.href;
    } catch (_err) {}
    return '';
  }

  function normalize(detail) {
    if (!detail || typeof detail !== 'object') throw new Error('proof packet must be an object');
    var type = clean(detail.type, 20).toLowerCase();
    if (!TYPES[type]) throw new Error('unsupported proof type');
    var id = clean(detail.id, 120);
    if (!id) throw new Error('proof packet requires id');
    var status = clean(detail.status || 'UNKNOWN', 16).toUpperCase();
    if (!STATUSES[status]) status = 'UNKNOWN';
    return {
      id: id,
      type: type,
      title: clean(detail.title || 'Proof', 180),
      status: status,
      sourceRef: clean(detail.sourceRef || 'UNKNOWN', 160),
      sha256: clean(detail.sha256 || 'UNKNOWN', 96),
      provenance: clean(detail.provenance || 'UNKNOWN', 180),
      capturedAt: clean(detail.capturedAt || detail.createdAt || '', 80),
      url: safeUrl(detail.url, { allowBlob:true, allowLocal:true }),
      snapshotUrl: safeUrl(detail.snapshotUrl, { allowBlob:true, allowLocal:true }),
      liveUrl: safeUrl(detail.liveUrl, { allowBlob:false, allowLocal:false }),
      allowLive: detail.allowLive === true,
      blocks: Array.isArray(detail.blocks) ? detail.blocks.slice(0, 500) : [],
      data: detail.data,
      text: clean(detail.text || '', 200000),
      fields: detail.fields && typeof detail.fields === 'object' ? detail.fields : {},
      mime: clean(detail.mime || '', 100),
      externalUrl: safeUrl(detail.externalUrl || detail.url, { allowBlob:false, allowLocal:false })
    };
  }

  function $root() { return $(ROOT).first(); }
  function $viewer() { return $root().find(VIEWER).first(); }
  function $stage() { return $viewer().find('[data-proof-stage]').first(); }

  function metaCell(label, value, code) {
    var $cell = $('<div>', { 'class':'proofMetaCell' });
    $('<small>', { text: label }).appendTo($cell);
    $(code ? '<code>' : '<span>').text(clean(value || 'UNKNOWN', 180)).appendTo($cell);
    return $cell;
  }

  function renderMeta(proof) {
    var $v = $viewer();
    $v.find('[data-proof-kind]').text(proof.type.toUpperCase());
    $v.find('[data-proof-title]').text(proof.title);
    $v.find('[data-proof-status]').attr('data-status', proof.status).text(proof.status);
    var $meta = $v.find('[data-proof-meta]').empty();
    $meta.append(metaCell('source', proof.sourceRef, true));
    $meta.append(metaCell('sha256', proof.sha256, true));
    $meta.append(metaCell('provenance', proof.provenance, false));
    $meta.append(metaCell('captured', proof.capturedAt || 'UNKNOWN', false));
    var $external = $v.find('[data-proof-external]');
    $external.prop('hidden', !proof.externalUrl).attr('href', proof.externalUrl || '#');
  }

  function empty(message) {
    $stage().append($('<div>', { 'class':'proofEmpty', text: message }));
  }

  function renderImage(proof, url) {
    if (!url) return empty('No safe image preview URL was supplied for this proof.');
    var $wrap = $('<div>', { 'class':'proofImageWrap' });
    $('<img>', { src:url, alt:proof.title, loading:'eager', referrerpolicy:'no-referrer' })
      .on('error', function () { $wrap.empty(); $('<div>', { 'class':'proofEmpty', text:'Image preview failed to load.' }).appendTo($wrap); })
      .appendTo($wrap);
    $stage().append($wrap);
  }

  function renderPdf(proof) {
    if (!proof.url) return empty('No safe PDF URL or blob was supplied.');
    var $object = $('<object>', { 'class':'proofPdf', type:'application/pdf', data:proof.url });
    $('<p>', { text:'Embedded PDF preview is unavailable in this WebView. Use Open source.' }).appendTo($object);
    $stage().append($object);
  }

  function appendDocBlock($doc, block) {
    if (!block || typeof block !== 'object') return;
    var type = clean(block.type || 'paragraph', 24).toLowerCase();
    var value = clean(block.text || '', 20000);
    if (type === 'heading') {
      var level = Math.max(1, Math.min(3, Number(block.level) || 2));
      $('<h' + level + '>', { text:value }).appendTo($doc);
    } else if (type === 'quote') {
      $('<blockquote>', { text:value }).appendTo($doc);
    } else if (type === 'code') {
      $('<pre>').append($('<code>', { text:value })).appendTo($doc);
    } else if (type === 'list') {
      var $list = $('<' + (block.ordered ? 'ol' : 'ul') + '>');
      (Array.isArray(block.items) ? block.items : []).slice(0, 200).forEach(function (item) {
        $('<li>', { text:clean(item, 5000) }).appendTo($list);
      });
      $list.appendTo($doc);
    } else if (type === 'table') {
      var rows = Array.isArray(block.rows) ? block.rows.slice(0, 100) : [];
      var $table = $('<table>');
      rows.forEach(function (row, rowIndex) {
        var $tr = $('<tr>').appendTo($table);
        (Array.isArray(row) ? row : []).slice(0, 20).forEach(function (cell) {
          $('<' + (rowIndex === 0 && block.header !== false ? 'th' : 'td') + '>', { text:clean(cell, 4000) }).appendTo($tr);
        });
      });
      $table.appendTo($doc);
    } else if (type === 'image') {
      var imageUrl = safeUrl(block.url, { allowBlob:true, allowLocal:true });
      if (imageUrl) $('<img>', { src:imageUrl, alt:clean(block.alt || '', 200), loading:'lazy', referrerpolicy:'no-referrer' }).css({maxWidth:'100%', height:'auto'}).appendTo($doc);
    } else {
      $('<p>', { text:value }).appendTo($doc);
    }
  }

  function renderDocx(proof) {
    var $doc = $('<article>', { 'class':'proofDoc' });
    if (!proof.blocks.length) {
      $('<p>', { text:'DOCX proof has no structured preview blocks. Raw Office HTML is intentionally not executed.' }).appendTo($doc);
    } else {
      proof.blocks.forEach(function (block) { appendDocBlock($doc, block); });
    }
    $stage().append($doc);
  }

  function renderWebsite(proof) {
    var $wrap = $('<div>', { 'class':'proofWebsite' });
    if (proof.snapshotUrl) {
      $('<img>', { 'class':'proofWebsiteShot', src:proof.snapshotUrl, alt:proof.title + ' website snapshot', referrerpolicy:'no-referrer' }).appendTo($wrap);
    }
    if (proof.allowLive && proof.liveUrl) {
      $('<iframe>', {
        'class':'proofWebsiteFrame',
        src:proof.liveUrl,
        title:proof.title + ' sandboxed website view',
        sandbox:'',
        referrerpolicy:'no-referrer',
        loading:'lazy'
      }).appendTo($wrap);
    }
    if (!proof.snapshotUrl && !(proof.allowLive && proof.liveUrl)) {
      $('<div>', { 'class':'proofEmpty', text:'No captured website snapshot is attached. Live browsing is disabled unless the proof packet explicitly opts in.' }).appendTo($wrap);
    }
    $stage().append($wrap);
  }

  function renderText(proof, asJson) {
    var value = proof.text;
    if (asJson) {
      try { value = JSON.stringify(proof.data == null ? {} : proof.data, null, 2); }
      catch (_err) { value = '{}'; }
    }
    $('<pre>', { 'class':'proofText', text:value || '(empty proof)' }).appendTo($stage());
  }

  function renderAsset(proof) {
    var $wrap = $('<section>', { 'class':'proofAsset' });
    var $preview = $('<div>', { 'class':'proofAssetPreview' }).appendTo($wrap);
    if (proof.snapshotUrl || proof.url) {
      $('<img>', { src:proof.snapshotUrl || proof.url, alt:proof.title, referrerpolicy:'no-referrer' }).appendTo($preview);
    } else {
      $('<span>', { text:'No visual preview' }).appendTo($preview);
    }
    var $grid = $('<div>', { 'class':'proofAssetGrid' }).appendTo($wrap);
    Object.keys(proof.fields).slice(0, 24).forEach(function (key) {
      var $cell = $('<div>', { 'class':'proofAssetCell' }).appendTo($grid);
      $('<small>', { text:clean(key, 60) }).appendTo($cell);
      $('<code>', { text:clean(proof.fields[key], 1000) }).appendTo($cell);
    });
    $stage().append($wrap);
  }

  function render(proof) {
    renderMeta(proof);
    $stage().empty();
    if (proof.type === 'pdf') renderPdf(proof);
    else if (proof.type === 'docx') renderDocx(proof);
    else if (proof.type === 'website') renderWebsite(proof);
    else if (proof.type === 'image') renderImage(proof, proof.snapshotUrl || proof.url);
    else if (proof.type === 'asset') renderAsset(proof);
    else if (proof.type === 'json') renderText(proof, true);
    else renderText(proof, false);
  }

  function open(detail) {
    current = normalize(detail);
    render(current);
    $viewer().prop('hidden', false).attr('data-proof-type', current.type);
    $root().trigger('luhm:proof:opened', [$.extend({}, current)]);
    return $.extend({}, current);
  }

  function close() {
    var closed = current;
    current = null;
    $viewer().prop('hidden', true).removeAttr('data-proof-type');
    $stage().empty();
    $root().trigger('luhm:proof:closed', [closed ? { id:closed.id, type:closed.type } : {}]);
  }

  function init() {
    var $r = $root();
    if (!$r.length || $r.data('luhmProofViewerReady')) return;
    $r.data('luhmProofViewerReady', true);

    $r.on('click.luhmProofViewer', '[data-proof-close]', close);
    $r.on('click.luhmProofViewer', '[data-proof-pin]', function () {
      if (!current) return;
      $r.trigger('luhm:proof:pin-request', [{ id:current.id, type:current.type, sourceRef:current.sourceRef, sha256:current.sha256 }]);
    });

    window.addEventListener('luhm:proof:open', function (event) {
      try { open(event.detail || {}); }
      catch (err) {
        console.warn('LuHm proof packet rejected:', err.message);
        $r.trigger('luhm:proof:rejected', [{ reason:clean(err.message, 180) }]);
      }
    });
    window.addEventListener('luhm:proof:close', close);

    window.luhmProofViewer = Object.freeze({
      version:'0.1.0-beta',
      types:Object.freeze(Object.keys(TYPES)),
      open:open,
      close:close,
      current:function () { return current ? $.extend(true, {}, current) : null; }
    });
  }

  $(init);
})(window.jQuery, window);
