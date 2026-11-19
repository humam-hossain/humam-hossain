#!/usr/bin/env python3
"""
scripts/configure_profile.py
Interactive Terminal TUI Setup Wizard for Muhammed Humam Hossain (@humam-hossain).
Provides full hjkl / Vim-style keyboard navigation, live search, and lists public
GitHub repositories ordered by latest committed repo (pushed_at descending).
Saves preferences to profile_config.json and builds dark_mode.svg & light_mode.svg.
Standard library only (zero external dependencies).
"""

from __future__ import annotations

import datetime
import html
import json
import os
from pathlib import Path
import re
import select
import shutil
import subprocess
import sys
import termios
import tty
import urllib.error
import urllib.request

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "profile_config.json"
BUILD_SCRIPT = ROOT_DIR / "scripts" / "build_profile.py"

# ANSI 24-bit TrueColor Palettes
CYAN = "\033[38;2;88;166;255m"
GREEN = "\033[38;2;63;185;80m"
AMBER = "\033[38;2;255;166;87m"
RED = "\033[38;2;248;81;73m"
MUTED = "\033[38;2;139;148;158m"
WHITE = "\033[38;2;255;255;255m"
BG_ACTIVE = "\033[48;2;22;27;34m"
BG_HIGHLIGHT = "\033[48;2;30;42;56m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def strip_ansi(text: str) -> str:
    """Removes ANSI escape codes to measure true visible string width."""
    return re.sub(r"\033\[[0-9;]*[a-zA-Z]", "", text)


def pad_line(text: str, cols: int) -> str:
    """Pads text with spaces to match column width without wrapping."""
    vis_len = len(strip_ansi(text))
    if vis_len < cols:
        return text + " " * (cols - vis_len)
    elif vis_len > cols:
        # Simple visible clamp
        raw_chars = []
        cur_vis = 0
        in_esc = False
        for ch in text:
            if ch == "\033":
                in_esc = True
                raw_chars.append(ch)
            elif in_esc:
                raw_chars.append(ch)
                if ch.isalpha():
                    in_esc = False
            else:
                if cur_vis < cols - 1:
                    raw_chars.append(ch)
                    cur_vis += 1
                else:
                    raw_chars.append("…")
                    break
        raw_chars.append(RESET)
        return "".join(raw_chars)
    return text


class TerminalUI:
    """Context manager for raw terminal cbreak mode with alternate screen buffer."""

    def __init__(self) -> None:
        self.is_tty = sys.stdin.isatty() and sys.stdout.isatty()
        self.fd = sys.stdin.fileno() if self.is_tty else None
        self.old_settings = None

    def __enter__(self) -> TerminalUI:
        if self.is_tty and self.fd is not None:
            self.old_settings = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)
            # Switch to alternate screen, hide cursor
            sys.stdout.write("\033[?1049h\033[?25l")
            sys.stdout.flush()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.is_tty and self.fd is not None and self.old_settings is not None:
            # Restore normal screen and visible cursor
            sys.stdout.write("\033[?25h\033[?1049l")
            sys.stdout.flush()
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)


def read_key(fd: int) -> str:
    """Reads a single keypress or escape sequence from stdin."""
    b = os.read(fd, 1)
    if not b:
        return ""
    ch = b.decode("utf-8", errors="ignore")
    if ch == "\x1b":
        # Check if more characters are waiting (ANSI escape sequence)
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            seq = os.read(fd, 16).decode("utf-8", errors="ignore")
            if seq == "[A":
                return "UP"
            elif seq == "[B":
                return "DOWN"
            elif seq == "[C":
                return "RIGHT"
            elif seq == "[D":
                return "LEFT"
            elif seq.startswith("[3"):
                return "DELETE"
            elif seq.startswith("[5") or seq.startswith("[I"):
                return "PAGE_UP"
            elif seq.startswith("[6") or seq.startswith("[G"):
                return "PAGE_DOWN"
            elif seq.startswith("[H") or seq.startswith("[1"):
                return "HOME"
            elif seq.startswith("[F") or seq.startswith("[4"):
                return "END"
            return "ESC"
        return "ESC"
    elif ch in ("\r", "\n"):
        return "ENTER"
    elif ch == " ":
        return "SPACE"
    elif ch in ("\x7f", "\x08"):
        return "BACKSPACE"
    elif ch == "\x03":
        return "CTRL_C"
    elif ch == "\t":
        return "TAB"
    return ch


def prompt_line_editor(tui: TerminalUI, title: str, prompt_label: str, initial_text: str = "") -> str:
    """
    Interactive line editor with visible hardware & software cursor, horizontal
    scrolling, space insertion, backspace, delete, and readline keybindings.
    """
    if not tui.is_tty or tui.fd is None:
        try:
            val = input(f"{prompt_label} [{initial_text}]: ").strip()
            return val if val else initial_text
        except Exception:
            return initial_text

    buf = list(initial_text)
    pos = len(buf)

    try:
        while True:
            cols, rows = shutil.get_terminal_size((80, 24))
            prefix_str = "  ❯ "
            prefix_len = 4
            avail_width = max(10, cols - prefix_len - 2)

            # Horizontal scroll viewport
            view_start = 0
            if pos >= avail_width:
                view_start = pos - avail_width + 1
            visible_buf = buf[view_start : view_start + avail_width]
            rel_pos = pos - view_start

            # Prominent visual cursor block (reverse video)
            before_chars = "".join(visible_buf[:rel_pos])
            if rel_pos < len(visible_buf):
                cur_char = visible_buf[rel_pos]
                after_chars = "".join(visible_buf[rel_pos + 1:])
                cursor_char_rendered = f"\033[7m{cur_char}\033[0m"
                edit_display = f"{before_chars}{cursor_char_rendered}{after_chars}"
            else:
                cursor_char_rendered = "\033[7m \033[0m"
                edit_display = f"{before_chars}{cursor_char_rendered}"

            lines = [
                f"{AMBER}{BOLD}=== {title} ==={RESET}",
                f"{MUTED}Edit text below. Press [Enter] to submit, [Esc] to cancel/keep original.{RESET}",
                "",
                f"{CYAN}{BOLD}{prompt_label}:{RESET}",
                f"{prefix_str}{BOLD}{edit_display}{RESET}",
                "",
                f"{MUTED}[Enter]: Submit  |  [Esc]: Keep '{initial_text}'  |  [Ctrl+U]: Clear  |  [Ctrl+W]: Del Word{RESET}",
            ]

            frame_lines = [pad_line(line, cols) for line in lines]
            # Pad remaining screen lines to avoid debris
            while len(frame_lines) < rows:
                frame_lines.append(" " * cols)

            # Draw frame, then make hardware cursor visible and place it at (row 5, col prefix_len + 1 + rel_pos)
            cursor_row = 5
            cursor_col = prefix_len + 1 + rel_pos
            frame = "\033[H" + "\n".join(frame_lines) + f"\033[?25h\033[{cursor_row};{cursor_col}H"
            sys.stdout.write(frame)
            sys.stdout.flush()

            key = read_key(tui.fd)
            if key == "ENTER":
                break
            elif key in ("ESC", "CTRL_C"):
                return initial_text
            elif key in ("SPACE", " "):
                buf.insert(pos, " ")
                pos += 1
            elif key == "BACKSPACE":
                if pos > 0:
                    buf.pop(pos - 1)
                    pos -= 1
            elif key == "DELETE":
                if pos < len(buf):
                    buf.pop(pos)
            elif key == "LEFT":
                if pos > 0:
                    pos -= 1
            elif key == "RIGHT":
                if pos < len(buf):
                    pos += 1
            elif key in ("HOME", "\x01"):  # Home or Ctrl+A
                pos = 0
            elif key in ("END", "\x05"):   # End or Ctrl+E
                pos = len(buf)
            elif key == "\x15":            # Ctrl+U (clear line)
                buf = []
                pos = 0
            elif key == "\x0b":            # Ctrl+K (kill line to end)
                buf = buf[:pos]
            elif key == "\x17":            # Ctrl+W (delete previous word)
                while pos > 0 and buf[pos - 1] == " ":
                    buf.pop(pos - 1)
                    pos -= 1
                while pos > 0 and buf[pos - 1] != " ":
                    buf.pop(pos - 1)
                    pos -= 1
            elif len(key) == 1 and 32 <= ord(key) <= 126:
                buf.insert(pos, key)
                pos += 1
    finally:
        # Hide hardware cursor again for clean list navigation
        if tui.is_tty:
            sys.stdout.write("\033[?25l")
            sys.stdout.flush()

    result = "".join(buf).strip()
    return result if result else initial_text


