#!/bin/bash
# start_cgps.sh — robust auto-launch for cgps -s
# Raspberry Pi 5 + VK172 (USB NMEA)
set -euo pipefail

# --- Find the GPS serial device (prefer stable by-id path) ---
find_gps_device() {
  # by-id gives a stable symlink if available
  if [ -d /dev/serial/by-id ]; then
    local byid
    byid=$(ls -1 /dev/serial/by-id 2>/dev/null | grep -Ei 'gps|qstarz|prolific|cp21|ch341|u-blox|vk|g-mouse' || true)
    if [ -n "$byid" ]; then
      echo "/dev/serial/by-id/${byid%%$'\n'*}"
      return 0
    fi
  fi
  # Fallbacks
  for dev in /dev/ttyACM0 /dev/ttyUSB0 /dev/ttyACM1 /dev/ttyUSB1; do
    [ -e "$dev" ] && echo "$dev" && return 0
  done
  return 1
}

echo "Detecting GPS device..."
while ! GPSDEV="$(find_gps_device)"; do
  echo "  GPS not found yet; waiting..."
  sleep 2
done
echo "  Using $GPSDEV"

# --- Restart gpsd cleanly on that device ---
sudo systemctl stop gpsd.socket gpsd >/dev/null 2>&1 || true
sudo pkill -x gpsd >/dev/null 2>&1 || true
sleep 0.5
sudo gpsd -n "$GPSDEV" -F /var/run/gpsd.sock

# --- Wait until gpsd is outputting something useful ---
echo "Waiting for GPS data from gpsd..."
# Wait for either TPV or GGA to appear (timeout ~45s)
if ! timeout 45s bash -c 'gpspipe -w -n 10 2>/dev/null | grep -m1 -E "\"class\":\"TPV\"|GGA" >/dev/null'; then
  echo "No GPS data yet (still OK—cold start can take minutes). Launching viewer anyway."
fi

# --- Launch viewer (GUI if available, else console) ---
if [ -n "${DISPLAY:-}" ] && command -v x-terminal-emulator >/dev/null 2>&1; then
  x-terminal-emulator -T "GPS Monitor" -e bash -lc "cgps -s"
elif [ -n "${DISPLAY:-}" ] && command -v lxterminal >/dev/null 2>&1; then
  lxterminal --title="GPS Monitor" -e "cgps -s"
else
  # No GUI? run in current TTY
  exec cgps -s
fi
