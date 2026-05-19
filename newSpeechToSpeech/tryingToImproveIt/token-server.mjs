import fs from 'node:fs'
import http from 'node:http'
import path from 'node:path'

const TOKEN_PORT = 8787

function readApiKeyFromEnvFile(envPath) {
  if (!fs.existsSync(envPath)) {
    return ''
  }

  for (const rawLine of fs.readFileSync(envPath, 'utf8').split(/\r?\n/)) {
    const line = rawLine.trim()
    if (!line || line.startsWith('#') || !line.includes('=')) {
      continue
    }

    const [key, ...rest] = line.split('=')
    if (key.trim() !== 'OPENAI_API_KEY') {
      continue
    }

    return rest.join('=').trim().replace(/^['"]|['"]$/g, '')
  }

  return ''
}

function resolveApiKey() {
  return (
    process.env.OPENAI_API_KEY ||
    readApiKeyFromEnvFile(path.resolve(process.cwd(), '.env')) ||
    readApiKeyFromEnvFile(path.resolve(process.cwd(), '..', '.env'))
  )
}

function writeJson(res, statusCode, payload) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  })
  res.end(JSON.stringify(payload))
}

const server = http.createServer(async (req, res) => {
  if (!req.url) {
    writeJson(res, 404, { error: 'Missing URL.' })
    return
  }

  if (req.method === 'OPTIONS') {
    writeJson(res, 204, {})
    return
  }

  if (req.method !== 'GET' || req.url !== '/token') {
    writeJson(res, 404, { error: 'Not found.' })
    return
  }

  const apiKey = resolveApiKey()
  if (!apiKey) {
    writeJson(res, 500, {
      error:
        'OPENAI_API_KEY is missing. Set it in your shell, tryingToImproveIt/.env, or the repo-root .env.',
    })
    return
  }

  try {
    const upstream = await fetch(
      'https://api.openai.com/v1/realtime/client_secrets',
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session: {
            type: 'realtime',
            model: 'gpt-realtime',
            audio: {
              output: {
                voice: 'cedar',
              },
            },
          },
        }),
      },
    )

    const text = await upstream.text()
    res.writeHead(upstream.status, {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET,OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    })
    res.end(text)
  } catch (error) {
    const message =
      error instanceof Error ? error.message : 'Failed to mint token.'
    writeJson(res, 500, { error: message })
  }
})

server.listen(TOKEN_PORT, '127.0.0.1', () => {
  console.log(`Token server listening on http://127.0.0.1:${TOKEN_PORT}`)
})
