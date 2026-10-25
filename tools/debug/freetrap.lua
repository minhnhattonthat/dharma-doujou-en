-- Free-space trap: log every CPU read of the free ranges the build writes into (docs/re/graphics.md).
-- Run on the ORIGINAL ROM over every warp: any "FREETRAP" line in a log means the range is not free.
--   python -X utf8 tools/warp.py --all --rom "rom/Dharma Doujou (Japan).sfc" --script tools/debug/freetrap.lua
-- then: grep -h FREETRAP work/qa/warp/*/log.txt
local ranges = {  -- bank, first address, last address (file 0x16910-, 0x270A0-, 0xE2E90-, 0xF5130-, 0xA5990-)
  {0x82, 0xE910, 0xFFFF}, {0x84, 0xF0A0, 0xFFFF}, {0x9C, 0xAE90, 0xFFFF}, {0x9E, 0xD130, 0xFFFF},
  {0x94, 0xD990, 0xFFFF},
}
local seen = {}
local function hook(addr, value)
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  if seen[pc] then return end
  seen[pc] = true
  L.log(string.format("FREETRAP f%d pc=%06X read %06X", L.frame, pc, addr))
end
for _, r in ipairs(ranges) do
  for _, bank in ipairs({r[1], r[1] & 0x7F}) do
    emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, (bank << 16) | r[2], (bank << 16) | r[3],
      emu.cpuType.snes, emu.memType.snesMemory)
  end
end
