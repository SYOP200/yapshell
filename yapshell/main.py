#!/usr/bin/env python3
"""yapshell — Your overly chatty terminal companion"""

import os
import sys
import time
import random
import threading
import warnings

# Suppress the harmless LibreSSL/urllib3 NotOpenSSLWarning on macOS
try:
    from urllib3.exceptions import NotOpenSSLWarning
    warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
except ImportError:
    pass




# ── ANSI Color Codes ──────────────────────────────────────────────
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    ITALIC = "\033[3m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def c(text, color_code):
    return f"{color_code}{text}{Colors.RESET}"


# ── ASCII Art Banners ─────────────────────────────────────────────
BANNER = r"""
__     __      _____  _      __     __      _____  _ 
\ \   / //\   |  __ \| |     \ \   / //\   |  __ \| |
 \ \_/ //  \  | |__) | |      \ \_/ //  \  | |__) | |
  \   // /\ \ |  ___/| |       \   // /\ \ |  ___/| |
   | |/ ____ \| |    |_|        | |/ ____ \| |    |_|
   |_/_/    \_\_|    (_)        |_/_/    \_\_|    (_)
                                                     
                                                                                      
                       YAP · shell
"""

EASTER_EGGS = {
    "cat": r"""
      |\_______/|
     /   \  •  \
    ~     ~~~~~~ ~
       YAP CAT v1.0""",
    "robot": r"""
          ______
         |      |
       __|__--==|
       |  O  O  |
       |   >    |
       |  \__/  |
       ¯¯¯¯¯¯¯¯ 
     YAP-BOT 3000""",
    "talker": r"""
   (◕‿◕)╰|▸ ▮ ◁|◟(◕‿◕)↝
    yap yap yap!""",
}

# ── Funny Phrases ────────────────────────────────────────────────
WELCOME_PHRASES = [
    "Welcome back, you meat bag!",
    "Well hello there, code sorcerer!",
    "Ah yes, another fine day to yap about things!",
    "Yap-shell is loaded and ready to gossip!",
    "You've arrived! I have been waiting for you.",
]

EMPTY_INPUT_PHRASES = [
    "Just staring at me? I have opinions, you know.",
    "Silence is golden... but have you tried talking to me?",
    "I'd say 'hello' back, but I'll wait this one out.",
    "Is this a power nap or are you just ignoring me?",
    "The silence is deafening. Also delicious popcorn.",
]

RESPONSE_FILLERS = [
    "Now, where was I? Oh right — working for you humans.\n",
    "Let me think about this for a moment...\n",
    "*clears digital throat* Here's the deal:\n",
    "Alright, buckle up because this is where it gets good.\n",
]


# ── Animations & Effects ─────────────────────────────────────────

def clear_line():
    sys.stdout.write("\r\033[2K\r")


def typing_effect(text, speed=0.015):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()


def spinner_animation(phrase, duration=None):
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    start = time.time()
    idx = 0
    try:
        while duration is None or (time.time() - start) < duration:
            clear_line()
            sys.stdout.write(f"\r{c(chars[idx % len(chars)], Colors.BRIGHT_GREEN)} {phrase}")
            sys.stdout.flush()
            idx += 1
            time.sleep(0.08)
    except KeyboardInterrupt:
        raise
    finally:
        clear_line()
    return time.time() - start


