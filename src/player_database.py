from dataclasses import dataclass
import os

try:
    import psycopg2
except ImportError:
    # Allow the Pygame UI to launch in offline/demo mode without this driver.
    psycopg2 = None

@dataclass
class Player:
    player_id: int
    equipment_id: int
    codename: str
    team: str
    
    def set_codename(self, codename):
        self.codename = codename

# Define connection parameters (override with PHOTON_DB_* environment variables)
connection_params = {
    "dbname":   os.environ.get("PHOTON_DB_NAME", "photon"),
    "user":     os.environ.get("PHOTON_DB_USER", "student"),
    "password": os.environ.get("PHOTON_DB_PASSWORD", "student"),
    "host":     os.environ.get("PHOTON_DB_HOST", "127.0.0.1"),
    "port":     os.environ.get("PHOTON_DB_PORT", "5432"),
}

class playerDatabase:
    # Initialize the database object and connect to PostgreSQL.
    def __init__(self):
        self.conn = None
        self.cursor = None

        if psycopg2 is None:
            print("psycopg2 is not installed; running player-entry UI in offline demo mode.")
            return

        try:
            self.conn = psycopg2.connect(**connection_params)
            self.cursor = self.conn.cursor()

            # Confirm that the application connected to PostgreSQL.
            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()
            print(f"Connected to - {version}")
        except Exception as error:
            print(f"Error connecting to PostgreSQL database: {error}")

    # Disconnect from the database
    def disconnect(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None

    # Find a player by ID and return the player row or None if it is not found
    def get_player(self, player_id):
        self.cursor.execute(
            """
            SELECT id, codename
            FROM public.players
            WHERE id = %s
            """,
            (player_id,),
        )
        return self.cursor.fetchone()

    # Find a player by codename (ignoring case) and return the player row or None
    def get_player_by_codename(self, codename):
        self.cursor.execute(
            """
            SELECT id, codename
            FROM public.players
            WHERE lower(codename) = lower(%s)
            """,
            (codename,),
        )
        return self.cursor.fetchone()

    # Add a new player if the ID is not already in the database
    def add_player(self, player_id, codename):
        if self.get_player(player_id) is not None:
            return False

        self.cursor.execute(
            """
            INSERT INTO public.players (id, codename)
            VALUES (%s, %s)
            """,
            (player_id, codename),
        )
        self.conn.commit()
        return True

    def start_game(self, players):
        """Create a game and an initial score row for each player."""
        with self.conn:
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS public.photon_games (
                    game_id BIGSERIAL PRIMARY KEY,
                    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    finished_at TIMESTAMPTZ,
                    status TEXT NOT NULL DEFAULT 'active'
                )
                """
            )
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS public.photon_game_scores (
                    game_id BIGINT NOT NULL REFERENCES public.photon_games(game_id),
                    player_id INTEGER NOT NULL,
                    codename TEXT NOT NULL,
                    team TEXT NOT NULL,
                    equipment_id INTEGER NOT NULL,
                    score INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (game_id, player_id)
                )
                """
            )
            self.cursor.execute(
                "INSERT INTO public.photon_games DEFAULT VALUES RETURNING game_id"
            )
            game_id = self.cursor.fetchone()[0]
            self.cursor.executemany(
                """
                INSERT INTO public.photon_game_scores
                    (game_id, player_id, codename, team, equipment_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [(game_id, player.player_id, player.codename, player.team, player.equipment_id)
                 for player in players],
            )
        return game_id

    def update_game_score(self, game_id, player_id, score):
        """Persist a player's current score for one game."""
        with self.conn:
            self.cursor.execute(
                """
                UPDATE public.photon_game_scores SET score = %s
                WHERE game_id = %s AND player_id = %s
                """,
                (score, game_id, player_id),
            )
            if self.cursor.rowcount != 1:
                raise ValueError("Player score row not found")

    def finish_game(self, game_id, status):
        """Mark a game completed or cancelled."""
        if status not in ("completed", "cancelled"):
            raise ValueError("Invalid game status")
        with self.conn:
            self.cursor.execute(
                """
                UPDATE public.photon_games
                SET finished_at = CURRENT_TIMESTAMP, status = %s
                WHERE game_id = %s
                """,
                (status, game_id),
            )

    def get_game_scores(self, game_id):
        """Retrieve the saved player scores for a game."""
        self.cursor.execute(
            """
            SELECT player_id, codename, team, equipment_id, score
            FROM public.photon_game_scores
            WHERE game_id = %s
            ORDER BY score DESC, codename
            """,
            (game_id,),
        )
        return self.cursor.fetchall()

    # Print the entire players table
    def print_all_players(self):
        self.cursor.execute(
            "SELECT id, codename FROM public.players ORDER BY id;"
        )
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)
            
    # Clear database
    def clear_players(self): # TESTING ONLY, DO NOT USE FOR ANYTHING FINAL IN THE PROJECT!!!!!!!
        self.cursor.execute("TRUNCATE public.players")
        self.conn.commit()
