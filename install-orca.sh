#!/usr/bin/env bash
# ============================================================
#  ORCA - full installer for Linux / macOS.
#  Send teammates this ONE file. They run:
#     chmod +x install-orca.sh && ./install-orca.sh
#  Installs git / python / node (via the system package manager),
#  clones the repo, sets up backend + frontend, offers to start.
#  Safe to run again.
# ============================================================
set -euo pipefail

REPO_URL="https://github.com/nilanshpratapanand/ORCA-Marine-Ecosystem-Reasoning-with-Collaborative-Agents.git"
if [ -d "$HOME/Desktop" ]; then
  DEST="$HOME/Desktop/ORCA-Marine-Ecosystem-Reasoning-with-Collaborative-Agents"
else
  DEST="$HOME/ORCA-Marine-Ecosystem-Reasoning-with-Collaborative-Agents"
fi

echo
echo "============================================================"
echo "  ORCA installer"
echo "  target folder: $DEST"
echo "============================================================"
echo

# ---------- prerequisites ----------
missing=0
for c in git python3 node npm; do
  command -v "$c" >/dev/null 2>&1 || { echo "[ .. ] $c not found"; missing=1; }
done

if [ "$missing" = 1 ]; then
  if command -v pacman >/dev/null 2>&1; then
    echo "[deps] Arch detected - installing via pacman"
    sudo pacman -S --needed --noconfirm git python nodejs npm rust
  elif command -v apt-get >/dev/null 2>&1; then
    echo "[deps] Debian/Ubuntu detected - installing via apt"
    sudo apt-get update
    sudo apt-get install -y git python3 python3-venv python3-pip nodejs npm
  elif command -v dnf >/dev/null 2>&1; then
    echo "[deps] Fedora detected - installing via dnf"
    sudo dnf install -y git python3 python3-pip nodejs npm
  elif command -v brew >/dev/null 2>&1; then
    echo "[deps] macOS/Homebrew detected"
    brew install git python node
  else
    echo "[ERROR] Couldn't detect a package manager."
    echo "        Install git, python3 (with the venv module), nodejs and npm"
    echo "        yourself, then run this script again."
    exit 1
  fi
fi

# prefer python 3.12 if it exists, else whatever python3 is
PY=python3
command -v python3.12 >/dev/null 2>&1 && PY=python3.12
echo "[python] using: $($PY --version)"

# ---------- get the repo ----------
echo
if [ -d "$DEST/.git" ] && git -C "$DEST" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[repo] already there - pulling latest"
  git -C "$DEST" pull --ff-only
elif [ -f "$DEST/backend/app/main.py" ]; then
  echo "[ERROR] $DEST has project files but is not a working git checkout."
  echo "        Rename or delete that folder, then run this again."
  exit 1
else
  [ -e "$DEST" ] && { echo "[repo] removing incomplete download..."; rm -rf "$DEST"; }
  echo "[repo] cloning..."
  git clone "$REPO_URL" "$DEST"
fi

if [ ! -f "$DEST/setup.bat" ] && [ ! -f "$DEST/backend/requirements.txt" ]; then
  echo "[ERROR] clone looks incomplete. Delete $DEST and run this again."
  exit 1
fi
cd "$DEST"

# ---------- backend ----------
echo
echo "[backend] setting up virtual environment..."
cd backend
if [ ! -x "venv/bin/python" ]; then
  "$PY" -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if [ ! -f .env ]; then
  cp .env.example .env
  echo "[backend] created backend/.env  ->  add a free GROQ_API_KEY (optional)"
  echo "          https://console.groq.com/keys"
fi
deactivate
cd ..

# ---------- frontend ----------
echo
echo "[frontend] installing npm packages..."
cd frontend
npm install
cd ..

echo
echo "============================================================"
echo "  Setup complete.  Project: $DEST"
echo "============================================================"
echo
read -r -p "Start the app now? [y/N] " ans
case "$ans" in
  [yY]*) exec ./run.sh ;;
  *) echo "Later: cd \"$DEST\" && ./run.sh" ;;
esac
