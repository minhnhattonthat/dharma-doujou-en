-- Cold-boot warp to a named scene (tools/debug/scenes.lua, loaded first), then shot + optional savestate.
-- Run it through tools/warp.py; by hand:
--   emu.py ROM --out work/qa/warp --script tools/debug/scenes.lua --script tools/debug/warp.lua
--          --var "SCENE='stage3'" --frames 9000 [--var "SAVE='C:/abs/work/states/stage3.mss'"] [--var HOLD=120]
--          [--var AFTER_MASH=40]  (press A every 40 frames during HOLD, to page through text after arrival)
-- Needs --frames (a timeout): the run stops itself HOLD frames after the scene is reached, and fails (exit 2) if
-- the scene was not reached by frame FRAMES-1. The log gets "WARP ok <scene> f<frame>".
-- RAM (docs/re/debug.md): $17 mode, $19 sub-state, $781C main-menu cursor, $04B8 stage, $04B6 sub-stage,
-- $024E stage result (2 = cleared).
local W = emu.memType.snesWorkRam
assert(SC, "load tools/debug/scenes.lua before warp.lua")
local scene = SC.scenes[SCENE or ""]
if not scene then error("unknown SCENE '" .. tostring(SCENE) .. "'; see tools/debug/scenes.lua") end

local function r16(a) return emu.read16(a, W) end
local function at(mode, sub) return r16(0x17) == mode and (sub == nil or r16(0x19) == sub) end
local env = { r16 = r16, at = at, w16 = function(a, v) emu.write16(a, v, W) end }

-- Controller 2: emu.setInput(.., 1) lands on pad 1 under --testRunner (no port-2 device), so feed the auto-read
-- registers JOY2L/H ($421A/B) from a read callback instead. Bits as the game sees the word at $421A.
local BITS = { a = 0x80, x = 0x40, l = 0x20, r = 0x10, b = 0x8000, y = 0x4000, select = 0x2000, start = 0x1000,
  up = 0x800, down = 0x400, left = 0x200, right = 0x100 }
local p2 = nil
for _, base in ipairs({ 0x00421A, 0x80421A }) do
  emu.addMemoryCallback(function(addr)
    if not p2 then return nil end
    if L.frame >= p2.stop then p2 = nil; return nil end
    return (addr & 1) == 0 and (p2.w & 0xFF) or (p2.w >> 8)
  end, emu.callbackType.read, base, base + 1, emu.cpuType.snes, emu.memType.snesMemory)
end
local function press(spec, port, n)
  if port == "both" then press(spec, 1, n); return press(spec, 2, n) end
  if port == 2 then
    local w = 0; for k in spec:gmatch("[^+]+") do w = w | assert(BITS[k], k) end
    p2 = { w = w, stop = L.frame + (n or 4) }
  else L.press(spec, n or 4) end
end

local steps, i, t0, ts, done = scene, 1, nil, nil, nil
L.log("WARP start " .. SCENE)
L.on_frame(function(n)
  if done then
    if AFTER_MASH and n > done and (n - done) % AFTER_MASH == 0 then press("a") end
    if n == done + (HOLD or 60) then
      L.shot(SCENE .. ".png"); L.log(string.format("WARP ok %s f%d", SCENE, done))
      if SAVE then L.save_state(SAVE, function() L.finish(0) end) else L.finish(0) end
    end
    return
  end
  if FRAMES and n >= FRAMES - 1 then return L.fail(string.format("WARP fail %s: stuck at step %d (mode=%02X sub=%02X)",
    SCENE, i, r16(0x17), r16(0x19))) end
  local s = steps[i]
  if not s then done = n; return end
  if not L.route_done() or (p2 and n < p2.stop) then return end
  t0, ts = t0 or n, ts or n
  if s.wait then
    if not s.wait(env) then
      t0 = n
      if s.mash and (n - ts) % (s.every or 40) == 0 then press(s.mash, s.port) end
      return
    end
    if n - t0 < (s.delay or 0) then return end
  elseif s.frames and n - t0 < s.frames then return end
  if s.poke then for a, v in pairs(s.poke) do emu.write16(a, v, W) end end
  if s.run then s.run(env) end
  if s.press then press(s.press, s.port, s.hold) end
  i, t0, ts = i + 1, nil, nil
end)
