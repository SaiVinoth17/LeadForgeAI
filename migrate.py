import sqlite3
import os

DB_PATH = os.path.join("data", "leadforge.db")

def migrate():
    if not os.path.exists(DB_PATH):
        print("Database not found, nothing to migrate.")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # We will try to add columns one by one. If they exist, sqlite throws OperationalError.
    columns_to_add = [
        ("opportunity_score", "INTEGER DEFAULT 0"),
        ("website_type", "VARCHAR(50)"),
        ("has_professional_email", "VARCHAR(10)"),
        ("has_online_booking", "VARCHAR(10)"),
        ("has_logo", "VARCHAR(10)"),
        ("call_script", "TEXT"),
        ("meeting_points", "TEXT")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE leads ADD COLUMN {col_name} {col_type}")
            print(f"Added column {col_name}")
        except sqlite3.OperationalError:
            pass
            
    # RC1 fields
    try:
        cursor.execute('ALTER TABLE leads ADD COLUMN confidence_score INTEGER DEFAULT 0')
        print("Added confidence_score column.")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute('ALTER TABLE leads ADD COLUMN confidence_reasons TEXT')
        print("Added confidence_reasons column.")
    except sqlite3.OperationalError:
        pass
        
    # Migrate old statuses
    cursor.execute("UPDATE leads SET status='Discovery' WHERE status='New'")
    cursor.execute("UPDATE leads SET status='Qualified' WHERE status='Contacted'")
    cursor.execute("UPDATE leads SET status='Proposal' WHERE status='Proposal Sent'")
    cursor.execute("UPDATE leads SET status='Meeting' WHERE status='Meeting Scheduled'")
    cursor.execute("UPDATE leads SET status='Negotiation' WHERE status='Negotiating'")
    
    # Initialize opportunity_score with lead_score for existing rows
    try:
        cursor.execute("UPDATE leads SET opportunity_score = lead_score WHERE opportunity_score = 0 OR opportunity_score IS NULL")
    except Exception as e:
        print(f"Error updating opportunity_score: {e}")
        
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
