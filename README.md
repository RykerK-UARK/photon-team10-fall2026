# Photon - Team 10 (Fall 2026)

A Pygame laser-tag operator interface. Sprint 3 has player entry, a standalone
30-second pre-game countdown, and a separate play-action screen showing both team rosters.
Gameplay events/scoring are not implemented yet.

## Run locally (macOS / Windows / Linux)

1. Open this project folder in VS Code or a terminal.
2. Install the Python dependencies:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

   On Windows, use `py -m pip ...` if `python3` is not available.
3. Start the application:

   ```bash
   python3 src/main.py
   ```

   On Windows, use `py src/main.py` as appropriate.

The PostgreSQL driver is optional for a local UI demonstration; without a
working PostgreSQL connection, players exist only in the running program.
A database connection is required to save players to PostgreSQL.

The connection defaults to `photon` / `student` / `student` on `127.0.0.1:5432`.
To use different settings, set `PHOTON_DB_NAME`, `PHOTON_DB_USER`,
`PHOTON_DB_PASSWORD`, `PHOTON_DB_HOST`, or `PHOTON_DB_PORT` before starting.

## Controls

- Enter a numeric **Equipment ID** (hardware ID), codename, and choose a team.
- Click **ADD PLAYER** to add the player to the roster.
- Click **START GAME** or press **F5** to open the **countdown screen** first.
  After 30 seconds, the play-action screen opens automatically with both team rosters.
- During the countdown, press **ESC** to cancel and go back to player entry, or
  **SPACE** to skip it.
- On the play-action screen, click **BACK TO ENTRY** or press **ESC** to return.
- On the player-entry screen, click **CLEAR ALL PLAYERS** or press **F12** to
  clear the on-screen roster. This does not delete anything from the PostgreSQL
  players table.

## Linux installation script

On a Debian/Ubuntu system, from the project directory, run:

```bash
sudo bash install.sh
photon
```

The Linux install script uses `apt-get` and is not intended for macOS. On macOS
or Windows, use the local Python instructions above instead.

## Modifying the countdown

The default countdown is `GameStartCountdown` in `src/game_start_countdown.py`,
which shows the images in `assets/countdown_images/`. A text-only alternative,
`GameCountdown` in `src/countdown.py`, can be swapped in by changing the import
and the `register("countdown", ...)` line in `src/main.py`.

A countdown is a `Screen` that returns `"play_action"` when it finishes and
`"player_entry"` when cancelled. The `install.sh` script copies the whole `src`
and `assets` folders.
