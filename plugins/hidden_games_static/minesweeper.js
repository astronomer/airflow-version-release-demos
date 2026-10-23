const { createElement: h, useState } = globalThis.React;
const { Box, Button, Heading, HStack, Text } = globalThis.ChakraUI;

const PUZZLE = {"size":8,"clues":[[0,1,3],[0,3,0],[0,6,1],[0,7,0],[1,6,1],[2,0,3],[2,2,3],[2,6,1],[3,1,3],[3,3,4],[3,7,1],[4,2,3],[4,5,0],[5,1,2],[5,3,2],[5,4,1],[6,5,1],[6,6,0],[7,1,1],[7,3,1]],"mines":[[0,0],[1,0],[1,1],[1,5],[2,3],[2,4],[3,0],[3,2],[4,0],[4,3],[4,7],[5,2],[7,0],[7,4]]};

const N = PUZZLE.size;
const key = (r, c) => `${r},${c}`;
const CLUES = new Map(PUZZLE.clues.map(([r, c, v]) => [key(r, c), v]));
const MINES = new Set(PUZZLE.mines.map(([r, c]) => key(r, c)));
const CLUE_COLORS = ["fg.muted", "blue.solid", "green.solid", "red.solid", "purple.solid"];
const SAFE_CELLS = N * N - MINES.size;

const neighbors = (k) => {
  const [r, c] = k.split(",").map(Number);
  const out = [];
  for (let dr = -1; dr <= 1; dr++) {
    for (let dc = -1; dc <= 1; dc++) {
      if ((dr || dc) && r + dr >= 0 && r + dr < N && c + dc >= 0 && c + dc < N) {
        out.push(key(r + dr, c + dc));
      }
    }
  }
  return out;
};

const count = (k) => neighbors(k).filter((nb) => MINES.has(nb)).length;

const uncover = (start, opened) => {
  const next = new Set(opened);
  const queue = [...start];
  while (queue.length) {
    const k = queue.pop();
    if (next.has(k) || CLUES.has(k)) continue;
    next.add(k);
    if (count(k) === 0) queue.push(...neighbors(k));
  }
  return next;
};

const Minesweeper = () => {
  const [flags, setFlags] = useState(new Set());
  const [opened, setOpened] = useState(new Set());
  const [exploded, setExploded] = useState(null);

  const solved =
    !exploded &&
    (CLUES.size + opened.size === SAFE_CELLS || (flags.size === MINES.size && [...flags].every((k) => MINES.has(k))));
  const over = Boolean(exploded) || solved;
  const isShown = (k) => CLUES.has(k) || opened.has(k);

  const open = (cells) => {
    const targets = cells.filter((k) => !flags.has(k) && !isShown(k));
    const mine = targets.find((k) => MINES.has(k));
    if (mine) {
      setExploded(mine);
      return;
    }
    setOpened((prev) => uncover(targets, prev));
  };

  const onClick = (event, k) => {
    if (over || event.ctrlKey) return;
    if (isShown(k)) {
      const value = CLUES.get(k) ?? count(k);
      const around = neighbors(k);
      if (around.filter((nb) => flags.has(nb)).length === value) open(around);
      return;
    }
    if (!flags.has(k)) open([k]);
  };

  const onFlag = (event, k) => {
    event.preventDefault();
    if (over || isShown(k)) return;
    setFlags((prev) => {
      const next = new Set(prev);
      next.has(k) ? next.delete(k) : next.add(k);
      return next;
    });
  };

  const reset = () => {
    setFlags(new Set());
    setOpened(new Set());
    setExploded(null);
  };

  const cells = [];
  for (let r = 0; r < N; r++) {
    for (let c = 0; c < N; c++) {
      const k = key(r, c);
      const shown = isShown(k);
      const value = CLUES.get(k) ?? count(k);
      let content = "";
      let bg = "bg.emphasized";
      if (shown) {
        bg = CLUES.has(k) ? "bg" : "bg.subtle";
        content = value === 0 && !CLUES.has(k) ? "" : String(value);
      } else if (exploded && MINES.has(k)) {
        bg = k === exploded ? "red.solid" : "bg.emphasized";
        content = flags.has(k) ? "\u{1F6A9}" : "\u{1F4A3}";
      } else if (flags.has(k)) {
        content = exploded ? "❌" : "\u{1F6A9}";
      }
      cells.push(
        h(
          Box,
          {
            as: "button",
            key: k,
            onClick: (event) => onClick(event, k),
            onContextMenu: (event) => onFlag(event, k),
            h: "36px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            borderWidth: 1,
            borderRadius: 2,
            bg,
            fontSize: "lg",
            fontWeight: "bold",
            color: shown ? (CLUE_COLORS[value] ?? "orange.solid") : "fg",
            cursor: over ? "default" : "pointer",
            _hover: over || shown ? {} : { borderColor: "fg.muted" },
          },
          content,
        ),
      );
    }
  }

  let status = `Flags placed: ${flags.size}`;
  if (exploded) status = "Boom. Game over.";
  else if (solved) status = "Cleared.";

  return h(
    Box,
    { borderWidth: 1, borderRadius: 4, p: 3, order: 0 },
    h(Heading, { size: "md", mb: 1 }, "Minesweeper"),
    h(
      Text,
      { mb: 3, color: "fg.muted" },
      "Numbers count the mines in the 8 cells around them. Left-click to uncover a cell, right-click (Ctrl+click on a Mac trackpad) to flag a mine. Click a number whose flags are all placed to uncover the rest of its neighbors.",
    ),
    h(
      HStack,
      { alignItems: "flex-start", gap: 6, flexWrap: "wrap" },
      h(Box, { display: "grid", gridTemplateColumns: `repeat(${N}, 36px)`, gap: "2px" }, cells),
      h(
        Box,
        null,
        h(Text, { mb: 2, fontWeight: exploded || solved ? "bold" : "normal" }, status),
        h(Button, { size: "sm", variant: "outline", onClick: reset }, exploded ? "Try again" : "Reset"),
      ),
    ),
  );
};

globalThis.AirflowPlugin = Minesweeper;
