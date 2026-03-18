"""
=============================================================
  BEHAVIORAL DETECTION SCRIPT - For Educational / Lab Use Only
  File: detector.py
  How to run: python detector.py
=============================================================
  What this does:
  - Scans all running processes on your computer
  - Looks for SUSPICIOUS BEHAVIOR patterns typical of keyloggers:
      1. High keyboard API usage
      2. Frequent file writes to text/log files
      3. Network connections (possible data exfiltration)
      4. Processes with suspicious names or hidden windows
  - Gives each process a RISK SCORE and prints a report
=============================================================
"""

import psutil
import os
import sys
import time
import datetime
import platform

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────
SCAN_INTERVAL  = 3     # seconds between scans
RISK_THRESHOLD = 3     # score >= this → flagged as suspicious

# Keywords that appear in known keylogger / spyware file names
SUSPICIOUS_NAMES = [
    "keylog", "logger", "spy", "hook", "monitor",
    "capture", "record", "sniff", "stealth", "ghost",
    "rat", "trojan", "backdoor", "hack"
]

# File extensions that keyloggers typically write to
LOG_EXTENSIONS = [".txt", ".log", ".dat", ".csv", ".json"]

# Processes that are always safe to ignore (system processes)
WHITELIST = [
    "system", "svchost", "explorer", "dwm", "csrss",
    "smss", "wininit", "services", "lsass", "spoolsv",
    "taskmgr", "python", "pythonw", "cmd", "powershell",
    "bash", "sh", "zsh", "fish", "code", "cursor",
    "chrome", "firefox", "safari", "edge", "brave",
    "slack", "teams", "zoom", "discord"
]


# ──────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def is_whitelisted(proc_name):
    """Returns True if the process is a known safe system process."""
    name_lower = proc_name.lower()
    for safe in WHITELIST:
        if safe in name_lower:
            return True
    return False


def check_suspicious_name(proc_name):
    """Check if the process name contains suspicious keywords."""
    name_lower = proc_name.lower()
    for keyword in SUSPICIOUS_NAMES:
        if keyword in name_lower:
            return True, keyword
    return False, None


def check_open_files(proc):
    """
    Check if the process has any log/text files open for writing.
    This is a major red flag — keyloggers write keys to files.
    """
    suspicious_files = []
    try:
        open_files = proc.open_files()
        for f in open_files:
            _, ext = os.path.splitext(f.path)
            if ext.lower() in LOG_EXTENSIONS:
                # Check if it's writable (not a system read-only file)
                suspicious_files.append(f.path)
    except (psutil.AccessDenied, psutil.NoSuchProcess, PermissionError):
        pass
    return suspicious_files


def check_network_connections(proc):
    """
    Check if the process has active outbound network connections.
    A keylogger sending data to an attacker would show up here.
    """
    connections = []
    try:
        conns = proc.connections(kind="inet")
        for conn in conns:
            if conn.status == "ESTABLISHED" and conn.raddr:
                connections.append(f"{conn.raddr.ip}:{conn.raddr.port}")
    except (psutil.AccessDenied, psutil.NoSuchProcess, PermissionError):
        pass
    return connections


def check_cpu_pattern(proc):
    """
    Keyloggers often show a specific CPU pattern:
    - Very low CPU (sleeping between key checks)
    - But consistent — never fully 0%
    Returns True if CPU looks like a polling loop.
    """
    try:
        # Sample CPU usage twice, 0.3s apart
        cpu1 = proc.cpu_percent(interval=0.3)
        return 0.1 < cpu1 < 5.0   # Low but non-zero — polling pattern
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        return False


def check_hidden_or_background(proc):
    """
    Check if the process has no visible window (running hidden).
    Legitimate apps usually have windows. Keyloggers often don't.
    """
    try:
        # On Windows: check if the process has any visible windows
        if platform.system() == "Windows":
            import ctypes
            return proc.num_handles() > 0  # simplified heuristic
        else:
            # On Linux/Mac: check if process is a daemon (no controlling terminal)
            return proc.terminal() is None
    except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError):
        return False


# ──────────────────────────────────────────────
# MAIN ANALYSIS FUNCTION
# ──────────────────────────────────────────────

