import psycopg.extras

# This works, even though psycopg2.extensions wasn't imported.
psycopg.extensions.extend()
