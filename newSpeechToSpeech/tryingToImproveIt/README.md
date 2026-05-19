# Realtime TypeScript Demo

This is a minimal browser-based Realtime API demo for students.
It uses Vite and `@openai/agents` to create a voice conversation in the browser via WebRTC.

## Files

- `src/main.ts`: bootstraps the page and starts the realtime session
- `src/style.css`: simple page styling
- `index.html`: Vite entry page
- `package.json`: dependencies and npm scripts
- `token-server.mjs`: local helper that mints ephemeral Realtime keys
- `dev.mjs`: starts both the token server and Vite dev server

## Setup

1. Run `npm install`
2. Make `OPENAI_API_KEY` available in your shell, in `tryingToImproveIt/.env`, or in the repo-root `.env`
3. Run `npm run dev`
4. Open the page and allow microphone access

Simplest launcher from the repo root:

```bash
run_tryingToImproveIt.cmd
```

## Important

Do not commit ephemeral keys or long-lived API keys.
This version mints the ephemeral key automatically through a small local helper server, so the browser does not need a manual paste step.

## How It Works

This section explains the actual runtime flow in more detail.

At a high level, this project is a browser-based speech-to-speech demo that uses the OpenAI Realtime API through the JavaScript Agents SDK. The key design choice is that the browser is responsible for the actual voice session, while a tiny local helper process is responsible for minting short-lived authentication tokens. That split is what makes the demo feel simple to use without exposing a long-lived API key directly in frontend code.

### 1. Startup flow

When you run:

```bash
npm run dev
```

the project does not just start Vite directly.

Instead, `package.json` points `dev` at `dev.mjs`.

`dev.mjs` starts two processes:

1. `token-server.mjs`
2. `vite`

The token server listens locally on `127.0.0.1:8787`.
Vite serves the frontend app for the browser.

This means the app is really a small two-part local system:

- a frontend dev server
- a local token minting helper

The repo-root launcher `run_tryingToImproveIt.cmd` is just a convenience wrapper that changes into this directory and runs `npm.cmd run dev`.

### 2. Why there is a token server at all

The browser should not be given your normal OpenAI API key directly.

Instead, the correct pattern for this kind of browser Realtime app is:

1. a trusted local/server-side component uses `OPENAI_API_KEY`
2. that trusted component requests a short-lived Realtime client secret
3. the browser receives only that short-lived secret
4. the browser uses the short-lived secret to connect to the Realtime API

That is what `token-server.mjs` is doing.

It reads `OPENAI_API_KEY` from one of these places:

- the current shell environment
- `tryingToImproveIt/.env`
- the repo-root `.env`

Then, when the frontend asks for a token, the helper sends a request to OpenAI's `realtime/client_secrets` endpoint and gets back an ephemeral key that starts with `ek_`.

That key is temporary. The point is not to make expiration go away. The point is to make the refresh happen automatically so you do not have to manually copy/paste the token every time you test the app.

### 3. Frontend connection flow

Once the browser loads the page, `src/main.ts` creates the visible page structure and calls `startRealtimeDemo(...)` from `src/realtime.ts`.

That function does the following:

1. creates a `RealtimeAgent`
2. creates a `RealtimeSession`
3. fetches a fresh ephemeral key from `http://127.0.0.1:8787/token`
4. calls `session.connect({ apiKey })`
5. lets the browser ask for microphone permission

So the browser itself is still doing the actual Realtime voice session. The local helper is only there to handle secure token minting.

### 4. Why this path works better than the older Python path

This project is based on the browser/WebRTC approach rather than the older Python `ffmpeg` streaming approach.

That matters because browsers usually do a better job with:

- microphone capture
- output playback
- device routing
- built-in echo cancellation
- built-in noise suppression
- low-friction permission handling

So even though this project does not contain custom low-level echo-cancellation code, it often behaves better simply because the browser audio stack is doing more of the hard work for you.

### 5. Transcript flow

This project now shows a live transcript on screen for both the user and the assistant.

That transcript is not assembled by separately listening to raw audio bytes in the UI.
Instead, it is rendered from the session history maintained by the Realtime SDK.

More specifically:

- `src/realtime.ts` listens for `history_updated`
- the handler receives the current normalized session history
- the code filters that history down to user and assistant message items
- it extracts text from the message content
- it renders those entries into the transcript panel

This is a good design because the SDK is already maintaining a structured representation of the conversation. That means the UI does not need to guess whether a particular transcript fragment belongs to the user or the assistant.

The transcript currently shows:

- `You` for user messages
- `Assistant` for assistant messages
- the item status if present

The transcript order was also changed so the newest messages appear first. That means the conversation effectively grows upward, which makes it easier to see the most recent turn without scrolling to the bottom.

### 6. What files are responsible for what

Here is the practical file map:

- `src/main.ts`
  Builds the page structure and passes DOM elements into the realtime startup code.

- `src/realtime.ts`
  Contains the session startup logic, token fetch call, OpenAI realtime session setup, and transcript rendering.

- `src/style.css`
  Controls the visual layout, including the transcript panel.

- `token-server.mjs`
  Local helper server that reads `OPENAI_API_KEY`, asks OpenAI for an ephemeral Realtime client secret, and returns it to the browser.

- `dev.mjs`
  Process orchestrator that starts both the token helper and the Vite frontend server together.

- `package.json`
  Defines the scripts and dependency list, including the `dev` command that launches the whole local flow.

### 7. What happens when something goes wrong

There are a few common failure modes:

- Missing `OPENAI_API_KEY`
  The token helper cannot mint a client secret, so the frontend will fail before connecting.

- Token helper not running
  The frontend will fail to fetch `http://127.0.0.1:8787/token`.

- Vite not running
  The browser app itself will not load.

- Microphone permission denied
  The page may load and the session may connect, but audio input will not work correctly.

- Expired ephemeral key
  Normally this is avoided because the browser fetches a fresh one right before connecting. If the page sits around too long and reconnect logic were added later, then a new token would need to be minted again.

### 8. Current design intention

The intention of this folder is not to be the permanent polished final product. It is the active iteration space for improving the browser-based demo that has been working best so far.

So the practical mental model is:

- `OLDbestWorkingSpeechToSpeech` is the frozen reference copy
- `tryingToImproveIt` is the place to keep experimenting
- this README exists to explain the moving pieces so future edits are less mysterious

