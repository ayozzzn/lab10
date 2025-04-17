import psycopg2
import csv
from tabulate import tabulate

conn = psycopg2.connect(
    host = 'localhost',
    dbname = 'phonebook',
    user = 'aio',
    password = '',
    port = 5432
)

cur = conn.cursor()

cur.execute('''
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            surname VARCHAR(255) NOT NULL,
            phone VARCHAR(255) NOT NULL
        );
''')
conn.commit()

check = True
start = True
back = False

while check :
    if start or back :
        start = False
        print('''
            phonebook menu:
              1. 'i' - Insert data (csv file or console)
              2. 'u' - Update data
              3. 'q' - Query data
              4. 'd' - Delete data
              5. 's' - Show all data
              6. 'c' - Clear data
              7. 'f' - Exit program
              ''')
        
    command = input("Enter command: ").lower()

    if command == "i" :
        choice = input("csv or manual input ('csv' / 'con'): ").lower()
        if choice == "con" :
            name  = input("First name: ")
            surname = input("Last name: ")
            phone = input("Phone number: ")
            cur.execute("INSERT INTO phonebook (name, surname, phone) VALUES (%s, %s, %s)", (name, surname, phone))
            conn.commit()
            print("Data inserted.")
        elif choice == "csv" :
            filepath = input("Enter path to csv file: ")
            with open(filepath, 'r') as f :
                reader = csv.reader(f)
                next(reader)
                for row in reader :
                    if len(row) == 3 :
                        cur.execute("INSERT INTO phonebook (name, surname, phone) VALUES (%s, %s, %s)", (row[0], row[1], row[2]))
            conn.commit()
            print("Data inserted.")
        back = input("Type 'back' ro return to menu: ").lower() == "back"
    
    elif command == "u" :
        column = input("which column to update? (name / surname / phone): ").lower()
        if column == "name" :
            old = input("Current name: ")
            new = input("New name: ")
            cur.execute("UPDATE phonebook SET name = %s WHERE name = %s", (new, old))
        elif column == "surname" :
            old = input("Current surname: ")
            new = input("New surname: ")
            cur.execute("UPDATE phonebook SET surname = %s WHERE surname = %s", (new, old))
        elif column == "phone" :
            old = "Current phone number: "
            new = "New phone number: "
            cur.execute("UPDATE phonebook SET phone = %s WHERE phone = %s", (new, old))
        conn.commit()
        print("Data updated.")
        back = input("Type 'back' to return to menu: ").lower() == "back"
    
    elif command == "q" :
        column = input("Which field to search by? (id / name / surname / phone): ").lower()
        value = input("Search value: ")
        if column == "id" :
            cur.execute(f"SELECT * FROM phonebook WHERE user_id = %s", (value,))
        else :
            cur.execute(f"SELECT * FROM phonebook WHERE {column} ILIKE %s", (f"%{value}%",))
        rows = cur.fetchall()
        print(tabulate(rows, headers=["ID", "First name", "Last name", "Phone"], tablefmt='fancy_grid'))
        back = input("Type 'back' to return to menu: ").lower() == "back"

    elif command == "d" :
        name = input("Enter first name: ")
        surname = input("Enter last name: ")
        cur.execute("DELETE FROM phonebook WHERE name = %s AND surname = %s", (name, surname))
        conn.commit()
        print("Contact deleted.")
        back = input("Type 'back' to return to menu: ").lower() == "back"
    
    elif command == "s" :
        cur.execute("SELECT * FROM phonebook;")
        rows = cur.fetchall()
        print(tabulate(rows, headers=["ID", "First name", "Last name", "Phone"], tablefmt='fancy_grid'))
        back = input("Type 'back' to return to menu: ").lower() == "back"

    elif command == "c" :
        confirm = input("Are you sure you want to delete all data? (yes / no): ").lower()
        if confirm == "yes":
            cur.execute("DELETE FROM phonebook;")
            cur.execute("ALTER SEQUENCE phonebook_user_id_seq RESTART WITH 1;")
            conn.commit()
            print("All records deleted.")
        else :
            print("Operaion canceled.")
        back = input("Type 'back' to return to menu: ").lower() == "back"

    elif command == "f" :
        print("Exciting program. Bye!")
        check = False

conn.commit()
cur.close()
conn.close()