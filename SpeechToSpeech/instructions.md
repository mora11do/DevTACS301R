Build a classroom voice demo using the OpenAI Realtime API
Build a Python-based web app that demonstrates real-time speech-to-speech conversation using the OpenAI Realtime API (gpt-realtime-2). The purpose is a classroom demo where a professor speaks into a laptop mic and the model responds through overhead speakers (via HDMI). The conversation transcript should display on screen (projected for the class to read).
Tech stack

Python backend (FastAPI or Flask, your choice)
Simple HTML/JS frontend served by the Python server
WebSocket connection from the browser to the OpenAI Realtime API (use WebRTC if easier, otherwise WebSocket)
No frameworks on the frontend — plain HTML/CSS/JS is fine

API details

Model: gpt-realtime-2
The API key will be provided via a .env file as OPENAI_API_KEY
Use the standard OpenAI Realtime API WebSocket endpoint: wss://api.openai.com/v1/realtime

Critical audio configuration — apply these settings in the session.update event:
json{
  "type": "session.update",
  "session": {
    "model": "gpt-realtime-2",
    "audio": {
      "input": {
        "noise_reduction": { "type": "far_field" },
        "turn_detection": {
          "type": "server_vad",
          "threshold": 0.75,
          "silence_duration_ms": 800
        }
      }
    }
  }
}
Explanation of why these settings matter (so Codex understands and doesn't remove them):

far_field noise reduction: the laptop mic and HDMI overhead speakers are in the same room. Without this, the model hears its own audio output coming back through the mic and responds to itself in a feedback loop. far_field does acoustic echo cancellation optimized for this separated mic/speaker scenario.
threshold: 0.75: raises the voice activity detection bar so faint echoes that survive echo cancellation don't trigger a new response. Default is 0.5.
silence_duration_ms: 800: gives the speaker a little more time before the model decides they've stopped talking, reducing false triggers from brief audio gaps.

Interruption support
The model must support being interrupted mid-response, just like a human conversation. When the VAD detects the user speaking while the model is responding:

Cancel the in-progress response (response.cancel)
Clear the output audio buffer (output_audio_buffer.clear)
Truncate the conversation item (conversation.item.truncate) so the model knows where it was cut off
Start listening for the new input immediately

Transcript UI requirements

Display the full conversation transcript on screen, clearly distinguishing user speech vs model responses (e.g. different colors or labels like "Professor:" and "AI:")
Transcript should update in real time as the model speaks (stream the words as they arrive, don't wait for the full response)
Text should be large enough to read on a projector from the back of a classroom (minimum 20px, ideally larger)
Show a clear visual status indicator: "Listening...", "Thinking...", "Speaking..." so the class knows what state the model is in
Dark background is preferable for projector readability
Auto-scroll to the latest message

General behavior

The assistant should be open-ended and conversational — no specific subject or persona, just a capable general assistant
System prompt: "You are a helpful, articulate assistant being demonstrated in a university classroom. Keep responses clear and engaging, suitable for an academic audience. You can discuss any topic."
The demo should run with a single python app.py command and open in the browser at localhost:8000 (or similar)
Include a requirements.txt
Include a .env.example file showing the required env vars

Known classroom constraints to keep in mind

Only the professor near the laptop mic will be speaking — no need for room-wide mic pickup
Audio output goes through HDMI to overhead classroom speakers
The echo/feedback problem described above is the primary technical risk — the audio settings above are the mitigation
No push-to-talk — the interaction must be fully hands-free and natural
