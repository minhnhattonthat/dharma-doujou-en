-- Log each RLE resource decode, A = resource index (docs/re/graphics.md): frame, index, loader.
-- Two loaders: $80:9D4E (to WRAM) and $80:8941 (to the NMI DMA buffer).
-- Finds which scene loads a resource.   warp.py SCENE --hold N --script tools/debug/reslog.lua
for pc, name in pairs({ [0x809D53] = "wram", [0x808952] = "dma" }) do
  L.on_exec(pc, pc, function()
    L.log(string.format("f%d res %d %s", L.frame, emu.getState()["cpu.a"] & 0xFF, name))
  end)
end
