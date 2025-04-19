import requests
import csv
import io
import tempfile
import os
import sys
import time
from pyswip.prolog import Prolog
from pyswip.easy import registerForeign, Functor, Variable, Atom


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

# Utility: convert a comma-separated cell to a Prolog list
def to_prolog_list(cell_value: str) -> str:
    items = [item.strip() for item in cell_value.split(',') if item.strip()]
    inner = ",".join([f"'{item}'" for item in items])  # Quote each item properly
    return f"[{inner}]"

# Generate the Prolog knowledge base from the Google Sheet
def generate_kb() -> str:
    print(f"{Colors.CYAN}Fetching attraction data...{Colors.END}")
    
    try:
        resp = requests.get(CSV_URL)
        resp.raise_for_status()
        text = resp.text
    except Exception as e:
        print(f"{Colors.RED}Error fetching data: {e}{Colors.END}")
        sys.exit(1)
        
    reader = csv.DictReader(io.StringIO(text))

    lines = []
    # Declarations
    lines.append(":- dynamic known/3, multivalued/1, attraction/12.")
    lines.append("% Declare multivalued attributes")
    lines.append("multivalued(indoor_outdoor).")
    lines.append("multivalued(best_time).\n")

    # Facts
    attraction_count = 0
    for row in reader:
        name = row['Attraction Name'].replace("'", "\\'")
        type_ = row['Type']
        budget = row['Budget']
        time_needed = row['Time Needed']
        dist = row['Distance from Residence']
        io_cell = to_prolog_list(row['Indoor/Outdoor'])
        popularity = row['Popularity']
        phys = row['Physical Activity']
        best_times = to_prolog_list(row['Best Time'])
        access = row['Accessibility']
        desc = row['Description'].replace("'", "\\'")
        link = row['Link'].replace("'", "\\'")

        fact = (
            f"attraction('{name}',{type_},{budget},{time_needed},"
            f"{dist},{io_cell},{popularity},{phys},{best_times},{access},"
            f"'{desc}','{link}')."
        )
        lines.append(fact)
        attraction_count += 1

    print(f"{Colors.GREEN}Loaded {attraction_count} attractions successfully!{Colors.END}")

    # Askables
    lines.append("\n% --- Ask Implementation ---")
    lines.append("ask(A, V):-")
    lines.append("    known(yes, A, V), !.")
    lines.append("ask(A, V):-")
    lines.append("    known(_, A, V), !, fail.")
    lines.append("ask(A, V):-")
    lines.append("    \\+multivalued(A),")
    lines.append("    known(yes, A, V2),")
    lines.append("    V \\== V2, !, fail.")
    lines.append("ask(A, V):-")
    lines.append("    read_py(A, V, Y),")
    lines.append("    assertz(known(Y, A, V)),")
    lines.append("    Y == yes.\n")

    # Wrapper predicates
    wrappers = [
        'attraction_type', 'budget', 'time_available', 'distance_from_residence',
        'indoor_outdoor', 'popularity', 'physical_activity', 'time_of_day', 'accessibility'
    ]
    for w in wrappers:
        lines.append(f"{w}(X) :- ask({w}, X).")

    # Recommendation rule
    lines.append("\n% --- Recommendation Rule ---")
    lines.append("recommend(Name) :-")
    lines.append("    attraction(Name,Type,Budget,TimeNeeded,Dist,IO,Pop,Phys,BestTimes,Acc,Desc,Link),")
    lines.append("    attraction_type(Type),")
    lines.append("    budget(Budget),")
    lines.append("    time_available(TimeNeeded),")
    lines.append("    distance_from_residence(Dist),")
    lines.append("    % The indoor_outdoor matching allows attractions to match based on a value present in their IO list")
    lines.append("    % When user selects 'either', read_py will accept any IO value (indoor/outdoor/both)")
    lines.append("    % When an attraction has 'both' value, it will match with user selections of 'indoor' or 'outdoor'")
    lines.append("    member(IOVal, IO), indoor_outdoor(IOVal),")
    lines.append("    popularity(Pop),")
    lines.append("    physical_activity(Phys),")
    lines.append("    member(ChosenTime, BestTimes), time_of_day(ChosenTime),")
    lines.append("    accessibility(Acc).")
    
    # Add show_recommendation predicate to display details
    lines.append("\nshow_recommendation(Name) :-")
    lines.append("    attraction(Name,_,_,_,_,_,_,_,_,_,Desc,Link),")
    lines.append("    write_py(Name),")
    lines.append("    write_py(Desc),")
    lines.append("    write_py(Link).")

    kb = "\n".join(lines)
    tf = tempfile.NamedTemporaryFile(delete=False, suffix='.pl', mode='w', encoding='utf-8')
    tf.write(kb)
    tf.close()
    return tf.name

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