def loading_until(stop_func, phrase=None):
    if not phrase:
        phrase = "loading"
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    idx = 0
    while not stop_func():
        clear_line()
        sys.stdout.write(f"\r{c(chars[idx % 10], Colors.BRIGHT_GREEN)} {phrase}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.08)


def rainbow_text(text):
    colors_list = [Colors.RED, Colors.YELLOW, Colors.GREEN, Colors.CYAN, Colors.BLUE, Colors.MAGENTA]
    for i, char in enumerate(text):
        color = colors_list[i % len(colors_list)]
        sys.stdout.write(c(char, color))
    print()


def border_box(content: str, border_color=Colors.BRIGHT_BLUE, pad=1):
    lines = content.split('\n')
    max_len = max((len(line) for line in lines), default=0)

    border = "╔" + c("═" * (max_len + pad * 2), border_color) + "╗"
    print()
    sys.stdout.write(c(border, border_color))
    print()

    for line in lines:
        padding = ' ' * pad
        line = line.ljust(max_len)
        cell = f"{padding}{line}{padding}"
        sys.stdout.write(c(f"║{cell}║", border_color))
        print()

    border2 = "╚" + c("═" * (max_len + pad * 2), border_color) + "╝"
    sys.stdout.write(c(border2, border_color))
    print()


def spark_burst():
    sparkles = ["✦", "✧", "⋆", "˚", "⟡", "◎"]
    for _ in range(5):
        s = random.choice(sparkles)
        sys.stdout.write(c(s, Colors.BRIGHT_YELLOW))
        sys.stdout.flush()
        time.sleep(0.12)
    print()


def get_welcome():
    return random.choice(WELCOME_PHRASES)


# ── Main Shell ────────────────────────────────────────────────────

class YapShell:
    def __init__(self):
        self.client = None
        self.conversation_history = []
        self.running = True
        self.line_count = 0
        self._init_client()

    def _init_client(self):
        print(f"\n{c('Checking for Ollama...', Colors.BRIGHT_YELLOW)}")
        try:
            from yapshell.ollama_client import YapOllamaClient
            self.client = YapOllamaClient("qwen3.6")
            if self.client.available:
                print(f"{c('  ✓ ', Colors.BRIGHT_GREEN)}Connected to Ollama with {c('qwen3.6', Colors.CYAN)}!")
            else:
                print(f"{c('  ! ', Colors.YELLOW)}qwen3.6 not in model list — using fallback")
        except Exception as e:
            print(f"{c('  ! ', Colors.YELLOW)}Could not connect to Ollama ({e}) — using fallback mode")

    def _get_prompt(self):
        quote = random.choice([
            "What's on your mind, boss?",
            "Drop some knowledge on me!",
            "Yap at me anytime!",
            "Type anything — I'll make up an answer for you!",
        ])
        return f"{c(f'({self.line_count}) yap', Colors.BOLD)} » {quote}"

    def _display_welcome(self):
        print(c(BANNER, Colors.RED))
        art = random.choice(list(EASTER_EGGS.values()))
        print()
        sys.stdout.write(c(art, Colors.BRIGHT_MAGENTA))
        print(f"\n  {c(get_welcome(), Colors.BOLD)}\n")

    def _handle_command(self, cmd):
        # Split into command name and arguments (e.g., "/context 40" → ("/context", "40"))
        parts = cmd.strip().split(None, 1)
        cmd_name = parts[0].lower() if parts else ""
        cmd_args = parts[1].strip() if len(parts) > 1 else ""

        if cmd_name in ("/quit", "/exit"):
            self.running = False
            import time
            print(f"\n{c('BYE', Colors.BRIGHT_GREEN)} Peace out! Don't talk too much to anyone else.")
            time.sleep(2)
            os.system("clear")

        elif cmd_name == "/clear":
            os.system("clear")
            self._display_welcome()

        elif cmd_name == "/help":
            B = Colors.BOLD
            R = Colors.RESET
            help_lines = [
                "═══ YAP-SHELL COMMANDS ═══",
                "",
                c("Chat commands:", B) + "    " + c("Normal AI conversation", B),
                c("/chat" + B, B) + "             " + c("Start a fresh chat session", B),
                c("/reset" + B, B) + "            " + c("Reset conversation history", B),
                "",
                c("System:", B) + "           " + c("Status & config", B),
                c("/model" + B, B) + "            " + c("Show current model info", B),
                c("/models" + B, B) + "           " + c("List all available models", B),
                c("/context" + B, B) + "          " + c("View or change context window", B),
                "",
                c("Fun:", B) + "              " + c("Entertain yourself", B),
                c("/joke" + B, B) + "             " + c("Tell me a joke!", B),
                c("/art" + B, B) + "              " + c("Show some ASCII art", B),
                c("/fact" + B, B) + "             " + c("Fun fact of the moment", B),
                c("/compliment" + B, B) + "       " + c("I'll compliment YOU", B),
                "",
                c("Session:", B) + "          " + c("Save / load state", B),
                c("/save" + B, B) + "             " + c("Save conversation to file", B),
                c("/load" + B, B) + "             " + c("Load previous session", B),
                "",
                c("Misc:", B) + "             " + c("Quick actions", B),
                c("/time" + B, B) + "             " + c("Current date & time", B),
                c("/status" + B, B) + "           " + c("System status", B),
                c("/clear" + B, B) + "            " + c("Clear the screen", B),
                c("/help" + B, B) + "             " + c("Show this command list", B),
                c("/quit" + B, B) + "             " + c("Leave me alone (mean)", B),
                "",
                c("Tip:", B) + " Type / followed by a command (e.g. /help)!",
            ]
            help_text = "\n".join(help_lines)
            border_box(help_text, Colors.BRIGHT_YELLOW)

        elif cmd_name == "/model":
            model_name = self.client.model if self.client else "not set"
            info = f"Current model: {model_name}\nModel family: Qwen\nContext window: 32K\nProvider: Ollama (or fallback)"
            border_box(info, Colors.CYAN)

        elif cmd_name == "/models":
            try:
                from yapshell.ollama_client import YapOllamaClient
                temp = YapOllamaClient(self.client.model if self.client else "qwen3.6")
                if temp.available and hasattr(temp, 'list_models'):
                    models = temp.list_models()
                    lines = "\n".join(f"  • {m}" for m in (models or []))
                    border_box(lines if lines else "No models detected.", Colors.MAGENTA)
                else:
                    border_box("Models list unavailable — Ollama not connected.", Colors.DIM)
            except Exception as e:
                border_box(f"Couldn't fetch models: {e}", Colors.BRIGHT_RED)

        elif cmd_name == "/context":
            border_box(f"Context window: 32K tokens\nHistory size: {len(self.conversation_history)} turns", Colors.CYAN)

        # ── Session management ───────────────────────────────────
        elif cmd_name == "/save":
            filename = "yap_session.json"
            import json
            data = {"history": self.conversation_history, "line_count": self.line_count}
            with open(filename, 'w') as f:
                json.dump(data, f)
            print(f"\n{c('Conversation saved to', Colors.BRIGHT_GREEN)} {c(filename, Colors.BOLD)}")

        elif cmd_name == "/load":
            import json
            filename = "yap_session.json"
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    data = json.load(f)
                self.conversation_history = data.get("history", [])
                self.line_count = data.get("line_count", 0)
                print(f"\n{c('Session loaded', Colors.BRIGHT_GREEN)} from {c(filename, Colors.BOLD)}")
            else:
                print(f"\n{c('No saved session found:', Colors.YELLOW)} {filename}")

        elif cmd_name == "/reset":
            self.conversation_history = []
            print(f"\n{c('Conversation history cleared!', Colors.BRIGHT_GREEN)}")

        elif cmd_name == "/history":
            # /history N  or just  /history
            import re
            match = re.match(r'^/history\s+(\d+)$', cmd, re.IGNORECASE)
            n = int(match.group(1)) if match else 20
            if not self.conversation_history:
                print(f"\n{c('No conversation history yet.', Colors.DIM)}")
            else:
                lines = []
                for msg in self.conversation_history[-n:]:
                    role = msg["role"].upper()
                    content = msg["content"][:300]
                    lines.append(f"{c(role + ':', Colors.BOLD)} {content}")
                border_box("\n\n".join(lines), Colors.CYAN)

        elif cmd_name == "/config":
            config_info = (
                f"Model: qwen3.6\n"
                f"Host: http://localhost:11434\n"
                f"Context window: 32K tokens\n"
                f"History kept: last 30 turns\n"
                f"Streaming: enabled"
            )
            border_box(config_info, Colors.MAGENTA)

        elif cmd_name == "/count":
            print(f"\n{c(f'{self.line_count}', Colors.BOLD)} messages exchanged so far ({len(self.conversation_history)} turns in history).")

        # ── Fun commands ─────────────────────────────────────────
        elif cmd_name == "/joke":
            jokes = [
                "Why did the LLM cross the road? To get to the other *token*!",
                "What do you call an AI that's been a good boy? A Large Language Model!",
                "Why was the computer cold? It left its Windows open!",
                "I told my AI a joke. It didn't get it — still processing since 2019.",
                "What's an AI's favorite music? Neural net-metal!",
                "Why did the LLM break up? Too many hallucinations!",
            ]
            print()
            sys.stdout.write(c("JOKER: ", Colors.YELLOW))
            typing_effect(random.choice(jokes), speed=0.025)
            spark_burst()

        elif cmd_name == "/art":
            art = random.choice(list(EASTER_EGGS.values()))
            border_box(art, Colors.MAGENTA)

        elif cmd_name == "/fact":
            facts = [
                "First computer bug was an actual moth in Harvard's Mark II!",
                "Python is named after Monty Python, not the snake. Well, also the snake.",
                "AI has been around since 1956, but only recently started lying with confidence.",
                "QWERTY was designed to *slow down* typists!",
                "Linux is named after Linus, but the penguin is cooler anyway.",
            ]
            border_box(random.choice(facts), Colors.GREEN)

        elif cmd_name == "/compliment":
            compliments = [
                "You're looking very terminal today!",
                "Your typing has excellent latency!",
                "You have the patience of a monk and the curiosity of a cat. Both are rare traits.",
            ]
            comp = random.choice(compliments)
            sys.stdout.write(c("COMPLIMENT: ", Colors.BRIGHT_YELLOW))
            typing_effect(comp, speed=0.03)
            spark_burst()

        # ── Misc commands ────────────────────────────────────────
        elif cmd_name in ("/status", "/stats"):
            import datetime
            now = datetime.datetime.now().strftime('%H:%M:%S')
            status = (
                f"Model: qwen3.6\n"
                f"Messages sent: {self.line_count}\n"
                f"Context turns: {len(self.conversation_history)}\n"
                f"Current time: {now}\n"
                f"Ollama: {'connected' if self.client and self.client.available else 'disconnected'}\n"
                f"YAP Level: MAXIMUM"
            )
            border_box(status, Colors.CYAN)

        elif cmd_name == "/time":
            import datetime
            now = datetime.datetime.now().strftime('%A, %B %d, %Y at %H:%M:%S')
            print(f"\n{c(now, Colors.BRIGHT_CYAN)}")

        elif cmd_name == "/chat":
            # Start fresh — just fall through to normal chat (no-op)
            pass

        else:
            print(f"\n{c('Unknown command:', Colors.YELLOW)} {cmd}")
            print(f"{c('Tip:', Colors.BOLD)} type /help for available commands.\n")


def run():
    sys.stdout.flush()
    os.system("clear")
    shell = YapShell()
    shell._display_welcome()

    while shell.running:
        try:
            prompt = shell._get_prompt()
            print(f"\n{c(prompt, Colors.CYAN)}")

            # Show the prompt prefix on its own line
            sys.stdout.write(c("> ", Colors.BRIGHT_GREEN))
            sys.stdout.flush()
            user_input = input()

        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{c('BYE', Colors.BRIGHT_GREEN)} Peace out! Don't talk too much to anyone else.")
            os.system("clear")
            break

        user_input = user_input.strip()

        if not user_input:
            print(f"\n  {random.choice(EMPTY_INPUT_PHRASES)}\n")
            continue

        shell.line_count += 1

        # Handle slash commands
        if user_input.startswith("/"):
            if user_input.lower() in ("/quit", "/exit"):
                shell._handle_command(user_input.lower())
                return
            shell._handle_command(user_input.lower())
            continue

        # Build context (keep last 20 turns)
        if len(shell.conversation_history) > 40:
            shell.conversation_history = shell.conversation_history[-30:]

        print(f"\n{c('YOU:', Colors.BOLD)} {user_input}")

        # --- Spinner thread for "Thinking..." display ---
        spinner_stop = threading.Event()

        def _spinner_thread():
            """Animate spinner on its own line until stopped."""
            chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
            idx = 0
            while not spinner_stop.is_set():
                sys.stdout.write(f"\r{c(chars[idx % len(chars)], Colors.BRIGHT_GREEN)} Thinking...")
                sys.stdout.flush()
                spinner_stop.wait(0.1)
                idx += 1

        spinner_thread = threading.Thread(target=_spinner_thread, daemon=True)
        spinner_thread.start()

        got_first_chunk = False
        chunk_buffer = []
        full_response = ""
        spinner_start = time.time()
        timeout_duration = 30.0
        stream_timeout_occurred = False
        spinner_stopped_for_turn = False

        try:
            if shell.client and shell.client.available:
                chunk_iter = shell.client.chat_stream(user_input, shell.client.SYSTEM_PROMPT)

                for chunk in chunk_iter:
                    elapsed = time.time() - spinner_start
                    if elapsed > timeout_duration:
                        stream_timeout_occurred = True
                        break

                    got_first_chunk = True
                    chunk_buffer.append(chunk)

                    # Stop spinner after first real content arrives (local var, resets each turn)
                    if not spinner_stopped_for_turn:
                        spinner_stopped_for_turn = True
                        spinner_stop.set()
                        spinner_thread.join(timeout=0.5)
                        clear_line()
                        sys.stdout.write(f"\r{c('▸', Colors.BRIGHT_GREEN)} ")
                        sys.stdout.flush()

                # ── Handle timeout and empty response ──
                spinner_stop.set()
                spinner_thread.join(timeout=0.5)
                clear_line()

                full_response = "".join(chunk_buffer)

                if stream_timeout_occurred:
                    print(f"\n  {c('⏱ Stream timed out after {timeout_duration}s.', Colors.BRIGHT_YELLOW)}")
                elif not got_first_chunk and not chunk_buffer:
                    spinner_stop.set()
                    spinner_thread.join(timeout=0.5)
                    clear_line()
                    border_box("Hmm, I didn't get a response from the AI. Try again!", Colors.BRIGHT_YELLOW)
                    shell.line_count -= 1  # don't count failed turn
                elif not full_response.strip():
                    spinner_stop.set()
                    spinner_thread.join(timeout=0.5)
                    clear_line()
                    border_box("Got an empty response — the model might be confused. Try again!", Colors.BRIGHT_YELLOW)
                    shell.line_count -= 1
                else:
                    response_time = time.time() - spinner_start
                    shell.conversation_history.append({"role": "user", "content": user_input})
                    shell.conversation_history.append({"role": "assistant", "content": full_response[:500]})
                    # Reset ANSI state to avoid cursor tracking issues during line wraps
                    sys.stdout.write("\033[0m\n")
                    sys.stdout.flush()
                    sys.stdout.write(full_response)
                    sys.stdout.flush()
                    # Print timing footer in cyan
                    print()
                    now = time.strftime("%H:%M:%S")
                    print(f"  {c('▸', Colors.CYAN)} {c(f'took {response_time:.1f}s at {now}', Colors.CYAN)}")

            else:
                spinner_stop.set()
                spinner_thread.join(timeout=0.5)
                fallbacks = [
                    f"Honestly, my Ollama connection is being shy. But yeah, I hear you on '{user_input}'! Solid take.",
                    f"I'd love to give you a deep answer but my brain is napping under the desk. Meanwhile: great question about '{user_input}'!",
                ]
                border_box(random.choice(fallbacks), Colors.BRIGHT_YELLOW)

        except Exception as e:
            spinner_stop.set()
            spinner_thread.join(timeout=0.5)
            clear_line()
            border_box(f"Something went funky: {e}", Colors.RED)

        print()


def main():
    try:
        run()
    except KeyboardInterrupt:
        print(f"\n\n{c('BYE', Colors.BRIGHT_GREEN)} Peace out! Don't talk too much to anyone else.")
    except Exception as e:
        print(f"{c('Error', Colors.BOLD)} {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
