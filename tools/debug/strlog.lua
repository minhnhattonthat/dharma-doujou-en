-- Log each engine-2 string draw (tools: docs/re/text.md, Engine 2): frame, string id $0238, column $023A, row $023C,
-- once per (id, column, row). Finds which string draws a given screen element.
--   warp.py SCENE --script tools/debug/strlog.lua
local W = emu.memType.snesWorkRam
local seen = {}
for _, pc in ipairs({ 0x84D94C, 0x84D982 }) do
  L.on_exec(pc, pc, function()
    local id, col, row = emu.read16(0x238, W), emu.read16(0x23A, W), emu.read16(0x23C, W)
    local k = pc .. ":" .. id .. ":" .. col .. ":" .. row
    if not seen[k] then
      seen[k] = true
      L.log(string.format("f%d str %d col %d row %d bg%d", L.frame, id, col, row, pc == 0x84D94C and 1 or 2))
    end
  end)
end
