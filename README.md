# 🔐 Keylogger & Behavioral Detection Lab

> Academic Lab Project | Ethical Hacking & Cybersecurity  
> Tested on Kali Linux inside VirtualBox  
> For educational purposes only

---

## 📌 Topic
Simple Keylogger and Behavioral Detection Script

---

## 📁 Files

| File | Purpose |
|---|---|
| `keylogger.py` | Records every keystroke to a log file |
| `detector.py` | Scans processes for suspicious behavior |
| `analyze_log.py` | Analyzes and reconstructs the keylog |
| `requirements.txt` | Required Python libraries |

---

## ⚙️ Installation
```bash
pip3 install pynput psutil --break-system-packages
```

---

## ▶️ How to Run

### Run the Keylogger
```bash
python3 keylogger.py
```
Type anything in another terminal — press **ESC** to stop.  
Output: `keylog.txt` is created automatically.

### Analyze the Log
```bash
python3 analyze_log.py
```

### Run the Behavioral Detector
Open a second terminal while keylogger is running:
```bash
python3 detector.py
```

---

## 🔍 How Behavioral Detection Works

Instead of signature-based detection, this script monitors **what a process does**:

| Suspicious Behavior | Risk Score |
|---|---|
| Name contains keylog/spy/hook | +3 |
| Has log/text files open | +2 |
| Active network connections | +2 |
| Low consistent CPU (polling) | +1 |
| No visible window | +1 |

Score ≥ 3 → flagged as **SUSPICIOUS**

---

## 📊 Lab Results

| Metric | Value |
|---|---|
| Total characters captured | 504 |
| Words reconstructed | 14 |
| Unique keys logged | 48 |
| Special keys captured | ✅ Yes |
| Behavioral detection | ✅ Flagged |

---

## 📚 References

- IJCRT 2024 — Real-Time Keylogger Detection Using Python
- arXiv 2025 — Towards Trustworthy Keylogger Detection
- ResearchGate — Survey of Keylogger Technologies

---

## ⚠️ Disclaimer

This project is strictly for **educational and academic purposes only**.  
Tested only on the developer's own machine inside a Virtual Machine.  
Using a keylogger on another person's device without consent is **illegal**.

---

*Built with Python 🐍 | Kali Linux 🐉 | Academic Use Only 📚*
