# Photon - Team 10 (Fall 2026)

A Pygame laser-tag operator interface. Sprint 3 has player entry, a 30-second
pre-game countdown, and a play-action screen showing both team rosters.
Gameplay events/scoring are not implemented yet.

## Run locally (macOS / Windows / Linux)

1. Open this project folder in VS Code or a terminal.
2. Install the Python dependencies:

   ```bash
   python3 -m pip install pygame psycopg2-binary
   ```

   On Windows, use `py -m pip ...` if `python3` is not available.
3. Start the application:

   ```bash
   python3 main.py
   ```

   On Windows, use `py main.py` as appropriate.

The PostgreSQL driver is optional for a local UI demonstration; without a
working PostgreSQL connection, players exist only in the running program.
A database connection is required to save players to PostgreSQL.

## Controls

- Enter a numeric **Equipment ID** (hardware ID), codename, and choose a team.
- Click **ADD PLAYER** to add the player to the roster.
- Click **START GAME** or press **F5** to open the play-action screen and start
  the **30-second countdown**. Team rosters remain visible while it counts down.
- On the play-action screen, click **BACK TO ENTRY** or press **ESC** to return.
- On the player-entry screen, click **CLEAR ALL PLAYERS** or press **F12** to
  clear player entries. When connected, this also clears the PostgreSQL players
  table. Clearing is never automatic on exit.

## Linux installation script

On a Debian/Ubuntu system, from the project directory, run:

```bash
sudo bash install.sh
photon
```

The Linux install script uses `apt-get` and is not intended for macOS. On macOS
or Windows, use the local Python instructions above instead.
