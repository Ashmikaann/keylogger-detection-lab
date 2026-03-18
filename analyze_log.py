"""
=============================================================
  KEYLOG ANALYZER - For Educational / Lab Use Only
  File: analyze_log.py
  How to run: python analyze_log.py
=============================================================
  Reads the keylog.txt file and generates a human-readable
  analysis report showing:
  - Total keys logged
  - Most common keys
  - Reconstructed typed words
  - Session info
=============================================================
"""

import os
import re
from collections import Counter

LOG_FILE = "keylog.txt"


def load_log(filepath):
    """Read the raw keylog file."""
    if not os.path.exists(filepath):
        print(f"[!] Log file not found: {filepath}")
        print("[!] Run keylogger.py first to generate it.")
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def extract_typed_text(raw):
    """
    Reconstructs what the user actually typed:
    - Applies [BACK] as actual backspace deletions
    - Treats [ENTER] as a newline
    - Ignores other special keys for the text reconstruction
    """
    # Split by special key markers and process
    segments = re.split(r'(\[[^\]]+\])', raw)
    result = []
    for seg in segments:
        if seg == "[BACK]":
            if result:
                result.pop()
        elif seg == "[ENTER]":
            result.append("\n")
        elif seg == "[TAB]":
            result.append("    ")
        elif seg.startswith("[") and seg.endswith("]"):
            pass   # Skip other special keys in reconstruction
        else:
            result.append(seg)
    return "".join(result)


def count_key_frequencies(raw):
    """Counts how many times each key was pressed."""
    # Find all special keys like [ENTER], [BACK], etc.
    special_keys = re.findall(r'\[[^\]]+\]', raw)
    # Find all regular characters (everything not in brackets)
    regular_text = re.sub(r'\[[^\]]+\]', '', raw)
    regular_chars = [c for c in regular_text if c.strip()]

    freq = Counter()
    freq.update(regular_chars)
    freq.update(special_keys)
    return freq


def extract_sessions(raw):
    """Finds all session blocks in the log file."""
    sessions = re.findall(
        r'SESSION STARTED: (.+?)\n(.*?)SESSION ENDED:\s+(.+?)\n.*?Total keys:\s+(\d+).*?Duration:\s+([\d.]+)',
        raw, re.DOTALL
    )
    return sessions


def print_analysis(raw):
    """Print a full analysis of the log file."""
    print("\n" + "=" * 60)
    print("  KEYLOG ANALYSIS REPORT")
    print("=" * 60)

    # ── Session summary ──
    sessions = extract_sessions(raw)
    if sessions:
        print(f"\n📋 SESSIONS FOUND: {len(sessions)}")
        for i, (start, _, end, keys, dur) in enumerate(sessions, 1):
            print(f"  Session {i}: Started {start.strip()}")
            print(f"             Ended   {end.strip()}")
            print(f"             Keys: {keys}  |  Duration: {dur}s")
    else:
        print("\n📋 No complete sessions found in log.")

    # ── Key frequency ──
    freq = count_key_frequencies(raw)
    print(f"\n⌨️  TOP 15 MOST PRESSED KEYS:")
    print(f"  {'Key':<20} {'Count':>8}")
    print(f"  {'-'*20}  {'-'*8}")
    for key, count in freq.most_common(15):
        bar = "█" * min(count, 30)
        print(f"  {repr(key):<20} {count:>5}  {bar}")

    # ── Reconstructed text ──
    typed = extract_typed_text(raw)
    # Remove session headers
    typed_clean = re.sub(r'={20,}.*?={20,}', '', typed, flags=re.DOTALL).strip()

    print(f"\n📝 RECONSTRUCTED TYPED TEXT:")
    print("-" * 60)
    # Show first 500 chars max
    preview = typed_clean[:500]
    if len(typed_clean) > 500:
        preview += f"\n... [{len(typed_clean) - 500} more characters]"
    print(preview if preview.strip() else "(nothing typed yet or only special keys)")
    print("-" * 60)

    # ── Simple stats ──
    words = re.findall(r'\b\w+\b', typed_clean)
    print(f"\n📊 QUICK STATS:")
    print(f"  Total characters logged : {len(raw)}")
    print(f"  Reconstructed chars     : {len(typed_clean)}")
    print(f"  Estimated words typed   : {len(words)}")
    print(f"  Unique keys used        : {len(freq)}")

    print("\n" + "=" * 60)


def main():
    print(f"[+] Reading log file: {os.path.abspath(LOG_FILE)}")
    raw = load_log(LOG_FILE)
    if raw:
        print_analysis(raw)


if __name__ == "__main__":
    main()