def fetch_user_repos(username: str) -> list[dict]:
    """
    Fetches all public repositories for username ordered by latest commit / push.
    Queries GitHub API with sort=pushed&direction=desc.
    """
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or os.environ.get("PROFILE_TOKEN")
    headers = {"User-Agent": "neofetch-profile-wizard"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    all_repos = []
    page = 1
    while page <= 3:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}&sort=pushed&direction=desc"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if not data or not isinstance(data, list):
                    break
                for r in data:
                    all_repos.append({
                        "name": r.get("name", ""),
                        "description": r.get("description") or "",
                        "stars": r.get("stargazers_count", 0),
                        "language": r.get("language") or "Code",
                        "pushed_at": r.get("pushed_at") or "",
                        "fork": r.get("fork", False),
                    })
                if len(data) < 100:
                    break
                page += 1
        except Exception:
            break

    # Guarantee strict ordering by latest push date descending
    all_repos.sort(key=lambda x: x.get("pushed_at") or "", reverse=True)
    return all_repos


def prepare_repos_list(fetched_repos: list[dict], current_featured: list[dict]) -> tuple[list[dict], list[str]]:
    """
    Ensures repositories from the last configuration change come up first,
    preserving their custom descriptions and selected state, followed by
    the remaining repositories ordered by latest commit (pushed_at descending).
    """
    repo_map = {r["name"]: dict(r) for r in fetched_repos}

    ordered_repos = []
    selected_names = []
    seen = set()

    # 1. Place all projects from the user's last change at the top in their saved order
    for p in current_featured:
        name = p.get("repo")
        if not name or name in seen:
            continue
        seen.add(name)
        selected_names.append(name)

        # Merge live repo metadata if available, but preserve custom description
        if name in repo_map:
            repo_entry = dict(repo_map[name])
            if p.get("description"):
                repo_entry["description"] = p["description"]
            ordered_repos.append(repo_entry)
        else:
            ordered_repos.append({
                "name": name,
                "description": p.get("description") or "Unix software & tools",
                "stars": 0,
                "language": "Code",
                "pushed_at": "",
                "fork": False,
            })

    # 2. Append all remaining repositories ordered by latest push date
    for r in fetched_repos:
        if r["name"] not in seen:
            seen.add(r["name"])
            ordered_repos.append(dict(r))

    # Fallback default selection if nothing was previously configured
    if not selected_names and ordered_repos:
        selected_names = [r["name"] for r in ordered_repos[:4]]

    return ordered_repos, selected_names


# ==============================================================================
# Step 1: Featured Projects Multi-Select (hjkl navigation, Space toggle, / search)
# ==============================================================================

