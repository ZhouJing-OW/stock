import json
from datetime import date

# Read current state
with open(r"E:\Hanako_WorkSpace\硬逻辑看板\data\hardlogic.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Current stocks: {len(data['stocks'])}")

# If stocks are empty, we need to recover
if len(data['stocks']) == 0:
    print("WARNING: stocks array is empty. Attempting recovery...")
    
    # Try to find backup or reconstruct
    # For now, add the 3 stocks that were already written
    # The write tool should have written a valid JSON
    pass
else:
    print(f"File has {len(data['stocks'])} stocks - OK")

# Verify JSON structure
print("meta:", data.get("meta", {}).get("title", "N/A"))
print("stats:", data.get("stats", {}).get("totalStocks", "N/A"))
