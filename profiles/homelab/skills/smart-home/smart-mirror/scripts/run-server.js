/**
 * HermesMirror Headless Server — Log-Capture Wrapper
 *
 * Node.js buffers stdout when not connected to a TTY (common in background
 * processes and CI). This wrapper captures all stdout and stderr to a file
 * while also piping through to the terminal for real-time visibility.
 *
 * Usage:
 *   node scripts/run-server.js
 *
 * Watch live:
 *   tail -f /tmp/hermesmirror-server.log
 */
const { spawn } = require("child_process");
const fs = require("fs");

const LOG_PATH = "/tmp/hermesmirror-server.log";
const log = fs.createWriteStream(LOG_PATH, { flags: "w" });

const child = spawn("node", ["serveronly/index.js"], {
  cwd: __dirname + "/..",
  stdio: ["inherit", "pipe", "pipe"],
  env: { ...process.env, FORCE_COLOR: "0" },
});

child.stdout.on("data", (d) => {
  log.write(d);
  process.stdout.write(d);
});

child.stderr.on("data", (d) => {
  log.write(d);
  process.stderr.write(d);
});

child.on("exit", (code) => {
  log.write(`\n--- EXIT CODE: ${code} ---\n`);
  log.end();
  console.log(`\nServer exited (code ${code}). Full log at ${LOG_PATH}`);
  process.exit(code);
});

console.log(`HermesMirror server starting — log file: ${LOG_PATH}`);
