import React, { useState, useEffect, useSyncExternalStore } from "react";
import {
  ChakraProvider,
  createSystem,
  defaultConfig,
  Box,
  Text,
  Heading,
  Button,
  Badge,
  Flex,
  Grid,
  Card,
  Separator,
  Stack,
  Input,
  Switch,
  Tabs,
} from "@chakra-ui/react";
import type { SystemContext } from "@chakra-ui/react";

declare global {
  var ChakraUISystem: SystemContext | undefined;
}

const _root = document.documentElement;
const _tmp = document.createElement("div");
_tmp.style.color = getComputedStyle(_root).getPropertyValue("--chakra-colors-black").trim();
document.body.appendChild(_tmp);
const AIRFLOW_DARK_BG = getComputedStyle(_tmp).color;
document.body.removeChild(_tmp);

const defaultSystem = createSystem(defaultConfig);
const activeSystem = globalThis.ChakraUISystem ?? defaultSystem;

let _darkListeners = new Set<() => void>();
const _observer = new MutationObserver(() => _darkListeners.forEach((fn) => fn()));
_observer.observe(_root, { attributes: true, attributeFilter: ["class"] });

function useIsDark() {
  return useSyncExternalStore(
    (cb) => { _darkListeners.add(cb); return () => _darkListeners.delete(cb); },
    () => _root.classList.contains("dark"),
  );
}

const COLOR_PALETTES = [
  "gray", "blue", "green", "red", "orange",
  "yellow", "teal", "cyan", "purple", "pink",
];

const SHADES = ["50", "100", "200", "300", "400", "500", "600", "700", "800", "900", "950"] as const;

function ColorSwatch({ palette, shade }: { palette: string; shade: string }) {
  return (
    <Box
      bg={`${palette}.${shade}`}
      h="8"
      w="100%"
      borderRadius="sm"
      display="flex"
      alignItems="center"
      justifyContent="center"
    >
      <Text fontSize="2xs" fontWeight="bold" color={Number(shade) >= 500 ? "white" : "black"}>
        {shade}
      </Text>
    </Box>
  );
}

function ColorPalettes() {
  return (
    <Stack gap="3">
      {COLOR_PALETTES.map((palette) => (
        <Flex key={palette} gap="1" alignItems="center">
          <Text fontWeight="semibold" fontSize="xs" w="55px" flexShrink={0}>
            {palette}
          </Text>
          <Flex gap="0.5" flex="1">
            {SHADES.map((shade) => (
              <ColorSwatch key={shade} palette={palette} shade={shade} />
            ))}
          </Flex>
        </Flex>
      ))}
    </Stack>
  );
}

function Buttons() {
  return (
    <Stack gap="3">
      {(["solid", "outline", "ghost", "subtle"] as const).map((variant) => (
        <Box key={variant}>
          <Text fontSize="xs" fontWeight="semibold" mb="1">{variant}</Text>
          <Flex gap="1.5" flexWrap="wrap">
            {COLOR_PALETTES.slice(0, 6).map((palette) => (
              <Button key={palette} variant={variant} colorPalette={palette} size="xs">
                {palette}
              </Button>
            ))}
          </Flex>
        </Box>
      ))}
    </Stack>
  );
}

function Badges() {
  return (
    <Stack gap="3">
      {(["solid", "outline", "subtle"] as const).map((variant) => (
        <Box key={variant}>
          <Text fontSize="xs" fontWeight="semibold" mb="1">{variant}</Text>
          <Flex gap="1.5" flexWrap="wrap">
            {COLOR_PALETTES.slice(0, 6).map((palette) => (
              <Badge key={palette} variant={variant} colorPalette={palette} size="sm">
                {palette}
              </Badge>
            ))}
          </Flex>
        </Box>
      ))}
    </Stack>
  );
}

function Typography() {
  return (
    <Stack gap="2">
      {(["2xl", "xl", "lg", "md", "sm"] as const).map((size) => (
        <Heading key={size} size={size}>Heading {size}</Heading>
      ))}
      <Separator />
      <Text fontSize="md">Body text (md)</Text>
      <Text fontSize="sm">Body text (sm)</Text>
      <Text color="fg.muted">Muted text (fg.muted)</Text>
      <Text color="fg.subtle">Subtle text (fg.subtle)</Text>
    </Stack>
  );
}