def select_projects_tui(tui: TerminalUI, repos: list[dict], current_selected_names: list[str]) -> list[dict]:
    """
    Interactive TUI menu for repository selection with hjkl vim controls.
    List is ordered strictly by latest committed repo (pushed_at descending).
    """
    if not tui.is_tty or tui.fd is None or not repos:
        # Fallback for non-interactive
        return repos[:4]

    selected_set = set(current_selected_names)
    cursor = 0
    scroll_offset = 0
    search_query = ""
    search_mode = False

    while True:
        cols, rows = shutil.get_terminal_size((80, 24))

        # Filter items if search query is set
        if search_query:
            filtered_indices = [
                idx for idx, r in enumerate(repos)
                if search_query.lower() in r["name"].lower() or search_query.lower() in r["description"].lower()
            ]
        else:
            filtered_indices = list(range(len(repos)))

        if cursor >= len(filtered_indices):
            cursor = max(0, len(filtered_indices) - 1)

        # Header area: 5 lines, footer: 3 lines
        viewport_height = max(5, rows - 9)
        if cursor < scroll_offset:
            scroll_offset = cursor
        elif cursor >= scroll_offset + viewport_height:
            scroll_offset = cursor - viewport_height + 1

        lines = []
        # Title Banner
        lines.append(f"{AMBER}{BOLD}=== [Step 1/5] Select Featured Projects (hjkl to navigate) ==={RESET}")
        lines.append(f"{MUTED}Repositories ordered by latest commit. Toggle with [Space], search with [/], finish with [Enter].{RESET}")

        # Status Line
        search_status = f"{CYAN}Search: [{search_query}\033[7m \033[0m]{RESET} " if search_mode else (f"{MUTED}Filter: '{search_query}' (press / to edit){RESET} " if search_query else f"{MUTED}Filter: [press /]{RESET} ")
        sel_count_color = GREEN if 1 <= len(selected_set) <= 5 else (RED if len(selected_set) > 5 else AMBER)
        lines.append(f"Selected: {sel_count_color}{BOLD}{len(selected_set)}/5 projects{RESET}  |  Total: {len(repos)} repos  |  {search_status}")
        lines.append(f"{MUTED}{'─' * (cols - 2)}{RESET}")

        # List Area
        visible_indices = filtered_indices[scroll_offset : scroll_offset + viewport_height]
        for v_idx, orig_idx in enumerate(visible_indices):
            actual_pos = scroll_offset + v_idx
            repo = repos[orig_idx]
            name = repo["name"]
            is_selected = name in selected_set
            check_box = f"{GREEN}[x]{RESET}" if is_selected else f"{MUTED}[ ]{RESET}"

            # Format push date
            pushed_raw = repo.get("pushed_at", "")
            pushed_str = pushed_raw[:10] if pushed_raw else "    -     "

            lang = repo.get("language") or "Code"
            desc = repo.get("description") or ""

            # Truncate desc for neat layout
            max_desc_len = max(10, cols - 56)
            if len(desc) > max_desc_len:
                desc = desc[:max_desc_len - 1] + "…"

            is_active = (actual_pos == cursor)
            if is_active:
                arrow = f"{CYAN}{BOLD}❯{RESET}"
                line_str = f"{arrow} {check_box} {BOLD}{CYAN}{name:<22}{RESET} {MUTED}{pushed_str}{RESET} {AMBER}{lang:<10}{RESET} {desc}"
            else:
                arrow = " "
                line_str = f"{arrow} {check_box} {BOLD}{name:<22}{RESET} {MUTED}{pushed_str}{RESET} {MUTED}{lang:<10}{RESET} {MUTED}{desc}{RESET}"

            lines.append(line_str)

        # Fill viewport gap if filtered list is short
        for _ in range(viewport_height - len(visible_indices)):
            lines.append("")

        # Footer Help Bar
        lines.append(f"{MUTED}{'─' * (cols - 2)}{RESET}")
        if search_mode:
            lines.append(f"{CYAN}{BOLD}[Search Mode]{RESET} Type to filter, [Enter] or [Esc] to return to hjkl navigation.")
        else:
            lines.append(f"{BOLD}[j/k or ↓/↑]{RESET} Nav  {BOLD}[Space]{RESET} Toggle  {BOLD}[h/l]{RESET} PgUp/PgDn  {BOLD}[/]{RESET} Search  {BOLD}[Enter]{RESET} Confirm  {BOLD}[q]{RESET} Quit")

        # Render zero-flicker frame
        frame_lines = [pad_line(line, cols) for line in lines]
        while len(frame_lines) < rows:
            frame_lines.append(" " * cols)
        frame = "\033[H" + "\n".join(frame_lines)
        sys.stdout.write(frame)
        sys.stdout.flush()

        key = read_key(tui.fd)

        if search_mode:
            if key in ("ENTER", "ESC"):
                search_mode = False
            elif key in ("SPACE", " "):
                search_query += " "
                cursor = 0
            elif key == "BACKSPACE":
                if search_query:
                    search_query = search_query[:-1]
                    cursor = 0
            elif key == "CTRL_C":
                search_mode = False
                search_query = ""
            elif len(key) == 1 and 32 <= ord(key) <= 126:
                search_query += key
                cursor = 0
            continue

        # Normal hjkl navigation mode
        if key in ("j", "DOWN"):
            if cursor < len(filtered_indices) - 1:
                cursor += 1
        elif key in ("k", "UP"):
            if cursor > 0:
                cursor -= 1
        elif key in ("h", "LEFT", "PAGE_UP"):
            cursor = max(0, cursor - viewport_height)
        elif key in ("l", "RIGHT", "PAGE_DOWN"):
            cursor = min(len(filtered_indices) - 1, cursor + viewport_height)
        elif key in ("g", "HOME"):
            cursor = 0
        elif key in ("G", "END"):
            cursor = max(0, len(filtered_indices) - 1)
        elif key in ("SPACE", " "):
            if filtered_indices and 0 <= cursor < len(filtered_indices):
                repo_name = repos[filtered_indices[cursor]]["name"]
                if repo_name in selected_set:
                    selected_set.remove(repo_name)
                else:
                    selected_set.add(repo_name)
        elif key == "/":
            search_mode = True
        elif key == "ENTER":
            if not selected_set:
                # If nothing selected, select current cursor item
                if filtered_indices and 0 <= cursor < len(filtered_indices):
                    selected_set.add(repos[filtered_indices[cursor]]["name"])
            break
        elif key in ("q", "CTRL_C"):
            # Exit confirmation or abort
            break

    # Build chosen list preserving sort by latest pushed_at
    chosen_repos = [r for r in repos if r["name"] in selected_set]
    return chosen_repos[:5]


# ==============================================================================
# Step 1b: Edit Project Descriptions
# ==============================================================================

def edit_project_descriptions_tui(tui: TerminalUI, chosen_repos: list[dict], current_projects: list[dict]) -> list[dict]:
    """Allows user to inspect and edit one-line descriptions for selected projects."""
    if not tui.is_tty or tui.fd is None:
        return [
            {"repo": r["name"], "description": r.get("description") or "Unix software & tools"}
            for r in chosen_repos
        ]

    # Map existing descriptions
    desc_map = {}
    for p in current_projects:
        desc_map[p.get("repo", "")] = p.get("description", "")

    projects_data = []
    for r in chosen_repos:
        name = r["name"]
        def_desc = desc_map.get(name) or r.get("description") or "Unix software & tools"
        projects_data.append({"repo": name, "description": def_desc})

    cursor = 0
    # Items: [projects...] + [Done & Continue]
    while True:
        cols, rows = shutil.get_terminal_size((80, 24))
        total_items = len(projects_data) + 1  # +1 for continue button

        lines = [
            f"{AMBER}{BOLD}=== [Step 1b] Confirm Project Descriptions ==={RESET}",
            f"{MUTED}Select a project and press [Enter] to customize its description. Press [c] to continue.{RESET}",
            f"{MUTED}{'─' * (cols - 2)}{RESET}",
        ]

        for idx, p in enumerate(projects_data):
            is_active = (cursor == idx)
            arrow = f"{CYAN}{BOLD}❯{RESET}" if is_active else " "
            hdr = f"{BOLD}{CYAN if is_active else WHITE}[{idx + 1}] {p['repo']}{RESET}"
            lines.append(f"{arrow} {hdr}")
            lines.append(f"    {MUTED}Description:{RESET} {p['description']}")
            lines.append("")

        # Continue button
        is_cont_active = (cursor == len(projects_data))
        cont_arrow = f"{GREEN}{BOLD}❯{RESET}" if is_cont_active else " "
        cont_btn = f"{GREEN}{BOLD}[ Finish Projects & Continue -> ]{RESET}" if is_cont_active else f"{MUTED}[ Finish Projects & Continue -> ]{RESET}"
        lines.append(f"{cont_arrow} {cont_btn}")
        lines.append("")
        lines.append(f"{MUTED}{'─' * (cols - 2)}{RESET}")
        lines.append(f"{BOLD}[j/k or ↓/↑]{RESET} Nav  {BOLD}[J/K]{RESET} Reorder  {BOLD}[Enter]{RESET} Edit  {BOLD}[c]{RESET} Continue")

        frame_lines = [pad_line(line, cols) for line in lines]
        while len(frame_lines) < rows:
            frame_lines.append(" " * cols)
        frame = "\033[H" + "\n".join(frame_lines)
        sys.stdout.write(frame)
        sys.stdout.flush()

        key = read_key(tui.fd)
        if key in ("j", "DOWN"):
            cursor = min(total_items - 1, cursor + 1)
        elif key in ("k", "UP"):
            cursor = max(0, cursor - 1)
        elif key in ("K", "U"):
            if 0 < cursor < len(projects_data):
                projects_data[cursor], projects_data[cursor - 1] = projects_data[cursor - 1], projects_data[cursor]
                cursor -= 1
        elif key in ("J", "D"):
            if 0 <= cursor < len(projects_data) - 1:
                projects_data[cursor], projects_data[cursor + 1] = projects_data[cursor + 1], projects_data[cursor]
                cursor += 1
        elif key in ("c", "C"):
            break
        elif key == "ENTER":
            if cursor == len(projects_data):
                break
            else:
                p = projects_data[cursor]
                new_desc = prompt_line_editor(
                    tui,
                    f"Edit Description for '{p['repo']}'",
                    "One-line description",
                    initial_text=p["description"]
                )
                p["description"] = new_desc

    return projects_data