def analyze_process(proc):
    """
    Analyzes a single process and returns a risk report.
    
    Risk scoring:
    +3  → Suspicious name (contains 'keylog', 'spy', etc.)
    +2  → Has log/text files open for writing
    +2  → Has active outbound network connections
    +1  → Shows CPU polling pattern (low, consistent)
    +1  → Running with no visible window (hidden)
    """
    report = {
        "pid":          proc.pid,
        "name":         "unknown",
        "risk_score":   0,
        "flags":        [],
        "open_logs":    [],
        "connections":  [],
        "verdict":      "CLEAN"
    }

    try:
        report["name"] = proc.name()

        if is_whitelisted(report["name"]):
            return None   # Skip known-safe processes

        # --- CHECK 1: Suspicious name ---
        has_bad_name, keyword = check_suspicious_name(report["name"])
        if has_bad_name:
            report["risk_score"] += 3
            report["flags"].append(f"Suspicious name keyword: '{keyword}'")

        # --- CHECK 2: Log files open ---
        log_files = check_open_files(proc)
        if log_files:
            report["risk_score"] += 2
            report["open_logs"] = log_files
            report["flags"].append(f"Has {len(log_files)} log/text file(s) open")

        # --- CHECK 3: Outbound network ---
        conns = check_network_connections(proc)
        if conns:
            report["risk_score"] += 2
            report["connections"] = conns
            report["flags"].append(f"Active outbound connection(s): {conns}")

        # --- CHECK 4: CPU polling pattern ---
        if check_cpu_pattern(proc):
            report["risk_score"] += 1
            report["flags"].append("CPU pattern resembles a polling loop")

        # --- CHECK 5: Hidden/background process ---
        if check_hidden_or_background(proc):
            report["risk_score"] += 1
            report["flags"].append("Running without a visible window")

        # --- VERDICT ---
        if report["risk_score"] >= RISK_THRESHOLD:
            report["verdict"] = "⚠️  SUSPICIOUS"
        elif report["risk_score"] > 0:
            report["verdict"] = "?  REVIEW"
        else:
            report["verdict"] = "✓  CLEAN"

    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

    return report


def print_report(results, scan_num):
    """Prints a nicely formatted scan report."""
    suspicious = [r for r in results if "SUSPICIOUS" in r["verdict"]]
    review     = [r for r in results if "REVIEW"    in r["verdict"]]
    clean      = [r for r in results if "CLEAN"     in r["verdict"]]

    print("\n" + "=" * 65)
    print(f"  BEHAVIORAL DETECTION SCAN #{scan_num}  —  {get_timestamp()}")
    print(f"  Processes scanned: {len(results)}   "
          f"Suspicious: {len(suspicious)}   "
          f"Review: {len(review)}   "
          f"Clean: {len(clean)}")
    print("=" * 65)

    if suspicious:
        print("\n🚨 SUSPICIOUS PROCESSES DETECTED:")
        print("-" * 65)
        for r in suspicious:
            print(f"  PID {r['pid']:>6}  |  {r['name']:<30}  |  Score: {r['risk_score']}")
            for flag in r["flags"]:
                print(f"             ↳ {flag}")
            if r["open_logs"]:
                for lf in r["open_logs"]:
                    print(f"             ↳ Log file: {lf}")
            if r["connections"]:
                for c in r["connections"]:
                    print(f"             ↳ Network:  {c}")
    else:
        print("\n✅ No suspicious processes found this scan.")

    if review:
        print("\n⚠️  PROCESSES TO REVIEW:")
        print("-" * 65)
        for r in review:
            print(f"  PID {r['pid']:>6}  |  {r['name']:<30}  |  Score: {r['risk_score']}")
            for flag in r["flags"]:
                print(f"             ↳ {flag}")

    print()


def save_report_to_file(results, scan_num, filepath="detection_report.txt"):
    """Appends the scan results to a text file."""
    with open(filepath, "a", encoding="utf-8") as f:
        suspicious = [r for r in results if "SUSPICIOUS" in r["verdict"]]
        f.write(f"\n{'='*65}\n")
        f.write(f"SCAN #{scan_num}  —  {get_timestamp()}\n")
        f.write(f"Total scanned: {len(results)} | Suspicious: {len(suspicious)}\n")
        for r in [r for r in results if r["risk_score"] > 0]:
            f.write(f"\n  [{r['verdict']}] PID {r['pid']} — {r['name']} (score={r['risk_score']})\n")
            for flag in r["flags"]:
                f.write(f"      • {flag}\n")
        f.write(f"{'='*65}\n")


# ──────────────────────────────────────────────
# MAIN LOOP
# ──────────────────────────────────────────────

def main():
    print("=" * 65)
    print("  BEHAVIORAL KEYLOGGER DETECTOR")
    print("  Educational use only — Lab project")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  Started: {get_timestamp()}")
    print("=" * 65)
    print(f"\n  Scanning every {SCAN_INTERVAL} seconds.")
    print("  Press CTRL+C to stop.\n")

    scan_num = 0

    try:
        while True:
            scan_num += 1
            results = []

            # Iterate over every running process
            for proc in psutil.process_iter(['pid', 'name']):
                report = analyze_process(proc)
                if report is not None:
                    results.append(report)

            print_report(results, scan_num)
            save_report_to_file(results, scan_num)

            time.sleep(SCAN_INTERVAL)

    except KeyboardInterrupt:
        print("\n\n[+] Detector stopped by user.")
        print(f"[+] Full report saved to: {os.path.abspath('detection_report.txt')}")


if __name__ == "__main__":
    main()
