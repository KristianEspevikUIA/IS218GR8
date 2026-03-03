#!/usr/bin/env python
"""
Demonstration script for Available AEDs feature
Shows how to use the API and filter open AEDs
"""
import sys
import json
from app.models.data_model import DataModel


def print_header(title):
    """Print formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_aed(aed, index):
    """Print formatted AED information"""
    print(f"\n{index}. {aed['site_name']}")
    print(f"   Distance: {aed['distance_km']} km ({aed['distance_meters']:.0f}m)")
    print(f"   Address: {aed['site_address']}, {aed['site_post_code']} {aed['site_post_area']}")
    if aed.get('opening_hours_text'):
        print(f"   Hours: {aed['opening_hours_text']}")
    if aed.get('site_description'):
        print(f"   Description: {aed['site_description']}")
    if aed.get('site_access_info'):
        print(f"   Access: {aed['site_access_info']}")
    print(f"   Coordinates: ({aed['site_latitude']}, {aed['site_longitude']})")
    if aed.get('serial_number'):
        print(f"   Serial: {aed['serial_number']}")


def demo_kristiansand():
    """Demo 1: Get available AEDs in Kristiansand (default)"""
    print_header("Demo 1: Available AEDs in Kristiansand (15 km radius)")
    
    data_model = DataModel()
    aeds = data_model.get_available_aeds()
    
    print(f"\n✓ Found {len(aeds)} available AEDs\n")
    
    if aeds:
        for i, aed in enumerate(aeds, 1):
            print_aed(aed, i)
    else:
        print("⚠ No available AEDs found in this radius")
    
    return aeds


def demo_custom_radius():
    """Demo 2: Search with custom radius (5 km around Kristiansand)"""
    print_header("Demo 2: Available AEDs within 5 km (Kristiansand)")
    
    data_model = DataModel()
    aeds = data_model.get_available_aeds(
        latitude=58.1414,
        longitude=8.0842,
        distance=5000  # 5 km
    )
    
    print(f"\n✓ Found {len(aeds)} available AEDs within 5 km\n")
    
    if aeds:
        for i, aed in enumerate(aeds, 1):
            print_aed(aed, i)
    else:
        print("⚠ No available AEDs found within 5 km")
    
    return aeds


def demo_different_city():
    """Demo 3: Search around a different city (Oslo)"""
    print_header("Demo 3: Available AEDs in Oslo (10 km radius)")
    
    data_model = DataModel()
    aeds = data_model.get_available_aeds(
        latitude=59.9139,      # Oslo city center
        longitude=10.7522,
        distance=10000  # 10 km
    )
    
    print(f"\n✓ Found {len(aeds)} available AEDs in Oslo area\n")
    
    if aeds:
        # Show only first 3 in demo
        for i, aed in enumerate(aeds[:3], 1):
            print_aed(aed, i)
        if len(aeds) > 3:
            print(f"\n... and {len(aeds) - 3} more AEDs")
    else:
        print("⚠ No available AEDs found in this area")
    
    return aeds


def demo_analysis():
    """Demo 4: Analysis of results"""
    print_header("Demo 4: Analysis - Statistics")
    
    data_model = DataModel()
    aeds = data_model.get_available_aeds()
    
    if not aeds:
        print("No AEDs to analyze")
        return
    
    print(f"\nTotal available AEDs: {len(aeds)}")
    print(f"Nearest AED: {aeds[0]['site_name']} ({aeds[0]['distance_km']} km)")
    print(f"Farthest AED: {aeds[-1]['site_name']} ({aeds[-1]['distance_km']} km)")
    
    # Calculate average distance
    avg_distance = sum(aed['distance_km'] for aed in aeds) / len(aeds)
    print(f"Average distance: {avg_distance:.2f} km")
    
    # Count by area
    areas = {}
    for aed in aeds:
        area = aed.get('site_post_area', 'Unknown')
        areas[area] = areas.get(area, 0) + 1
    
    print(f"\nAEDs by area:")
    for area, count in sorted(areas.items(), key=lambda x: x[1], reverse=True):
        print(f"  {area}: {count}")
    
    # Get nearby (within 5 km)
    nearby = [aed for aed in aeds if aed['distance_km'] <= 5]
    print(f"\nAEDs within 5 km: {len(nearby)}")
    for aed in nearby:
        print(f"  - {aed['site_name']} ({aed['distance_km']} km)")


def demo_json_output():
    """Demo 5: Raw JSON output"""
    print_header("Demo 5: JSON Output Format")
    
    data_model = DataModel()
    aeds = data_model.get_available_aeds(distance=5000)  # 5 km
    
    if aeds:
        # Show first AED as JSON
        output = {
            "count": len(aeds),
            "first_aed": aeds[0],
            "all_aeds": aeds
        }
        print("\nJSON Response (first AED detail):")
        print(json.dumps(output['first_aed'], indent=2))
    else:
        print("No AEDs to display as JSON")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("  AVAILABLE AEDs FEATURE - DEMONSTRATION")
    print("=" * 60)
    print("\nThis script demonstrates the Available AEDs feature")
    print("using the Hjertestarterregister API.\n")
    print("Prerequisites:")
    print("  1. Flask server must be running (py run.py)")
    print("  2. .env file must contain Hjertestarterregister credentials")
    print("  3. Internet connection required for API access")
    
    try:
        # Run all demos
        demo_kristiansand()
        demo_custom_radius()
        demo_different_city()
        demo_analysis()
        demo_json_output()
        
        # Final summary
        print_header("Summary")
        print("""
✓ Available AEDs Feature Successfully Demonstrated

Key Features Shown:
  ✓ Default search (Kristiansand, 15 km)
  ✓ Custom radius search (5 km)
  ✓ Different location search (Oslo)
  ✓ Statistical analysis of results
  ✓ JSON output format

All AEDs are filtered to show ONLY:
  • IS_OPEN = "Y" (currently open based on operating hours)
  • ACTIVE = "Y" (not decommissioned)

Results are sorted by distance (nearest first).

For more information, see:
  - AVAILABLE_AEDS_QUICK_START.md - Quick reference
  - AVAILABLE_AEDS_GUIDE.md - Complete documentation
        """)
        
    except Exception as e:
        print(f"\n✗ Error running demos: {e}")
        print("\nMake sure:")
        print("  1. The Flask server is running (py run.py)")
        print("  2. .env file has valid Hjertestarterregister credentials")
        print("  3. You have internet connection")
        sys.exit(1)


if __name__ == '__main__':
    main()
