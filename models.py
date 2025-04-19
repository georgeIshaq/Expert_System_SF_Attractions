# ANSI color codes for terminal styling
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Google Sheet constants
SHEET_ID = "1Pxl4hiuPvVcCBXIakqzsBzO9IYpo635ZbHfHsdj1c5Y"
GID = "1095660313"
CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export"
    f"?format=csv&gid={GID}"
)

# Define all possible values for each attribute with nicer display names
ATTRIBUTE_VALUES = {
    'attraction_type': ['museum', 'landmark', 'park', 'viewpoint', 'cultural_site', 
                       'water_activity', 'historical_site', 'art_gallery'],
    'budget': ['free', 'low_cost', 'moderate', 'expensive'],
    'time_available': ['quick_visit', 'half_day', 'full_day'],
    'distance_from_residence': ['walking_distance', 'short_transit', 'long_transit'],
    'indoor_outdoor': ['indoor', 'outdoor', 'either'],  # 'either' in UI corresponds to accepting any indoor/outdoor/both value
    'popularity': ['touristy', 'local_favorite', 'hidden_gem'],
    'physical_activity': ['minimal', 'moderate', 'active'],
    'time_of_day': ['morning', 'afternoon', 'evening', 'night'],
    'accessibility': ['wheelchair_accessible', 'limited_accessibility']
}

# Friendly display names for attributes
ATTRIBUTE_DISPLAY_NAMES = {
    'attraction_type': 'Type of Attraction',
    'budget': 'Price Range',
    'time_available': 'Time You Want to Spend',
    'distance_from_residence': 'Distance from Your Location',
    'indoor_outdoor': 'Indoor or Outdoor Preference',
    'popularity': 'Popularity Level',
    'physical_activity': 'Amount of Physical Activity',
    'time_of_day': 'Best Time to Visit',
    'accessibility': 'Accessibility Requirements'
} 