#!/usr/bin/env node
// qihang-bridge —— 跨平台零依赖浏览器接入工具（仓库维护用，不随 release 交付）
// 契约：不写死任何路径、不假设任何端口；一切从系统检索 + DevToolsActivePort 取得。
// 用法：node scripts/browser-bridge/qihang-bridge.mjs <doctor|open|text|eval|tabs|tab-new|shot>
// 依赖：node >= 22（自带 fetch / WebSocket）。无第三方包。

import { execFile, spawn } from "node:child_process";
import { promisify } from "node:util";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const run = promisify(execFile);
const HOME = os.homedir();
const IS_WIN = process.platform === "win32";
const IS_MAC = process.platform === "darwin";
const STATE_DIR = path.join(HOME, ".qihang");
const STATE_FILE = path.join(STATE_DIR, "bridge.json");
const BROWSER_ROOT = path.join(STATE_DIR, "browser");

const BROWSERS = [
  {
    name: "edge",
    win: ["msedge.exe"],
    mac: ["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
          path.join(HOME, "Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge")],
    linux: ["microsoft-edge", "microsoft-edge-stable", "microsoft-edge-beta"],
    linuxPaths: ["/opt/microsoft/msedge/microsoft-edge", "/usr/bin/microsoft-edge"],
    macBundleId: "com.microsoft.edgemac",
    profileName: { win: "Microsoft/Edge/User Data", mac: "Microsoft Edge", linux: "microsoft-edge" },
  },
  {
    name: "chrome",
    win: ["chrome.exe"],
    mac: ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
          path.join(HOME, "Applications/Google Chrome.app/Contents/MacOS/Google Chrome")],
    linux: ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"],
    linuxPaths: ["/opt/google/chrome/chrome", "/snap/bin/chromium"],
    macBundleId: "com.google.Chrome",
    profileName: { win: "Google/Chrome/User Data", mac: "Google/Chrome", linux: "google-chrome" },
  },
];

// ---------- 1. 浏览器可执行文件检索 ----------
async function regQuery(key) {
  try {
    const { stdout } = await run("reg", ["query", key, "/ve"], { windowsHide: true });
    for (const line of stdout.split(/\r?\n/)) {
      const m = line.match(/REG_SZ\s+(.+?)\s*$/);
      if (m) return m[1];
    }
  } catch { /* key 不存在 */ }
  return null;
}

function existsFile(p) {
  try { return fs.statSync(p).isFile(); } catch { return false; }
}

async function findExe(b) {
  const found = [];
  if (IS_WIN) {
    // 优先级 1：注册表 App Paths（HKLM / WOW6432Node / HKCU）
    const roots = [
      "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths",
      "HKLM\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\App Paths",
      "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths",
    ];
    for (const exe of b.win) {
      for (const root of roots) {
        const v = await regQuery(`${root}\\${exe}`);
        if (v && existsFile(v)) { found.push({ source: `registry:${root.split("\\")[0]}`, exe: v }); break; }
      }
    }
    // 优先级 2：文件候选
    const bases = [process.env["ProgramFiles(x86)"], process.env.ProgramFiles, process.env.LOCALAPPDATA].filter(Boolean);
    const rels = b.name === "edge"
      ? ["Microsoft\\Edge\\Application\\msedge.exe"]
      : ["Google\\Chrome\\Application\\chrome.exe"];
    for (const base of bases) {
      for (const rel of rels) {
        const p = path.join(base, rel);
        if (existsFile(p) && !found.some(f => f.exe.toLowerCase() === p.toLowerCase())) {
          found.push({ source: "filesystem", exe: p });
        }
      }
    }
  } else if (IS_MAC) {
    try {
      const { stdout } = await run("mdfind", [`kMDItemCFBundleIdentifier == '${b.macBundleId}'`]);
      for (const line of stdout.split(/\r?\n/).filter(Boolean)) {
        const macos = path.join(line, "Contents/MacOS");
        try {
          for (const f of fs.readdirSync(macos)) {
            const p = path.join(macos, f);
            if (existsFile(p) && !found.some(x => x.exe === p)) found.push({ source: "mdfind", exe: p });
          }
        } catch { /* ignore */ }
      }
    } catch { /* mdfind 不可用 */ }
    for (const p of b.mac) {
      if (existsFile(p) && !found.some(x => x.exe === p)) found.push({ source: "filesystem", exe: p });
    }
  } else {
    for (const name of b.linux) {
      try {
        const { stdout } = await run("which", [name]);
        const p = stdout.trim();
        if (p && existsFile(p) && !found.some(x => x.exe === p)) found.push({ source: "which", exe: p });
      } catch { /* not found */ }
    }
    for (const p of b.linuxPaths) {
      if (existsFile(p) && !found.some(x => x.exe === p)) found.push({ source: "filesystem", exe: p });
    }
  }
  return found;
}

