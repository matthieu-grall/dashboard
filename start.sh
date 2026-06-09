#!/bin/bash
# =============================================================================
# start.sh
# Main launcher — called by dashboard.desktop on double-click.
#
# What it does:
#   1. Validates the environment (venv, update.py, data/)
#   2. Runs update.py to fetch fresh data
#   3. Opens the browser in kiosk (full-screen, no chrome) mode
#   4. Loops every 15 minutes to refresh data and reload the page
#
# All output is written to start.log in the project directory.
# =============================================================================

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

LOG="$DIR/start.log"
INTERVAL=900   # refresh interval in seconds (15 minutes)

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG"
}

# Clear the log on each fresh start
> "$LOG"
log "=== Starting dashboard ==="
log "Project directory: $DIR"

# -----------------------------------------------------------------------------
# Sanity checks
# -----------------------------------------------------------------------------

if [ ! -f "$DIR/venv/bin/python" ]; then
    log "ERROR: virtual environment not found — run install.sh first"
    exit 1
fi
log "venv OK"

if [ ! -f "$DIR/update.py" ]; then
    log "ERROR: update.py not found"
    exit 1
fi
log "update.py found"

# -----------------------------------------------------------------------------
# Initial data fetch
# -----------------------------------------------------------------------------

log "Running update.py..."
venv/bin/python update.py >> "$LOG" 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    log "ERROR: update.py failed (exit code $EXIT_CODE)"
else
    log "update.py OK"
fi

if [ ! -f "$DIR/data/dashboard.json" ]; then
    log "ERROR: data/dashboard.json missing after update.py"
else
    log "dashboard.json ready"
fi

# -----------------------------------------------------------------------------
# Browser detection — prefer Firefox, fall back to Chromium variants
# -----------------------------------------------------------------------------

if command -v firefox &> /dev/null; then
    BROWSER="firefox"
elif command -v chromium-browser &> /dev/null; then
    BROWSER="chromium-browser"
elif command -v chromium &> /dev/null; then
    BROWSER="chromium"
fi

log "Browser detected: ${BROWSER:-none}"

# -----------------------------------------------------------------------------
# Launch browser in kiosk mode
#
# Firefox: uses a dedicated profile stored in .firefox-profile/ to set two
# preferences that allow fetch() across local file:// origins — otherwise the
# browser silently blocks dashboard.json from loading.
#
# Chromium: equivalent behaviour achieved via command-line flags.
# --disable-gpu and related flags prevent EGL driver errors on Raspberry Pi.
# -----------------------------------------------------------------------------

if [ -n "$BROWSER" ]; then
    if [ "$BROWSER" = "firefox" ]; then
        log "Launching Firefox in kiosk mode..."
        PROFILE_DIR="$DIR/.firefox-profile"
        mkdir -p "$PROFILE_DIR"
        # Allow fetch() between local file:// URLs (blocked by default in Firefox)
        cat > "$PROFILE_DIR/user.js" << 'PREFS'
user_pref("security.fileuri.strict_origin_policy", false);
user_pref("privacy.file_unique_origin", false);
PREFS
        firefox --kiosk --profile "$PROFILE_DIR" "file://$DIR/index.html" >> "$LOG" 2>&1 &
    else
        log "Launching Chromium in kiosk mode..."
        $BROWSER \
            --kiosk \
            --noerrdialogs \
            --disable-infobars \
            --disable-session-crashed-bubble \
            --disable-gpu \                   # prevents EGL driver errors on RPi
            --disable-software-rasterizer \
            --disable-dev-shm-usage \
            --allow-file-access-from-files \  # allow fetch() on file:// pages
            --disable-web-security \
            "file://$DIR/index.html" >> "$LOG" 2>&1 &
    fi
    BROWSER_PID=$!
    log "Browser PID: $BROWSER_PID"
else
    log "ERROR: no supported browser found (install firefox or chromium)"
    exit 1
fi

# -----------------------------------------------------------------------------
# Refresh loop — update data and reload the page every INTERVAL seconds
# xdotool sends F5 to the active window; install it with: sudo apt install xdotool
# -----------------------------------------------------------------------------

log "Refresh loop started (every ${INTERVAL}s)"
while true; do
    sleep $INTERVAL
    log "Refreshing data..."
    venv/bin/python update.py >> "$LOG" 2>&1
    if command -v xdotool &> /dev/null; then
        xdotool key F5
        log "Page reloaded (xdotool F5)"
    fi
done