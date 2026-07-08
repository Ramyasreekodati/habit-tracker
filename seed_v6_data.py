import sqlite3
import datetime
import random

def seed_db():
    conn = sqlite3.connect('growthos.db')
    c = conn.cursor()
    
    print("Initializing tables...")
    c.execute('''CREATE TABLE IF NOT EXISTS engine_health (date TEXT UNIQUE, sleep REAL, water INT, walk INT, exercise INT, meditation INT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS engine_career (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, category TEXT, description TEXT, resume_impact TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS engine_learning_debt (id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, status TEXT)''')
    
    print("Clearing old data...")
    c.execute("DELETE FROM engine_health")
    c.execute("DELETE FROM engine_career")
    
    print("Generating 30 days of Health data...")
    today = datetime.date.today()
    for i in range(30):
        date = today - datetime.timedelta(days=i)
        # Creating a realistic sleep pattern that dips occasionally
        sleep = round(random.uniform(6.0, 8.5), 1)
        if i % 7 == 0: sleep = round(random.uniform(4.5, 6.0), 1) # Occasional bad night
        water = random.randint(5, 10)
        walk = random.choice([0, 30, 45, 60])
        c.execute("INSERT INTO engine_health (date, sleep, water, walk, exercise, meditation) VALUES (?,?,?,?,0,0)", 
                  (str(date), sleep, water, walk))
                  
    print("Generating Career Output data...")
    categories = ["Git Commit", "Project Feature", "SQL Problem", "Application"]
    for i in range(55): # 55 outputs over 30 days
        date = today - datetime.timedelta(days=random.randint(0, 30))
        cat = random.choice(categories)
        if cat == "Git Commit":
            desc = "Refactored API endpoint"
            impact = "Improved backend efficiency and code maintainability."
        elif cat == "Project Feature":
            desc = "Implemented RAG retrieval pipeline"
            impact = "Built vector search capabilities using LangChain."
        elif cat == "SQL Problem":
            desc = "Solved LeetCode Hard"
            impact = "Demonstrated advanced query optimization."
        else:
            desc = "Applied for AI Engineer role"
            impact = "Targeted startup application."
            
        c.execute("INSERT INTO engine_career (date, category, description, resume_impact) VALUES (?,?,?,?)", 
                  (str(date), cat, desc, impact))

    conn.commit()
    conn.close()
    print("Successfully seeded GrowthOS with realistic 30-day data!")

if __name__ == "__main__":
    seed_db()
