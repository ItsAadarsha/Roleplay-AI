# Terminal UI helpers — colors, formatted output, and user input
import datetime

# ANSI color codes
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RED = "\033[91m"


def header(text):
    # Prints a bold magenta banner around the given text
    line = "=" * max(40, len(text) + 4)
    print(f"{MAGENTA}{line}{RESET}")
    print(f"{BOLD}{MAGENTA}  {text}{RESET}")
    print(f"{MAGENTA}{line}{RESET}")


def subheader(text):
    print(f"{BOLD}{CYAN}{text}{RESET}")


def info(text):
    # Informational message in cyan
    print(f"{CYAN}[i]{RESET} {text}")


def success(text):
    # Success confirmation in green
    print(f"{GREEN}[✓]{RESET} {text}")


def error(text):
    # Error message in red
    print(f"{RED}[!] {text}{RESET}")


def prompt_input(prompt_text):
    # Styled input prompt; returns the raw string the user typed
    return input(f"{BOLD}{YELLOW}{prompt_text}{RESET} ")


def print_sessions(sessions):
    # Lists sessions with index, timestamp, and message count
    if not sessions:
        info("No previous sessions found.")
        return
    print()
    print(f"{BOLD}Previous sessions:{RESET}")
    for i, s in enumerate(sessions, start=1):
        created = s.get("created_at")
        if isinstance(created, datetime.datetime):
            created = created.strftime("%Y-%m-%d %H:%M")
        msg_count = len(s.get("messages", []))
        print(f"  {i}. {created} ({msg_count} messages)")
    print(f"  N. Start new session")


def print_message(role, name, content):
    # Prints a chat message; user lines show "You:", assistant lines show the persona name
    if role == "user":
        print(f"{BOLD}{YELLOW}You:{RESET} {content}")
    else:
        print(f"{BOLD}{YELLOW}{name}:{RESET} {content}")
