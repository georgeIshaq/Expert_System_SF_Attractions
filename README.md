# San Francisco Attractions Recommender

This project is a recommendation system that suggests attractions in San Francisco based on user preferences. It uses a combination of Python and Prolog to provide an interactive interface for users to specify their preferences and receive personalized recommendations.

## Features
- **Interactive User Interface**: Users can specify their preferences for various attributes such as type of attraction, budget, time available, distance, indoor/outdoor preference, popularity, physical activity level, best time to visit, and accessibility requirements.
- **Prolog Integration**: The system uses Prolog to handle the logic and reasoning for generating recommendations based on user inputs.
- **Special Handling for Preferences**: Includes special handling for preferences like "either" for indoor/outdoor and "limited accessibility" to include wheelchair-accessible locations.

## Project Structure
The codebase is organized into several modules:
- `main.py`: Entry point for the application
- `models.py`: Contains data models and constants
- `prolog_utils.py`: Utilities for working with Prolog
- `recommender.py`: Contains the core RecommenderSystem class

## Setup
1. **Clone the Repository**: Clone this repository to your local machine.
   ```bash
   git clone <repository-url>
   ```
2. **Install Dependencies**: Ensure you have Python installed along with the required packages. You can install the necessary packages using pip:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Application**: Execute the main script to start the recommender system.
   ```bash
   python main.py
   ```

## Usage
- Upon running the application, you will be greeted with a welcome message and prompted to enter your preferences for various attributes.
- Follow the on-screen instructions to select your preferences.
- The system will provide a list of recommended attractions based on your inputs.
- You can choose to get new recommendations or exit the application at any time.

## Customization
- The system uses a Google Sheet as a data source for attractions. You can modify the sheet to update or add new attractions.
- The Prolog knowledge base is dynamically generated from the Google Sheet data, allowing for easy updates and maintenance.
- The sheet ID and GID can be changed in `models.py` to point to a different data source.

## Contributing
Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments
- This project uses the [pyswip](https://github.com/yuce/pyswip) library to interface with SWI-Prolog from Python.
- Special thanks to all contributors and users who have provided feedback and suggestions.
