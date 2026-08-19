"""
SummaryGitStatus - Automatic Git Repository Status Viewer GUI Application
Entry point.
"""

import sys
import os
import tkinter as tk
from app_gui import SummaryGitStatus

def main():
    root = tk.Tk()
    
    # Try setting window icon if available or handle high DPI
    try:
        if sys.platform == "win32":
            root.tk.call('tk', 'scaling', 1.25)
    except Exception:
        pass

    app = SummaryGitStatus(root)
    root.mainloop()

if __name__ == "__main__":
    main()
