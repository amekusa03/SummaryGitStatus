"""
Internationalization (i18n) module for SummaryGitStatus.
Provides localized string mappings and language management for English and Japanese.
"""

import locale
import os
from typing import Dict, Any

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "ja": {
        # General & App Header
        "app_title": "SummaryGitStatus - Gitリポジトリステータス一覧",
        "header_title": "📁 Git リポジトリ ステータス一覧",
        "language_label": "言語 / Lang:",
        
        # Path Bar
        "parent_folder": "親フォルダ:",
        "browse_btn": "参照...",
        "search_depth": "探索階層:",
        "start_scan_btn": "🔍 スキャン開始",
        "select_folder_dialog": "探索する親フォルダを選択",
        
        # Summary Cards
        "card_total": "全リポジトリ",
        "card_clean": "クリーン",
        "card_modified": "変更あり / 要対応",
        "card_push_pull": "未Push / 未Pull",
        
        # Filter Bar
        "filter_label": "絞り込み:",
        "keyword_search": "キーワード検索:",
        "reset_btn": "リセット",
        "filter_all": "すべて",
        "filter_modified": "要対応/変更あり",
        "filter_clean": "クリーン",
        "filter_ahead": "未Push (Ahead)",
        "filter_behind": "未Pull (Behind)",
        "filter_conflict": "コンフリクト",
        
        # Table Columns
        "col_name": "リポジトリ名",
        "col_branch": "現在のブランチ",
        "col_status": "ステータス",
        "col_changes": "変更内容 (Stage/Unstage/Untrack)",
        "col_sync": "Push/Pull (Ahead/Behind)",
        "col_stash": "Stash",
        "col_last_date": "最終コミット日時",
        "col_last_msg": "最新コミットメッセージ",
        "col_path": "パス",
        
        # Table Item Contents
        "status_error": "❌ エラー",
        "status_clean": "✅ Clean",
        "status_clean_desc": "なし (変更ゼロ)",
        "status_modified": "⚠️ 変更あり",
        "tag_conflict": "競合",
        "tag_stage": "Stage",
        "tag_unstage": "Unstage",
        "tag_untrack": "Untrack",
        "sync_synced": "同期済み",
        "sync_ahead": "⬆ Ahead {n}",
        "sync_behind": "⬇ Behind {n}",
        
        # Status Bar & Notifications
        "status_ready": "準備完了。親フォルダを指定して「スキャン開始」を押してください。",
        "status_scanning_dir": "リポジトリ探索中: {dir} ...",
        "status_scanning_progress": "スキャン中 ({completed}/{total}): {name}",
        "status_scan_complete": "スキャン完了: 全 {total} 個のリポジトリを検出しました。",
        "status_refreshed_repo": "リポジトリ \"{name}\" のステータスを更新しました。",
        "status_copied": "クリップボードにコピーしました: {text}",
        
        # Bottom Export Buttons
        "btn_export_csv": "CSV出力",
        "btn_export_json": "JSON出力",
        
        # Context Menu
        "menu_open_folder": "📁 フォルダを開く ({name})",
        "menu_open_terminal": "💻 ターミナルで開く",
        "menu_open_vscode": "📝 VS Codeで開く",
        "menu_refresh_repo": "🔄 このリポジトリのみ状態再更新",
        "menu_copy_path": "📋 パスをコピー",
        
        # Dialogs
        "dialog_input_error": "入力エラー",
        "dialog_invalid_dir": "有効なフォルダパスを指定してください。",
        "dialog_info": "情報",
        "dialog_no_data": "出力するリポジトリデータがありません。",
        "dialog_success": "成功",
        "dialog_saved_csv": "CSVファイルを保存しました:\n{path}",
        "dialog_saved_json": "JSONファイルを保存しました:\n{path}",
        "file_type_csv": "CSVファイル",
        "file_type_json": "JSONファイル",
    },
    "en": {
        # General & App Header
        "app_title": "SummaryGitStatus - Git Repositories Status Viewer",
        "header_title": "📁 Git Repositories Status Overview",
        "language_label": "Language / 言語:",
        
        # Path Bar
        "parent_folder": "Parent Folder:",
        "browse_btn": "Browse...",
        "search_depth": "Depth:",
        "start_scan_btn": "🔍 Scan Repos",
        "select_folder_dialog": "Select parent folder to scan",
        
        # Summary Cards
        "card_total": "Total Repos",
        "card_clean": "Clean",
        "card_modified": "Modified / Attention",
        "card_push_pull": "Unpushed / Unpulled",
        
        # Filter Bar
        "filter_label": "Filter:",
        "keyword_search": "Search:",
        "reset_btn": "Reset",
        "filter_all": "All",
        "filter_modified": "Needs Attention / Modified",
        "filter_clean": "Clean",
        "filter_ahead": "Unpushed (Ahead)",
        "filter_behind": "Unpulled (Behind)",
        "filter_conflict": "Conflicts",
        
        # Table Columns
        "col_name": "Repository Name",
        "col_branch": "Current Branch",
        "col_status": "Status",
        "col_changes": "Changes (Stage/Unstage/Untrack)",
        "col_sync": "Push/Pull (Ahead/Behind)",
        "col_stash": "Stash",
        "col_last_date": "Last Commit Date",
        "col_last_msg": "Last Commit Message",
        "col_path": "Path",
        
        # Table Item Contents
        "status_error": "❌ Error",
        "status_clean": "✅ Clean",
        "status_clean_desc": "None (No changes)",
        "status_modified": "⚠️ Modified",
        "tag_conflict": "Conflict",
        "tag_stage": "Stage",
        "tag_unstage": "Unstage",
        "tag_untrack": "Untrack",
        "sync_synced": "Up-to-date",
        "sync_ahead": "⬆ Ahead {n}",
        "sync_behind": "⬇ Behind {n}",
        
        # Status Bar & Notifications
        "status_ready": "Ready. Specify a parent folder and click \"Scan Repos\".",
        "status_scanning_dir": "Scanning repositories in: {dir} ...",
        "status_scanning_progress": "Scanning ({completed}/{total}): {name}",
        "status_scan_complete": "Scan complete: Found {total} repositories.",
        "status_refreshed_repo": "Status updated for repository \"{name}\".",
        "status_copied": "Copied to clipboard: {text}",
        
        # Bottom Export Buttons
        "btn_export_csv": "Export CSV",
        "btn_export_json": "Export JSON",
        
        # Context Menu
        "menu_open_folder": "📁 Open Folder ({name})",
        "menu_open_terminal": "💻 Open in Terminal",
        "menu_open_vscode": "📝 Open in VS Code",
        "menu_refresh_repo": "🔄 Refresh Single Repo Status",
        "menu_copy_path": "📋 Copy Path",
        
        # Dialogs
        "dialog_input_error": "Input Error",
        "dialog_invalid_dir": "Please specify a valid directory path.",
        "dialog_info": "Info",
        "dialog_no_data": "No repository data to export.",
        "dialog_success": "Success",
        "dialog_saved_csv": "Saved CSV file successfully:\n{path}",
        "dialog_saved_json": "Saved JSON file successfully:\n{path}",
        "file_type_csv": "CSV File",
        "file_type_json": "JSON File",
    }
}