function FormElements() {
  const [checked, setChecked] = useState(false);

  return (
    <Stack gap="3">
      <Input placeholder="Default input" size="sm" />
      <Flex gap="3" alignItems="center" flexWrap="wrap">
        {(["blue", "green", "red", "purple"] as const).map((palette) => (
          <Switch.Root
            key={palette}
            colorPalette={palette}
            checked={checked}
            onCheckedChange={(e) => setChecked(e.checked)}
            size="sm"
          >
            <Switch.HiddenInput />
            <Switch.Control>
              <Switch.Thumb />
            </Switch.Control>
            <Switch.Label>{palette}</Switch.Label>
          </Switch.Root>
        ))}
      </Flex>
    </Stack>
  );
}

function SampleCard({ palette }: { palette: string }) {
  return (
    <Card.Root size="sm">
      <Card.Header pb="1">
        <Flex justifyContent="space-between" alignItems="center">
          <Card.Title fontSize="sm">Card</Card.Title>
          <Badge colorPalette={palette} variant="subtle" size="sm">{palette}</Badge>
        </Flex>
      </Card.Header>
      <Card.Body py="2">
        <Text color="fg.muted" fontSize="xs">
          Surface colors, radius, and shadows from the theme.
        </Text>
      </Card.Body>
      <Card.Footer pt="1">
        <Button colorPalette={palette} variant="outline" size="xs">Action</Button>
      </Card.Footer>
    </Card.Root>
  );
}

function ThemeExplorer() {
  const isDark = useIsDark();
  const bg = isDark ? AIRFLOW_DARK_BG : "white";
  const [isCustomTheme, setIsCustomTheme] = useState(false);

  useEffect(() => {
    fetch("ui/config", { credentials: "same-origin" })
      .then((r) => r.json())
      .then((data) => setIsCustomTheme(data.theme != null))
      .catch(() => {});
  }, []);

  return (
    <div id="theme-explorer-root" style={{ padding: "24px", maxWidth: "1200px", margin: "0 auto", backgroundColor: bg }}>
      <ChakraProvider value={activeSystem}>
        <Flex justifyContent="space-between" alignItems="center" mb="6">
          <Box>
            <Heading size="2xl">Theme Explorer</Heading>
            <Text color="fg.muted" mt="1">
              Visualizing the active Chakra UI theme in Airflow
            </Text>
          </Box>
          <Badge
            colorPalette={isCustomTheme ? "green" : "blue"}
            variant="subtle"
            size="lg"
            p="2"
          >
            {isCustomTheme ? "Custom Theme Active" : "Default Theme Active"}
          </Badge>
        </Flex>

        <Tabs.Root defaultValue="colors" variant="line">
          <Tabs.List>
            <Tabs.Trigger value="colors">Colors</Tabs.Trigger>
            <Tabs.Trigger value="typography">Typography</Tabs.Trigger>
            <Tabs.Trigger value="components">Components</Tabs.Trigger>
          </Tabs.List>

          <Box mt="6">
            <Tabs.Content value="colors">
              <ColorPalettes />
            </Tabs.Content>
            <Tabs.Content value="typography">
              <Typography />
            </Tabs.Content>
            <Tabs.Content value="components">
              <Stack gap="8">
                <Buttons />
                <Separator />
                <Badges />
                <Separator />
                <FormElements />
                <Separator />
                <Grid templateColumns="repeat(3, 1fr)" gap="4">
                  {(["blue", "green", "red"] as const).map((p) => (
                    <SampleCard key={p} palette={p} />
                  ))}
                </Grid>
              </Stack>
            </Tabs.Content>
          </Box>
        </Tabs.Root>
      </ChakraProvider>
    </div>
  );
}

globalThis["Theme Explorer"] = ThemeExplorer;
globalThis.AirflowPlugin = ThemeExplorer;

export default ThemeExplorer;
