import './style.css'
import { RealtimeAgent, RealtimeSession } from '@openai/agents/realtime'
import type { RealtimeItem } from '@openai/agents/realtime'

const agent = new RealtimeAgent({
  name: 'Assistant',
  instructions: [
    'You are a helpful, articulate assistant being demonstrated in a university classroom.',
    'Keep spoken answers clear, natural, and concise by default.',
    'If the user interrupts, pivot to the newest request immediately.',
    'If audio is unclear, ask for a short repeat instead of guessing.',
  ].join(' '),
})

let session: RealtimeSession | null = null

const app = document.querySelector<HTMLDivElement>('#app')
if (!app) {
  throw new Error('Missing app root.')
}

app.innerHTML = `
  <main class="page">
    <h1 class="title">Speech-to-Speech Classroom Demo</h1>
    <div class="controls">
      <button id="connectBtn">Connect</button>
      <button id="disconnectBtn" disabled>Disconnect</button>
      <span id="status" class="status">Disconnected</span>
    </div>
    <p class="hint">Lecture demo backend behavior, plus automatic ephemeral tokens and far-field echo reduction.</p>
    <div id="log" class="log"></div>
    <div id="error" class="error"></div>
  </main>
`

const connectBtn = document.getElementById('connectBtn') as HTMLButtonElement
const disconnectBtn = document.getElementById('disconnectBtn') as HTMLButtonElement
const statusEl = document.getElementById('status') as HTMLSpanElement
const logEl = document.getElementById('log') as HTMLDivElement
const errorEl = document.getElementById('error') as HTMLDivElement

function setStatus(text: string) {
  statusEl.textContent = text
}

function setError(text: string) {
  errorEl.textContent = text
}

function extractMessage(item: RealtimeItem): string {
  if (item.type !== 'message') {
    return ''
  }

  return item.content
    .map((part) => {
      if ('text' in part && typeof part.text === 'string') {
        return part.text
      }
      if ('transcript' in part && typeof part.transcript === 'string') {
        return part.transcript
      }
      return ''
    })
    .join('')
    .trim()
}

function renderHistory(history: RealtimeItem[]) {
  const fragments = history
    .filter((item) => item.type === 'message' && (item.role === 'user' || item.role === 'assistant'))
    .map((item) => {
      const text = extractMessage(item)
      if (!text) {
        return ''
      }

      const kind = item.role === 'user' ? 'user' : 'assistant'
      const speaker = item.role === 'user' ? 'Professor:' : 'AI:'
      return `<div class="message ${kind}"><span class="speaker">${speaker}</span><span>${escapeHtml(text)}</span></div>`
    })
    .filter(Boolean)

  logEl.innerHTML = fragments.join('')
  logEl.scrollTop = logEl.scrollHeight
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

async function fetchClientSecret(): Promise<string> {
  const response = await fetch('/token')
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}))
    const message = payload.error?.message || payload.error || 'Failed to create Realtime client secret.'
    throw new Error(String(message))
  }

  const payload = await response.json()
  if (!payload.client_secret) {
    throw new Error('Realtime client secret missing from token response.')
  }
  return payload.client_secret as string
}

async function connect() {
  connectBtn.disabled = true
  disconnectBtn.disabled = false
  setError('')
  setStatus('Connecting...')
  renderHistory([])

  const clientSecret = await fetchClientSecret()

  session = new RealtimeSession(agent, {
    model: 'gpt-realtime',
    config: {
      voice: 'cedar',
      audio: {
        input: {
          noiseReduction: {
            type: 'far_field',
          },
          transcription: {
            model: 'gpt-4o-mini-transcribe',
          },
          turnDetection: {
            type: 'semantic_vad',
            eagerness: 'medium',
          },
        },
      },
    },
  })

  session.on('history_updated', (history) => {
    renderHistory(history)
  })

  session.on('audio_start', () => {
    setStatus('Speaking...')
  })

  session.on('audio_stopped', () => {
    setStatus('Listening...')
  })

  session.on('audio_interrupted', () => {
    setStatus('Listening...')
  })

  session.on('transport_event', (event) => {
    if (event.type === 'input_audio_buffer.speech_started') {
      setStatus('Professor speaking...')
    } else if (event.type === 'input_audio_buffer.speech_stopped') {
      setStatus('Thinking...')
    }
  })

  session.on('error', (event) => {
    const message =
      typeof event.error === 'string'
        ? event.error
        : (event.error as { message?: string })?.message || 'Realtime session error.'
    setError(message)
  })

  try {
    await session.connect({ apiKey: clientSecret })
    setStatus('Listening...')
  } catch (error) {
    session.close()
    session = null
    connectBtn.disabled = false
    disconnectBtn.disabled = true
    setStatus('Disconnected')
    throw error
  }
}

function disconnect() {
  if (session) {
    session.close()
    session = null
  }
  connectBtn.disabled = false
  disconnectBtn.disabled = true
  setStatus('Disconnected')
}

connectBtn.addEventListener('click', async () => {
  try {
    await connect()
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    setError(message)
    disconnect()
  }
})

disconnectBtn.addEventListener('click', () => {
  disconnect()
})