FILTER_KEYS = [
    ("filter_all", "all"),
    ("filter_modified", "modified"),
    ("filter_clean", "clean"),
    ("filter_ahead", "ahead"),
    ("filter_behind", "behind"),
    ("filter_conflict", "conflict")
]

COLUMN_KEYS = [
    ("name", "col_name", 160),
    ("branch", "col_branch", 130),
    ("status", "col_status", 110),
    ("changes", "col_changes", 190),
    ("sync", "col_sync", 140),
    ("stash", "col_stash", 60),
    ("last_date", "col_last_date", 120),
    ("last_msg", "col_last_msg", 200),
    ("path", "col_path", 250),
]

def get_default_language() -> str:
    """Detect default language from environment or system locale."""
    try:
        lang, _ = locale.getdefaultlocale()
        if lang and lang.startswith("ja"):
            return "ja"
    except Exception:
        pass
    
    for env in ("LC_ALL", "LC_MESSAGES", "LANG"):
        val = os.environ.get(env, "")
        if val.lower().startswith("ja"):
            return "ja"
    return "ja"

_current_language = get_default_language()

def set_language(lang: str):
    """Set current active language ('ja' or 'en')."""
    global _current_language
    if lang in TRANSLATIONS:
        _current_language = lang

def get_language() -> str:
    """Get current active language."""
    return _current_language

def t(key: str, **kwargs: Any) -> str:
    """Translate a key with optional formatting arguments."""
    lang_dict = TRANSLATIONS.get(_current_language, TRANSLATIONS["ja"])
    text = lang_dict.get(key, TRANSLATIONS["ja"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