// ---------- 2. 运行中实例反查 ----------
// 进程名（msedge/chrome）→ BROWSERS 内部键（edge/chrome）。缺失会导致状态文件写坏、profile 复用失效。
function browserKey(s) {
  const t = String(s || "").toLowerCase();
  if (/edge|msedge/.test(t)) return "edge";
  if (/chrome|chromium/.test(t)) return "chrome";
  return null;
}

function parseArgs(cmdline) {
  const out = {};
  const mPort = cmdline.match(/--remote-debugging-port=(\d+)/);
  const mDir = cmdline.match(/--user-data-dir=(?:"([^"]+)"|(\S+))/);
  if (mPort) out.port = Number(mPort[1]);
  if (mDir) out.userDataDir = (mDir[1] || mDir[2] || "").replace(/"+$/, "");
  return out;
}

const PROCESS_WARNINGS = [];

async function listBrowserProcesses() {
  const procs = [];
  try {
    if (IS_WIN) {
      const ps = [
        "$ErrorActionPreference='SilentlyContinue';",
        "Get-CimInstance Win32_Process",
        "| Where-Object { $_.Name -in @('msedge.exe','chrome.exe') }",
        "| Select-Object ProcessId,Name,ExecutablePath,CommandLine",
        "| ConvertTo-Json -Compress -Depth 3",
      ].join(" ");
      const { stdout } = await run("powershell", ["-NoProfile", "-NonInteractive", "-Command", ps], { maxBuffer: 1 << 24 });
      const raw = JSON.parse(stdout.trim() || "[]");
      for (const r of Array.isArray(raw) ? raw : [raw]) {
        procs.push({
          pid: r.ProcessId,
          name: (r.Name || "").replace(/\.exe$/i, ""),
          exe: r.ExecutablePath,
          cmdline: r.CommandLine || "",
        });
      }
    } else {
      const { stdout } = await run("ps", ["-eo", "pid,args"], { maxBuffer: 1 << 24 });
      for (const line of stdout.split(/\r?\n/)) {
        if (!/msedge|Microsoft Edge|chrome|Chromium/i.test(line)) continue;
        const m = line.trim().match(/^(\d+)\s+(.*)$/);
        if (!m) continue;
        const cmdline = m[2];
        const exe = (cmdline.match(/^"([^"]+)"/) || cmdline.match(/^(\S+)/) || [])[1] || "";
        const name = /edge/i.test(exe) ? "edge" : "chrome";
        procs.push({ pid: Number(m[1]), name, exe, cmdline });
      }
    }
  } catch (e) {
    PROCESS_WARNINGS.push(`进程反查失败（${process.platform}）：${e.message}`);
  }
  return procs;
}

function readActivePort(profile) {
  try {
    const lines = fs.readFileSync(path.join(profile, "DevToolsActivePort"), "utf8").split(/\r?\n/).filter(Boolean);
    if (lines.length >= 2) return { port: Number(lines[0]), wsPath: lines[1] };
  } catch { /* 无文件或未写出 */ }
  return null;
}

async function runningDebugInstances(procs) {
  const out = [];
  for (const p of procs) {
    if (!/--remote-debugging-port/.test(p.cmdline)) continue;
    if (/--type=/.test(p.cmdline)) continue; // 只取主进程
    const a = parseArgs(p.cmdline);
    if (a.port === undefined) continue;
    if (a.port) {
      a.portFrom = "cmdline";
    } else {
      // --remote-debugging-port=0：cmdline 里没有真实端口，必须回读 DevToolsActivePort
      if (!a.userDataDir) continue;
      const real = readActivePort(a.userDataDir);
      if (!real) continue;
      a.port = real.port;
      a.wsPath = real.wsPath;
      a.portFrom = "DevToolsActivePort";
    }
    if (!(await isCdpAlive(a.port))) continue; // 陈旧/已死实例剔除
    out.push({ ...p, ...a, procName: p.name, name: browserKey(p.name || p.exe) || p.name });
  }
  return out;
}

// ---------- 3. 状态文件 ----------
function readState() {
  try { return JSON.parse(fs.readFileSync(STATE_FILE, "utf8")); } catch { return {}; }
}
function writeState(patch) {
  const cur = readState();
  const next = { ...cur, ...patch };
  fs.mkdirSync(STATE_DIR, { recursive: true });
  fs.writeFileSync(STATE_FILE, JSON.stringify(next, null, 2), "utf8");
  return next;
}

// ---------- 4. 启动 + 读 DevToolsActivePort ----------
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function launchBrowser(exe, profile, url) {
  fs.mkdirSync(profile, { recursive: true });
  const args = [
    "--remote-debugging-port=0",
    `--user-data-dir=${profile}`,
    "--no-first-run",
    "--no-default-browser-check",
  ];
  if (process.env.QIHANG_HEADLESS === "1") args.push("--headless=new");
  args.push(url || "about:blank");
  // 必须用 spawn：execFile 的子进程会随本进程退出而被回收（实测 detached 亦无效），
  // 导致浏览器无法跨 agent 轮次存活。spawn + detached + unref 才能留下常驻实例。
  const child = spawn(exe, args, { detached: true, windowsHide: false, stdio: "ignore" });
  // 若该 profile 已被另一个实例占用，Chromium 的单实例锁会让这个新进程「交接后立即退出」，
  // 且永远不写 DevToolsActivePort。实测：成功启动时子进程存活、225ms 内即写出端口文件。
  // 因此「子进程立即退出」是可靠的快速失败信号，可把 40s 超时压到约 1.2s。
  let exited = false;
  child.on("exit", () => { exited = true; });
  child.on("error", () => { exited = true; });
  child.unref();
  return waitForPort(profile, Date.now(), { exited: () => exited });
}

async function waitForPort(profile, startedAt, { timeoutMs = 20000, exited = () => false } = {}) {
  const f = path.join(profile, "DevToolsActivePort");
  const deadline = Date.now() + timeoutMs;
  const graceMs = startedAt + 1200;
  while (Date.now() < deadline) {
    try {
      const st = fs.statSync(f);
      // 必须是本次启动新写的，否则可能是上次残留
      if (st.mtimeMs >= startedAt - 1000) {
        const lines = fs.readFileSync(f, "utf8").split(/\r?\n/).filter(Boolean);
        if (lines.length >= 2 && (await isCdpAlive(Number(lines[0])))) {
          return { port: Number(lines[0]), wsPath: lines[1] };
        }
      }
    } catch { /* 尚未写出 */ }
    if (exited() && Date.now() > graceMs) {
      throw new Error(
        `浏览器进程启动后立即退出：profile 已被另一个实例占用（Chromium 单实例锁）\n` +
        `  profile: ${profile}\n` +
        `  处理：关闭正在使用该 profile 的浏览器窗口，或改用 --browser ${BROWSERS[0].name === "edge" ? "chrome" : "edge"}`
      );
    }
    await sleep(200);
  }
  throw new Error(`等待 DevToolsActivePort 超时（${Math.round(timeoutMs / 1000)}s）：${profile}`);
}

async function isCdpAlive(port) {
  try {
    const ctl = AbortSignal.timeout(1500);
    const r = await fetch(`http://127.0.0.1:${port}/json/version`, { signal: ctl });
    const j = await r.json();
    return Boolean(j && j.webSocketDebuggerUrl);
  } catch { return false; }
}

// ---------- 5. 极简 CDP 客户端 ----------
const INTERNAL_URL = /^(edge|chrome|about|devtools|chrome-extension|edge-extension):/i;

// 多标签页选择：优先非内部页；可用 tab 关键字（URL 子串或 1-based 序号）指定。
// 显式指定但匹配不到时报错——静默回退到别的标签页会让 agent 读到错误页面。
function pickPage(pages, tab) {
  if (!pages.length) return null;
  if (tab !== undefined && tab !== true) {
    const s = String(tab);
    if (/^\d+$/.test(s)) {
      const i = Number(s) - 1;
      if (!pages[i]) throw new Error(`--tab ${s} 越界：当前只有 ${pages.length} 个 page 目标（用 tabs 查看）`);
      return pages[i];
    }
    const hit = pages.find(p => (p.url || "").includes(s) || (p.title || "").includes(s));
    if (!hit) throw new Error(`--tab "${s}" 未匹配任何标签页（用 tabs 查看）`);
    return hit;
  }
  const real = pages.filter(p => !INTERNAL_URL.test(p.url || ""));
  const pool = real.length ? real : pages;
  return pool[pool.length - 1];
}

// 统一的页面求值：把 CDP 的 exceptionDetails 变成真实错误，避免「静默 undefined + exit 0」
// （agent 会把 undefined 当成"页面为空"，这是最危险的一类失败）
async function evalIn(inst, expression, { retryMs = 0, retryUntil = null } = {}) {
  const deadline = Date.now() + retryMs;
  for (;;) {
    const r = await inst.send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    if (r.error) throw new Error(`Runtime.evaluate 失败：${r.error.message}`);
    const d = r.result;
    if (d?.exceptionDetails) {
      throw new Error(`页面抛出异常：${d.exceptionDetails.exception?.description || d.exceptionDetails.text || JSON.stringify(d.exceptionDetails)}`);
    }
    const v = d?.result?.value;
    if (!retryUntil || retryUntil(v) || Date.now() > deadline) return v;
    await sleep(250);
  }
}

// 返回结构化结果，body 缺失时不再抛异常（页面尚在加载）
const TEXT_EXPR =
  "(function(){var b=document.body;return JSON.stringify({title:document.title,url:location.href,ready:document.readyState,text:b?b.innerText:''})})()";

async function cdp(port, { tab, activate = false } = {}) {
  const version = await (await fetch(`http://127.0.0.1:${port}/json/version`)).json();
  const ws = new WebSocket(version.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  let seq = 0;
  const pending = new Map();
  ws.onmessage = e => {
    const msg = JSON.parse(e.data);
    if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
  };
  const send = (method, params = {}, sessionId) => new Promise(res => {
    const id = ++seq;
    pending.set(id, res);
    ws.send(JSON.stringify(sessionId ? { id, method, params, sessionId } : { id, method, params }));
  });
  const targets = await send("Target.getTargets");
  let pages = targets.result.targetInfos.filter(t => t.type === "page");
  // 浏览器存活但一个 page 目标都没有（用户关光了所有标签页）→ 自动新建一个，避免死路
  if (!pages.length) {
    await newTab(port, "about:blank").catch(() => null);
    await sleep(400);
    const again = await send("Target.getTargets");
    pages = again.result.targetInfos.filter(t => t.type === "page");
  }
  let page;
  try {
    page = pickPage(pages, tab);
  } catch (e) {
    await closeWs(ws);
    throw e;
  }
  if (!page) {
    await closeWs(ws);
    throw new Error(`未找到可操作的 page 目标（现有 ${targets.result.targetInfos.length} 个 target，page ${pages.length} 个）`);
  }
  const attached = await send("Target.attachToTarget", { targetId: page.targetId, flatten: true });
  if (!attached.result?.sessionId) {
    await closeWs(ws);
    throw new Error(`attachToTarget 失败：${JSON.stringify(attached.error || attached)}`);
  }
  const sessionId = attached.result.sessionId;
  // 仅截图需要把目标标签页置前台（否则可见模式下可能是空白/陈旧帧）。
  // 默认不置前台 —— 读取 text/eval 时抢用户窗口焦点是不可接受的副作用。
  if (activate) await send("Target.activateTarget", { targetId: page.targetId });
  const inst = {
    port,
    version: version.Browser,
    pageUrl: page.url,
    pageCount: pages.length,
    send: (method, params) => send(method, params, sessionId),
    close: () => closeWs(ws),
  };
  CURRENT = inst;
  return inst;
}

// 列出 page 目标（顺序与 --tab 的序号一致）
async function listTabs(port) {
  const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  return (Array.isArray(list) ? list : []).filter(t => t.type === "page");
}

// 新建标签页。Edge/Chrome 都要求 PUT；部分版本需要 POST，两者都试。
async function newTab(port, url) {
  for (const method of ["PUT", "POST"]) {
    try {
      const r = await fetch(`http://127.0.0.1:${port}/json/new?${encodeURIComponent(url)}`, { method });
      if (r.ok) return await r.json();
    } catch { /* 换下一个方法 */ }
  }
  throw new Error("新建标签页失败：/json/new 不可用");
}

// 关闭 WebSocket 并等待其 close 事件。必须等：直接 ws.close() 后就退出进程会触发
// libuv 断言（!(handle->flags & UV_HANDLE_CLOSING)）而 abort。
function closeWs(ws) {
  return new Promise(res => {
    let done = false, timer;
    const fin = () => { if (done) return; done = true; clearTimeout(timer); res(); };
    timer = setTimeout(fin, 500);
    if (timer.unref) timer.unref();
    ws.onclose = fin;
    ws.onerror = fin;
    try { ws.close(); } catch { fin(); }
  });
}

// 统一收尾：关闭 WS 后让事件循环自然排空。
// 为什么不用 process.exit()：本进程同时存在 undici 的 HTTP keep-alive socket（来自 fetch）
// 与 WebSocket 时，强制退出会在 Node 24/Windows 上触发 libuv 断言并 abort（已最小复现）。
let CURRENT = null;
async function finish(code = 0) {
  process.exitCode = code;
  if (CURRENT) { const c = CURRENT; CURRENT = null; try { await c.close(); } catch { /* ignore */ } }
}

// ---------- 6. 解析入口 ----------
function ensureBrowser({ browserName }) {
  return BROWSERS.find(x => x.name === browserName) || BROWSERS[0];
}

async function resolve({ preferBrowser, url, fresh, tab, port: wantPort, activate = false }) {
  const names = BROWSERS.map(b => b.name);
  if (preferBrowser && !names.includes(preferBrowser)) {
    throw new Error(`未知浏览器 "${preferBrowser}"，可选：${names.join(" / ")}`);
  }
  // ⓪ 显式指定调试端口 → 只接入该端口，不做任何猜测（用于接入用户自己已登录的调试实例）
  if (wantPort) {
    const p = Number(wantPort);
    if (!Number.isInteger(p) || p <= 0 || p > 65535) throw new Error(`--port 必须是 1-65535 的整数，收到 "${wantPort}"`);
    if (!(await isCdpAlive(p))) {
      throw new Error(`端口 ${p} 上没有可用的 CDP 调试实例（用 doctor 查看当前有哪些）`);
    }
    const inst = await cdp(p, { tab, activate });
    // 显式按端口接入的是「用户的」实例：状态里只留端口，清掉自有实例字段，
    // 避免与自有 profile/exe 混成一条记录（曾导致 close_own 误判）。
    writeState({
      port: p, via: "attach-port",
      browser: undefined, exe: undefined, exeSource: undefined,
      profile: undefined, profileSource: undefined, wsPath: undefined,
    });
    return { inst, how: `attach-port:${p}`, detail: { port: p } };
  }
  const procs = await listBrowserProcesses();
  const live = await runningDebugInstances(procs);
  const state = readState();

  // ① 已有「本包自己的」调试实例 → 直接接入（零用户操作）
  //    ⚠️ 绝不隐式接管用户自己的调试实例：用户实例只能通过 --port 显式接入。
  //    否则 `open <url>` 会在零状态下把用户已登录的标签页导航走（已实测的破坏性副作用）。
  if (live.length && !fresh) {
    const isOurs = l => l.userDataDir && path.resolve(l.userDataDir).startsWith(path.resolve(BROWSER_ROOT) + path.sep);
    const own = state.profile
      ? live.find(l => l.userDataDir && path.resolve(l.userDataDir) === path.resolve(state.profile))
      : null;
    const pick = own || live.find(l => isOurs(l) && (!preferBrowser || l.name === preferBrowser)) || live.find(isOurs);
    if (pick) {
      const inst = await cdp(pick.port, { tab, activate });
      writeState({ browser: pick.name, exe: pick.exe, profile: pick.userDataDir, port: pick.port, wsPath: pick.wsPath, via: "attach-running" });
      return { inst, how: "attach-running", detail: pick };
    }
    // 有别人的实例但没有自己的 → 不碰它，继续走「自己启动」分支
  }

  // ②/③ 需要启动：检索 exe + 定 profile
  const order = preferBrowser
    ? [preferBrowser, ...BROWSERS.map(b => b.name).filter(n => n !== preferBrowser)]
    : BROWSERS.map(b => b.name);

  const attempts = [];
  for (const name of order) {
    const b = ensureBrowser({ browserName: name });
    const exes = await findExe(b);
    if (!exes.length) { attempts.push(`${name}: 未找到可执行文件`); continue; }

    // profile 优先级：状态文件 → 新建（平台约定位置）
    let profile = null, profileSource = null;
    if (state.browser === name && state.profile && fs.existsSync(state.profile)) {
      profile = state.profile; profileSource = "state-file";
      // 该 profile 已被运行中实例占用 → 直接接入，避免重复启动
      const owner = live.find(l => l.userDataDir && path.resolve(l.userDataDir) === path.resolve(profile));
      if (owner) {
        try {
          const inst = await cdp(owner.port, { tab, activate });
          writeState({ browser: name, exe: owner.exe, profile, port: owner.port, wsPath: owner.wsPath, via: "attach-profile-owner" });
          return { inst, how: "attach-profile-owner", detail: owner };
        } catch (e) {
          // profile 被占用且接入失败：不能再对同一 profile 启动，直接换下一个浏览器
          attempts.push(`${name}: 占用实例接入失败 ${e.message}`);
          continue;
        }
      }
    }
    if (!profile) {
      profile = path.join(BROWSER_ROOT, name);
      profileSource = "new";
    }

    try {
      const { port, wsPath } = await launchBrowser(exes[0].exe, profile, url);
      const inst = await cdp(port, { tab, activate });
      writeState({ browser: name, exe: exes[0].exe, exeSource: exes[0].source, profile, profileSource, port, wsPath, via: "launched" });
      return { inst, how: "launched", detail: { name, exe: exes[0], profile, profileSource, port } };
    } catch (e) {
      attempts.push(`${name}: ${e.message}`);
    }
  }
  throw new Error("无法接入任何浏览器：\n  " + attempts.join("\n  "));
}

// ---------- CLI ----------
const [cmd, ...rest] = process.argv.slice(2);
const opts = {};
for (let i = 0; i < rest.length; i++) {
  if (rest[i].startsWith("--")) { opts[rest[i].slice(2)] = rest[i + 1] && !rest[i + 1].startsWith("--") ? rest[++i] : true; }
  else (opts._ = opts._ || []).push(rest[i]);
}

try {
  // 全局校验：--browser 拼错必须报错，不能静默回退到默认浏览器
  if (opts.browser && !BROWSERS.some(b => b.name === opts.browser)) {
    throw new Error(`未知浏览器 "${opts.browser}"，可选：${BROWSERS.map(b => b.name).join(" / ")}`);
  }
  await main(cmd, opts);
} catch (e) {
  console.error("错误：", e.message);
  await finish(1);
}

async function main(cmd, opts) {
  if (cmd === "doctor") {
    console.log("== 平台 ==", process.platform, os.release());
    console.log("== node ==", process.version);
    for (const b of BROWSERS) {
      const exes = await findExe(b);
      console.log(`\n[${b.name}] 可执行文件 ${exes.length} 个`);
      for (const e of exes) console.log(`   ${e.source.padEnd(12)} ${e.exe}`);
    }
    const procs = await listBrowserProcesses();
    const live = await runningDebugInstances(procs);
    console.log(`\n== 运行中浏览器进程 ${procs.length} 个 / 调试实例 ${live.length} 个 ==`);
    for (const l of live) console.log(`   pid=${l.pid} ${l.name} port=${l.port} profile=${l.userDataDir}`);
    for (const w of PROCESS_WARNINGS) console.log(`   ⚠ ${w}`);
    console.log("\n== 状态文件 ==", STATE_FILE);
    console.log(JSON.stringify(readState(), null, 2));
    console.log("\n== 日常 profile 候选 ==");
    for (const b of BROWSERS) {
      const p = IS_WIN ? path.join(process.env.LOCALAPPDATA || "", b.profileName.win)
        : IS_MAC ? path.join(HOME, "Library/Application Support", b.profileName.mac)
        : path.join(HOME, ".config", b.profileName.linux);
      console.log(`   ${b.name.padEnd(7)} ${fs.existsSync(p) ? "存在" : "缺失"}  ${p}`);
    }
    await finish(0);
    return;
  }

  if (cmd === "open") {
    const url = opts._?.[0] || "about:blank";
    const { inst, how, detail } = await resolve({ preferBrowser: opts.browser, port: opts.port, url, fresh: !!opts.fresh, tab: opts.tab });
    console.log(`接入方式 : ${how}`);
    console.log(`浏览器   : ${inst.version}`);
    console.log(`当前页   : ${inst.pageUrl}（page 目标 ${inst.pageCount} 个）`);
    console.log(`细节     : ${JSON.stringify(detail)}`);
    if (url !== "about:blank") {
      const prev = inst.pageUrl || "";
      const samePage = prev.split("#")[0] === url.split("#")[0];
      if (prev && how !== "launched" && !samePage && !/^(about|edge|chrome|devtools):/i.test(prev)) {
        console.log(`⚠️ 即将覆盖原页面：${prev}`);
        console.log(`   （如不希望覆盖，改用 tab-new ${url}）`);
      }
      const r = await inst.send("Page.navigate", { url });
      console.log(`导航     : ${r.error ? "失败 " + r.error.message : "已发起"}`);
      await sleep(1500);
    }
    const t = await evalIn(inst, "document.title");
    console.log(`标题     : ${t}`);
    await finish(0);
    return; // 不要在此前 close()：undici 的异步关闭与 exit 竞争会触发 libuv 断言崩溃
  }

  if (cmd === "eval") {
    const expr = opts.file ? fs.readFileSync(opts.file, "utf8") : opts._?.[0];
    if (!expr) throw new Error('用法：eval "<js表达式>" 或 eval --file <脚本路径>');
    const { inst } = await resolve({ preferBrowser: opts.browser, port: opts.port, fresh: !!opts.fresh, tab: opts.tab });
    const v = await evalIn(inst, expr);
    console.log(JSON.stringify(v ?? null, null, 2));
    await finish(0);
    return;
  }

  if (cmd === "text") {
    const { inst, how } = await resolve({ preferBrowser: opts.browser, port: opts.port, fresh: !!opts.fresh, tab: opts.tab });
    // 页面尚在加载时 body 可能还不存在 → 短暂重试，避免把"还在加载"误报成"页面为空"
    const raw = await evalIn(inst, TEXT_EXPR, { retryMs: 6000, retryUntil: v => { try { return JSON.parse(v).ready !== "loading"; } catch { return true; } } });
    let o; try { o = JSON.parse(raw); } catch { throw new Error(`无法解析页面信息：${raw}`); }
    console.log(`[${how}]`);
    console.log(o.title);
    console.log(o.url);
    console.log("---");
    console.log(o.text || "(正文为空)");
    if (o.ready === "loading") console.log("\n(提示：页面仍在加载中，内容可能不完整)");
    await finish(0);
    return;
  }

  if (cmd === "frames") {
    const { inst, how } = await resolve({ preferBrowser: opts.browser, port: opts.port, fresh: !!opts.fresh, tab: opts.tab });
    const v = await evalIn(inst, "JSON.stringify(Array.from(document.querySelectorAll('iframe')).map((f,i)=>({i,src:f.src,id:f.id})))");
    console.log(`[${how}] iframe 数：`);
    console.log(v);
    await finish(0);
    return;
  }

  if (cmd === "tabs") {
    const { inst } = await resolve({ preferBrowser: opts.browser, port: opts.port, fresh: !!opts.fresh });
    const tabs = await listTabs(inst.port);
    console.log(`page 目标 ${tabs.length} 个（序号即 --tab 的取值）：`);
    tabs.forEach((t, i) => console.log(`  ${i + 1}. ${t.url}\n     ${t.title || "(无标题)"}`));
    await finish(0);
    return;
  }

  if (cmd === "tab-new") {
    const url = opts._?.[0];
    if (!url) throw new Error('用法：tab-new "<url>"');
    const { inst } = await resolve({ preferBrowser: opts.browser, port: opts.port, fresh: !!opts.fresh });
    const t = await newTab(inst.port, url);
    console.log(`已新建标签页：${t.url || url}`);
    await finish(0);
    return;
  }

  if (cmd === "shot") {
    // 默认写到 ~/.qihang/shots/，绝不默认写进当前目录 —— 否则在仓库里跑 shot 会污染工作树
    const arg = opts.out || opts._?.[0];
    const out = arg
      ? path.resolve(arg)
      : (() => { const d = path.join(STATE_DIR, "shots"); fs.mkdirSync(d, { recursive: true }); return path.join(d, `shot-${Date.now()}.png`); })();
    const { inst } = await resolve({ preferBrowser: opts.browser, port: opts.port, fresh: !!opts.fresh, tab: opts.tab, activate: true });
    const r = await inst.send("Page.captureScreenshot", { format: "png" });
    if (r.error || !r.result?.data) throw new Error(`截图失败：${r.error?.message || "无数据"}`);
    fs.writeFileSync(out, Buffer.from(r.result.data, "base64"));
    console.log("已保存截图：", out, `(${fs.statSync(out).size} B)`);
    await finish(0);
    return;
  }

  const isHelp = cmd === undefined || ["help", "--help", "-h"].includes(cmd);
  if (!isHelp) console.error(`错误：未知子命令 "${cmd}"（用 help 查看用法）`);
  console.log(`qihang-bridge —— 跨平台零依赖浏览器接入

用法：
  node qihang-bridge.mjs doctor              诊断：检索浏览器、运行中实例、状态
  node qihang-bridge.mjs open <url>          接入并导航（自动探活/启动）
  node qihang-bridge.mjs text                读取当前页标题+URL+正文
  node qihang-bridge.mjs frames              列出当前页 iframe
  node qihang-bridge.mjs tabs                列出所有标签页（序号供 --tab 使用）
  node qihang-bridge.mjs tab-new <url>       新建标签页
  node qihang-bridge.mjs eval "<js>"         在页面执行 JS
  node qihang-bridge.mjs eval --file <脚本>  在页面执行 JS 文件（较长脚本用这个）
  node qihang-bridge.mjs shot [--out f.png | f.png]  截图（省略则存 ~/.qihang/shots/）

选项：
  --port <n>               直接接入指定 CDP 端口（用于用户自己已登录的调试实例）
  --browser edge|chrome    优先浏览器（默认 edge）
  --tab <序号|URL子串>     多标签页时指定目标页（序号见 tabs）
  --file <路径>            eval 子命令：从文件读取 JS（与位置参数二选一）
  --fresh                  忽略已运行实例，按 profile 重新接入
环境：
  QIHANG_HEADLESS=1        以无头模式启动（仅用于验证）`);
  await finish(isHelp ? 0 : 1);
}
