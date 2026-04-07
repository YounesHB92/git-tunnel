import sys
import os
import subprocess
import shutil
from pathlib import Path

def install():
    """
    Interactive install:
      - Sets git config --global user.device
      - Installs the prepare-commit-msg hook
      - Sets git config --global core.hooksPath
      - Adds the shell function hint
    """
    RESET = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'

    def ok(t):   print(f"  \033[92m✓\033[0m {t}")
    def info(t): print(f"  \033[96m→\033[0m {t}")
    def warn(t): print(f"  \033[93m⚠\033[0m  {t}")

    print(f"\n{BOLD}git-tunnel install{RESET}\n")

    # ── git check ─────────────────────────────────────────────────────────────
    if not shutil.which('git'):
        print(f"  \033[91m✗\033[0m  git is not installed or not on PATH.\n"
              f"     Install it from https://git-scm.com and re-run this command.\n")
        sys.exit(1)

    # ── Device name ───────────────────────────────────────────────────────────
    current = subprocess.run(
        ['git', 'config', '--global', 'user.device'],
        capture_output=True, text=True
    ).stdout.strip()

    if current:
        info(f"user.device already set to '{CYAN}{current}{RESET}'")
        answer = input("  Change it? [y/N] ").strip().lower()
        if answer != 'y':
            device = current
        else:
            device = input("  Enter device name (e.g. MacBook, Workstation, Server): ").strip()
    else:
        device = input("  Enter device name for this machine (e.g. MacBook, Workstation, Server): ").strip()

    if not device:
        warn("No device name entered — skipping.")
    else:
        subprocess.run(['git', 'config', '--global', 'user.device', device])
        ok(f"user.device set to '{device}'")

    # Hook installation
    hooks_dir = Path.home() / '.git-tunnel-hooks'
    hooks_dir.mkdir(exist_ok=True)

    # Find the hook bundled with the package
    pkg_hook = Path(__file__).parent/'hooks'/'prepare-commit-msg'
    dest = hooks_dir / 'prepare-commit-msg'
    shutil.copy(pkg_hook, dest)
    dest.chmod(0o755)
    ok(f"Hook installed → {dest}")

    # Point git at the hooks dir
    subprocess.run(['git', 'config', '--global', 'core.hooksPath', str(hooks_dir)])
    ok(f"core.hooksPath set to {hooks_dir}")

    # Shell function — write it directly into the user's shell config
    shell = os.environ.get('SHELL', '')
    if 'zsh' in shell:
        rc_file = Path.home() / '.zshrc'
    else:
        rc_file = Path.home() / '.bashrc'

    marker = '# git-tunnel shell function'
    fn_block = f'\n{marker}\nfunction git-tunnel() {{ git-tunnel-run "$@"; }}\n'

    rc_text = rc_file.read_text() if rc_file.exists() else ''
    if marker in rc_text:
        ok(f"Shell function already present in {rc_file}")
    else:
        with rc_file.open('a') as f:
            f.write(fn_block)
        ok(f"Shell function added to {rc_file}")

    print(f"\n{BOLD}All done!{RESET} Restart your shell or run:\n")
    print(f"  {CYAN}source {rc_file}{RESET}\n")







def help():
    RESET  = '\033[0m'
    BOLD   = '\033[1m'
    CYAN   = '\033[96m'
    YELLOW = '\033[93m'
    DIM    = '\033[2m'

    print(f"""
{BOLD}git-tunnel{RESET} — visualize git history as per-machine tunnels in your terminal

{BOLD}USAGE{RESET}
  {CYAN}git-tunnel{RESET} {DIM}[flags]{RESET}
  {CYAN}git-tunnel{RESET} {YELLOW}<command>{RESET}

{BOLD}FLAGS{RESET}
  {CYAN}--all{RESET}       Show full commit messages without truncation
  {CYAN}--help{RESET}      Show this help message

{BOLD}COMMANDS{RESET}
  {YELLOW}install{RESET}     Set up git-tunnel on this machine
              • prompts for a device name (stored in git config user.device)
              • installs the prepare-commit-msg hook globally
              • adds the git-tunnel shell function to your shell config

{BOLD}EXAMPLES{RESET}
  {DIM}# View the tunnel (compact, truncated messages){RESET}
  git-tunnel

  {DIM}# View the tunnel with full commit messages{RESET}
  git-tunnel --all

  {DIM}# First-time install{RESET}
  git-tunnel install
""")


def main():
    args = sys.argv[1:]
    if args and args[0] == 'install':
        install()
    elif '--help' in args or '-h' in args:
        help()
    else:
        from git_tunnel.tunnel import main as run
        run()
