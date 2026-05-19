import { spawn } from 'node:child_process'

const tokenServer = spawn(process.execPath, ['token-server.mjs'], {
  stdio: 'inherit',
  shell: false,
})

const viteProcess = spawn('cmd.exe', ['/c', 'npm.cmd', 'run', 'vite:dev'], {
  stdio: 'inherit',
  shell: false,
})

function shutdown(exitCode = 0) {
  if (!tokenServer.killed) {
    tokenServer.kill()
  }
  if (!viteProcess.killed) {
    viteProcess.kill()
  }
  process.exit(exitCode)
}

tokenServer.on('exit', (code) => {
  if (code && code !== 0) {
    shutdown(code)
  }
})

viteProcess.on('exit', (code) => {
  shutdown(code ?? 0)
})

process.on('SIGINT', () => shutdown(0))
process.on('SIGTERM', () => shutdown(0))
