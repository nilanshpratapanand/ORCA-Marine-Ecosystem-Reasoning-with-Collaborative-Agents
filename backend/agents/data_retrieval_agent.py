# data_retrieval_agent.py
#
# WHAT THIS FILE DOES:
# The Orchestrator sends this agent a request (region + date range).
# This agent looks up the data and sends it back.
# For now, since MOSDAC account approval is pending, we use FAKE sample
# data instead of a real database. This lets us test the whole pipeline
# today, and we swap in real data later WITHOUT changing the format.

# --- FAKE DATABASE (temporary stand-in for PostGIS) ---
# In real Python, a dictionary looks like {"key": value, "key2": value2}
# Think of this like a mini spreadsheet: each region name maps to its data.
FAKE_DATABASE = {
    "kochi coast": {
        "sst": 28.4,
        "chlorophyll": 0.6,
        "wave_height_m": 1.2,
        "source": "INCOIS",
    },
    "chennai coast": {
        "sst": 29.1,
        "chlorophyll": 0.4,
        "wave_height_m": 0.9,
        "source": "INCOIS",
    },
}


# --- THE AGENT FUNCTION ---
# "def" means "define a function" (same idea as a function in C).
# This function takes ONE input: a dictionary matching contracts.md Section 2.
def data_retrieval_agent(request):
    # Step 1: pull the region out of the incoming request.
    # request["region"] means "get the value stored under the key 'region'".
    region = request["region"]

    # Step 2: normalize it to lowercase so "Kochi Coast" and "kochi coast"
    # both match — small detail, but real-world text is messy like this.
    region_key = region.lower()

    # Step 3: check if we actually have data for this region.
    # "in" checks if a key exists in the dictionary — like checking if
    # something is present in a list.
    if region_key not in FAKE_DATABASE:
        # NO DATA CASE — per contracts.md, we return an error, we do NOT
        # make up a number. This is the "honesty over hallucination" rule.
        return {
            "task_id": request["task_id"],
            "status": "error",
            "reason": "no_data_for_region",
            "message": f"No cached data available for '{region}'",
        }

    # Step 4: we have data — look it up.
    data = FAKE_DATABASE[region_key]

    # Step 5: build the success response, matching contracts.md exactly.
    return {
        "task_id": request["task_id"],
        "status": "success",
        "data": {
            "sst": data["sst"],
            "chlorophyll": data["chlorophyll"],
            "wave_height_m": data["wave_height_m"],
        },
        "source": data["source"],
        "last_updated": "2026-08-23T06:00:00Z",  # fake timestamp for now
    }


# --- TEST BLOCK ---
# This part only runs if you run THIS file directly (not when another
# file imports it). It's how we test the function without needing the
# whole system built yet.
if __name__ == "__main__":
    # Build a fake request, exactly matching contracts.md Section 2 format.
    test_request = {
        "task_id": "task_001",
        "query_type": "fishing_safety",
        "region": "Kochi Coast",
        "date_range": {"start": "2026-08-23", "end": "2026-08-30"},
        "role": "fisherman",
    }

    # Call the function and print what it returns.
    result = data_retrieval_agent(test_request)
    print(result)

    # Also test the "no data" case, to prove error handling works.
    bad_request = {
        "task_id": "task_002",
        "query_type": "fishing_safety",
        "region": "Mumbai Coast",  # not in our fake database
        "date_range": {"start": "2026-08-23", "end": "2026-08-30"},
        "role": "fisherman",
    }
    result2 = data_retrieval_agent(bad_request)
    print(result2)