# ==============================================================================
# Step 2: Technical Skills Categories (hjkl navigation, edit, add, delete)
# ==============================================================================

def parse_skills_items(items_str: str) -> list[str]:
    """Splits comma-separated items into a list of clean strings."""
    if not items_str:
        return []
    return [item.strip() for item in items_str.split(",") if item.strip()]


def format_skills_items(items_list: list[str]) -> str:
    """Combines a list of skill items into a clean comma-separated string."""
    return ", ".join(items_list)


def manage_category_skills_tui(tui: TerminalUI, skill_entry: dict) -> tuple[dict | None, bool]:
    """
    Sub-menu for a single skill category.
    Allows:
    - Deleting individual skills (d / x / Delete / Backspace)
    - Adding new skills to this category
    - Editing / renaming individual skills
    - Renaming the category
    - Deleting the entire category
    Returns: (updated_skill_dict, was_category_deleted)
    """
    if not tui.is_tty or tui.fd is None:
        return skill_entry, False

    cat_name = skill_entry.get("category", "Skills")
    skills_list = parse_skills_items(skill_entry.get("items", ""))

    cursor = 0
    status_msg = ""

    while True:
        cols, rows = shutil.get_terminal_size((80, 24))

        btn_add_skill_idx = len(skills_list)
        btn_rename_cat_idx = len(skills_list) + 1
        btn_del_cat_idx = len(skills_list) + 2
        btn_done_idx = len(skills_list) + 3
        total_items = len(skills_list) + 4

        if cursor >= total_items:
            cursor = max(0, total_items - 1)

        lines = [
            f"{AMBER}{BOLD}=== Manage Category: {CYAN}{cat_name}{AMBER} ==={RESET}",
            f"{MUTED}Select a skill to delete or edit. Use [d/x/Del] to delete a skill, [Enter] to choose action.{RESET}",
            f"{MUTED}{'─' * (cols - 2)}{RESET}",
        ]

        if not skills_list:
            lines.append(f"  {MUTED}(No skills in this category yet. Select [+ Add Skill] below){RESET}")
        else:
            lines.append(f"{BOLD}Skills in '{cat_name}' ({len(skills_list)} items):{RESET}")
            for idx, item in enumerate(skills_list):
                is_active = (cursor == idx)
                arrow = f"{CYAN}{BOLD}❯{RESET}" if is_active else " "
                tag = f"  {RED}[d/x to delete]{RESET}" if is_active else ""
                item_txt = f"{BOLD}{CYAN if is_active else WHITE}{item}{RESET}"
                lines.append(f"{arrow} • {item_txt}{tag}")

        lines.append("")
        # Add Skill Button
        is_add_act = (cursor == btn_add_skill_idx)
        add_arrow = f"{AMBER}{BOLD}❯{RESET}" if is_add_act else " "
        add_btn = f"{AMBER}{BOLD}[ + Add Skill to {cat_name} ]{RESET}" if is_add_act else f"{MUTED}[ + Add Skill to {cat_name} ]{RESET}"
        lines.append(f"{add_arrow} {add_btn}")

        # Rename Category Button
        is_ren_act = (cursor == btn_rename_cat_idx)
        ren_arrow = f"{CYAN}{BOLD}❯{RESET}" if is_ren_act else " "
        ren_btn = f"{CYAN}{BOLD}[ ✎ Rename Category '{cat_name}' ]{RESET}" if is_ren_act else f"{MUTED}[ ✎ Rename Category '{cat_name}' ]{RESET}"
        lines.append(f"{ren_arrow} {ren_btn}")

        # Delete Category Button
        is_del_act = (cursor == btn_del_cat_idx)
        del_arrow = f"{RED}{BOLD}❯{RESET}" if is_del_act else " "
        del_btn = f"{RED}{BOLD}[ ✕ Delete Entire Category '{cat_name}' ]{RESET}" if is_del_act else f"{MUTED}[ ✕ Delete Entire Category '{cat_name}' ]{RESET}"
        lines.append(f"{del_arrow} {del_btn}")

        # Done / Back Button
        is_done_act = (cursor == btn_done_idx)
        done_arrow = f"{GREEN}{BOLD}❯{RESET}" if is_done_act else " "
        done_btn = f"{GREEN}{BOLD}[ ✓ Save & Back to Categories ]{RESET}" if is_done_act else f"{MUTED}[ ✓ Save & Back to Categories ]{RESET}"
        lines.append(f"{done_arrow} {done_btn}")

        if status_msg:
            lines.append("")
            lines.append(f"{GREEN}{BOLD}{status_msg}{RESET}")
            status_msg = ""

        lines.append(f"{MUTED}{'─' * (cols - 2)}{RESET}")
        lines.append(f"{BOLD}[j/k or ↓/↑]{RESET} Nav  {BOLD}[d/x/Del]{RESET} Delete  {BOLD}[Enter]{RESET} Select/Edit  {BOLD}[b/Esc/c]{RESET} Back")

        frame_lines = [pad_line(line, cols) for line in lines]
        while len(frame_lines) < rows:
            frame_lines.append(" " * cols)
        frame = "\033[H" + "\n".join(frame_lines)
        sys.stdout.write(frame)
        sys.stdout.flush()

        key = read_key(tui.fd)
        if key in ("j", "DOWN"):
            cursor = min(total_items - 1, cursor + 1)
        elif key in ("k", "UP"):
            cursor = max(0, cursor - 1)
        elif key in ("b", "B", "ESC", "c", "C", "q", "Q"):
            return {"category": cat_name, "items": format_skills_items(skills_list)}, False
        elif key in ("d", "D", "x", "X", "DELETE", "BACKSPACE"):
            if 0 <= cursor < len(skills_list):
                deleted_skill = skills_list.pop(cursor)
                status_msg = f"✓ Deleted skill '{deleted_skill}'"
                if cursor >= len(skills_list):
                    cursor = max(0, len(skills_list) - 1 if skills_list else 0)
            elif cursor == btn_del_cat_idx:
                return None, True
        elif key == "ENTER":
            if cursor == btn_done_idx:
                return {"category": cat_name, "items": format_skills_items(skills_list)}, False
            elif cursor == btn_del_cat_idx:
                return None, True
            elif cursor == btn_rename_cat_idx:
                new_cat = prompt_line_editor(tui, "Rename Category", "Category Name", cat_name)
                if new_cat.strip():
                    cat_name = new_cat.strip()
                    status_msg = f"✓ Renamed category to '{cat_name}'"
            elif cursor == btn_add_skill_idx:
                new_skill = prompt_line_editor(tui, f"Add Skill to '{cat_name}'", "Skill Name (e.g. Rust, Go, PyTorch)", "")
                if new_skill.strip():
                    added = parse_skills_items(new_skill)
                    skills_list.extend(added)
                    status_msg = f"✓ Added {len(added)} skill(s)"
                    cursor = len(skills_list) - 1
            elif 0 <= cursor < len(skills_list):
                old_skill = skills_list[cursor]
                edited = prompt_line_editor(tui, "Edit Skill", "Skill Name (leave empty to delete)", old_skill)
                if not edited.strip():
                    skills_list.pop(cursor)
                    status_msg = f"✓ Deleted skill '{old_skill}'"
                    if cursor >= len(skills_list):
                        cursor = max(0, len(skills_list) - 1 if skills_list else 0)
                else:
                    skills_list[cursor] = edited.strip()
                    status_msg = f"✓ Updated skill '{skills_list[cursor]}'"


