#!/bin/bash

set -e

# Set directory locations
INSTALL_DIR="/opt/photon"
VENV_DIR="$INSTALL_DIR/venv"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"

# Update apt (if necessary) and install python virtual environment
apt-get update
apt-get install -y python3-venv

# Create the installation directory
mkdir -p "$INSTALL_DIR"

# Create python virtual environment
python3 -m venv "$VENV_DIR"

# Install pip within virtual environment
"$VENV_DIR/bin/python" -m pip install --upgrade pip pygame psycopg2-binary

# Copy application files
cp -r "$SRC_DIR"/countdown_images "$INSTALL_DIR/"
cp -r "$SRC_DIR"/game_sounds      "$INSTALL_DIR/"
cp -r "$SRC_DIR"/helmet_sounds    "$INSTALL_DIR/"
cp -r "$SRC_DIR"/photon_tracks    "$INSTALL_DIR/"
cp "$SRC_DIR"/baseicon.jpg        "$INSTALL_DIR/"
cp "$SRC_DIR"/logo.jpg            "$INSTALL_DIR/"
cp "$SRC_DIR"/main.py             "$INSTALL_DIR/"
cp "$SRC_DIR"/player_database.py  "$INSTALL_DIR/"
cp "$SRC_DIR"/player_entry.py     "$INSTALL_DIR/"
cp "$SRC_DIR"/test_server.py      "$INSTALL_DIR/"

# Create a convenient command in /usr/local/bin called "photon"
cat > "/usr/local/bin/photon" <<EOF
#!/bin/sh
exec "$VENV_DIR/bin/python" "$INSTALL_DIR/main.py" "\$@"
EOF

# Make the command executable
chmod 755 "/usr/local/bin/photon"