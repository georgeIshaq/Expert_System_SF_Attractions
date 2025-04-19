import time
import sys
from pyswip.prolog import Prolog
from pyswip.easy import registerForeign, Atom
from models import Colors, ATTRIBUTE_VALUES, ATTRIBUTE_DISPLAY_NAMES

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
        #
        # Special handling for accessibility:
        # When user selects "limited_accessibility", wheelchair accessible
        # locations are also included in recommendations
        
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
            
            # Run the recommendation query and explicitly collect all results
            query = self.prolog.query("recommend(Name)")
            results = []
            try:
                solution = next(query)
                while solution:
                    results.append(solution.copy())  # Make a copy of the solution
                    try:
                        solution = next(query)
                    except StopIteration:
                        break
            except StopIteration:
                pass
            finally:
                # Always close the query
                query.close()
            
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