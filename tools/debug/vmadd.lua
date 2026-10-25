-- Who sets the VRAM address to a word in VMADD_LO..VMADD_HI? Logs frame, PC and address once per (PC, address):
-- finds code that writes a tilemap or tiles straight to VRAM (no WRAM buffer, no DMA from a table).
--   warp.py SCENE --script tools/debug/vmadd.lua --var VMADD_LO=0x7336 [--var VMADD_HI=0x7340]
local lo, hi = assert(VMADD_LO, "set VMADD_LO"), VMADD_HI or VMADD_LO
local seen, lowbyte = {}, 0
L.on_write(0x2116, 0x2117, function(addr, v)
  if addr & 1 == 0 then lowbyte = v; return end
  local a = (v << 8) | lowbyte
  local pc = L.pc()
  if a >= lo and a <= hi and not seen[pc .. ":" .. a] then
    seen[pc .. ":" .. a] = true
    L.log(string.format("f%d vmadd %04X pc=%06X", L.frame, a, pc))
  end
end)
