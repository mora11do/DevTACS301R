import './style.css'
import { startRealtimeDemo } from './realtime.ts'

document.querySelector<HTMLDivElement>('#app')!.innerHTML = `
  <main class="page">
    <section class="card">
      <div class="hero">
        <div>
          <h1>Realtime Audio Demo</h1>
          <p>
            This browser demo uses the OpenAI Realtime API through the TypeScript
            agents library.
          </p>
          <p>
            When you load the page, the dev server will mint an ephemeral realtime
            key automatically and then ask for microphone access.
          </p>
        </div>
        <p id="status" class="status">Waiting to connect...</p>
      </div>
      <section class="transcript-panel">
        <div class="transcript-header">
          <h2>Live Transcript</h2>
          <p>Both sides of the conversation appear here as the session updates.</p>
        </div>
        <div id="transcript" class="transcript-log">
          <p class="transcript-empty">Transcript will appear here once the conversation starts.</p>
        </div>
      </section>
    </section>
  </main>
`

void startRealtimeDemo(
  document.querySelector<HTMLElement>('#status')!,
  document.querySelector<HTMLElement>('#transcript')!,
)
