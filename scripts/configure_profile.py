#!/usr/bin/env python3
"""
scripts/configure_profile.py
Interactive CLI Wizard for Muhammed Humam Hossain (@humam-hossain).
Prompts you for your exact preferences (projects, skills, system info, contacts, ASCII art),
saves your answers to profile_config.json, and generates dark_mode.svg and light_mode.svg.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import readline
import sys
import urllib.error
import urllib.request

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "profile_config.json"

# ANSI Colors
CYAN = "\033[38;2;88;166;255m"
GREEN = "\033[38;2;63;185;80m"
AMBER = "\033[38;2;255;166;87m"
RED = "\033[38;2;248;81;73m"
MUTED = "\033[38;2;139;148;158m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner() -> None:
    print(f"\n{AMBER}{BOLD}=== Andrew6rant Neofetch Profile Interactive Setup Wizard ==={RESET}")
    print(f"{MUTED}Customize your GitHub profile README interactively.{RESET}")
    print(f"{MUTED}Press Enter on any prompt to accept the current/default value.{RESET}\n")


def prompt_text(label: str, default: str = "") -> str:
    """Prompts the user with an optional default value."""
    if default:
        p = f"{CYAN}?{RESET} {BOLD}{label}{RESET} [{MUTED}{default}{RESET}]: "
    else:
        p = f"{CYAN}?{RESET} {BOLD}{label}{RESET}: "
    try:
        val = input(p).strip()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{RED}Setup aborted.{RESET}")
        sys.exit(0)
    return val if val else default


def prompt_yes_no(label: str, default: bool = True) -> bool:
    """Prompts user with a yes/no question."""
    suffix = "[Y/n]" if default else "[y/N]"
    p = f"{CYAN}?{RESET} {BOLD}{label}{RESET} {MUTED}{suffix}{RESET}: "
    try:
        val = input(p).strip().lower()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{RED}Setup aborted.{RESET}")
        sys.exit(0)
    if not val:
        return default
    return val.startswith("y")


def fetch_user_repos(username: str) -> list[dict]:
    """Fetches public repositories for the user from GitHub API."""
    print(f"{MUTED}Fetching public repositories for @{username} from GitHub...{RESET}")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or os.environ.get("PROFILE_TOKEN")
    headers = {"User-Agent": "profile-wizard"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    all_repos = []
    page = 1
    while page <= 3:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}&sort=updated"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if not data or not isinstance(data, list):
                    break
                for r in data:
                    all_repos.append({
                        "name": r.get("name"),
                        "description": r.get("description") or "",
                        "stars": r.get("stargazers_count", 0),
                        "language": r.get("language") or "Code",
                    })
                if len(data) < 100:
                    break
                page += 1
        except Exception:
            break

    return all_repos


def setup_projects(current_config: dict, username: str) -> list[dict]:
    print(f"\n{GREEN}{BOLD}[1/5] Featured Projects{RESET}")
    print(f"{MUTED}Select which repositories you want to showcase in your profile.{RESET}\n")

    repos = fetch_user_repos(username)
    if repos:
        print(f"{BOLD}Available repositories on GitHub:{RESET}")
        for idx, r in enumerate(repos[:30], 1):
            desc = f" - {r['description'][:45]}..." if len(r['description']) > 45 else (f" - {r['description']}" if r['description'] else "")
            stars = f" (★ {r['stars']})" if r['stars'] > 0 else ""
            print(f"  {CYAN}{idx:2d}.{RESET} {BOLD}{r['name']}{RESET}{desc}{AMBER}{stars}{RESET}")
        print()

    current_projects = current_config.get("featured_projects", [])
    current_names = [p.get("repo") for p in current_projects]
    print(f"{MUTED}Currently featured: {', '.join(current_names) if current_names else 'None'}{RESET}")

    if repos:
        choice_str = prompt_text(
            "Enter repository numbers (e.g. 1, 3, 5) or repository names separated by commas",
            default=",".join(current_names[:4])
        )
    else:
        choice_str = prompt_text("Enter repository names separated by commas", default=",".join(current_names[:4]))

    selected_repos = []
    tokens = [t.strip() for t in choice_str.split(",") if t.strip()]

    for t in tokens:
        if t.isdigit() and repos and 1 <= int(t) <= len(repos):
            selected_repos.append(repos[int(t) - 1])
        else:
            # Match by name
            matched = next((r for r in repos if r["name"].lower() == t.lower()), None)
            if matched:
                selected_repos.append(matched)
            else:
                selected_repos.append({"name": t, "description": ""})

    # Limit to 5 max to prevent overflow
    selected_repos = selected_repos[:5]
    result_projects = []

    print(f"\n{MUTED}Now set a concise one-line description for each chosen project:{RESET}")
    for p in selected_repos:
        repo_name = p["name"]
        existing = next((cp for cp in current_projects if cp.get("repo") == repo_name), None)
        def_desc = existing.get("description") if existing else (p.get("description") or "Unix software & tools")
        desc = prompt_text(f"Description for '{repo_name}'", default=def_desc)
        result_projects.append({"repo": repo_name, "description": desc})

    return result_projects


def setup_skills(current_config: dict) -> list[dict]:
    print(f"\n{GREEN}{BOLD}[2/5] Technical Skills & Categories{RESET}")
    print(f"{MUTED}Group your languages, frameworks, systems, and tools into neat categories.{RESET}\n")

    current_skills = current_config.get("skills", [
        {"category": "Languages.Code", "items": "Python, C/C++, Bash, JavaScript"},
        {"category": "Languages.Systems", "items": "Linux, Docker, Git, CI/CD"},
        {"category": "Technologies.AI", "items": "PyTorch, OpenCV, ROS2, Gazebo"},
        {"category": "Technologies.SQA", "items": "PyTest, Jest, Static Analysis"},
    ])

    skills_list = []
    if prompt_yes_no("Would you like to customize each skills category?", default=True):
        for idx, s in enumerate(current_skills, 1):
            cat = prompt_text(f"Category {idx} Name", default=s.get("category", f"Category.{idx}"))
            items = prompt_text(f"Items for '{cat}'", default=s.get("items", ""))
            skills_list.append({"category": cat, "items": items})

        # Allow adding an extra category
        while prompt_yes_no("Add another skill category?", default=False):
            cat = prompt_text("New Category Name (e.g. Languages.Real)")
            items = prompt_text(f"Items for '{cat}' (e.g. English, Bengali)")
            if cat and items:
                skills_list.append({"category": cat, "items": items})
    else:
        skills_list = current_skills

    return skills_list


def setup_system_info(current_config: dict) -> tuple[dict, list[dict], dict]:
    print(f"\n{GREEN}{BOLD}[3/5] System Telemetry & Bio{RESET}")
    print(f"{MUTED}Configure the prompt line and system specs.{RESET}\n")

    user_info = current_config.get("user", {})
    prompt_hdr = prompt_text("Terminal Prompt (Header)", default=user_info.get("prompt_header", "humam@workstation"))
    user_info["prompt_header"] = prompt_hdr

    sys_info = current_config.get("system_info", [])
    def_os = next((x["value"] for x in sys_info if x["key"] == "OS"), "Arch Linux x86_64, Ubuntu")
    def_host = next((x["value"] for x in sys_info if x["key"] == "Host"), "Workstation")
    def_kernel = next((x["value"] for x in sys_info if x["key"] == "Kernel"), "Systems, SQA & Robotics")
    def_ide = next((x["value"] for x in sys_info if x["key"] == "IDE"), "Neovim, VSCode")
    def_shell = next((x["value"] for x in sys_info if x["key"] == "Shell"), "zsh 5.9")

    os_val = prompt_text("OS", default=def_os)
    host_val = prompt_text("Host", default=def_host)
    kernel_val = prompt_text("Kernel / Role", default=def_kernel)
    ide_val = prompt_text("IDE", default=def_ide)
    shell_val = prompt_text("Shell", default=def_shell)

    new_sys_info = [
        {"key": "OS", "value": os_val},
        {"key": "Host", "value": host_val},
        {"key": "Kernel", "value": kernel_val},
        {"key": "IDE", "value": ide_val},
        {"key": "Shell", "value": shell_val},
    ]

    telemetry = current_config.get("telemetry", {})
    uptime_start = prompt_text(
        "Uptime Start Date (YYYY-MM-DD) [First commit / birthdate]",
        default=telemetry.get("uptime_start_date", "2020-09-20")
    )
    telemetry["uptime_start_date"] = uptime_start
    telemetry["show_uptime"] = True
    telemetry["show_github_stats"] = True
    telemetry["show_loc"] = True

    return user_info, new_sys_info, telemetry


def setup_contacts(current_config: dict) -> list[dict]:
    print(f"\n{GREEN}{BOLD}[4/5] Contact Links{RESET}")
    print(f"{MUTED}Provide the contact handles to display.{RESET}\n")

    contacts = current_config.get("contacts", [])
    def_email = next((x["value"] for x in contacts if x["label"] == "Email"), "muhammed.humam.hossain@gmail.com")
    def_linkedin = next((x["value"] for x in contacts if x["label"] == "LinkedIn"), "in/humam-hossain-7ab762230")
    def_portfolio = next((x["value"] for x in contacts if x["label"] == "Portfolio"), "humam-hossain.github.io")

    email_val = prompt_text("Email Address", default=def_email)
    linkedin_val = prompt_text("LinkedIn Handle / Profile", default=def_linkedin)
    portfolio_val = prompt_text("Website / Portfolio Handle", default=def_portfolio)

    new_contacts = [
        {"label": "Email", "value": email_val, "url": f"mailto:{email_val}"},
        {"label": "LinkedIn", "value": linkedin_val, "url": f"https://www.linkedin.com/{linkedin_val}"},
        {"label": "Portfolio", "value": portfolio_val, "url": f"https://{portfolio_val}"},
    ]

    if prompt_yes_no("Add a Discord or Telegram handle?", default=False):
        label = prompt_text("Service Name (e.g. Discord, Telegram, X)")
        val = prompt_text(f"Handle for '{label}'")
        if label and val:
            new_contacts.append({"label": label, "value": val, "url": f"https://github.com/{val}"})

    return new_contacts


def setup_ascii_art() -> list[str]:
    print(f"\n{GREEN}{BOLD}[5/5] ASCII Art Selection (Left Column){RESET}")
    print(f"{MUTED}Choose your terminal artwork style:{RESET}")
    print(f"  {CYAN}1.{RESET} Arch Linux Logo (authentic Unix neofetch)")
    print(f"  {CYAN}2.{RESET} Monogram Banner (HUMAM HOSSAIN // WORKSTATION)")
    print(f"  {CYAN}3.{RESET} Custom (paste your own lines in profile_config.json)\n")

    choice = prompt_text("Select ASCII style [1-3]", default="1")
    if choice == "2":
        return [
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
    return [
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


def main() -> int:
    print_banner()

    current_config = {}
    if CONFIG_PATH.is_file():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                current_config = json.load(f)
        except Exception:
            pass

    username = current_config.get("user", {}).get("username", "humam-hossain")

    # 1. Projects
    featured_projects = setup_projects(current_config, username)

    # 2. Skills
    skills = setup_skills(current_config)

    # 3. System Info & Telemetry
    user_info, system_info, telemetry = setup_system_info(current_config)

    # 4. Contacts
    contacts = setup_contacts(current_config)

    # 5. ASCII Art
    ascii_art = setup_ascii_art()

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
    print(f"{CYAN}Compiling dark_mode.svg, light_mode.svg, and README.md...{RESET}")

    # Build profile SVGs
    import subprocess
    res = subprocess.run([sys.executable, str(ROOT_DIR / "scripts" / "build_profile.py")])
    if res.returncode == 0:
        print(f"\n{GREEN}{BOLD}🎉 Success! Your profile SVGs and README.md have been regenerated.{RESET}")
        print(f"{MUTED}You can re-run this setup wizard anytime with:{RESET}")
        print(f"  {BOLD}python3 scripts/configure_profile.py{RESET}\n")
    else:
        print(f"{RED}Build failed. Check scripts/build_profile.py output above.{RESET}")
        return res.returncode

    return 0


if __name__ == "__main__":
    sys.exit(main())
