"""
Tkinter/ttk GUI interface for SummaryGitStatus application.
"""

import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Optional

from git_scanner import RepoStatus, scan_repositories_multithreaded, get_repo_status
import utils


class SummaryGitStatus:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Git status viewer - SummaryGitStatus")
        self.root.geometry("1100x700")
        self.root.minsize(900, 550)

        # Application state
        self.repo_list: List[RepoStatus] = []
        self.filtered_repos: List[RepoStatus] = []
        self.is_scanning = False
        self.scan_queue = queue.Queue()
        self.sort_column = "name"
        self.sort_reverse = False

        # Apply modern styling
        self._setup_styles()

        # Build UI layout
        self._build_ui()

        # Start queue polling
        self.root.after(100, self._poll_queue)

        # Auto-set default directory to current user home or working dir
        default_dir = os.path.expanduser("~")
        self.dir_entry.insert(0, default_dir)

    def _setup_styles(self):
        """Configure ttk styles with a clean dark theme palette."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Color palette
        BG_COLOR = "#1e1e2e"
        PANEL_BG = "#252538"
        CARD_BG = "#2e2e44"
        TEXT_FG = "#cdd6f4"
        TEXT_MUTED = "#a6adc8"
        ACCENT_BLUE = "#89b4fa"
        ACCENT_GREEN = "#a6e3a1"
        ACCENT_WARN = "#f9e2af"
        ACCENT_ERR = "#f38ba8"

        self.root.configure(bg=BG_COLOR)

        # Style definitions
        self.style.configure(".", background=BG_COLOR, foreground=TEXT_FG, font=("DejaVu Sans", 10))
        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("Panel.TFrame", background=PANEL_BG)
        self.style.configure("Card.TFrame", background=CARD_BG, relief="flat")
        
        self.style.configure("TLabel", background=BG_COLOR, foreground=TEXT_FG)
        self.style.configure("Panel.TLabel", background=PANEL_BG, foreground=TEXT_FG)
        self.style.configure("CardTitle.TLabel", background=CARD_BG, foreground=TEXT_MUTED, font=("DejaVu Sans", 9, "bold"))
        self.style.configure("CardVal.TLabel", background=CARD_BG, foreground=TEXT_FG, font=("DejaVu Sans", 16, "bold"))
        self.style.configure("Header.TLabel", background=BG_COLOR, foreground=ACCENT_BLUE, font=("DejaVu Sans", 14, "bold"))

        # Entry & Combobox
        self.style.configure("TEntry", fieldbackground="#313244", foreground=TEXT_FG, insertcolor=TEXT_FG)
        self.style.configure("TCombobox", fieldbackground="#313244", background="#313244", foreground=TEXT_FG, arrowcolor=TEXT_FG)
        self.style.map("TCombobox", fieldbackground=[("readonly", "#313244")], foreground=[("readonly", TEXT_FG)])

        # Buttons
        self.style.configure("TButton", background="#45475a", foreground=TEXT_FG, font=("DejaVu Sans", 9, "bold"), borderwidth=0, padding=6)
        self.style.map("TButton", background=[("active", "#585b70"), ("disabled", "#313244")], foreground=[("disabled", "#6c7086")])

        self.style.configure("Primary.TButton", background=ACCENT_BLUE, foreground="#11111b", font=("DejaVu Sans", 9, "bold"), borderwidth=0, padding=6)
        self.style.map("Primary.TButton", background=[("active", "#b4befe"), ("disabled", "#313244")])

        # Progressbar
        self.style.configure("TProgressbar", thickness=8, troughcolor="#313244", background=ACCENT_BLUE)

        # Treeview
        self.style.configure(
            "Treeview",
            background="#1e1e2e",
            foreground=TEXT_FG,
            fieldbackground="#1e1e2e",
            rowheight=28,
            font=("DejaVu Sans", 9)
        )
        self.style.configure(
            "Treeview.Heading",
            background="#252538",
            foreground=ACCENT_BLUE,
            font=("DejaVu Sans", 9, "bold"),
            padding=5
        )
        self.style.map(
            "Treeview",
            background=[("selected", "#45475a")],
            foreground=[("selected", "#ffffff")]
        )
        self.style.map("Treeview.Heading", background=[("active", "#313244")])

    def _build_ui(self):
        """Construct all UI components."""
        # Top Container
        top_container = ttk.Frame(self.root, padding=(16, 12, 16, 8))
        top_container.pack(fill="x")

        # Header Title
        title_label = ttk.Label(top_container, text=" Git リポジトリ ステータス一覧", style="Header.TLabel")
        title_label.pack(side="top", anchor="w", pady=(0, 10))

        # Path selection controls
        path_frame = ttk.Frame(top_container, style="Panel.TFrame", padding=10)
        path_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(path_frame, text="親フォルダ:", style="Panel.TLabel", font=("DejaVu Sans", 9, "bold")).pack(side="left", padx=(0, 8))

        self.dir_entry = ttk.Entry(path_frame, font=("DejaVu Sans", 10))
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.dir_entry.bind("<Return>", lambda e: self.start_scan())

        browse_btn = ttk.Button(path_frame, text="参照...", command=self._browse_directory)
        browse_btn.pack(side="left", padx=(0, 12))

        ttk.Label(path_frame, text="探索階層:", style="Panel.TLabel").pack(side="left", padx=(0, 4))
        self.depth_var = tk.StringVar(value="3")
        depth_combo = ttk.Combobox(path_frame, textvariable=self.depth_var, values=["1", "2", "3", "4", "5"], width=3, state="readonly")
        depth_combo.pack(side="left", padx=(0, 12))

        self.scan_btn = ttk.Button(path_frame, text="🔍 スキャン開始", style="Primary.TButton", command=self.start_scan)
        self.scan_btn.pack(side="left")

        # Summary Dashboard Cards
        dash_frame = ttk.Frame(top_container)
        dash_frame.pack(fill="x", pady=(0, 10))

        self.card_total_val = self._create_card(dash_frame, "全リポジトリ", "0", 0)
        self.card_clean_val = self._create_card(dash_frame, "クリーン", "0", 1, value_color="#a6e3a1")
        self.card_mod_val = self._create_card(dash_frame, "変更あり / 要対応", "0", 2, value_color="#f9e2af")
        self.card_push_val = self._create_card(dash_frame, "未Push / 未Pull", "0", 3, value_color="#89b4fa")

        # Filter & Search bar
        filter_frame = ttk.Frame(top_container, style="Panel.TFrame", padding=(10, 8))
        filter_frame.pack(fill="x")

        ttk.Label(filter_frame, text="絞り込み:", style="Panel.TLabel", font=("DejaVu Sans", 9, "bold")).pack(side="left", padx=(0, 8))
        
        self.filter_var = tk.StringVar(value="すべて")
        filter_combo = ttk.Combobox(
            filter_frame, 
            textvariable=self.filter_var, 
            values=["すべて", "要対応/変更あり", "クリーン", "未Push (Ahead)", "未Pull (Behind)", "コンフリクト"],
            width=16,
            state="readonly"
        )
        filter_combo.pack(side="left", padx=(0, 16))
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        ttk.Label(filter_frame, text="キーワード検索:", style="Panel.TLabel", font=("DejaVu Sans", 9, "bold")).pack(side="left", padx=(0, 8))
        
        self.search_entry = ttk.Entry(filter_frame, font=("DejaVu Sans", 9))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.search_entry.bind("<KeyRelease>", lambda e: self.apply_filter())

        reset_filter_btn = ttk.Button(filter_frame, text="リセット", command=self._reset_filters)
        reset_filter_btn.pack(side="left")

        # Treeview Table Container
        table_container = ttk.Frame(self.root, padding=(16, 0, 16, 8))
        table_container.pack(fill="both", expand=True)

        columns = (
            ("name", "リポジトリ名", 160),
            ("branch", "現在のブランチ", 130),
            ("status", "ステータス", 110),
            ("changes", "変更内容 (Stage/Unstage/Untrack)", 180),
            ("sync", "Push/Pull (Ahead/Behind)", 130),
            ("stash", "Stash", 60),
            ("last_date", "最終コミット日時", 110),
            ("last_msg", "最新コミットメッセージ", 200),
            ("path", "パス", 250),
        )

        self.tree = ttk.Treeview(table_container, columns=[c[0] for c in columns], show="headings", selectmode="browse")

        for col_id, col_name, width in columns:
            self.tree.heading(col_id, text=col_name, command=lambda c=col_id: self.sort_by_column(c))
            self.tree.column(col_id, width=width, anchor="w")

        # Scrollbars
        vsb = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        # Row Tags for custom colors
        self.tree.tag_configure("clean", foreground="#a6e3a1")
        self.tree.tag_configure("modified", foreground="#f9e2af")
        self.tree.tag_configure("conflict", foreground="#f38ba8")
        self.tree.tag_configure("error", foreground="#6c7086")

        # Bind events
        self.tree.bind("<Double-1>", self._on_tree_double_click)
        self.tree.bind("<Button-3>", self._show_context_menu)
        self.tree.bind("<Button-2>", self._show_context_menu)  # For macOS right click

        # Bottom Bar (Status & Export)
        bottom_frame = ttk.Frame(self.root, padding=(16, 4, 16, 12))
        bottom_frame.pack(fill="x")

        self.progress_bar = ttk.Progressbar(bottom_frame, mode="determinate")
        self.progress_bar.pack(fill="x", pady=(0, 4))

        status_bar = ttk.Frame(bottom_frame)
        status_bar.pack(fill="x")

        self.status_label = ttk.Label(status_bar, text="準備完了。親フォルダを指定して「スキャン開始」を押してください。", foreground="#a6adc8")
        self.status_label.pack(side="left")

        export_json_btn = ttk.Button(status_bar, text="JSON出力", command=self._export_json)
        export_json_btn.pack(side="right", padx=(4, 0))

        export_csv_btn = ttk.Button(status_bar, text="CSV出力", command=self._export_csv)
        export_csv_btn.pack(side="right")

    def _create_card(self, parent, title, initial_val, col, value_color="#cdd6f4") -> ttk.Label:
        """Create a dashboard summary card widget."""
        card = ttk.Frame(parent, style="Card.TFrame", padding=(12, 8))
        card.grid(row=0, column=col, sticky="nsew", padx=4)
        parent.grid_columnconfigure(col, weight=1)

        lbl_title = ttk.Label(card, text=title, style="CardTitle.TLabel")
        lbl_title.pack(anchor="w")

        lbl_val = ttk.Label(card, text=initial_val, style="CardVal.TLabel", foreground=value_color)
        lbl_val.pack(anchor="w", pady=(2, 0))
        return lbl_val

    def _browse_directory(self):
        """Open directory dialog."""
        initial = self.dir_entry.get() or os.path.expanduser("~")
        chosen = filedialog.askdirectory(initialdir=initial, title="探索する親フォルダを選択")
        if chosen:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, chosen)
            self.start_scan()

    def start_scan(self):
        """Start asynchronous multithreaded scanning."""
        target_dir = self.dir_entry.get().strip()
        if not target_dir or not os.path.exists(target_dir):
            messagebox.showwarning("入力エラー", "有効なフォルダパスを指定してください。")
            return

        if self.is_scanning:
            return

        self.is_scanning = True
        self.scan_btn.config(state="disabled")
        self.repo_list.clear()
        self.tree.delete(*self.tree.get_children())
        self.progress_bar["value"] = 0
        self._update_cards(0, 0, 0, 0)

        max_depth = int(self.depth_var.get())
        self.status_label.config(text=f"リポジトリ探索中: {target_dir} ...")

        # Launch scanning thread
        def worker():
            def progress_cb(completed, total, repo_status):
                self.scan_queue.put(("PROGRESS", completed, total, repo_status))

            results = scan_repositories_multithreaded(
                root_dir=target_dir,
                max_depth=max_depth,
                progress_callback=progress_cb
            )
            self.scan_queue.put(("DONE", results))

        threading.Thread(target=worker, daemon=True).start()

    def _poll_queue(self):
        """Poll scan_queue for thread messages."""
        try:
            while True:
                msg = self.scan_queue.get_nowait()
                msg_type = msg[0]

                if msg_type == "PROGRESS":
                    _, completed, total, repo_status = msg
                    self.repo_list.append(repo_status)
                    pct = (completed / total) * 100 if total > 0 else 100
                    self.progress_bar["value"] = pct
                    self.status_label.config(text=f"スキャン中 ({completed}/{total}): {repo_status.name}")
                    self.apply_filter()

                elif msg_type == "DONE":
                    results = msg[1]
                    self.repo_list = results
                    self.is_scanning = False
                    self.scan_btn.config(state="normal")
                    self.progress_bar["value"] = 100
                    self.status_label.config(text=f"スキャン完了: 全 {len(self.repo_list)} 個のリポジトリを検出しました。")
                    self.apply_filter()

        except queue.Empty:
            pass

        self.root.after(100, self._poll_queue)

    def apply_filter(self):
        """Filter and update the table display."""
        search_kw = self.search_entry.get().strip().lower()
        filter_opt = self.filter_var.get()

        self.filtered_repos = []
        clean_cnt = 0
        mod_cnt = 0
        push_pull_cnt = 0

        for r in self.repo_list:
            if r.is_clean:
                clean_cnt += 1
            else:
                mod_cnt += 1

            if r.ahead > 0 or r.behind > 0:
                push_pull_cnt += 1

            # Match search keyword
            if search_kw:
                kw_match = (
                    search_kw in r.name.lower() or
                    search_kw in r.branch.lower() or
                    search_kw in r.path.lower() or
                    search_kw in r.last_commit_msg.lower()
                )
                if not kw_match:
                    continue

            # Match dropdown filter
            if filter_opt == "要対応/変更あり" and r.is_clean:
                continue
            elif filter_opt == "クリーン" and not r.is_clean:
                continue
            elif filter_opt == "未Push (Ahead)" and r.ahead == 0:
                continue
            elif filter_opt == "未Pull (Behind)" and r.behind == 0:
                continue
            elif filter_opt == "コンフリクト" and r.conflicts == 0:
                continue

            self.filtered_repos.append(r)

        self._update_cards(len(self.repo_list), clean_cnt, mod_cnt, push_pull_cnt)
        self._refresh_tree_display()

    def _update_cards(self, total: int, clean: int, mod: int, push_pull: int):
        """Update dashboard summary numbers."""
        self.card_total_val.config(text=str(total))
        self.card_clean_val.config(text=str(clean))
        self.card_mod_val.config(text=str(mod))
        self.card_push_val.config(text=str(push_pull))

    def _reset_filters(self):
        """Reset search entry and filter dropdown."""
        self.search_entry.delete(0, tk.END)
        self.filter_var.set("すべて")
        self.apply_filter()

    def _refresh_tree_display(self):
        """Populate treeview rows based on current filtered_repos."""
        self.tree.delete(*self.tree.get_children())

        for r in self.filtered_repos:
            if r.error:
                status_str = "❌ エラー"
                changes_str = r.error
                sync_str = "-"
                tag = "error"
            elif r.is_clean:
                status_str = "✅ Clean"
                changes_str = "なし (変更ゼロ)"
                tag = "clean"
            else:
                status_parts = []
                if r.conflicts > 0: status_parts.append(f"競合:{r.conflicts}")
                if r.staged > 0: status_parts.append(f"Stage:{r.staged}")
                if r.unstaged > 0: status_parts.append(f"Unstage:{r.unstaged}")
                if r.untracked > 0: status_parts.append(f"Untrack:{r.untracked}")
                
                status_str = "⚠️ 変更あり"
                changes_str = " / ".join(status_parts)
                tag = "conflict" if r.conflicts > 0 else "modified"

            sync_parts = []
            if r.ahead > 0: sync_parts.append(f"⬆ Ahead {r.ahead}")
            if r.behind > 0: sync_parts.append(f"⬇ Behind {r.behind}")
            sync_str = " / ".join(sync_parts) if sync_parts else "同期済み"

            item_values = (
                r.name,
                r.branch,
                status_str,
                changes_str,
                sync_str,
                str(r.stash_count) if r.stash_count > 0 else "-",
                r.last_commit_date or "-",
                r.last_commit_msg or "-",
                r.path
            )
            self.tree.insert("", "end", values=item_values, tags=(tag,))

    def sort_by_column(self, col: str):
        """Sort table by clicked column header."""
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        def sort_key(r: RepoStatus):
            val = getattr(r, col, "")
            if val is None:
                return ""
            return val

        self.filtered_repos.sort(key=sort_key, reverse=self.sort_reverse)
        self._refresh_tree_display()

    def _get_selected_repo(self) -> Optional[RepoStatus]:
        """Return selected RepoStatus object in treeview."""
        selected = self.tree.selection()
        if not selected:
            return None
        item_vals = self.tree.item(selected[0], "values")
        if not item_vals:
            return None
        repo_path = item_vals[8]  # Path column
        for r in self.repo_list:
            if r.path == repo_path:
                return r
        return None

    def _on_tree_double_click(self, event):
        """Double click opens repository folder."""
        repo = self._get_selected_repo()
        if repo:
            utils.open_in_file_manager(repo.path)

    def _show_context_menu(self, event):
        """Show context menu for selected item."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            repo = self._get_selected_repo()
            if not repo:
                return

            menu = tk.Menu(self.root, tearoff=0, bg="#252538", fg="#cdd6f4", activebackground="#45475a", activeforeground="#ffffff")
            menu.add_command(label=f"📁 フォルダを開く ({repo.name})", command=lambda: utils.open_in_file_manager(repo.path))
            menu.add_command(label="💻 ターミナルで開く", command=lambda: utils.open_in_terminal(repo.path))
            menu.add_command(label="📝 VS Codeで開く", command=lambda: utils.open_in_vscode(repo.path))
            menu.add_separator()
            menu.add_command(label="🔄 このリポジトリのみ状態再更新", command=lambda: self._refresh_single_repo(repo))
            menu.add_command(label="📋 パスをコピー", command=lambda: self._copy_to_clipboard(repo.path))
            menu.tk_popup(event.x_root, event.y_root)

    def _refresh_single_repo(self, repo: RepoStatus):
        """Refresh single repository status."""
        new_status = get_repo_status(repo.path)
        for i, r in enumerate(self.repo_list):
            if r.path == repo.path:
                self.repo_list[i] = new_status
                break
        self.apply_filter()
        self.status_label.config(text=f"リポジトリ '{repo.name}' のステータスを更新しました。")

    def _copy_to_clipboard(self, text: str):
        """Copy text to system clipboard."""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_label.config(text=f"クリップボードにコピーしました: {text}")

    def _export_csv(self):
        """Export list to CSV file dialog."""
        if not self.filtered_repos:
            messagebox.showinfo("情報", "出力するリポジトリデータがありません。")
            return
        fpath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV File", "*.csv")])
        if fpath:
            utils.export_to_csv(self.filtered_repos, fpath)
            messagebox.showinfo("成功", f"CSVファイルを保存しました:\n{fpath}")

    def _export_json(self):
        """Export list to JSON file dialog."""
        if not self.filtered_repos:
            messagebox.showinfo("情報", "出力するリポジトリデータがありません。")
            return
        fpath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON File", "*.json")])
        if fpath:
            utils.export_to_json(self.filtered_repos, fpath)
            messagebox.showinfo("成功", f"JSONファイルを保存しました:\n{fpath}")
