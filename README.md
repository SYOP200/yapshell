# yap-shell

Your overly chatty terminal companion running Qwen 3.6 via Ollama!

## Features
- **Funny phrases** — every interaction is a laugh
- **Cool ASCII art** — banners, cats, robots and more
- **Animations** — typing effects, spinners, rainbow text, sparkles
- **Border-box panels** — responses displayed in styled boxes
- **Slash commands** — `/joke`, `/art`, `/fact`, `/status`, etc.
- **Conversation context** — remembers the last 20 turns
- **Zero deps** — runs with just Python + Ollama installed

## Requirements
- Python 3.9+
- [Ollama](https://ollama.com) with `qwen3.6` model loaded

## Run
From the project root:
```bash
python3 -m yapshell.main
```

Or directly:
```bash
python3 yapshell/main.py
```

## Commands
| Command     | Description                  |
|-------------|------------------------------|
| (anything)  | Chat with YAP                |
| `/help`     | Show command list            |
| `/joke`     | Tell a joke                  |
| `/art`      | Show ASCII art               |
| `/fact`     | Random fun fact              |
| `/clear`    | Clear the screen             |
| `/status`   | System stats                 |
| `/compliment` | Get complimented           |
| `/quit`     | Exit gracefully              |

## How It Works
yap-shell talks to Ollama's CLI directly via subprocess — no Python API library needed. The `qwen3.6` model must be pulled and running:

```bash
ollama pull qwen3.6
# (optional) ollama run qwen3.6  # keep this running, or yap will auto-start it
python3 main.py
```
