import pandas as pd
import re
from geopy.geocoders import GoogleV3
from geopy.extra.rate_limiter import RateLimiter

# Google Maps API Key (replace with your actual key if necessary)
GOOGLE_API_KEY = "AIzaSyDtKLNFmOjR_8UIjwWYJeWLNOZ1HfYHeEo"

# ➔ Load your CSV file — FIXED the file path format here:
company_data = pd.read_csv(r"D:\Rangr_crm_project\companies.csv")

# ➔ Function to parse an address string into its components
def parse_address(address):
    pattern = r'^(.*?),\s*(.*?),\s*([A-Z]{2})\s+(\d{5})$'
    match = re.match(pattern, str(address))
    if match:
        return pd.Series({
            'address_line1': match.group(1),
            'city': match.group(2),
            'state': match.group(3),
            'zip_code': match.group(4)
        })
    else:
        return pd.Series({
            'address_line1': address,
            'city': '',
            'state': '',
            'zip_code': ''
        })

# ➔ PARSE the 'address' column and merge the result back to the original dataframe
parsed_addresses = company_data['address'].apply(parse_address)
company_data = pd.concat([company_data, parsed_addresses], axis=1)

# ➔ Add a 'country' column (required for Google Geocoding)
company_data['country'] = 'USA'  # or change if appropriate

# ➔ Initialize the geocoder
geolocator = GoogleV3(api_key=GOOGLE_API_KEY, user_agent="geocoding_app")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.5)

# ➔ Function to geocode a single address row
def geocode_address(row):
    try:
        address = f"{row['address_line1']}, {row['city']}, {row['state']} {row['zip_code']}, {row['country']}"
        location = geocode(address)
        if location:
            return pd.Series({'latitude': location.latitude, 'longitude': location.longitude})
        else:
            return pd.Series({'latitude': None, 'longitude': None})
    except Exception as e:
        return pd.Series({'latitude': None, 'longitude': None})

# ➔ APPLY geocoding to the dataframe (row by row — now it has address_line1, city, etc.)
company_data[['latitude', 'longitude']] = company_data.apply(geocode_address, axis=1)

# ➔ SAVE the result to a new CSV
company_data.to_csv(r"D:\Rangr_crm_project\company_data_geocoded.csv", index=False)

print("✅ Geocoding complete. Results saved to company_data_geocoded.csv")
