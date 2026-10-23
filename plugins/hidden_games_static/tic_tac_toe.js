const { createElement: h, useState } = globalThis.React;
const { Box, Button, Heading, HStack, Text } = globalThis.ChakraUI;

const LINES = [
  [0, 1, 2], [3, 4, 5], [6, 7, 8],
  [0, 3, 6], [1, 4, 7], [2, 5, 8],
  [0, 4, 8], [2, 4, 6],
];

const winner = (board) => {
  for (const [a, b, c] of LINES) {
    if (board[a] && board[a] === board[b] && board[a] === board[c]) {
      return board[a];
    }
  }
  return board.every(Boolean) ? "draw" : null;
};

const minimax = (board, player) => {
  const result = winner(board);
  if (result === "O") return { score: 1 };
  if (result === "X") return { score: -1 };
  if (result === "draw") return { score: 0 };
  let best = { score: player === "O" ? -2 : 2 };
  board.forEach((cell, i) => {
    if (cell) return;
    board[i] = player;
    const { score } = minimax(board, player === "O" ? "X" : "O");
    board[i] = null;
    if (player === "O" ? score > best.score : score < best.score) {
      best = { score, move: i };
    }
  });
  return best;
};

const MESSAGES = {
  X: "You won.",
  O: "O wins.",
  draw: "Draw.",
};

const TicTacToe = () => {
  const [board, setBoard] = useState(Array(9).fill(null));
  const result = winner(board);

  const play = (i) => {
    if (board[i] || result) return;
    const next = [...board];
    next[i] = "X";
    if (!winner(next)) {
      next[minimax(next, "O").move] = "O";
    }
    setBoard(next);
  };

  return h(
    Box,
    { borderWidth: 1, borderRadius: 4, p: 3, order: 0 },
    h(Heading, { size: "md", mb: 1 }, "You found a hidden game"),
    h(Text, { mb: 3, color: "fg.muted" }, "Tic-tac-toe. You are X."),
    h(
      HStack,
      { alignItems: "center", gap: 6 },
      h(
        Box,
        { display: "grid", gridTemplateColumns: "repeat(3, 56px)", gap: 1 },
        board.map((cell, i) =>
          h(
            Box,
            {
              as: "button",
              key: i,
              onClick: () => play(i),
              h: "56px",
              borderWidth: 1,
              borderRadius: 4,
              fontSize: "2xl",
              fontWeight: "bold",
              color: cell === "X" ? "blue.solid" : "red.solid",
              cursor: cell || result ? "default" : "pointer",
              _hover: cell || result ? {} : { bg: "bg.muted" },
            },
            cell,
          ),
        ),
      ),
      h(
        Box,
        null,
        h(Text, { mb: 2, minH: "1.5em" }, result ? MESSAGES[result] : ""),
        h(Button, { size: "sm", variant: "outline", onClick: () => setBoard(Array(9).fill(null)) }, "New game"),
      ),
    ),
  );
};

globalThis.AirflowPlugin = TicTacToe;
