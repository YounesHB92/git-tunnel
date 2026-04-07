# git-tunnel

Visualize your git history as **per-machine tunnels** in the terminal.

If you work across multiple machines like me — a MacBook, a Workstation, a Server — git
log treats them all the same which can be very annoying at some points. `git-tunnel` splits each machine into its own
colored column so you can see at a glance *where* every commit was made.

```
────────────────────────────────────────────────────────────────────────────────
  TIME              │ pre git-tunnel                       │ MacBook                              │ Workstation                          │ HASH
────────────────────────────────────────────────────────────────────────────────
  2 hours ago       │ · · · · · · · · · · · · · ·          │ WIP: invoice route                   │ · · · · · · · · · · · · · ·          │ 2c4930f
  3 hours ago       │ · · · · · · · · · · · · · ·          │ · · · · · · · · · · · · · ·          │ finished validation                  │ 6f46c9f
  1 day ago         │ added model                          │ · · · · · · · · · · · · · ·          │ · · · · · · · · · · · · · ·          │ fd7bcad
  1 day ago         │ initial setup                        │ · · · · · · · · · · · · · ·          │ · · · · · · · · · · · · · ·          │ f3bc95b
────────────────────────────────────────────────────────────────────────────────

  ■ pre git-tunnel   ■ MacBook   ■ Workstation
```

Commits made before `git-tunnel` was installed appear in a plain white
`pre git-tunnel` column — no history rewriting, no warnings.

---

## Install

The recommended way to install `git-tunnel` is with **pipx** or **uv** — both install it into an isolated environment and expose the `git-tunnel` command globally. This avoids the `externally-managed-environment` error you get with bare `pip` on Ubuntu 23.04+ and other modern Linux distros.

**pipx** (recommended for most users):
```bash
pipx install git-tunnel
```

**uv** (if you already use uv):
```bash
uv tool install git-tunnel
```

**pip** (virtualenv or older systems only):
```bash
pip install git-tunnel
```

> On Ubuntu 23.04+, Debian 12+, and similar distros, using `pip install` system-wide will likely fail with an `externally-managed-environment` error. Use `pipx` or `uv tool install` instead.

Don't have pipx? Install it first:
```bash
# Ubuntu / Debian
sudo apt install pipx
pipx ensurepath

# macOS
brew install pipx
pipx ensurepath
```

---

## Install (once per machine)

Run the interactive install:
```bash
git-tunnel install
```

This will:
- Ask for a device name (e.g. `MacBook`, `Workstation`, `Server`)
- Set `git config --global user.device`
- Install the `prepare-commit-msg` hook globally
- Point `git config --global core.hooksPath` at the hook

From this point on, every commit you make will automatically get a
`[device:YourDevice]` tag appended to the message — silently, without
you doing anything.

---

## Usage

Inside any git repo:
```bash
# Compact view (messages truncated)
git-tunnel

# Full view (complete commit messages)
git-tunnel --all
```

Not sure what's available? Run:
```bash
git-tunnel --help
```

---

## How it works

`git-tunnel` uses a global `prepare-commit-msg` hook that appends a
`[device:X]` tag to every commit message, where `X` comes from
`git config --global user.device`.

Your `user.name` is never touched — it stays clean for collaboration.
The device tag lives in the commit message body and is stripped from
the display in the tunnel view.

---

## Multiple machines

Set a different device name on each machine:
```bash
# MacBook
git-tunnel install  # enter "MacBook" when prompted

# Workstation
git-tunnel install  # enter "Workstation" when prompted

# Server
git-tunnel install  # enter "Server" when prompted
```

Since the hook is global, it applies to every repo on that machine
automatically.

---

## Zero dependencies

`git-tunnel` uses only the Python standard library and git itself.
No third-party packages required.

---

## License

MIT