def setup_skills_tui(tui: TerminalUI, current_config: dict) -> list[dict]:
    """Configures skills categories with hjkl navigation, inline editing, add, and delete."""
    skills = [dict(s) for s in current_config.get("skills", [
        {"category": "Languages.Code", "items": "Python, C/C++, Bash, JavaScript"},
        {"category": "Languages.Systems", "items": "Linux, Docker, Git, CI/CD"},
        {"category": "Technologies.AI", "items": "PyTorch, OpenCV, ROS2, Gazebo"},
        {"category": "Technologies.SQA", "items": "PyTest, Jest, Static Analysis"},
    ])]

    if not tui.is_tty or tui.fd is None:
        return skills

    cursor = 0
    status_msg = ""
    while True:
        cols, rows = shutil.get_terminal_size((80, 24))
        # Items: [skills...] + [Add Category] + [Continue]
        btn_add_idx = len(skills)
        btn_cont_idx = len(skills) + 1
        total_items = len(skills) + 2

        if cursor >= total_items:
            cursor = max(0, total_items - 1)

        lines = [
            f"{AMBER}{BOLD}=== [Step 2/5] Technical Skills & Categories ==={RESET}",
            f"{MUTED}Organize skill categories. [Enter] Manage Skills / Rename, [d/x/Del] Delete Category, [a] Add.{RESET}",
            f"{MUTED}{'─' * (cols - 2)}{RESET}",
        ]

        if not skills:
            lines.append(f"  {MUTED}(No skill categories defined. Select [+ Add New Skill Category] below){RESET}")
        else:
            for idx, s in enumerate(skills):
                is_active = (cursor == idx)
                arrow = f"{CYAN}{BOLD}❯{RESET}" if is_active else " "
                cat_name = f"{BOLD}{CYAN if is_active else WHITE}{s.get('category')}{RESET}"
                items_str = s.get("items", "")
                tag = f"  {RED}[d/x to delete]{RESET}" if is_active else ""
                lines.append(f"{arrow} {cat_name}: {items_str}{tag}")

        lines.append("")
        # Add button
        is_add_active = (cursor == btn_add_idx)
        add_arrow = f"{AMBER}{BOLD}❯{RESET}" if is_add_active else " "
        add_btn = f"{AMBER}{BOLD}[ + Add New Skill Category ]{RESET}" if is_add_active else f"{MUTED}[ + Add New Skill Category ]{RESET}"
        lines.append(f"{add_arrow} {add_btn}")

        # Continue button
        is_cont_active = (cursor == btn_cont_idx)
        cont_arrow = f"{GREEN}{BOLD}❯{RESET}" if is_cont_active else " "
        cont_btn = f"{GREEN}{BOLD}[ Continue to System Telemetry -> ]{RESET}" if is_cont_active else f"{MUTED}[ Continue to System Telemetry -> ]{RESET}"
        lines.append(f"{cont_arrow} {cont_btn}")

        if status_msg:
            lines.append("")
            lines.append(f"{GREEN}{BOLD}{status_msg}{RESET}")
            status_msg = ""

        lines.append(f"{MUTED}{'─' * (cols - 2)}{RESET}")
        lines.append(f"{BOLD}[j/k or ↓/↑]{RESET} Nav  {BOLD}[Enter]{RESET} Manage  {BOLD}[d/x/Del]{RESET} Delete Category  {BOLD}[a]{RESET} Add  {BOLD}[c]{RESET} Continue")

        frame_lines = [pad_line(line, cols) for line in lines]
        while len(frame_lines) < rows:
            frame_lines.append(" " * cols)
        frame = "\033[H" + "\n".join(frame_lines)
        sys.stdout.write(frame)
        sys.stdout.flush()

        key = read_key(tui.fd)
        if key in ("j", "DOWN"):
            cursor = min(total_items - 1, cursor + 1)
        elif key in ("k", "UP"):
            cursor = max(0, cursor - 1)
        elif key in ("c", "C"):
            break
        elif key in ("a", "A"):
            new_cat = prompt_line_editor(tui, "New Skill Category", "Category Name (e.g. Languages.Real)", "Languages.Real")
            new_items = prompt_line_editor(tui, "New Skill Category Items", f"Items for '{new_cat}' (comma-separated)", "")
            if new_cat.strip():
                skills.append({"category": new_cat.strip(), "items": new_items.strip()})
                status_msg = f"✓ Added category '{new_cat.strip()}'"
                cursor = len(skills) - 1
        elif key in ("d", "D", "x", "X", "DELETE", "BACKSPACE"):
            if 0 <= cursor < len(skills):
                deleted_cat = skills.pop(cursor)
                status_msg = f"✓ Deleted category '{deleted_cat.get('category')}'"
                if cursor >= len(skills):
                    cursor = max(0, len(skills) - 1 if skills else 0)
        elif key == "ENTER":
            if cursor == btn_cont_idx:
                break
            elif cursor == btn_add_idx:
                new_cat = prompt_line_editor(tui, "New Skill Category", "Category Name (e.g. Languages.Real)", "Languages.Real")
                new_items = prompt_line_editor(tui, "New Skill Category Items", f"Items for '{new_cat}' (comma-separated)", "")
                if new_cat.strip():
                    skills.append({"category": new_cat.strip(), "items": new_items.strip()})
                    status_msg = f"✓ Added category '{new_cat.strip()}'"
                    cursor = len(skills) - 1
            elif 0 <= cursor < len(skills):
                updated_entry, was_deleted = manage_category_skills_tui(tui, skills[cursor])
                if was_deleted:
                    deleted_cat = skills.pop(cursor)
                    status_msg = f"✓ Deleted category '{deleted_cat.get('category')}'"
                    if cursor >= len(skills):
                        cursor = max(0, len(skills) - 1 if skills else 0)
                elif updated_entry:
                    skills[cursor] = updated_entry

    return skills


