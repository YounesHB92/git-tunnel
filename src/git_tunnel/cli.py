import sys
import subprocess
import shutil
from pathlib import Path

def install():
    """
    Interactive setup:
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

    print(f"\n{BOLD}git-tunnel setup{RESET}\n")

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

    # Shell function hint
    print(f"\n{BOLD}Almost done!{RESET} Add this to your shell config (~/.zshrc or ~/.bashrc):\n")
    print(f"  {CYAN}function git-tunnel() {{ git-tunnel-run; }}{RESET}\n")
    print(f"Or just run:  {BOLD}git-tunnel-run{RESET}  directly.\n")







def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'install':
        install()
    else:
        from git_tunnel.tunnel import main as run
        run()
