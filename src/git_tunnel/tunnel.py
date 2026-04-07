import subprocess
import sys
import re

# Colors etc.
RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'

DEVICE_COLORS = [
    '\033[96m', # Cyan
    '\033[93m', # Yellow
    '\033[92m', # Green
    '\033[95m', # Magenta/Purpulish
    '\033[91m', # Red
    '\033[94m', # Blue
]

HASH_COLOR = '\033[90m'
TIME_COLOR = '\033[37m'
BORDER_COLOR = '\033[90m'
HEADER_COLOR = '\033[1;37m'
LEGACY_COLOR = '\033[37m'

# Layout
TIME_WIDTH = 17
MSG_WIDTH = 36
HASH_WIDTH = 9

DEVICE_TAG   = re.compile(r'\[device:(.+?)\]', re.IGNORECASE)
LEGACY_LABEL = 'pre git-tunnel'

def run_git_log():
    try:
        result = subprocess.run(
            ['git', 'log', '--pretty=format:%h|%an|%ar|%B|||END|||',
             '--exclude=refs/original/*', '--all'],
            capture_output=True, text=True
        )
    except FileNotFoundError:
        print(f"\n  ✗  git is not installed or not on PATH.\n"
              f"     Install it from https://git-scm.com\n")
        sys.exit(1)
    if result.returncode != 0:
        print(f"\n  ✗  Not a git repository. Run this inside a git project.\n")
        sys.exit(1)
    return result.stdout


def parse_commits(raw):
    entries = raw.split('|||END|||')
    commits = []
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        lines  = entry.split('\n')
        header = lines[0]
        parts  = header.split('|', 3)
        if len(parts) < 3:
            continue

        hash_ = parts[0].strip()
        author = parts[1].strip()
        time_ = parts[2].strip()
        first_line = parts[3].strip() if len(parts) > 3 else ''
        rest = '\n'.join(lines[1:]).strip()
        body = (first_line + '\n' + rest).strip()

        match = DEVICE_TAG.search(body)
        device = match.group(1).strip() if match else None

        clean_msg = DEVICE_TAG.sub('', body).strip().splitlines()
        clean_msg = ' '.join(l.strip() for l in clean_msg if l.strip())

        commits.append({
            'hash':    hash_,
            'author':  author,
            'device':  device,
            'time':    time_,
            'message': clean_msg,
        })

    seen, unique = set(), []
    for c in commits:
        if c['hash'] not in seen:
            seen.add(c['hash'])
            unique.append(c)
    return unique

def truncate(text, width):
    return text if len(text) <= width else text[:width - 1] + '…'

def border(ch):
    return f"{BORDER_COLOR}{ch}{RESET}"

def render(commits, show_all=False):
    has_legacy = any(c['device'] is None for c in commits)
    devices = [LEGACY_LABEL] if has_legacy else []

    for c in reversed(commits):
        if c['device'] and c['device'] not in devices:
            devices.append(c['device'])

    def get_color(d):
        if d == LEGACY_LABEL:
            return LEGACY_COLOR
        device_only = [x for x in devices if x != LEGACY_LABEL]
        idx = device_only.index(d) if d in device_only else 0
        return DEVICE_COLORS[idx % len(DEVICE_COLORS)]

    if show_all:
        max_msg = max((len(c['message']) for c in commits), default=MSG_WIDTH)
        col_w = max(max_msg, MSG_WIDTH) + 2
    else:
        col_w = MSG_WIDTH + 2

    row_total = TIME_WIDTH + (col_w + 3) * len(devices) + HASH_WIDTH + 4
    bar = BORDER_COLOR + '─' * row_total + RESET

    print(f"\n{bar}")
    header  = f"  {HEADER_COLOR}{'TIME':<{TIME_WIDTH}}{RESET}"
    header += border('│')
    for d in devices:
        color = get_color(d)
        label = truncate(d, col_w)
        header += f" {color}{BOLD}{label:<{col_w}}{RESET} {border('│')}"
    header += f" {HEADER_COLOR}{'HASH':<{HASH_WIDTH}}{RESET}"
    print(header)
    print(bar)

    for c in commits:
        device = c['device'] if c['device'] else LEGACY_LABEL
        time_str = truncate(c['time'], TIME_WIDTH)
        color = get_color(device)

        row = f"  {TIME_COLOR}{time_str:<{TIME_WIDTH}}{RESET}"
        row += border('│')

        for d in devices:
            if device == d:
                msg = c['message'] if show_all else truncate(c['message'], col_w)
                row += f" {color}{msg:<{col_w}}{RESET} {border('│')}"
            else:
                dots = DIM + '· ' * ((col_w + 1) // 2)
                row += f" {dots:<{col_w + len(DIM)}}{RESET} {border('│')}"

        row += f" {HASH_COLOR}{c['hash']}{RESET}"
        print(row)

    print(bar)
    print()
    legend = "  "
    for d in devices:
        legend += f"{get_color(d)}{BOLD}■ {d}{RESET}   "
    print(legend + "\n")


def check_device():
    try:
        device = subprocess.run(
            ['git', 'config', '--global', 'user.device'],
            capture_output=True, text=True
        ).stdout.strip()
    except FileNotFoundError:
        print(f"\n  ✗  git is not installed or not on PATH.\n"
              f"     Install it from https://git-scm.com\n")
        sys.exit(1)
    if not device:
        print(f"\n  {BOLD}First time?{RESET}  Run {BOLD}git-tunnel install{RESET} to set up your device.\n"
              f"  Your commits won't be tagged until you do.\n")


def main():
    show_all = '--all' in sys.argv
    check_device()
    raw = run_git_log()
    commits = parse_commits(raw)
    if not commits:
        print("\n  No commits found.\n")
        return
    render(commits, show_all=show_all)
