<p align="center">
  <img src="resources/AI Happy Design Icon.png" alt="AI Happy Design" width="128" height="128">
</p>

# AI Happy Design

**Give AI full control of your Figma canvas.**

A single Go binary, available as `ahd-figma` and the legacy `ai-happy-design` command, that connects any AI (Claude, GPT, Gemini, etc.) to Figma through a local WebSocket relay. Design, inspect, edit, and export from natural language.

Made by [Ashraf Ali](https://ashrafali.net) | [GitHub](https://github.com/nerveband/ai-happy-design) | MIT License

---

## Screenshot

<p align="center">
  <img src="resources/AI Happy Coder Screenshot v1.png" alt="AI Happy Design Plugin" width="420">
</p>

## Architecture

```
AI / LLM              CLI (scripting)
   |                    |
   v                    v
[MCP Server] -----> [WebSocket Relay] <-----> [Figma Plugin]
                    localhost:3055
```

One binary. Three modes:
- **MCP server** — schema-backed integration for AI editors (Claude Code, Cursor, Windsurf, etc.)
- **CLI** — direct commands and batch payloads. **10-50x faster than MCP for bulk operations** because it sends a single batch payload over one WebSocket connection instead of individual MCP tool calls. AI agents can use the CLI for heavy lifting.
- **Relay** — WebSocket bridge to the Figma plugin

## What's Included

- **15 tool domains**: paint, shape, text, layout, node, layer, component, style, variable, effect, boolean, page, document, export, design
- **Schema-backed MCP**: `ahd-figma mcp` exposes the same command schemas as the CLI plus resources for schemas, tools, and the design guide
- **Current Figma context APIs**: inspect Dev Mode focused node with `document.get_focused_node` and generated CSS with `node.get_css`
- **Batch operations**: Chain 150+ commands in one payload with step interpolation (`${{steps.name.result.id}}`), per-operation timing stats, ~27 ops/sec
- **Smart canvas placement**: `document.find_free_space` scans existing frames and returns exact coordinates — AI never guesses where to place new designs
- **Design tokens**: `design.compute_tokens` auto-computes fonts, spacing, padding, and layout for any canvas size — no Figma connection required
- **Design intelligence**: Built-in design guide the AI can call to learn typography, balance, visual hierarchy, and CSS-to-Figma translation
- **Auto-registration**: `ahd-figma register` detects installed AI editors and configures MCP automatically
- **Unicode-safe**: Full support for emojis, CJK, accented characters, em-dashes, and special characters
- **Local only**: Everything on localhost. Nothing leaves your machine.

## Quick Start

### 1. Install

Download the latest binary from [GitHub Releases](https://github.com/nerveband/ai-happy-design/releases):

```bash
# macOS (Apple Silicon)
curl -L https://github.com/nerveband/ai-happy-design/releases/latest/download/ai-happy-design_Darwin_arm64.tar.gz | tar xz
sudo mv ai-happy-design /usr/local/bin/

# macOS (Intel)
curl -L https://github.com/nerveband/ai-happy-design/releases/latest/download/ai-happy-design_Darwin_x86_64.tar.gz | tar xz
sudo mv ai-happy-design /usr/local/bin/

# Linux
curl -L https://github.com/nerveband/ai-happy-design/releases/latest/download/ai-happy-design_Linux_x86_64.tar.gz | tar xz
sudo mv ai-happy-design /usr/local/bin/
```

> **Building from source?** Run `codesign -s - ai-happy-design` on macOS after building. Release binaries are pre-signed.

### 2. Setup Plugin

```bash
ahd-figma setup
```

This extracts the embedded Figma plugin and opens Finder to the manifest file.

1. Figma desktop → **Plugins > Development > Import plugin from manifest**
2. Select the revealed `manifest.json`
3. Run: **Plugins > AI Happy Design**

### 3. Register with Your AI Editor

```bash
ahd-figma register
```

Auto-detects installed editors (Claude Code, Claude Desktop, Cursor, Windsurf, VS Code, Zed) and registers the MCP server. Or register with a specific editor:

```bash
ahd-figma register --editor "Claude Code"
ahd-figma register --editor "Cursor"
```

**Manual setup** (if you prefer):

<details>
<summary>Claude Code</summary>

```bash
claude mcp add ahd-figma -- ahd-figma mcp
```

Or add to `~/.claude.json`:
```json
{
  "mcpServers": {
    "ahd-figma": {
      "type": "stdio",
      "command": "ahd-figma",
      "args": ["mcp"]
    }
  }
}
```
</details>

<details>
<summary>Claude Desktop / Cursor / Windsurf</summary>

Add to your MCP config file:
```json
{
  "mcpServers": {
    "ahd-figma": {
      "command": "ahd-figma",
      "args": ["mcp"]
    }
  }
}
```
</details>

Restart your editor after registering. The MCP server auto-detects if a relay is already running and connects as a client — no need to start the relay separately.

### 3.5 Optional: Install the AI Skill Bundle

If you want a ready-made skill that helps AI agents call the CLI and follow the discovery-first workflow, use the packaged bundle:

- `ai-happy-design.skill` (repo root, also suitable as a release asset)

This is optional; the MCP server and CLI work without it.

### 4. Verify

```bash
ahd-figma tools --json       # List all tools
ahd-figma command document.get_info   # Test connection
```

### 5. Upgrade

```bash
ahd-figma upgrade
```

Auto-checks for updates daily and notifies you. Upgrade downloads and installs the new binary in-place.

## How It Works

### Using with an AI Agent (Recommended)

AI Happy Design ships with a **skill file** that teaches AI agents how to use the CLI. When you invoke the skill, the agent gets the full command reference, batch format, composite commands, design tokens, and best practices.

**Option A: Call the skill** (if installed via skillshare or `~/.claude/skills/`):

> "Use the ai-happy-design skill to create a 5-slide Instagram carousel about [topic]"

**Option B: Tell the AI to use the CLI directly:**

> "Use the ai-happy-design CLI to design an Instagram post about [topic]. Run `ahd-figma command design.compute_tokens` first for sizing."

The skill is the preferred approach — it gives the AI everything it needs in one shot, including composite command format, batch aliases, design token workflow, and common pitfalls.

### Installing the Skill

The skill file (`SKILL.md`) teaches AI agents how to call the CLI effectively.

```bash
# If using skillshare (syncs to all AI tools automatically)
# The skill is already at ~/.claude/skills/ai-happy-design/SKILL.md

# Or copy manually for Claude Code
mkdir -p ~/.claude/skills/ai-happy-design
cp path/to/SKILL.md ~/.claude/skills/ai-happy-design/SKILL.md
```

### What the Skill Teaches the AI

1. **Compute tokens** — get proportional font sizes and spacing for the target canvas
2. **Find free space** — get exact coordinates so designs never overlap
3. **Measure and fit text** — use `text.measure` and `text.fit_box` before locking dense layouts
4. **Think in CSS** — draft HTML/CSS-like structure, then translate sections to Figma commands
5. **Batch create** — write composite commands, `text.create_rich_block`, `layout.pricing_grid`, or primitive ops
6. **Export & iterate** — compare against the reference, adjust the batch, and rerun

## CLI Usage

The CLI is the fastest way to drive Figma operations — **recommended for AI agents doing bulk work**.

### Single command
```bash
ahd-figma command paint.set_solid -p '{"nodeId":"1:2","color":"#2563EB"}'
```

### Batch operations (fastest)
```bash
# From file — send 100+ operations in one shot:
ahd-figma batch -f payload.json

# Inline:
ahd-figma batch -o '[{"name":"card","command":"node.create_frame","params":{"width":320,"height":200}}]'
```

### List available actions
```bash
ahd-figma actions           # All domains and actions
ahd-figma actions document  # Just document actions
ahd-figma tools --llm       # Full LLM-focused catalog with examples
```

### Relay management
```bash
ai-happy-design relay start      # Background start
ai-happy-design relay status     # Check connection
ai-happy-design relay logs       # View logs
ai-happy-design relay stop       # Stop
```

### Channel resolution order
1. Positional argument
2. `--channel` flag
3. `AHD_CHANNEL` env var
4. Relay's active channel (auto-detected)

## Export Formats

Export any node as PNG, JPG, SVG, or PDF:

```bash
ahd-figma command export.image '{"nodeId":"47:765","format":"PNG","scale":2}' -o output.png
ahd-figma command export.image '{"nodeId":"47:765","format":"JPG","scale":1}' -o output.jpg
ahd-figma command export.svg '{"nodeId":"47:765"}' -o output.svg
ahd-figma command export.pdf '{"nodeId":"47:765"}' -o output.pdf
```

SVG exports are saved as raw SVG text. PNG/JPG/PDF are decoded from base64. The `-o` flag specifies the output path; without it, a filename is auto-generated from the node name.

## Composite Commands (v0.10+)

Write one high-level command, get a complete Figma slide or banner. Composites auto-expand into 5–15 primitive operations with design tokens, gradients, and layout.

```bash
# One slide command → 7-15 Figma operations
ahd-figma batch '[{
  "name": "s1",
  "command": "slide",
  "params": {
    "canvas": "1080x1350",
    "color": "#0C1E2C",
    "gradient": {"type":"LINEAR","angle":150,"stops":[
      {"color":"#0C1E2C","position":0},{"color":"#14344A","position":1}
    ]},
    "elements": [
      {"type": "eyebrow", "text": "RAMADAN 2026", "color": "#7FBCD2"},
      {"type": "headline", "text": "The Care\nBehind\nthe Care", "tier": "hero"},
      {"type": "bar", "color": "#029056"},
      {"type": "body", "text": "250+ chaplains serve.", "color": "#FAFCFBB3"},
      {"type": "cta", "text": "Donate Now", "bg": "#029056"},
      {"type": "url", "text": "example.com/donate"}
    ]
  }
}]'
```

Element types: `eyebrow`, `headline`, `body`, `bar`, `cta`, `url`, `counter`, `stats`, `progress`, `arabic`. Banner command supports `headline` and `subtitle`.

## HTML → Figma (v0.10+)

Extract slides and banners from styled HTML files directly into Figma:

```bash
# Parse HTML/CSS → composite batch JSON
ahd-figma extract social-posts.html --width 1080 --height 1350

# Full pipeline: HTML → Figma in one line
ahd-figma extract input.html -o /tmp/ops.json && ahd-figma batch /tmp/ops.json
```

The extract command parses `<style>` blocks, inline styles, gradients, colors, and font weights. Each `.slide` becomes a `slide` composite command, each `.email-banner` becomes a `banner`.

For high-fidelity recreation from screenshots or HTML/CSS references, use the measured workflow:

1. Inspect the reference with `node.get_css` when matching existing Figma nodes, or summarize the HTML/CSS structure yourself.
2. Measure critical copy with `text.measure`; fit constrained labels with `text.fit_box`.
3. Use `text.create_rich_block` for grouped headings, prices, bullets, and notes.
4. Use `layout.pricing_grid` for CSS-like card grids instead of hand-positioning every text node.
5. Export, compare visually, then adjust spacing, typography, and content in the same batch file.

See `docs/examples/html-css-recreation-workflow.json` for a compact executable-style payload.

## Benchmarking (v0.10+)

Provider-agnostic performance measurement — no LLM API calls built in:

```bash
# Time batch execution against Figma
ahd-figma benchmark exec ops.json --runs 3

# Time external LLM + execution (pipe any LLM output)
START=$(date +%s%N)
BATCH=$(curl -sS your-llm-api... | jq -r '.choices[0].message.content')
MS=$(( ($(date +%s%N) - START) / 1000000 ))
echo "$BATCH" | ahd-figma benchmark pipe --phase-a-ms $MS
```

## Performance

| Scenario | Time | Ops/sec |
|----------|------|---------|
| Single slide (composite) | ~1.4s | 6–8 |
| 5-slide carousel (20 ops) | ~2.8s | 7.3 |
| 36-frame campaign (146 ops) | ~18s | 8.1 |
| E2E with Cerebras LLM (1 slide) | ~2.0s | — |

CLI batch sends all operations over one WebSocket connection. MCP sends each tool call individually. For designs with 20+ operations, CLI batch is significantly faster.

Batch output includes per-operation `elapsedMs` and a `timing` summary with `totalMs`, `avgMs`, and `opsPerSec`.

## Do's and Don'ts

**Do:**
- Discover with `ahd-figma tools --llm --json`, MCP `tools/list`, or `ahd_describe`
- Call `document.find_free_space` before creating new frames — it returns exact coordinates
- Call `design.compute_tokens` to get sizing for your canvas
- Use CLI batch for multi-element designs (3+ elements)
- Use `document.get_focused_node` and `node.get_css` before matching existing Figma context
- Use **absolute x/y positioning** for main layout + auto-layout only for badges/buttons
- Always pass `lineHeightUnit: "PERCENT"` with `text.set_line_height` (default is PIXELS)
- Export at scale=2 for crisp output
- Name every element descriptively

**Don't:**
- Guess frame positions — always use `find_free_space`
- Create cards as rectangles with floating text (use frames with children)
- Leave default names like "Frame 47"
- Use text below 16px on 1080px social media canvases
- Mix padding/spacing values across sibling cards
- Use `lineHeight: 140` without `lineHeightUnit: "PERCENT"` (140 pixels != 140%)
- Skip the balance check on sibling elements

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Plugin "Disconnected" | Start relay: `ahd-figma relay start` |
| Commands fail | Run `ahd-figma tools --llm --json` or MCP `tools/list` to rediscover tools |
| Wrong port | Edit Relay URL in plugin UI |
| Channel mismatch | Copy key from plugin, pass via `--channel` |
| Plugin won't load | Run `ahd-figma setup --force` to re-extract |
| Binary killed on macOS (source build) | Run `codesign -s - /path/to/ahd-figma` |
| MCP not loading in editor | Run `ahd-figma register --force` to re-register |

## Prerequisites

- Figma desktop app
- Go 1.21+ (only for building from source)
- Node.js 18+ (only for building from source)

## All Commands

| Command | Description |
|---------|-------------|
| `ahd-figma setup` | Extract and install the Figma plugin |
| `ahd-figma register` | Auto-register MCP with detected AI editors |
| `ahd-figma mcp` | Start MCP server (stdio transport, for AI editors) |
| `ahd-figma ws` | Start WebSocket relay only |
| `ahd-figma command <action>` | Execute a single command |
| `ahd-figma batch` | Execute a batch of commands |
| `ahd-figma actions` | List all domain.action pairs |
| `ahd-figma tools` | Print tool catalog |
| `ahd-figma extract <file.html>` | Parse HTML/CSS into batch JSON |
| `ahd-figma benchmark exec/pipe` | Provider-agnostic performance benchmarking |
| `ai-happy-design relay start/stop/status/logs` | Manage the relay process |
| `ahd-figma upgrade` | Upgrade to the latest version |

## Usage Scenarios

### Scenario 1: AI Agent Designs from a Prompt

Invoke the skill, then describe what you want:

> **You:** "Use the ai-happy-design skill to create a 5-slide Instagram carousel about Muslim chaplains"

Or if the skill is auto-loaded (via skillshare or Claude Code settings):

> **You:** "Design a 5-slide Instagram carousel about Muslim chaplains in Figma"

The AI reads the skill, then uses the CLI:
1. `ahd-figma command design.compute_tokens '{"width":1080,"height":1350}'` — sizing
2. `ahd-figma command document.find_free_space '{"width":1080,"height":1350}'` — placement
3. Writes composite `slide` commands to a JSON file
4. `ahd-figma batch /tmp/slides.json` — creates everything in Figma
5. `ahd-figma command export.image '{"nodeId":"...","scale":2}'` — verifies

### Scenario 2: CLI Batch from a JSON File

Write (or have AI generate) a JSON batch file and execute it directly:

```bash
# Create a batch file with composite commands
cat > /tmp/slides.json << 'EOF'
[
  {"name":"s1","command":"slide","params":{"canvas":"1080x1350","color":"#1a1a2e",
    "elements":[
      {"type":"headline","text":"Hello World","tier":"hero"},
      {"type":"body","text":"Made with AI Happy Design","color":"#ffffffB3"}
    ]}}
]
EOF

# Execute against Figma
ahd-figma batch /tmp/slides.json
```

### Scenario 3: HTML File → Figma

Have a designer's HTML spec? Extract and execute in one pipeline:

```bash
# Two-step (inspect the JSON first)
ahd-figma extract mockup.html --width 1080 --height 1350 -o /tmp/ops.json
ahd-figma batch /tmp/ops.json

# One-liner
ahd-figma extract mockup.html -o /tmp/ops.json && ahd-figma batch /tmp/ops.json
```

### Scenario 4: LLM Generates JSON, CLI Executes

Use any LLM (Cerebras, OpenAI, Claude API, local models) to generate the batch JSON, then pipe it to the CLI:

```bash
# Cerebras (fast, cheap)
curl -sS https://api.cerebras.ai/v1/chat/completions \
  -H "Authorization: Bearer $CEREBRAS_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen-3-235b-a22b-instruct-2507","messages":[
    {"role":"system","content":"Output ONLY a JSON array of slide composite commands."},
    {"role":"user","content":"Create a fundraiser slide, 1080x1350, dark blue theme"}
  ]}' | jq -r '.choices[0].message.content' | ahd-figma batch

# OpenAI
curl -sS https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"gpt-4o","messages":[
    {"role":"system","content":"Output ONLY a JSON array of slide composite commands."},
    {"role":"user","content":"Create a fundraiser slide"}
  ]}' | jq -r '.choices[0].message.content' | ahd-figma batch
```

### Scenario 5: Multi-File Batch

Execute multiple JSON files at once, or an entire directory:

```bash
ahd-figma batch slides.json banners.json     # two files
ahd-figma batch ./campaign/                    # all .json in directory
ahd-figma batch *.json --parallel              # concurrent (max 4)
```

### Scenario 6: Benchmark Your Pipeline

Measure end-to-end performance with any LLM provider:

```bash
# Just measure execution speed
ahd-figma benchmark exec ops.json --runs 3

# Measure LLM generation + execution
START=$(date +%s%N)
JSON=$(curl -sS your-llm... | jq -r '.choices[0].message.content')
MS=$(( ($(date +%s%N) - START) / 1000000 ))
echo "$JSON" | ahd-figma benchmark pipe --phase-a-ms $MS
```

## Documentation

See `docs/` for detailed guides:
- [Getting Started](docs/getting-started.md)
- [LLM Integration](docs/llm-integration.md)
- [CLI Batch & Payloads](docs/cli-batch-and-payloads.md)
- [Image Fill Contract](docs/image-fill-contract.md)
- [Troubleshooting](docs/troubleshooting.md)

## License

MIT — see [LICENSE](LICENSE).
