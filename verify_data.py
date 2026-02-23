import os
import sys
from dotenv import load_dotenv

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.data_model import DataModel

def verify_supabase_data():
    load_dotenv()
    
    print("Connecting to Supabase...")
    model = DataModel()
    
    if not model.supabase_client:
        print("Error: Could not connect to Supabase.")
        return

    print("Querying 'places' table...")
    try:
        # Fetch all rows from the places table
        response = model.supabase_client.table('places').select("*").execute()
        places = response.data
        
        count = len(places)
        print(f"\n✓ Verification Successful!")
        print(f"✓ Found {count} records in the 'places' table:\n")
        
        for place in places:
            print(f"- [ID: {place.get('id')}] {place.get('name')} ({place.get('city')})")
            
    except Exception as e:
        print(f"Error querying database: {e}")

if __name__ == "__main__":
    verify_supabase_data()