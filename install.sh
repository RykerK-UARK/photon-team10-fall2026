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
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r "$SRC_DIR/requirements.txt"

# Copy application files
cp -r "$SRC_DIR"/assets              "$INSTALL_DIR/"
cp -r "$SRC_DIR"/src                 "$INSTALL_DIR/"

# Create a convenient command in /usr/local/bin called "photon"
cat > "/usr/local/bin/photon" <<EOF
#!/bin/sh
exec "$VENV_DIR/bin/python" "$INSTALL_DIR/src/main.py" "\$@"
EOF

# Make the command executable
chmod 755 "/usr/local/bin/photon"