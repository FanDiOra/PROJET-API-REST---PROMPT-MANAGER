import psycopg2
from faker import Faker
import random

# Créer une instance de Faker
fake = Faker()

# Configuration de la connexion à PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="projet_api_rest_bd",
    user="fatee",
    password="fatee26ODC"
)

# Créer un curseur
cur = conn.cursor()

# Fonction pour insérer des données factices dans la table "group"
def insert_groups(num_records):
    for _ in range(num_records):
        name = fake.company()
        cur.execute("""
            INSERT INTO "group" (name)
            VALUES (%s)
        """, (name,))
    conn.commit()

# Fonction pour insérer des données factices dans la table "user"
def insert_users(num_records):
    cur.execute('SELECT groupID FROM "group"')
    group_ids = [row[0] for row in cur.fetchall()]

    for _ in range(num_records):
        firstname = fake.first_name()
        lastname = fake.last_name()
        login = fake.user_name()
        password = fake.password()
        role = fake.random_element(elements=('admin', 'user'))
        groupID = random.choice(group_ids) if group_ids else None
        
        cur.execute("""
            INSERT INTO "user" (firstname, lastname, login, password, role, groupID)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (firstname, lastname, login, password, role, groupID))
    conn.commit()

# Fonction pour insérer des données factices dans la table "prompt"
def insert_prompts(num_records):
    cur.execute('SELECT userID FROM "user"')
    user_ids = [row[0] for row in cur.fetchall()]

    for _ in range(num_records):
        content = fake.text()
        status = fake.random_element(elements=('on hold', 'activated', 'to review', 'reminder', 'to delete'))
        price = fake.random_number(digits=4)
        creation_date = fake.date_time_this_year()
        edit_date = fake.date_time_this_year()
        user_id = random.choice(user_ids) if user_ids else None
        
        cur.execute("""
            INSERT INTO "prompt" (content, status, price, creation_date, edit_date, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (content, status, price, creation_date, edit_date, user_id))
    conn.commit()

# Fonction pour insérer des données factices dans la table "vote"
def insert_votes(num_records):
    cur.execute('SELECT userID FROM "user"')
    user_ids = [row[0] for row in cur.fetchall()]

    cur.execute('SELECT promptID FROM "prompt"')
    prompt_ids = [row[0] for row in cur.fetchall()]

    for _ in range(num_records):
        vote_value = fake.random_int(min=-10, max=10)
        user_id = random.choice(user_ids) if user_ids else None
        prompt_id = random.choice(prompt_ids) if prompt_ids else None

        cur.execute("""
            INSERT INTO "vote" (vote_value, user_id, prompt_id)
            VALUES (%s, %s, %s)
        """, (vote_value, user_id, prompt_id))
    conn.commit()

# Fonction pour insérer des données factices dans la table "note"
def insert_notes(num_records):
    cur.execute('SELECT userID FROM "user"')
    user_ids = [row[0] for row in cur.fetchall()]

    cur.execute('SELECT promptID FROM "prompt"')
    prompt_ids = [row[0] for row in cur.fetchall()]

    for _ in range(num_records):
        note_value = fake.random_number(digits=2)
        user_id = random.choice(user_ids) if user_ids else None
        prompt_id = random.choice(prompt_ids) if prompt_ids else None

        cur.execute("""
            INSERT INTO "note" (note_value, user_id, prompt_id)
            VALUES (%s, %s, %s)
        """, (note_value, user_id, prompt_id))
    conn.commit()

# Nombre de lignes à insérer
num_groups = 10
num_users = 75
num_prompts = 100
num_votes = 200
num_notes = 200

# Insertion des données factices
insert_groups(num_groups)
insert_users(num_users)
insert_prompts(num_prompts)
insert_votes(num_votes)
insert_notes(num_notes)

# Fermer le curseur et la connexion
cur.close()
conn.close()

print("Les données factices ont été insérées dans la base de données.")
