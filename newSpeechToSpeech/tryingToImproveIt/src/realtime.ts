import { RealtimeAgent, RealtimeSession } from '@openai/agents/realtime'

const DEFAULT_INSTRUCTIONS =
  'You are a helpful assistant. Keep your messages brief and concise.'
const TOKEN_ENDPOINT = 'http://127.0.0.1:8787/token'

async function fetchEphemeralKey(): Promise<string> {
  const response = await fetch(TOKEN_ENDPOINT)
  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.error || 'Failed to fetch an ephemeral Realtime key.')
  }

  if (!data.value) {
    throw new Error('Token endpoint returned no ephemeral key.')
  }

  return data.value
}

function extractMessageText(item: any): string {
  if (item?.type !== 'message' || !Array.isArray(item.content)) {
    return ''
  }

  return item.content
    .map((contentPart: any) => {
      if (contentPart.type === 'input_text' || contentPart.type === 'output_text') {
        return contentPart.text || ''
      }
      if (contentPart.type === 'input_audio' || contentPart.type === 'output_audio') {
        return contentPart.transcript || ''
      }
      return ''
    })
    .join(' ')
    .trim()
}

function renderTranscript(history: any[], transcriptEl: HTMLElement) {
  const transcriptItems = history
    .filter((item) => item?.type === 'message' && (item.role === 'user' || item.role === 'assistant'))
    .map((item) => ({
      id: item.itemId,
      role: item.role,
      status: item.status,
      text: extractMessageText(item),
    }))
    .filter((item) => item.text)
    .reverse()

  if (!transcriptItems.length) {
    transcriptEl.innerHTML = '<p class="transcript-empty">Transcript will appear here once the conversation starts.</p>'
    return
  }

  transcriptEl.innerHTML = transcriptItems
    .map(
      (item) => `
        <article class="transcript-item transcript-item-${item.role}">
          <header class="transcript-meta">
            <span class="transcript-speaker">${item.role === 'user' ? 'You' : 'Assistant'}</span>
            <span class="transcript-state">${item.status?.replace('_', ' ') ?? 'completed'}</span>
          </header>
          <p class="transcript-text">${item.text}</p>
        </article>
      `,
    )
    .join('')
}

export async function startRealtimeDemo(
  statusEl: HTMLElement,
  transcriptEl: HTMLElement,
) {
  const agent = new RealtimeAgent({
    name: 'Assistant',
    instructions: DEFAULT_INSTRUCTIONS,
  })

  const session = new RealtimeSession(agent, {
    model: 'gpt-realtime',
    config: {
      voice: 'cedar',
      turnDetection: {
        type: 'semantic_vad',
        eagerness: 'medium',
      },
    },
  })

  session.on('history_updated', (history) => {
    renderTranscript(history, transcriptEl)
  })

  try {
    statusEl.textContent = 'Fetching ephemeral key...'
    const apiKey = await fetchEphemeralKey()
    statusEl.textContent = 'Connecting...'
    await session.connect({ apiKey })
    statusEl.textContent = 'Connected. Start speaking.'
    console.log('Realtime session connected.')
  } catch (error) {
    statusEl.textContent = 'Connection failed. Check the console.'
    console.error(error)
  }
}
