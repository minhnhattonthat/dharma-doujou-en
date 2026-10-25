-- Scene list for tools/debug/warp.lua: name -> steps from a cold boot. Each step is one of
--   {wait=fn(e), delay=N, mash="a", every=40, port=2}  wait until fn is true for N frames, mashing meanwhile
--                                                      (first press on the step's first frame)
--   {frames=N}                                         plain delay
-- and may also carry poke={[addr]=word}, run=fn(e), press="a+start" (hold=frames, port=2), done after the wait.
-- e: e.at(mode, sub), e.r16(addr), e.w16(addr, v). RAM map: docs/re/debug.md.
SC = { scenes = {} }
local S = SC.scenes
local function cat(...) local t = {}; for _, l in ipairs({ ... }) do for _, s in ipairs(l) do t[#t + 1] = s end end; return t end
-- Menu screens inside mode 1 are told apart by the last menu string drawn ($0238).
local MAIN, NEWPW, CHAR, LIMIT = 0xA1, 0xA5, 0xA3, 0xA4
local function on(id) return function(e) return e.at(1, 1) and e.r16(0x238) == id end end
local function off(id) return function(e) return not (e.at(1, 1) and e.r16(0x238) == id) end end
local function screen(id, delay) return { wait = on(id), delay = delay or 60 } end
-- Leave screen `id` with A, pressing again if the press was dropped.
local function pick(id) return { wait = off(id), mash = "a", every = 240 } end

local function title() return { { wait = function(e) return e.at(0, 4) end, delay = 60 } } end
local function menu(item)
  return cat(title(), {
    { wait = on(MAIN), delay = 20, mash = "start", every = 60, poke = { [0x781C] = item } },
    { frames = 10 }, pick(MAIN),
  })
end
local function until_at(mode, sub, delay, key, every)
  return { wait = function(e) return e.at(mode, sub) end, delay = delay or 30, mash = key, every = every }
end
-- Story from "new game" to stage 1-1 play (mode 9 sub 1); mash A through every menu and the intro.
local function story_play() return cat(menu(0), { until_at(9, 1, 30, "a") }) end
-- Win the current round as if the board were cleared: the game itself advances the stage.
local function clear_as(stage, sub) return { poke = { [0x04B8] = stage, [0x04B6] = sub, [0x024E] = 2 } } end

S.title = title()
S.menu = cat(title(), { { wait = on(MAIN), delay = 30, mash = "start", every = 60 } })
S.attract = cat(title(), { { wait = function(e) return e.r16(0x1CF8) ~= 0 end, delay = 120 } })  -- $1CF8 demo flag

-- Story
S.story_menu = cat(menu(0), { screen(NEWPW) })                               -- new game / password
S.password = cat(S.story_menu, { { press = "down" }, { frames = 20 }, pick(NEWPW), { frames = 120 } })
S.password_end = cat(S.password, { { press = "start" }, { frames = 30 } })  -- confirm the blank password (msg 13?)
S.story_limit = cat(S.story_menu, { pick(NEWPW), screen(LIMIT) })           -- time limit / move limit
S.story_intro = cat(S.story_limit, { pick(LIMIT), until_at(3, 0, 200, "a") })
S.map = cat(menu(0), { until_at(7, 1, 60, "a") })
S.stage1 = story_play()
S.stage1_moves = cat(S.story_limit, { { press = "down" }, { frames = 20 }, pick(LIMIT), until_at(9, 1, 30, "a") })
-- stageN: clear stage N-1's last round; arrives at the outro scene (mode 13), then map, card, play follow.
for n = 2, 8 do
  S["stage" .. n] = cat(story_play(), { clear_as(n - 2, 2), until_at(13, nil, 150) })  -- 150: past the fade-in
end
-- Clearing the last stage (index 7): map, ending scene (mode 13), then the credits (mode 2).
S.ending = cat(story_play(), { clear_as(7, 2), until_at(13, nil, 150) })
S.credits = cat(story_play(), { clear_as(7, 2), until_at(2, nil, 300, "a") })
-- Story game over: drop pieces fast until the stack tops out, then the continue screen (mode 9 sub 4).
S.gameover = cat(story_play(), { until_at(9, 4, 30, "down", 10) })
S.gameover_quit = cat(S.gameover, { { press = "down" }, { frames = 20 }, { press = "a" }, { frames = 30 } })  -- 出直す

-- Training (修行編): character, difficulty (mode 10 sub 1), play.
S.training_char = cat(menu(1), { screen(CHAR) })
S.training_diff = cat(S.training_char, { pick(CHAR), until_at(10, 1, 60) })
S.training_play = cat(S.training_diff, { { press = "a" }, { frames = 300 } })

-- Quiz (問答)
S.quiz_menu = cat(menu(2), { screen(NEWPW) })
S.quiz_char = cat(S.quiz_menu, { pick(NEWPW), screen(CHAR) })
S.quiz_play = cat(S.quiz_char, { pick(CHAR), until_at(11, 1, 120) })
-- Clearing problem N sets $04C4 = N and goes on via table $80:F123: the next problem, or a scene (mode 13).
local function quiz_clear(n) return cat(S.quiz_char, { pick(CHAR), until_at(11, 1, 60),
  { poke = { [0x04C4] = n - 1, [0x024E] = 2 } } }) end
for n = 2, 5 do  -- quiz_lvN: 2nd problem of the Nth block of ten (rank plate; the 1st follows a scene)
  S["quiz_lv" .. n] = cat(quiz_clear(10 * n - 9), { until_at(11, 1, 120) })
end
for n = 1, 5 do  -- quiz_rankN: scene after problems 5, 15, 25, 35, 45
  S["quiz_rank" .. n] = cat(quiz_clear(10 * n - 5), { until_at(13, nil, 60) })
end
S.quiz_break = cat(quiz_clear(10), { until_at(13, nil, 60) })               -- scene after 10/20/30/40
S.quiz_master = cat(quiz_clear(50), { until_at(13, nil, 60) })              -- after the last problem
S.quiz_gameover = cat(S.quiz_char, { pick(CHAR), until_at(11, 1, 60), until_at(11, 4, 30, "a", 60) })

-- 2P vs (mode 8; sub 2 = play). $190A/$190C = wins of P1/P2; two wins -> victory scene (mode 13 sub $1B).
S.versus_char = cat(menu(3), { screen(CHAR) })
local vs_start = { wait = function(e) return e.at(8, 2) end, delay = 60, mash = "a", every = 120, port = "both" }
S.versus_play = cat(S.versus_char, { vs_start })
S.versus_win = cat(S.versus_char, { vs_start, { poke = { [0x190A] = 2, [0x024E] = 1 } }, until_at(13, nil, 60) })
S.tutorial = cat(menu(4), { screen(CHAR), pick(CHAR), until_at(6, 1, 120) })
S.options = cat(menu(5), { until_at(5, 1, 60) })
