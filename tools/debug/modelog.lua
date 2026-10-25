-- Logs every change of the scene state machine: $17 = mode (table $80:A129), $19 = sub-state.
--   emu.py ROM --route r.txt --script tools/debug/modelog.lua [--var "EXTRA={0x1A25,0x0238}"]
-- EXTRA: more 16-bit WRAM words to print beside each change.
local W = emu.memType.snesWorkRam
local function rd(a) return emu.read16(a, W) end
local last
L.on_frame(function(n)
  local cur = string.format("mode=%02X sub=%02X", rd(0x17), rd(0x19))
  for _, a in ipairs(EXTRA or {}) do cur = cur .. string.format(" %04X=%04X", a, rd(a)) end
  if cur ~= last then L.log(string.format("f%d %s", n, cur)); last = cur end
end)
