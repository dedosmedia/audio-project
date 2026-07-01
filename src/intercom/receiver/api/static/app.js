const talkButton = document.getElementById("talk");
const statusEl = document.getElementById("status");
const muteButton = document.getElementById("mute");
const volUpButton = document.getElementById("vol-up");
const volDownButton = document.getElementById("vol-down");

// Must match shared/constants.py MAX_VOLUME.
const MAX_VOLUME = 2;
const VOLUME_STEP_PERCENT = 10;

let audioContext = null;
let workletNode = null;
let mediaStream = null;
let socket = null;

// The GStreamer `volume` element is linear amplitude, but perceived
// loudness is roughly cubic: a linear slider makes the bottom of the
// range sound much louder than the percentage suggests. Map the
// displayed/stepped percentage through a cubic curve instead.
function linearToPercent(linear) {
  return Math.round(Math.cbrt(linear / MAX_VOLUME) * 100);
}

function percentToLinear(percent) {
  const fraction = Math.max(0, Math.min(100, percent)) / 100;
  return MAX_VOLUME * fraction ** 3;
}

function renderStatus(status) {
  const percent = linearToPercent(status.volume);
  statusEl.textContent = `${status.running ? "receiver activo" : "receiver detenido"} · volumen ${percent}%${status.muted ? " · silenciado" : ""}`;
  muteButton.classList.toggle("muted", status.muted);
}

async function refreshStatus() {
  const response = await fetch("/status");
  renderStatus(await response.json());
}

async function postJSON(path, body) {
  const response = await fetch(path, {
    method: "POST",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  renderStatus(await response.json());
}

async function startTalking() {
  if (audioContext) {
    return;
  }

  talkButton.classList.add("active");

  audioContext = new AudioContext();
  await audioContext.audioWorklet.addModule("/pcm-worklet.js");

  mediaStream = await navigator.mediaDevices.getUserMedia({
    audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true },
  });

  const protocol = location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${protocol}://${location.host}/ws/talk?sample_rate=${audioContext.sampleRate}`);
  socket.binaryType = "arraybuffer";

  await new Promise((resolve, reject) => {
    socket.onopen = resolve;
    socket.onerror = reject;
  });

  const source = audioContext.createMediaStreamSource(mediaStream);
  workletNode = new AudioWorkletNode(audioContext, "pcm-capture-processor");
  workletNode.port.onmessage = (event) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(event.data);
    }
  };
  source.connect(workletNode);
}

function stopTalking() {
  talkButton.classList.remove("active");

  if (workletNode) {
    workletNode.port.onmessage = null;
    workletNode.disconnect();
    workletNode = null;
  }
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;
  }
  if (socket) {
    socket.close();
    socket = null;
  }
  if (audioContext) {
    audioContext.close();
    audioContext = null;
  }
}

talkButton.addEventListener("mousedown", startTalking);
talkButton.addEventListener("touchstart", (event) => {
  event.preventDefault();
  startTalking();
});
talkButton.addEventListener("mouseup", stopTalking);
talkButton.addEventListener("mouseleave", stopTalking);
talkButton.addEventListener("touchend", stopTalking);
talkButton.addEventListener("touchcancel", stopTalking);

volUpButton.addEventListener("click", async () => {
  const response = await fetch("/status");
  const status = await response.json();
  const percent = linearToPercent(status.volume);
  await postJSON("/volume", { value: percentToLinear(percent + VOLUME_STEP_PERCENT) });
});

volDownButton.addEventListener("click", async () => {
  const response = await fetch("/status");
  const status = await response.json();
  const percent = linearToPercent(status.volume);
  await postJSON("/volume", { value: percentToLinear(percent - VOLUME_STEP_PERCENT) });
});

muteButton.addEventListener("click", () => postJSON("/mute"));

refreshStatus();