# Class to handle user interactions
class RecommenderSystem:
    def __init__(self, kb_file):
        self.kb_file = kb_file
        self.prolog = Prolog()
        self.prolog.consult(kb_file)
        self.user_responses = {}
        self.exit_requested = False
        
        # Register foreign functions
        registerForeign(self.read_py)
        registerForeign(self.write_py)
        
        # Note: Special handling is implemented for indoor/outdoor preference
        # When user selects "either", the system will accept attractions with
        # any indoor, outdoor, or both values
        # When an attraction is listed as "both", it will match with user
        # selections of "indoor" or "outdoor"
        
    def read_py(self, attribute, value, result):
        """Prolog callback to get user input for an attribute and value."""
        # Check if exit was requested in a previous question
        if self.exit_requested:
            result.unify(Atom('no'))
            return False
            
        attr_name = str(attribute)
        val = str(value)
        
        # Only ask once for each attribute
        if attr_name not in self.user_responses:
            selected_value = self.get_user_choice(attr_name)
            
            # Check if user wants to exit
            if selected_value == "EXIT":
                self.exit_requested = True
                result.unify(Atom('no'))
                return False
                
            self.user_responses[attr_name] = selected_value
        
        # Special handling for indoor/outdoor preference
        if attr_name == 'indoor_outdoor':
            # When user selects "either", accept any indoor/outdoor value
            if self.user_responses[attr_name] == 'either':
                result.unify(Atom('yes'))
                return True
                
            # When an attraction has "both" as a value and user selected "indoor" or "outdoor"
            # "both" should match with either indoor or outdoor user selections
            if val == 'both' and self.user_responses[attr_name] in ['indoor', 'outdoor']:
                result.unify(Atom('yes'))
                return True
        
        # Special handling for accessibility preference
        if attr_name == 'accessibility':
            # If user selects limited_accessibility, also include wheelchair_accessible locations
            if self.user_responses[attr_name] == 'limited_accessibility' and val == 'wheelchair_accessible':
                result.unify(Atom('yes'))
                return True
        
        # Check if the user's choice matches the current value being tested
        if val == self.user_responses[attr_name]:
            result.unify(Atom('yes'))
            return True
        else:
            result.unify(Atom('no'))
            return False
            
    def get_user_choice(self, attribute):
        """Get user's choice for a given attribute."""
        values = ATTRIBUTE_VALUES.get(attribute, [])
        if not values:
            return None
            
        display_name = ATTRIBUTE_DISPLAY_NAMES.get(attribute, attribute.replace('_', ' ').title())
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}▶ What is your preference for {display_name}?{Colors.END}")
        
        # Print the options in a nice format
        for i, val in enumerate(values, 1):
            formatted_val = val.replace('_', ' ').title()
            print(f"{Colors.CYAN}{i}.{Colors.END} {formatted_val}")
            
        # Add exit option
        print(f"{Colors.RED}0. Exit Recommender{Colors.END}")
        
        while True:
            try:
                choice = input(f"{Colors.GREEN}Enter your choice (0-{len(values)}): {Colors.END}")
                
                # Check for exit
                if choice == '0':
                    return "EXIT"
                    
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(values):
                    selected = values[selected_index]
                    print(f"{Colors.GREEN}✓ You selected: {selected.replace('_', ' ').title()}{Colors.END}")
                    return selected
                else:
                    print(f"{Colors.RED}Invalid choice. Please enter a number between 0 and {len(values)}.{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}Please enter a valid number.{Colors.END}")
                
    def write_py(self, output):
        """Prolog callback for writing output."""
        print(str(output))
        sys.stdout.flush()
        return True
        
    def reset(self):
        """Reset the system for a new recommendation session."""
        self.user_responses = {}
        self.exit_requested = False
        list(self.prolog.query("retractall(known(_,_,_))."))
        
    def run_recommendation(self):
        """Run the recommendation process and display results."""
        try:
            # Show progress indicator
            print(f"{Colors.YELLOW}Analyzing your preferences...{Colors.END}")
            time.sleep(0.5)  # Small delay for better UX
            
            # Run the recommendation query
            results = list(self.prolog.query("recommend(Name)."))
            
            # Check if exit was requested
            if self.exit_requested:
                print(f"\n{Colors.YELLOW}Recommendation process canceled by user.{Colors.END}")
                return False
                
            # Display results
            if results:
                count = len(results)
                print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*20} RECOMMENDED ATTRACTIONS {'='*20}{Colors.END}")
                print(f"{Colors.GREEN}Found {count} attraction{'' if count == 1 else 's'} matching your preferences!{Colors.END}\n")
                
                for i, sol in enumerate(results, 1):
                    attraction_name = sol['Name']
                    # Get the detailed information
                    escaped_name = attraction_name.replace("'", "\\'")
                    details = list(self.prolog.query(f"attraction('{escaped_name}',_,_,_,_,_,_,_,_,_,Desc,Link)."))
                    
                    print(f"{Colors.BOLD}{Colors.CYAN}#{i}: {attraction_name}{Colors.END}")
                    if details:
                        print(f"{Colors.BOLD}Description:{Colors.END} {details[0]['Desc']}")
                        print(f"{Colors.BOLD}Link:{Colors.END} {Colors.UNDERLINE}{details[0]['Link']}{Colors.END}")
                    print()
                    
            else:
                print(f"\n{Colors.YELLOW}No attractions found that match all your preferences.{Colors.END}")
                print(f"{Colors.YELLOW}Consider broadening some of your preferences and try again.{Colors.END}")
                
            return True
                
        except Exception as e:
            print(f"{Colors.RED}Error during recommendation: {e}{Colors.END}")
            return False
            
    # Add required arity for foreign functions
    read_py.arity = 3
    write_py.arity = 1

