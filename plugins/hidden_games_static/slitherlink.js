const { createElement: h, useState } = globalThis.React;
const { Box, Button, Heading, HStack, Text } = globalThis.ChakraUI;

const PUZZLE = {"size":6,"clues":[[0,2,3],[0,4,2],[0,5,2],[1,0,1],[1,1,0],[3,0,2],[3,4,2],[3,5,1],[4,0,0],[4,2,3],[4,4,1],[5,1,0],[5,5,0]],"loop":[["h",0,0],["h",0,1],["h",0,3],["h",0,4],["h",1,2],["h",1,5],["h",2,5],["h",3,0],["h",4,1],["h",4,3],["h",4,4],["h",5,2],["v",0,0],["v",0,2],["v",0,3],["v",0,5],["v",1,0],["v",1,6],["v",2,0],["v",2,5],["v",3,1],["v",3,5],["v",4,2],["v",4,3]]};

const N = PUZZLE.size;
const CELL = 48;
const PAD = 16;
const SIZE = N * CELL + 2 * PAD;
const LOOP = new Set(PUZZLE.loop.map((e) => e.join(",")));
const NONE = 0;
const LINE = 1;
const CROSS = 2;

const EDGES = [];
for (let r = 0; r <= N; r++) for (let c = 0; c < N; c++) EDGES.push(["h", r, c]);
for (let r = 0; r < N; r++) for (let c = 0; c <= N; c++) EDGES.push(["v", r, c]);

const endpoints = ([kind, r, c]) => {
  const x1 = PAD + c * CELL;
  const y1 = PAD + r * CELL;
  return kind === "h" ? [x1, y1, x1 + CELL, y1] : [x1, y1, x1, y1 + CELL];
};

const Slitherlink = () => {
  const [marks, setMarks] = useState({});
  const lines = Object.keys(marks).filter((k) => marks[k] === LINE);
  const solved = lines.length === LOOP.size && lines.every((k) => LOOP.has(k));

  const cycle = (k) => {
    if (solved) return;
    setMarks((prev) => ({ ...prev, [k]: ((prev[k] ?? NONE) + 1) % 3 }));
  };

  const edgeElements = EDGES.map((edge) => {
    const k = edge.join(",");
    const [x1, y1, x2, y2] = endpoints(edge);
    const mark = marks[k] ?? NONE;
    const mx = (x1 + x2) / 2;
    const my = (y1 + y2) / 2;
    return h(
      "g",
      { key: k, onClick: () => cycle(k), style: { cursor: solved ? "default" : "pointer" } },
      h("line", { x1, y1, x2, y2, stroke: "transparent", strokeWidth: 16 }),
      mark === LINE &&
        h("line", {
          x1,
          y1,
          x2,
          y2,
          stroke: solved ? "var(--chakra-colors-green-solid)" : "currentColor",
          strokeWidth: 5,
          strokeLinecap: "round",
        }),
      mark === CROSS &&
        h("path", {
          d: `M${mx - 4},${my - 4}L${mx + 4},${my + 4}M${mx + 4},${my - 4}L${mx - 4},${my + 4}`,
          stroke: "var(--chakra-colors-red-solid)",
          strokeWidth: 2,
        }),
    );
  });

  const dots = [];
  for (let r = 0; r <= N; r++) {
    for (let c = 0; c <= N; c++) {
      dots.push(h("circle", { key: `d${r},${c}`, cx: PAD + c * CELL, cy: PAD + r * CELL, r: 4, fill: "currentColor" }));
    }
  }

  const clues = PUZZLE.clues.map(([r, c, v]) =>
    h(
      "text",
      {
        key: `c${r},${c}`,
        x: PAD + c * CELL + CELL / 2,
        y: PAD + r * CELL + CELL / 2,
        textAnchor: "middle",
        dominantBaseline: "central",
        fill: "currentColor",
        style: { pointerEvents: "none", fontSize: 22, fontWeight: 700 },
      },
      String(v),
    ),
  );

  return h(
    Box,
    { borderWidth: 1, borderRadius: 4, p: 3, order: 0 },
    h(Heading, { size: "md", mb: 1 }, "Slitherlink"),
    h(
      Text,
      { mb: 3, color: "fg.muted" },
      "Draw one closed loop along the dots. Each number says how many of its 4 sides the loop uses. Click an edge to cycle: line, cross, empty.",
    ),
    h(
      HStack,
      { alignItems: "flex-start", gap: 6, flexWrap: "wrap" },
      h(Box, { color: "fg" }, h("svg", { width: SIZE, height: SIZE, viewBox: `0 0 ${SIZE} ${SIZE}` }, clues, edgeElements, dots)),
      h(
        Box,
        null,
        h(Text, { mb: 2 }, solved ? "Solved." : `Lines drawn: ${lines.length}`),
        h(Button, { size: "sm", variant: "outline", onClick: () => setMarks({}) }, "Reset"),
      ),
    ),
  );
};

globalThis.AirflowPlugin = Slitherlink;
