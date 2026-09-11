# 📁 SummaryGitStatus

[English](README.md) | [日本語](README.ja.md)

**SummaryGitStatus** is a lightweight, cross-platform Python GUI application that automatically discovers and inspects multiple Git repositories under a designated parent folder. It provides a real-time overview of current branch names, working tree changes (Staged / Unstaged / Untracked / Conflicts), push/pull synchronization states (Ahead / Behind), and latest commit details.

---

## 🌟 Key Features

- **⚡ Fast Multi-Threaded Scanning**
  - Recursively discovers `.git` repositories under a parent folder using parallel threads.
  - Configurable search depth (1 to 5 levels).
  - Fully asynchronous UI that remains smooth and responsive even with hundreds of repositories.

- **🌐 Bilingual Support (English & Japanese)**
  - Instantly toggle between English and Japanese via the language selector in the top-right corner.
  - Automatically defaults to system locale.

- **📊 Dashboard & Status Summary Cards**
  - Live summary counters: Total Repositories, Clean, Modified / Needs Attention, and Unpushed / Unpulled.
  - Color-coded status tags (Green: Clean, Yellow: Modified, Red: Conflict, Gray: Error).

- **🔍 Incremental Search & Filter**
  - Real-time search filtering across repository name, branch, path, and last commit message.
  - Quick filter presets: *All*, *Needs Attention / Modified*, *Clean*, *Unpushed (Ahead)*, *Unpulled (Behind)*, and *Conflicts*.
  - Sort table by clicking any column header (ascending / descending).

- **🖱️ Convenient Actions & Context Menu**
  - Double-click any row to open the folder in your system file manager.
  - Right-click context menu:
    - 📁 Open in File Manager
    - 💻 Open in Terminal
    - 📝 Open in VS Code
    - 🔄 Refresh Single Repo Status
    - 📋 Copy Path to Clipboard

- **💾 Data Export**
  - Export filtered results directly to **CSV** or **JSON** formats.

- **📦 Zero External Dependencies**
  - Built entirely with Python's standard library (`tkinter`, `ttk`, `subprocess`, `concurrent.futures`). No `pip install` required!

---

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- Git CLI installed and available in your `PATH`

### Run
Clone the repository and run `main.py`:

```bash
python3 main.py
```

---

## 📁 Project Structure

```
SummaryGitStatus/
├── main.py              # Application entry point
├── app_gui.py           # Tkinter/ttk GUI interface and logic
├── git_scanner.py       # Git repository discovery & status inspection module
├── i18n.py              # Internationalization (i18n) module (EN / JA)
├── utils.py             # External tool launchers & export utilities
├── README.md            # Documentation (English)
└── README.ja.md         # Documentation (Japanese)
```

---

## 📄 License

MIT License
