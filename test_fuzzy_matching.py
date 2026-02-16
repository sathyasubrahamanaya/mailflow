"""
Quick test to verify fuzzy name matching works for variations
"""
from difflib import get_close_matches

# Simulate database contacts
database_names = ["Sathya", "Arjun", "John Doe", "Jane Smith"]

# Test variations
test_names = [
    "Satya",      # Missing 'h'
    "sathya",     # Lowercase
    "SATHYA",     # Uppercase
    "Sathyaa",    # Extra letter
    "aurjun",     # Typo + lowercase
    "Arjun",      # Exact match
    "ARJUN",      # Uppercase
    "Arjuna",     # Extra letter
]

print("Testing Fuzzy Name Matching:")
print("=" * 60)
print(f"Database has: {database_names}\n")

for test_name in test_names:
    # Convert to lowercase for case-insensitive matching
    matches = get_close_matches(test_name.lower(), [n.lower() for n in database_names], n=1, cutoff=0.6)
    
    if matches:
        # Find the original name from database
        matched_index = [n.lower() for n in database_names].index(matches[0])
        found_name = database_names[matched_index]
        print(f"✅ '{test_name}' → Found: '{found_name}'")
    else:
        print(f"❌ '{test_name}' → Not found")

print("\n" + "=" * 60)
print("Cutoff = 0.6 means 60% similarity required")
