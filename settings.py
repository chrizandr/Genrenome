"""Settings file."""
import os

# Heroku run on Postgres
url = os.environ["DATABASE_URL"]
DB_URL = "postgres+psycopg2" + "".join(url.split("postgres")[1::])

# Local running on SQLite
# DB_URL = 'sqlite:///database.db'
Key = "sgjngfdfg//23/=+342][234097824-1<><123><!@#$#%^]"
