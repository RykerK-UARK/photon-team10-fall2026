import psycopg2
from psycopg2 import sql

# Define connection parameters
connection_params = {
    'dbname': 'photon',
    'user': 'student',
    'password': 'student',
    'host': '127.0.0.1',
    'port': '5432'
}

class database:
    # Initialize database object and connect to database
    def __init__(self):
        try:
            self.conn = psycopg2.connect(**connection_params)
            self.cursor = self.conn.cursor()
            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()
            print(f"Connected to - {version}")

            #cursor.execute('''
            #    CREATE TABLE IF NOT EXISTS players (
            #        id SERIAL PRIMARY KEY,
            #        codename VARCHAR(15)
            #    );
            #''')

            self.conn.commit()
        except Exception as error:
            print(f"Error connecting to PostgreSQL database: {error}")

    # Disconnect from the database
    def db_disconnect(self):
    if self.cursor:
        self.cursor.close()
    if self.conn:
        self.conn.close()

    # Add a codename to the corresponding id
    def db_add(self, id, codename):
        # if current players in database is less than 15
            self.cursor.execute('''
                UPDATE players
                SET codename = %s
                WHERE id = %s
            ''', (codename, id))
            self.conn.commit()

    # Print the entire players table
    def db_print_all(self):
        self.cursor.execute("SELECT * FROM players;")
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)