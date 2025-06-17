#!/bin/bash

# 📁 Path to your repo
cd /mnt/nasdrive/jupyter/EMS_QI_Projects || {
  echo "❌ Failed to enter project directory."
  exit 1
}

# 🗂️ Pull latest changes
echo "🔄 Pulling latest changes from origin/main..."
git pull origin main --rebase

# 💬 Determine commit message
if [ -n "$1" ]; then
    COMMIT_MSG="$1"
else
    COMMIT_MSG="Auto commit on $(date +'%Y-%m-%d %H:%M:%S')"
fi

# 🔍 Check for any local changes
if git status --porcelain | grep . >/dev/null; then
    echo "📦 Changes detected. Committing and pushing..."
    git add .
    git commit -m "$COMMIT_MSG"
    git push origin main
else
    echo "✅ No changes to commit. Working tree clean."
fi
