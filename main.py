import os
import sys
from models import Colors
from prolog_utils import generate_kb
from recommender import RecommenderSystem

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