# Main function
def main():
    # Generate knowledge base only once
    kb_file = generate_kb()
    recommender = RecommenderSystem(kb_file)
    
    try:
        keep_running = True
        
        while keep_running:
            # Display welcome banner
            print(f"\n{Colors.BOLD}{Colors.HEADER}{'*'*70}")
            print(f"*{'SAN FRANCISCO ATTRACTIONS RECOMMENDER':^68}*")
            print(f"{'*'*70}{Colors.END}")
            
            print(f"\n{Colors.CYAN}Welcome to your personal SF tour guide!{Colors.END}")
            print("I'll recommend attractions based on your preferences.")
            print("For each category, select your preference from the options provided.")
            print(f"{Colors.YELLOW}You can exit the recommender at any time by selecting '0'.{Colors.END}")
            
            # Reset system for new session if needed
            if recommender.user_responses:
                recommender.reset()
                
            # Run the recommendation engine
            success = recommender.run_recommendation()
            
            # Skip asking about retrying if user explicitly requested exit
            if recommender.exit_requested:
                keep_running = False
                continue

            # Ask if user wants to try again
            if success:
                print(f"\n{Colors.HEADER}Would you like to get new recommendations?{Colors.END}")
                print(f"{Colors.CYAN}1.{Colors.END} Yes, start again")
                print(f"{Colors.CYAN}2.{Colors.END} No, exit the recommender")
                
                while True:
                    try:
                        choice = input(f"{Colors.GREEN}Enter your choice (1-2): {Colors.END}")
                        if choice == '1':
                            break
                        elif choice == '2':
                            keep_running = False
                            break
                        else:
                            print(f"{Colors.RED}Invalid choice. Please enter 1 or 2.{Colors.END}")
                    except ValueError:
                        print(f"{Colors.RED}Please enter a valid number.{Colors.END}")
            else:
                # If recommendation was canceled, ask if user wants to try again
                print(f"\n{Colors.HEADER}Would you like to start over?{Colors.END}")
                print(f"{Colors.CYAN}1.{Colors.END} Yes, try again")
                print(f"{Colors.CYAN}2.{Colors.END} No, exit")
                
                while True:
                    try:
                        choice = input(f"{Colors.GREEN}Enter your choice (1-2): {Colors.END}")
                        if choice == '1':
                            break
                        elif choice == '2':
                            keep_running = False
                            break
                        else:
                            print(f"{Colors.RED}Invalid choice. Please enter 1 or 2.{Colors.END}")
                    except ValueError:
                        print(f"{Colors.RED}Please enter a valid number.{Colors.END}")
                    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Program interrupted by user.{Colors.END}")
    finally:
        # Clean up
        os.unlink(kb_file)
        print(f"\n{Colors.GREEN}Thank you for using the SF Attractions Recommender!{Colors.END}")
        print(f"{Colors.CYAN}Have a great time in San Francisco!{Colors.END}\n")

if __name__ == '__main__':
    main()