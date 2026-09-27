import psycopg2
from psycopg2 import sql

# Define connection parameters 
connection_params = {
    "dbname":   "photon",
    "user":     "student",
    "password": "student",
    "host":     "127.0.0.1",
    "port":     "5432",
}


class playerDatabase:
    # Initialize the database object and connect to PostgreSQL.
    def __init__(self):
        self.conn = None
        self.cursor = None

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
    def clear_players(self): # TESTING ONLY
        self.cursor.execute("TRUNCATE public.players")
        self.conn.commit()

	# Determines the id for a new player based on current state of database 
    def get_new_player_id(self, team):
        # Get modifier to help differentiate teams
        team_modifier = 0 if team=="Red" else 1
        
        # Iterate over rows
        n_players_on_team = 0
        self.cursor.execute(
            "SELECT id FROM public.players ORDER BY id;"
        )
        rows = self.cursor.fetchall()
        for row in rows:
            if row == None:
                continue
            if (row[0] + team_modifier) % 2 == 0:
                n_players_on_team += 1
                
        # N of players on team is equal to player ID with respect to that team
        return n_players_on_team * 2 + team_modifier
		
