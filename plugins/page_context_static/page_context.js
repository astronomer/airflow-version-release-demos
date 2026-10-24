const { createElement: h } = globalThis.React;
const { Box, Code, Heading, Text } = globalThis.ChakraUI;

const PageContext = (props) =>
  h(
    Box,
    { p: 4 },
    h(Heading, { size: "md", mb: 2 }, `Task ${props.taskId} in Dag ${props.dagId}`),
    h(Text, null, `State: ${props.taskInstance?.state}, try ${props.taskInstance?.try_number}, operator ${props.taskInstance?.operator_name}`),
    h(Text, null, `Dag run state: ${props.dagRun?.state}, Dag tags: ${props.dag?.tags?.map((tag) => tag.name).join(", ")}`),
    h(Heading, { size: "sm", mt: 4, mb: 2 }, "All props"),
    h(Code, { as: "pre", display: "block", whiteSpace: "pre-wrap", p: 2 }, JSON.stringify(props, null, 2)),
  );

globalThis.AirflowPlugin = PageContext;
