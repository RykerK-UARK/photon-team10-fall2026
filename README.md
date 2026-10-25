# Photon - Team 10 (Fall 2026)

A Pygame laser-tag operator interface. Sprint 3 has player entry, a standalone
30-second pre-game countdown, and a separate play-action screen showing both team rosters.
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
- Click **START GAME** or press **F5** to open the **countdown screen** first.
  After 30 seconds, the play-action screen opens automatically with both team rosters.
- During the countdown, press **ESC** to cancel and go back to player entry.
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

## Modifying the countdown

The countdown lives entirely in `countdown.py` in the `run_countdown(screen, clock)`
function. It uses the existing Pygame display and clock, so a replacement can
change the images, sounds, or animation without altering `player_entry.py` or
`play_action.py`. Keep these three return values in the replacement:

- `"complete"` when the countdown finishes and play action should open.
- `"back"` when the operator cancels and returns to player entry.
- `"quit"` when the window is closed.

The `install.sh` script includes `countdown.py` for Linux installations.
