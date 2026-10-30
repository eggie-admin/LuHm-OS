const $ = id => document.getElementById(id);
let stream = null, recorder = null, chunks = [];
const setStatus = (id, value) => { $(id).textContent = value; };

async function scan() {
  try {
    const response = await fetch('/api/status', {cache: 'no-store'});
    const data = await response.json();
    setStatus('aiStatus', data.ollama.connected ? 'Ollama ready' : 'Ollama offline');
    setStatus('model', data.model);
    setStatus('devs', data.video_devices.join(', ') || 'No /dev/video nodes');
    setStatus('gadget', data.usb_gadget_config_present ? 'Present (unverified)' : 'Not found');
  } catch (error) { setStatus('aiStatus', 'Local server disconnected'); }
}

async function refreshSources() {
  const devices = (await navigator.mediaDevices.enumerateDevices()).filter(d => d.kind === 'videoinput');
  $('sources').replaceChildren();
  for (const device of devices) {
    const option = document.createElement('option');
    option.value = device.deviceId;
    option.textContent = device.label || 'Camera ' + ($('sources').length + 1);
    $('sources').append(option);
  }
}

async function startCamera() {
  try {
    if (!navigator.mediaDevices?.getUserMedia) throw new Error('Browser camera API unavailable');
    if (recorder && recorder.state === 'recording') recorder.stop();
    if (stream) stream.getTracks().forEach(track => track.stop());
    const selected = $('sources').value;
    stream = await navigator.mediaDevices.getUserMedia({
      audio: false, video: selected ? {deviceId: {ideal: selected}} : {width: {ideal: 1280}, height: {ideal: 720}}
    });
    $('preview').srcObject = stream;
    await refreshSources();
    const actualId = stream.getVideoTracks()[0]?.getSettings().deviceId;
    if (actualId) $('sources').value = actualId;
    setStatus('cameraStatus', 'Live');
    $('photo').disabled = false;
    $('record').disabled = false;
  } catch (error) {
    setStatus('cameraStatus', 'Unavailable: ' + (error.name || error.message));
    $('photo').disabled = true;
    $('record').disabled = true;
  }
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url; anchor.download = filename;
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 15000);
}

function snapshot() {
  if (!stream) return;
  const video = $('preview');
  if (!video.videoWidth) return;
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth; canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  canvas.toBlob(blob => {
    if (blob) downloadBlob(blob, 'hydra-photo-' + Date.now() + '.png');
  }, 'image/png');
}

function startRecording() {
  if (!stream || !window.MediaRecorder) { alert('MediaRecorder is not available in this browser'); return; }
  chunks = [];
  try {
    recorder = new MediaRecorder(stream);
    recorder.ondataavailable = event => { if (event.data.size) chunks.push(event.data); };
    recorder.onstop = () => {
      const blob = new Blob(chunks, {type: recorder.mimeType || 'video/webm'});
      downloadBlob(blob, 'hydra-video-' + Date.now() + '.webm');
      $('record').disabled = false; $('stop').disabled = true;
    };
    recorder.start();
    $('record').disabled = true; $('stop').disabled = false;
  } catch (error) { alert('Recording error: ' + error.message); }
}

function bubble(message, className) {
  const node = document.createElement('div');
  node.className = 'bubble ' + className;
  node.textContent = message;
  $('conversation').append(node);
  $('conversation').scrollTop = $('conversation').scrollHeight;
  return node;
}

$('chatForm').addEventListener('submit', async event => {
  event.preventDefault();
  const prompt = $('question').value.trim();
  if (!prompt) return;
  $('question').value = '';
  bubble(prompt, 'user');
  const reply = bubble('Thinking locally…', 'guide');
  try {
    const response = await fetch('/api/ask', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({prompt})
    });
    const data = await response.json();
    reply.textContent = data.answer || data.error || 'No response';
  } catch (error) { reply.textContent = 'The local Ollama service is unavailable.'; }
});

$('start').addEventListener('click', startCamera);
$('sources').addEventListener('change', startCamera);
$('photo').addEventListener('click', snapshot);
$('record').addEventListener('click', startRecording);
$('stop').addEventListener('click', () => { if (recorder?.state === 'recording') recorder.stop(); });
$('refresh').addEventListener('click', scan);
document.addEventListener('keydown', event => {
  const tag = document.activeElement?.tagName;
  if (event.code === 'Space' && !['TEXTAREA','INPUT','BUTTON','SELECT'].includes(tag) && stream) {
    event.preventDefault(); snapshot();
  }
});
scan();
