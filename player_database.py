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