# ==============================================================================
# Step 3: System Telemetry & Specs (hjkl navigation, edit fields)
# ==============================================================================

def setup_system_info_tui(tui: TerminalUI, current_config: dict) -> tuple[dict, list[dict], dict]:
    """Configures system specs, terminal prompt, and uptime telemetry."""
    user_info = dict(current_config.get("user", {}))
    telemetry = dict(current_config.get("telemetry", {}))

    prompt_hdr = user_info.get("prompt_header", "humam@workstation")
    sys_info = current_config.get("system_info", [])
    def_os = next((x["value"] for x in sys_info if x["key"] == "OS"), "Arch Linux x86_64, Ubuntu")
    def_host = next((x["value"] for x in sys_info if x["key"] == "Host"), "Workstation")
    def_kernel = next((x["value"] for x in sys_info if x["key"] == "Kernel"), "Systems, SQA & Robotics")
    def_ide = next((x["value"] for x in sys_info if x["key"] == "IDE"), "Neovim, VSCode")
    def_shell = next((x["value"] for x in sys_info if x["key"] == "Shell"), "zsh 5.9")
    uptime_start = telemetry.get("uptime_start_date", "2020-09-20")

    fields = [
        {"key": "Prompt Header", "value": prompt_hdr},
        {"key": "OS", "value": def_os},
        {"key": "Host", "value": def_host},
        {"key": "Kernel / Role", "value": def_kernel},
        {"key": "IDE", "value": def_ide},
        {"key": "Shell", "value": def_shell},
        {"key": "Uptime Start Date", "value": uptime_start},
    ]

    # Dynamically preserve any additional custom fields from last configuration
    standard_keys = {"OS", "Host", "Kernel", "IDE", "Shell"}
    for extra in sys_info:
        if extra.get("key") not in standard_keys and extra.get("key"):
            fields.append({"key": extra["key"], "value": extra.get("value", "")})

    if not tui.is_tty or tui.fd is None:
        user_info["prompt_header"] = prompt_hdr
        return user_info, [dict(x) for x in sys_info], telemetry

    cursor = 0
    while True:
        cols, rows = shutil.get_terminal_size((80, 24))
        btn_cont_idx = len(fields)
        total_items = len(fields) + 1

        lines = [
            f"{AMBER}{BOLD}=== [Step 3/5] System Specs & Bio Telemetry ==={RESET}",
            f"{MUTED}Customize the Neofetch prompt and system specs. Press [Enter] to edit, [c] to continue.{RESET}",
            f"{MUTED}{'─' * (cols - 2)}{RESET}",
        ]

        for idx, f in enumerate(fields):
            is_active = (cursor == idx)
            arrow = f"{CYAN}{BOLD}❯{RESET}" if is_active else " "
            k_str = f"{BOLD}{CYAN if is_active else WHITE}{f['key']:<20}{RESET}"
            lines.append(f"{arrow} {k_str}: {f['value']}")

        lines.append("")
        is_cont_active = (cursor == btn_cont_idx)
        cont_arrow = f"{GREEN}{BOLD}❯{RESET}" if is_cont_active else " "
        cont_btn = f"{GREEN}{BOLD}[ Continue to Contacts -> ]{RESET}" if is_cont_active else f"{MUTED}[ Continue to Contacts -> ]{RESET}"
        lines.append(f"{cont_arrow} {cont_btn}")

        lines.append(f"{MUTED}{'─' * (cols - 2)}{RESET}")
        lines.append(f"{BOLD}[j/k or ↓/↑]{RESET} Nav  {BOLD}[Enter]{RESET} Edit  {BOLD}[c]{RESET} Continue")

        frame_lines = [pad_line(line, cols) for line in lines]
        while len(frame_lines) < rows:
            frame_lines.append(" " * cols)
        frame = "\033[H" + "\n".join(frame_lines)
        sys.stdout.write(frame)
        sys.stdout.flush()

        key = read_key(tui.fd)
        if key in ("j", "DOWN"):
            cursor = min(total_items - 1, cursor + 1)
        elif key in ("k", "UP"):
            cursor = max(0, cursor - 1)
        elif key in ("c", "C"):
            break
        elif key == "ENTER":
            if cursor == btn_cont_idx:
                break
            elif 0 <= cursor < len(fields):
                f = fields[cursor]
                f["value"] = prompt_line_editor(tui, f"Edit {f['key']}", f['key'], f["value"])

    # Compile result structures
    user_info["prompt_header"] = fields[0]["value"]
    compiled_sys_info = [
        {"key": "OS", "value": fields[1]["value"]},
        {"key": "Host", "value": fields[2]["value"]},
        {"key": "Kernel", "value": fields[3]["value"]},
        {"key": "IDE", "value": fields[4]["value"]},
        {"key": "Shell", "value": fields[5]["value"]},
    ]
    for extra_field in fields[7:]:
        compiled_sys_info.append({"key": extra_field["key"], "value": extra_field["value"]})
    telemetry["uptime_start_date"] = fields[6]["value"]
    telemetry["show_uptime"] = True
    telemetry["show_github_stats"] = True
    telemetry["show_loc"] = True

    return user_info, compiled_sys_info, telemetry


# ==============================================================================
# Step 4: Contact Handles (hjkl navigation, edit, add, delete)
# ==============================================================================

