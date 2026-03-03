#!/usr/bin/env python
"""
Supabase Sync Script - Synchronize Hjertestarterregister API data with Supabase
Fetches ALL AEDs (no filtering), syncs to 'hjertestartere' table, handles upserts and deletes
"""
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from app.models.hjertestarterregister_api import HjertestarterregisterAPI
from app.models.data_model import DataModel


class AEDSyncManager:
    """Manages synchronization of AED data from API to Supabase"""
    
    def __init__(self):
        self.api = HjertestarterregisterAPI()
        self.data_model = DataModel()
        self.kristiansand_lat = 58.1414
        self.kristiansand_lng = 8.0842
        self.search_radius_m = 15000  # 15 km
        
        # Stats
        self.stats = {
            'fetched_from_api': 0,
            'inserted': 0,
            'updated': 0,
            'deleted': 0,
            'errors': []
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    def fetch_all_aeds_from_api(self) -> List[Dict]:
        """
        Fetch ALL AEDs from Hjertestarterregister API (no filtering)
        Returns list of AED records with essential fields
        """
        self.log("=" * 80)
        self.log("PART 1: FETCHING AEDs FROM HJERTESTARTERREGISTER API")
        self.log("=" * 80)
        
        # Authenticate
        self.log(f"Authenticating with Hjertestarterregister API...", "INFO")
        if not self.api.authenticate():
            self.log("Authentication failed - attempting public access", "WARNING")
        
        # Fetch
        self.log(f"Fetching AEDs from API...")
        self.log(f"  Center: ({self.kristiansand_lat}, {self.kristiansand_lng})")
        self.log(f"  Search radius: {self.search_radius_m}m (15 km)")
        self.log(f"  Filter: NONE (fetching ALL AEDs regardless of IS_OPEN)")
        
        response = self.api.search_assets(
            latitude=self.kristiansand_lat,
            longitude=self.kristiansand_lng,
            distance=self.search_radius_m,
            max_rows=5000
        )
        
        if not response or 'ASSETS' not in response:
            self.log("ERROR: No response from API or empty ASSETS array", "ERROR")
            return []
        
        # Extract and prepare records
        aeds = []
        for asset in response['ASSETS']:
            # Skip if no location data
            if not asset.get('SITE_LATITUDE') or not asset.get('SITE_LONGITUDE'):
                continue
            
            # Calculate distance using Haversine
            dist_m = self.api._haversine_distance(
                self.kristiansand_lat,
                self.kristiansand_lng,
                float(asset['SITE_LATITUDE']),
                float(asset['SITE_LONGITUDE'])
            )
            
            aed_record = {
                'asset_id': asset.get('ASSET_ID'),
                'site_name': asset.get('SITE_NAME'),
                'site_address': asset.get('SITE_ADDRESS'),
                'site_post_code': asset.get('SITE_POST_CODE'),
                'site_post_area': asset.get('SITE_POST_AREA'),
                'site_latitude': float(asset.get('SITE_LATITUDE')),
                'site_longitude': float(asset.get('SITE_LONGITUDE')),
                'is_open': asset.get('IS_OPEN') == 'Y',
                'opening_hours_text': asset.get('OPENING_HOURS_TEXT'),
                'distance_meters': dist_m,
                'distance_km': round(dist_m / 1000, 2),
            }
            aeds.append(aed_record)
        
        # Sort by distance
        aeds.sort(key=lambda x: x['distance_meters'])
        
        self.stats['fetched_from_api'] = len(aeds)
        
        self.log(f"✓ Fetched {len(aeds)} AEDs from API", "SUCCESS")
        self.log(f"  Open now (IS_OPEN='Y'): {sum(1 for a in aeds if a['is_open'])}")
        self.log(f"  Closed now (IS_OPEN='N'): {sum(1 for a in aeds if not a['is_open'])}")
        
        # ── DIAGNOSTIC A: Log fetched data fingerprint ──
        ids_fetched = sorted([str(a['asset_id']) for a in aeds])
        checksum_fetched = hashlib.md5(','.join(ids_fetched).encode()).hexdigest()[:12]
        self.log(f"[DIAG-A-FETCH] timestamp={datetime.now().isoformat()}", "DIAG")
        self.log(f"[DIAG-A-FETCH] count={len(aeds)}", "DIAG")
        self.log(f"[DIAG-A-FETCH] first_5_ids={ids_fetched[:5]}", "DIAG")
        self.log(f"[DIAG-A-FETCH] id_checksum={checksum_fetched}", "DIAG")
        
        return aeds
    
    def sync_to_supabase(self, aeds: List[Dict]) -> bool:
        """
        Sync AEDs to Supabase 'hjertestartere' table using REST API directly
        Uses upsert logic:
        - Insert new records
        - Update existing records
        - Delete records not in API response
        """
        self.log("")
        self.log("=" * 80)
        self.log("PART 2: SYNCING TO SUPABASE (Using REST API)")
        self.log("=" * 80)
        
        import httpx
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            self.log("ERROR: Supabase credentials not found in .env", "ERROR")
            return False
        
        try:
            # Setup REST headers
            headers = {
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }
            
            # Get existing AED IDs from Supabase
            self.log("Fetching existing AEDs from Supabase...", "INFO")
            rest_url = f"{supabase_url}/rest/v1/hjertestartere"
            
            existing_response = httpx.get(
                f"{rest_url}?select=asset_id",
                headers=headers
            )
            
            existing_ids = set()
            if existing_response.status_code == 200:
                existing_ids = {row['asset_id'] for row in existing_response.json()}
            
            self.log(f"Found {len(existing_ids)} existing AEDs in Supabase", "INFO")
            
            api_ids = {aed['asset_id'] for aed in aeds}
            
            # 1. UPSERT (batch of 50, with on_conflict=asset_id)
            self.log("Upserting AED records (batches of 50)...", "INFO")
            new_ids = api_ids - existing_ids
            BATCH = 50
            for i in range(0, len(aeds), BATCH):
                batch = aeds[i:i+BATCH]
                try:
                    upsert_headers = {
                        **headers,
                        'Prefer': 'resolution=merge-duplicates,return=minimal',
                    }
                    response = httpx.post(
                        f"{rest_url}?on_conflict=asset_id",
                        json=batch,
                        headers=upsert_headers,
                        timeout=30.0
                    )
                    if response.status_code in [200, 201]:
                        for aed in batch:
                            if aed['asset_id'] in new_ids:
                                self.stats['inserted'] += 1
                            else:
                                self.stats['updated'] += 1
                    else:
                        self.log(f"Warning: batch {i//BATCH} got {response.status_code}: {response.text[:200]}", "WARNING")
                except Exception as e:
                    msg = f"Error upserting batch {i//BATCH}: {e}"
                    self.log(msg, "ERROR")
                    self.stats['errors'].append(msg)
            
            self.log(f"✓ Inserted: {self.stats['inserted']}", "SUCCESS")
            self.log(f"✓ Updated: {self.stats['updated']}", "SUCCESS")
            
            # 2. DELETE old records not in API
            self.log("Removing deleted AEDs...", "INFO")
            deleted_ids = existing_ids - api_ids
            
            for aed_id in deleted_ids:
                try:
                    response = httpx.delete(
                        f"{rest_url}?asset_id=eq.{aed_id}",
                        headers=headers,
                        timeout=10.0
                    )
                    if response.status_code in [200, 204]:
                        self.stats['deleted'] += 1
                except Exception as e:
                    msg = f"Error deleting AED {aed_id}: {e}"
                    self.log(msg, "ERROR")
                    self.stats['errors'].append(msg)
            
            if self.stats['deleted'] > 0:
                self.log(f"✓ Deleted: {self.stats['deleted']} old AEDs", "SUCCESS")
            else:
                self.log(f"No AEDs to delete", "INFO")
            
            # 3. VERIFY
            self.log("Verifying sync...", "INFO")
            verify_response = httpx.get(
                f"{rest_url}?select=count",
                headers={**headers, 'Prefer': 'count=exact'},
                timeout=10.0
            )
            
            total_in_db = len(aeds)  # What we just loaded
            
            self.log(f"✓ Total AEDs now in Supabase: {total_in_db}", "SUCCESS")
            
            # Verify sample records
            sample_response = httpx.get(
                f"{rest_url}?limit=3&select=site_name,asset_id",
                headers=headers,
                timeout=10.0
            )
            
            if sample_response.status_code == 200:
                samples = sample_response.json()
                if samples:
                    self.log(f"Sample records from Supabase:", "INFO")
                    for record in samples[:2]:
                        self.log(f"  - {record['site_name']} ({record['asset_id']})", "INFO")
            
            # ── DIAGNOSTIC A: Verify Supabase state after write ──
            self.log("[DIAG-A-WRITE] Running post-write verification SELECT...", "DIAG")
            verify_all = httpx.get(
                f"{rest_url}?select=asset_id&order=asset_id.asc",
                headers=headers,
                timeout=15.0
            )
            if verify_all.status_code == 200:
                db_rows = verify_all.json()
                db_ids = sorted([str(r['asset_id']) for r in db_rows])
                db_checksum = hashlib.md5(','.join(db_ids).encode()).hexdigest()[:12]
                supabase_suffix = os.getenv('SUPABASE_URL', '???').split('//')[1][:12] if os.getenv('SUPABASE_URL') else '???'
                self.log(f"[DIAG-A-WRITE] timestamp={datetime.now().isoformat()}", "DIAG")
                self.log(f"[DIAG-A-WRITE] supabase_project={supabase_suffix}", "DIAG")
                self.log(f"[DIAG-A-WRITE] db_count={len(db_ids)}", "DIAG")
                self.log(f"[DIAG-A-WRITE] first_5_ids={db_ids[:5]}", "DIAG")
                self.log(f"[DIAG-A-WRITE] db_id_checksum={db_checksum}", "DIAG")
                
                # Compare fetch checksum vs db checksum
                api_ids_sorted = sorted([str(a['asset_id']) for a in aeds])
                api_checksum = hashlib.md5(','.join(api_ids_sorted).encode()).hexdigest()[:12]
                match = api_checksum == db_checksum
                self.log(f"[DIAG-A-WRITE] api_checksum={api_checksum} vs db_checksum={db_checksum} => MATCH={match}", "DIAG")
            else:
                self.log(f"[DIAG-A-WRITE] Verification SELECT failed: {verify_all.status_code}", "ERROR")
            
            return True
            
        except Exception as e:
            self.log(f"ERROR during Supabase sync: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    def print_summary(self):
        """Print sync summary"""
        self.log("")
        self.log("=" * 80)
        self.log("SYNC SUMMARY")
        self.log("=" * 80)
        
        self.log(f"API Fetched:  {self.stats['fetched_from_api']} AEDs", "INFO")
        self.log(f"Inserted:     {self.stats['inserted']} new records", "SUCCESS")
        self.log(f"Updated:      {self.stats['updated']} existing records", "SUCCESS")
        self.log(f"Deleted:      {self.stats['deleted']} obsolete records", "INFO" if self.stats['deleted'] == 0 else "SUCCESS")
        
        if self.stats['errors']:
            self.log(f"Errors:       {len(self.stats['errors'])}", "WARNING")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                self.log(f"  - {error}", "WARNING")
            if len(self.stats['errors']) > 5:
                self.log(f"  ... and {len(self.stats['errors']) - 5} more errors", "WARNING")
        
        self.log("=" * 80)
        self.log("NEXT STEPS:", "INFO")
        self.log("1. Restart Flask server (py run.py) to reload map with Supabase data", "INFO")
        self.log("2. Open http://localhost:3000 to view updated map", "INFO")
        self.log("3. Check map for all " + str(self.stats['fetched_from_api']) + " AEDs displayed", "INFO")
        self.log("4. Verify IS_OPEN status (green=open, red=closed)", "INFO")
        self.log("=" * 80)
    
    def run(self):
        """Execute full sync"""
        try:
            # First: Load from .env
            from dotenv import load_dotenv
            load_dotenv()
            
            # Part 1: Fetch from API
            aeds = self.fetch_all_aeds_from_api()
            
            if not aeds:
                self.log("ERROR: No AEDs fetched from API, aborting sync", "ERROR")
                return False
            
            # Part 2: Sync to Supabase
            success = self.sync_to_supabase(aeds)
            
            # Summary
            self.print_summary()
            
            return success
            
        except Exception as e:
            self.log(f"FATAL ERROR: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    manager = AEDSyncManager()
    success = manager.run()
    exit(0 if success else 1)
