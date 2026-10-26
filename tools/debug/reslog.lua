-- Log each RLE resource decode ($80:9D53, A = resource index; docs/re/graphics.md): frame and index.
-- Finds which scene loads a resource.   warp.py SCENE --hold N --script tools/debug/reslog.lua
L.on_exec(0x809D53, 0x809D53, function()
  L.log(string.format("f%d res %d", L.frame, emu.getState()["cpu.a"] & 0xFF))
end)