def setup_contacts_tui(tui: TerminalUI, current_config: dict) -> list[dict]:
    """Configures contact links with hjkl navigation."""
    contacts = [dict(c) for c in current_config.get("contacts", [
        {"label": "Email", "value": "muhammed.humam.hossain@gmail.com", "url": "mailto:muhammed.humam.hossain@gmail.com"},
        {"label": "LinkedIn", "value": "in/humam-hossain-7ab762230", "url": "https://www.linkedin.com/in/humam-hossain-7ab762230/"},
        {"label": "Portfolio", "value": "humam-hossain.github.io", "url": "https://github.com/humam-hossain"},
    ])]

    if not tui.is_tty or tui.fd is None:
        return contacts

    cursor = 0
    while True:
        cols, rows = shutil.get_terminal_size((80, 24))
        btn_add_idx = len(contacts)
        btn_cont_idx = len(contacts) + 1
        total_items = len(contacts) + 2

        lines = [
            f"{AMBER}{BOLD}=== [Step 4/5] Contact Handles ==={RESET}",
            f"{MUTED}Provide the handles to show in your profile. Press [Enter] to edit, [a] to add, [d] to delete.{RESET}",
            f"{MUTED}{'─' * (cols - 2)}{RESET}",
        ]

        for idx, c in enumerate(contacts):
            is_active = (cursor == idx)
            arrow = f"{CYAN}{BOLD}❯{RESET}" if is_active else " "
            lbl = f"{BOLD}{CYAN if is_active else WHITE}{c.get('label'):<12}{RESET}"
            lines.append(f"{arrow} {lbl}: {c.get('value')} ({c.get('url', '')})")

        lines.append("")
        is_add_active = (cursor == btn_add_idx)
        add_arrow = f"{AMBER}{BOLD}❯{RESET}" if is_add_active else " "
        add_btn = f"{AMBER}{BOLD}[ + Add New Handle ]{RESET}" if is_add_active else f"{MUTED}[ + Add New Handle ]{RESET}"
        lines.append(f"{add_arrow} {add_btn}")

        is_cont_active = (cursor == btn_cont_idx)
        cont_arrow = f"{GREEN}{BOLD}❯{RESET}" if is_cont_active else " "
        cont_btn = f"{GREEN}{BOLD}[ Continue to ASCII Art -> ]{RESET}" if is_cont_active else f"{MUTED}[ Continue to ASCII Art -> ]{RESET}"
        lines.append(f"{cont_arrow} {cont_btn}")

        lines.append(f"{MUTED}{'─' * (cols - 2)}{RESET}")
        lines.append(f"{BOLD}[j/k or ↓/↑]{RESET} Nav  {BOLD}[Enter]{RESET} Edit  {BOLD}[a]{RESET} Add  {BOLD}[d]{RESET} Delete  {BOLD}[c]{RESET} Continue")

        frame_lines = [pad_line(line, cols) for line in lines]
        while len(frame_lines) < rows:
            frame_lines.append(" " * cols)
        frame = "\033[H" + "\n".join(frame_lines)
        sys.stdout.write(frame)
        sys.stdout.flush()

        key = read_key(tui.fd)
        if key in ("j", "DOWN"):
            cursor = min(total_items - 1, cursor + 1)
        elif key in ("k", "UP"):
            cursor = max(0, cursor - 1)
        elif key in ("c", "C"):
            break
        elif key in ("a", "A"):
            label = prompt_line_editor(tui, "Add Contact", "Platform Label (e.g. Discord, Telegram, X)", "Discord")
            val = prompt_line_editor(tui, f"Add {label} Handle", f"Handle / Username for {label}", "")
            if label and val:
                url = f"mailto:{val}" if label.lower() == "email" else f"https://github.com/{val}"
                contacts.append({"label": label, "value": val, "url": url})
                cursor = len(contacts) - 1
        elif key in ("d", "D", "x"):
            if 0 <= cursor < len(contacts) and len(contacts) > 1:
                contacts.pop(cursor)
                cursor = min(cursor, len(contacts) - 1)
        elif key == "ENTER":
            if cursor == btn_cont_idx:
                break
            elif cursor == btn_add_idx:
                label = prompt_line_editor(tui, "Add Contact", "Platform Label (e.g. Discord, Telegram, X)", "Discord")
                val = prompt_line_editor(tui, f"Add {label} Handle", f"Handle / Username for {label}", "")
                if label and val:
                    url = f"mailto:{val}" if label.lower() == "email" else f"https://github.com/{val}"
                    contacts.append({"label": label, "value": val, "url": url})
            elif 0 <= cursor < len(contacts):
                c = contacts[cursor]
                c["value"] = prompt_line_editor(tui, f"Edit {c['label']}", c["label"], c["value"])
                if c["label"].lower() == "email":
                    c["url"] = f"mailto:{c['value']}"
                elif "linkedin" in c["label"].lower():
                    clean_in = c["value"].strip("/").replace("in/", "")
                    c["url"] = f"https://www.linkedin.com/in/{clean_in}/"
                elif "portfolio" in c["label"].lower() or "web" in c["label"].lower():
                    clean_web = c["value"].replace("https://", "").replace("http://", "").strip("/")
                    c["url"] = f"https://{clean_web}"

    return contacts


# ==============================================================================
# Step 5: ASCII Art Selection (Live Preview with hjkl)
# ==============================================================================

ARCH_ASCII = [
    "                   -`                 ",
    "                  .o+`                ",
    "                 `ooo/                ",
    "                `+oooo:               ",
    "               `+oooooo:              ",
    "               -+oooooo+:             ",
    "             `/:-:++oooo+:            ",
    "            `/++++/+++++++:           ",
    "           `/++++++++++++++:          ",
    "          `/+++ooooooooooooo/`        ",
    "         ./ooosssso++osssssso+`       ",
    "        .oossssso-````/ossssss+`      ",
    "       -osssssso.      :ssssssso.     ",
    "      :osssssss/        osssso+++.    ",
    "     /ossssssss/        +ssssooo/-    ",
    "   `/ossssso+/:-        -:/+osssso+-  ",
    "  `+sso+:-`                 `.-/+oso: ",
    " `++:.                           `-/+/",
    " .`                                 `/",
    "                                      ",
    "         HUMAM HOSSAIN // WORKSTATION ",
    "         ============================ ",
    "         [AI & ROBOTICS / SYSTEMS]    ",
    "                                      ",
    "            github.com/humam-hossain  ",
]

MONOGRAM_ASCII = [
    "   ▄▄     ▄▄   ",
    "   ██     ██   ",
    "   ██     ██   ",
    "   █████████   ",
    "   █████████   ",
    "   ██     ██   ",
    "   ██     ██   ",
    "   ▀▀     ▀▀ _ ",
    "               ",
    "  HUMAM HOSSAIN",
    "  ============= ",
    "  [AI & ROBOT] ",
    "  arch-linux-64",
    "  workstation  ",
]


