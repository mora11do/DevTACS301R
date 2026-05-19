const connectBtn = document.getElementById("connectBtn");
const disconnectBtn = document.getElementById("disconnectBtn");
const statusEl = document.getElementById("status");
const logEl = document.getElementById("log");
const errorEl = document.getElementById("error");

let pc = null;
let dc = null;
let audioEl = null;
let localStream = null;
let userMessage = null;
let assistantMessage = null;

function extractErrorMessage(text, fallback) {
  if (!text) {
    return fallback;
  }

  try {
    const parsed = JSON.parse(text);
    const message = parsed.error?.message || parsed.error;
    if (typeof message === "string" && message.trim()) {
      return message;
    }
  } catch {}

  const titleMatch = text.match(/<title>([^<]+)<\/title>/i);
  if (titleMatch) {
    return titleMatch[1].trim();
  }

  return fallback;
}

function setStatus(text) {
  statusEl.textContent = text;
}

function setError(text) {
  errorEl.textContent = text || "";
}

function scrollLog() {
  logEl.scrollTop = logEl.scrollHeight;
}

function clearDrafts() {
  userMessage = null;
  assistantMessage = null;
}

function ensureMessage(kind) {
  const draft = kind === "user" ? userMessage : assistantMessage;
  if (draft) {
    return draft;
  }

  const row = document.createElement("div");
  row.className = `message ${kind}`;

  const speaker = document.createElement("span");
  speaker.className = "speaker";
  speaker.textContent = kind === "user" ? "Professor:" : "AI:";

  const text = document.createElement("span");
  text.className = "text";

  row.appendChild(speaker);
  row.appendChild(text);
  logEl.appendChild(row);
  scrollLog();

  if (kind === "user") {
    userMessage = text;
    assistantMessage = null;
    return text;
  }

  assistantMessage = text;
  return text;
}

function appendToMessage(kind, chunk) {
  const node = ensureMessage(kind);
  node.textContent += chunk;
  scrollLog();
}

function replaceMessage(kind, text) {
  const node = ensureMessage(kind);
  node.textContent = text;
  scrollLog();
}

function handleRealtimeEvent(event) {
  const type = event.type;

  if (type === "input_audio_buffer.speech_started") {
    setStatus("Listening...");
    userMessage = null;
    return;
  }

  if (type === "input_audio_buffer.speech_stopped") {
    setStatus("Thinking...");
    return;
  }

  if (type === "conversation.item.input_audio_transcription.delta") {
    appendToMessage("user", event.delta || "");
    return;
  }

  if (type === "conversation.item.input_audio_transcription.completed") {
    replaceMessage("user", event.transcript || "");
    return;
  }

  if (type === "response.created") {
    setStatus("Speaking...");
    assistantMessage = null;
    return;
  }

  if (type === "response.output_audio_transcript.delta") {
    appendToMessage("assistant", event.delta || "");
    return;
  }

  if (type === "response.output_text.delta") {
    appendToMessage("assistant", event.delta || "");
    return;
  }

  if (type === "response.done") {
    setStatus("Listening...");
    assistantMessage = null;
    return;
  }

  if (type === "error") {
    const message = event.error?.message || "Realtime error.";
    setError(message);
  }
}

async function connect() {
  connectBtn.disabled = true;
  disconnectBtn.disabled = false;
  setError("");
  setStatus("Connecting...");
  clearDrafts();

  audioEl = document.createElement("audio");
  audioEl.autoplay = true;

  localStream = await navigator.mediaDevices.getUserMedia({
    audio: {
      channelCount: 1,
      echoCancellation: true,
      noiseSuppression: true,
      autoGainControl: true,
    },
  });

  pc = new RTCPeerConnection();
  pc.ontrack = (event) => {
    audioEl.srcObject = event.streams[0];
  };
  pc.onconnectionstatechange = () => {
    if (pc.connectionState === "connected") {
      setStatus("Listening...");
    }
    if (pc.connectionState === "failed" || pc.connectionState === "disconnected" || pc.connectionState === "closed") {
      if (pc) {
        disconnect();
      }
    }
  };

  for (const track of localStream.getTracks()) {
    pc.addTrack(track, localStream);
  }

  dc = pc.createDataChannel("oai-events");
  dc.addEventListener("message", (event) => {
    handleRealtimeEvent(JSON.parse(event.data));
  });

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);

  const tokenResponse = await fetch("/token");
  if (!tokenResponse.ok) {
    const text = await tokenResponse.text();
    throw new Error(extractErrorMessage(text, "Failed to create Realtime client secret."));
  }

  const tokenPayload = await tokenResponse.json();
  const clientSecret = tokenPayload.client_secret;
  if (!clientSecret) {
    throw new Error("Realtime client secret was missing from the server response.");
  }

  const response = await fetch("https://api.openai.com/v1/realtime/calls", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${clientSecret}`,
      "Content-Type": "application/sdp",
    },
    body: offer.sdp,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(extractErrorMessage(text, "Session creation failed."));
  }

  const answer = {
    type: "answer",
    sdp: await response.text(),
  };
  await pc.setRemoteDescription(answer);
}

function disconnect() {
  connectBtn.disabled = false;
  disconnectBtn.disabled = true;
  setStatus("Disconnected");

  if (dc) {
    dc.close();
    dc = null;
  }

  if (pc) {
    pc.close();
    pc = null;
  }

  if (localStream) {
    for (const track of localStream.getTracks()) {
      track.stop();
    }
    localStream = null;
  }

  if (audioEl) {
    audioEl.srcObject = null;
    audioEl = null;
  }

  clearDrafts();
}

connectBtn.addEventListener("click", async () => {
  try {
    await connect();
  } catch (error) {
    setError(error.message || String(error));
    disconnect();
  }
});

disconnectBtn.addEventListener("click", () => {
  disconnect();
});
