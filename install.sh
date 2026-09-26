#!/bin/bash

set -e

INSTALL_DIR="/opt/photon"
VENV_DIR="$INSTALL_DIR/venv"

# Update apt (if necessary) and install python virtual environment
apt-get update
apt-get install -y python3-venv

# Create python virtual environment
python3 -m venv "$VENV_DIR"

# Install pip within virtual environment
"$VENV_DIR/bin/python" -m pip install --upgrade pip

# Copy application files (will add later)

# Create a convenient command in /usr/local/bin called "photon"
cat > "/usr/local/bin/photon" <<EOF
#!/bin/sh
exec "$VENV_DIR/bin/python" "$INSTALL_DIR/photon.py" "\$@"
EOF

# Make the command executable
chmod 755 "/usr/local/bin/photon"