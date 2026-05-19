# newSpeechToSpeech

This folder contains a few different speech-to-speech experiments and snapshots.

## Main folders

### `OLDbestWorkingSpeechToSpeech`
This is the preserved copy of the browser-based demo that was working best at the time.

- Treat this as a frozen snapshot.
- It exists so there is a known-good reference point.
- The intent is to avoid editing it unless there is a deliberate reason to update the snapshot itself.

### `class_material`
This is the original teaching/demo material folder.

- It includes the older Python demos for speech, transcription, and realtime audio.
- It also includes the original `realtime-ts` browser demo that was running through Vite.
- This folder is useful as the source/origin of the examples, but it is not the main place for current iteration.

### `tryingToImproveIt`
This is the active browser-based experiment folder.

- This is where current changes should go.
- It is based on the browser realtime demo rather than the Python path.
- It currently includes automatic ephemeral token fetching, a simple local launcher flow, and an on-screen transcript.

## Launchers

### `run_tryingToImproveIt.cmd`
Starts the current browser-based experiment in `tryingToImproveIt`.

### `run_realtime_safe.cmd`
Starts the safer Python-based realtime experiment from the older `class_material` path.

### `run_realtime_barge_in.cmd`
Starts the interruptible Python-based realtime experiment from the older `class_material` path.

## Current recommendation

If the goal is to keep improving the best browser demo, work in `tryingToImproveIt`.

If the goal is to reference the known-good snapshot, look at `OLDbestWorkingSpeechToSpeech`.

If the goal is to inspect the older course/demo material, look at `class_material`.
