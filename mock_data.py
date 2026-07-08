import sqlite3
import datetime
import random

def populate_mock_data():
    conn = sqlite3.connect('growthos.db')
    c = conn.cursor()
    
    # Generate past 30 days
    base_date = datetime.date.today() - datetime.timedelta(days=30)
    
    for i in range(30):
        current_date = base_date + datetime.timedelta(days=i)
        
        # Simulate realistic correlation: less sleep = less study & exercise
        sleep = round(random.uniform(4.0, 9.0), 1)
        
        if sleep < 6.0:
            study = round(random.uniform(0.0, 3.0), 1)
            exercise = False
        else:
            study = round(random.uniform(2.0, 8.0), 1)
            exercise = random.choice([True, False])
            
        reading = random.choice([True, False])
        coding = True if study > 4.0 else False
        
        c.execute('''
            INSERT INTO daily_logs (date, study_hours, sleep_hours, exercise, reading, coding_practice)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                study_hours=excluded.study_hours,
                sleep_hours=excluded.sleep_hours,
                exercise=excluded.exercise,
                reading=excluded.reading,
                coding_practice=excluded.coding_practice
        ''', (str(current_date), study, sleep, exercise, reading, coding))
        
    conn.commit()
    conn.close()
    print("Mock data generated successfully!")

if __name__ == "__main__":
    populate_mock_data()