def select_ascii_art_tui(tui: TerminalUI, current_config: dict) -> list[str]:
    """Allows selecting ASCII art style with real-time preview."""
    existing_custom = current_config.get("ascii_art")
    options = [
        {"name": "Arch Linux Logo (Authentic Unix Neofetch)", "lines": ARCH_ASCII},
        {"name": "Monogram Banner (HUMAM HOSSAIN // WORKSTATION)", "lines": MONOGRAM_ASCII},
        {"name": "Custom Artwork (Keep current from profile_config.json)", "lines": existing_custom or ARCH_ASCII},
    ]

    # Detect which option matches the last saved change so it comes up first
    cursor = 0
    if existing_custom:
        if existing_custom == MONOGRAM_ASCII:
            cursor = 1
        elif existing_custom == ARCH_ASCII:
            cursor = 0
        else:
            cursor = 2

    if not tui.is_tty or tui.fd is None:
        return options[cursor]["lines"]
    while True:
        cols, rows = shutil.get_terminal_size((80, 24))

        lines = [
            f"{AMBER}{BOLD}=== [Step 5/5] ASCII Art Selection (Left Column) ==={RESET}",
            f"{MUTED}Switch style with [j/k or ↑/↓]. Preview updates below. Press [Enter] to build profile.{RESET}",
            f"{MUTED}{'─' * (cols - 2)}{RESET}",
        ]

        for idx, opt in enumerate(options):
            is_active = (cursor == idx)
            arrow = f"{CYAN}{BOLD}❯{RESET}" if is_active else " "
            bullet = f"{GREEN}[*]{RESET}" if is_active else f"{MUTED}[ ]{RESET}"
            name = f"{BOLD}{CYAN if is_active else WHITE}{opt['name']}{RESET}"
            lines.append(f"{arrow} {bullet} {name}")

        lines.append("")
        lines.append(f"{AMBER}{BOLD}--- Live Preview ---{RESET}")
        preview_lines = options[cursor]["lines"]
        for p_line in preview_lines[:15]:
            lines.append(f"{CYAN}{p_line}{RESET}")

        lines.append(f"{MUTED}{'─' * (cols - 2)}{RESET}")
        lines.append(f"{BOLD}[j/k or ↓/↑]{RESET} Switch Style  {BOLD}[Enter]{RESET} Select & Build Profile")

        frame_lines = [pad_line(line, cols) for line in lines]
        while len(frame_lines) < rows:
            frame_lines.append(" " * cols)
        frame = "\033[H" + "\n".join(frame_lines)
        sys.stdout.write(frame)
        sys.stdout.flush()

        key = read_key(tui.fd)
        if key in ("j", "DOWN"):
            cursor = (cursor + 1) % len(options)
        elif key in ("k", "UP"):
            cursor = (cursor - 1) % len(options)
        elif key == "ENTER":
            return options[cursor]["lines"]


# ==============================================================================
# Main Execution Pipeline
# ==============================================================================

def main() -> int:
    # Handle help or non-interactive flags
    if "--help" in sys.argv or "-h" in sys.argv:
        print(f"{BOLD}Usage:{RESET} python3 scripts/configure_profile.py [--non-interactive]")
        print("Interactive setup wizard with hjkl Vim navigation and latest-committed repo sorting.")
        return 0

    current_config = {}
    if CONFIG_PATH.is_file():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                current_config = json.load(f)
        except Exception:
            pass

    username = current_config.get("user", {}).get("username", "humam-hossain")

    # Fetch repositories ordered by latest commit
    print(f"\n{CYAN}Fetching public repositories for @{username} sorted by latest commit...{RESET}")
    repos = fetch_user_repos(username)
    if not repos:
        # Fallback dummy list if offline or rate-limited
        repos = [
            {"name": "adb-permission-manager", "description": "Android permissions controller", "pushed_at": "2026-11-09", "language": "Python", "stars": 0},
            {"name": "Voice", "description": "Desktop push-to-talk STT/TTS", "pushed_at": "2026-11-03", "language": "Python", "stars": 0},
            {"name": "greeclimate", "description": "Gree minisplit HVAC controller", "pushed_at": "2026-10-17", "language": "Python", "stars": 0},
            {"name": "dots-hyprland", "description": "Usability-first dotfiles", "pushed_at": "2026-10-11", "language": "QML", "stars": 0},
            {"name": "antigravity-cli-statusline", "description": "Terminal statusline plugin", "pushed_at": "2026-08-14", "language": "Shell", "stars": 0},
        ]

    current_featured = current_config.get("featured_projects", [])
    # Always prioritize the last change: projects from profile_config.json come up first
    repos, current_selected_names = prepare_repos_list(repos, current_featured)

    with TerminalUI() as tui:
        # 1. Select Projects (last configured projects come up first, followed by latest commits)
        chosen_repos = select_projects_tui(tui, repos, current_selected_names)

        # 1b. Project Descriptions
        featured_projects = edit_project_descriptions_tui(tui, chosen_repos, current_featured)

        # 2. Skills Categories
        skills = setup_skills_tui(tui, current_config)

        # 3. System Telemetry & Specs
        user_info, system_info, telemetry = setup_system_info_tui(tui, current_config)

        # 4. Contacts
        contacts = setup_contacts_tui(tui, current_config)

        # 5. ASCII Art Style
        ascii_art = select_ascii_art_tui(tui, current_config)

    # Compile new config
    new_config = {
        "user": user_info,
        "system_info": system_info,
        "skills": skills,
        "featured_projects": featured_projects,
        "contacts": contacts,
        "telemetry": telemetry,
        "ascii_art": ascii_art,
    }

    # Save to profile_config.json
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(new_config, f, indent=2)

    print(f"\n{GREEN}{BOLD}✓ Saved configuration to {CONFIG_PATH}{RESET}")
    print(f"{CYAN}Compiling dark_mode.svg, light_mode.svg, and README.md...{RESET}\n")

    # Build profile SVGs
    res = subprocess.run([sys.executable, str(BUILD_SCRIPT)])
    if res.returncode == 0:
        print(f"\n{GREEN}{BOLD}🎉 Success! Profile rebuilt with your custom selections.{RESET}")
        print(f"{MUTED}You can re-launch this wizard anytime using:{RESET}")
        print(f"  {BOLD}python3 scripts/configure_profile.py{RESET}\n")
    else:
        print(f"{RED}Build failed. Check scripts/build_profile.py error output.{RESET}")
        return res.returncode

    return 0


if __name__ == "__main__":
    sys.exit(main())
