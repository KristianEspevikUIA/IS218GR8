#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from supabase import create_client

# Load from specific path
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_ANON_KEY')

print("Connecting to Supabase...")
print(f"URL: {url}\n")

try:
    client = create_client(url, key)
    print("✓ Successfully connected to Supabase!")
    
    # Try to query locations table
    try:
        response = client.table('locations').select('*').limit(1).execute()
        print("✓ 'locations' table exists!")
        print(f"  Current data: {len(response.data)} records")
    except Exception as e:
        print(f"✗ 'locations' table error: {str(e)[:150]}")
        print("\n========== ACTION NEEDED ==========")
        print("You must create the 'locations' table in Supabase:")
        print("https://app.supabase.com -> SQL Editor")
        print("""
CREATE TABLE locations (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR NOT NULL,
  latitude FLOAT NOT NULL,
  longitude FLOAT NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
        """)
except Exception as e:
    print(f"✗ Connection error: {e}")
