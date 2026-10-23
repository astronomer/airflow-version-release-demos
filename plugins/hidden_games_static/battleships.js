const { createElement: h, useEffect, useRef, useState } = globalThis.React;
const { Box, Button, Heading, HStack, Text } = globalThis.ChakraUI;

const PUZZLE = {"size":8,"fleet":[4,3,3,2,2,1,1,1],"rows":[4,1,4,1,1,0,5,1],"cols":[2,0,4,1,1,3,3,3],"shipGiven":[],"waterGiven":[[2,7],[6,2]],"ships":[[0,2],[0,5],[0,6],[0,7],[1,2],[2,0],[2,2],[2,5],[2,6],[3,2],[4,6],[6,0],[6,3],[6,4],[6,5],[6,7],[7,7]]};

const N = PUZZLE.size;
const SIDE = "32px";
const key = (r, c) => `${r},${c}`;
const SHIPS = new Set(PUZZLE.ships.map(([r, c]) => key(r, c)));
const GIVEN = new Map([
  ...PUZZLE.shipGiven.map(([r, c]) => [key(r, c), "ship"]),
  ...PUZZLE.waterGiven.map(([r, c]) => [key(r, c), "water"]),
]);
const UNKNOWN = 0;
const SHIP = 1;
const WATER = 2;

const header = (label, done, k) =>
  h(
    Box,
    { key: k, w: SIDE, h: SIDE, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "bold", color: done ? "fg.subtle" : "fg" },
    String(label),
  );

const Battleships = ({ asset }) => {
  const [marks, setMarks] = useState({});
  const isShip = (k) => GIVEN.get(k) === "ship" || marks[k] === SHIP;
  const placed = Object.keys(marks).filter((k) => marks[k] === SHIP);
  const solved = [...SHIPS].every(isShip) && placed.every((k) => SHIPS.has(k));

  const paint = useRef(null);

  useEffect(() => {
    const stop = () => {
      paint.current = null;
    };
    window.addEventListener("pointerup", stop);
    return () => window.removeEventListener("pointerup", stop);
  }, []);

  const apply = (k) => {
    if (paint.current === null || solved || GIVEN.has(k)) return;
    const value = paint.current;
    setMarks((prev) => ({ ...prev, [k]: value }));
  };

  const onPointerDown = (event, k) => {
    if (solved || GIVEN.has(k) || (event.button !== 0 && event.button !== 2)) return;
    event.preventDefault();
    const tool = event.button === 2 || event.ctrlKey ? SHIP : WATER;
    paint.current = (marks[k] ?? UNKNOWN) === tool ? UNKNOWN : tool;
    apply(k);
  };

  const onPointerMove = (event) => {
    if (paint.current === null) return;
    const cell = document.elementFromPoint(event.clientX, event.clientY)?.closest("[data-cell]");
    if (cell) apply(cell.dataset.cell);
  };

  const rowCount = (r) => Array.from({ length: N }, (_, c) => isShip(key(r, c))).filter(Boolean).length;
  const colCount = (c) => Array.from({ length: N }, (_, r) => isShip(key(r, c))).filter(Boolean).length;

  const grid = [h(Box, { key: "corner" })];
  PUZZLE.cols.forEach((v, c) => grid.push(header(v, colCount(c) === v, `col${c}`)));
  for (let r = 0; r < N; r++) {
    grid.push(header(PUZZLE.rows[r], rowCount(r) === PUZZLE.rows[r], `row${r}`));
    for (let c = 0; c < N; c++) {
      const k = key(r, c);
      const given = GIVEN.get(k);
      const state = given === "ship" ? SHIP : given === "water" ? WATER : (marks[k] ?? UNKNOWN);
      grid.push(
        h(
          Box,
          {
            as: given ? "div" : "button",
            key: k,
            "data-cell": k,
            onPointerDown: (event) => onPointerDown(event, k),
            onContextMenu: (event) => event.preventDefault(),
            w: SIDE,
            h: SIDE,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            borderWidth: 1,
            borderColor: given ? "fg.muted" : "border",
            bg: state === SHIP ? (solved ? "green.solid" : "fg") : state === WATER ? "blue.subtle" : "bg",
            color: "blue.fg",
            borderRadius: state === SHIP ? "full" : 0,
          },
          state === WATER ? "~" : "",
        ),
      );
    }
  }

  const fleet = PUZZLE.fleet.map((length, i) =>
    h(HStack, { key: i, gap: "2px" }, Array.from({ length }, (_, j) => h(Box, { key: j, w: "14px", h: "14px", bg: "fg", borderRadius: "full" }))),
  );

  return h(
    Box,
    { p: 4 },
    h(Heading, { size: "lg", mb: 1 }, `Battleships on ${asset?.name ?? "the high seas"}`),
    h(
      Text,
      { mb: 3, color: "fg.muted" },
      "Hide the fleet. The numbers say how many ship cells are in each row and column. Ships never touch, not even diagonally. Click or drag to place water, right-click or right-drag (Ctrl+click on a Mac trackpad) to place ships. Start on a marked cell to erase.",
    ),
    h(
      HStack,
      { alignItems: "flex-start", gap: 6, flexWrap: "wrap" },
      h(
        Box,
        {
          display: "grid",
          gridTemplateColumns: `repeat(${N + 1}, ${SIDE})`,
          gap: "2px",
          onPointerMove,
          userSelect: "none",
          touchAction: "none",
        },
        grid,
      ),
      h(
        Box,
        null,
        h(Text, { fontWeight: "bold", mb: 2 }, "Fleet"),
        h(Box, { display: "flex", flexDirection: "column", gap: 1, mb: 3 }, fleet),
        h(Text, { mb: 2 }, solved ? "Fleet found." : `Ship cells placed: ${placed.length} / ${SHIPS.size}`),
        h(Button, { size: "sm", variant: "outline", onClick: () => setMarks({}) }, "Reset"),
      ),
    ),
  );
};

globalThis.AirflowPlugin = Battleships;
