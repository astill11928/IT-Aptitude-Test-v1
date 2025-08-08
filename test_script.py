import json
import os
import textwrap
import sys # Import the sys module

# --- Helper function to handle bundled file paths ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Constants ---
# Use the helper function to define file paths
QUESTIONS_FILE = resource_path('questions.json')
RECOMMENDATIONS_FILE = resource_path('recommendations.json')

PROFICIENCY_LEVELS = {
    'Beginner': (0, 25),
    'Intermediate': (26, 50),
    'Advanced': (51, 75),
    'Expert': (76, 100)
}
# Categories for version 1.06
CATEGORIES = [
    "IT Operations & Support",
    "Network Engineering",
    "Cybersecurity",
    "Cloud Engineering",
    "Software Development",
    "Web Development"
]
QUESTIONS_PER_CATEGORY = 16

# --- Helper Functions ---

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def load_json_data(filename):
    """Loads data from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        print("This can happen if the JSON files were not bundled correctly.")
        input("Press Enter to exit.") # Add input to keep window open
        exit()
    except json.JSONDecodeError:
        print(f"Error: Could not decode the JSON from '{filename}'.")
        print("Please check the file for formatting errors.")
        input("Press Enter to exit.") # Add input to keep window open
        exit()

def get_proficiency_level(score):
    """Determines the proficiency level based on a percentage score."""
    for level, (min_score, max_score) in PROFICIENCY_LEVELS.items():
        if min_score <= score <= max_score:
            return level
    return "Unknown"

def display_question(question_data, question_number, total_questions):
    """Displays a single multiple-choice question."""
    print(f"Question {question_number}/{total_questions}: {question_data['category']} ({question_data['difficulty']})")
    print("-" * 50)
    # Use textwrap to format long questions nicely
    for line in textwrap.wrap(question_data['question'], width=80):
        print(line)
    print("\nOptions:")
    for key, value in question_data['options'].items():
        print(f"  {key.upper()}) {value}")
    print("-" * 50)

def get_user_answer(options):
    """Gets and validates the user's answer."""
    while True:
        answer = input("Your answer (A, B, C, or D): ").lower()
        if answer in options:
            return answer
        else:
            print("Invalid input. Please enter A, B, C, or D.")

def run_test(questions):
    """Main function to run the entire aptitude test."""
    # Initialize scores based on the categories
    scores = {category: {'correct': 0, 'total': 0} for category in CATEGORIES}
    total_questions_count = len(questions)

    for i, q_data in enumerate(questions, 1):
        clear_screen()
        display_question(q_data, i, total_questions_count)
        user_answer = get_user_answer(q_data['options'])

        category = q_data['category']
        if category in scores:
            scores[category]['total'] += 1
            if user_answer == q_data['answer'].lower():
                scores[category]['correct'] += 1
                print("\nCorrect!")
            else:
                print(f"\nIncorrect. The correct answer was {q_data['answer'].upper()}.")
        else:
            print(f"Warning: Question category '{category}' not found in scores dictionary.")


        input("\nPress Enter to continue to the next question...")

    return scores

def calculate_results(scores):
    """Calculates the final percentages and identifies the strongest area."""
    results = {}
    for category, data in scores.items():
        if data['total'] > 0:
            percentage = (data['correct'] / QUESTIONS_PER_CATEGORY) * 100
            results[category] = {
                'score': round(percentage),
                'proficiency': get_proficiency_level(percentage)
            }
        else:
            results[category] = {'score': 0, 'proficiency': 'Beginner'}

    # Determine the strongest category
    strongest_category = max(results, key=lambda cat: results[cat]['score'])
    return results, strongest_category

def display_report(results, strongest_category, recommendations):
    """Displays the final aptitude report and recommendations."""
    clear_screen()
    print("=" * 30)
    print("  Technology Aptitude Report  ")
    print("=" * 30)
    print("\nThis report highlights your areas of strongest aptitude based on your answers.")
    print("It is designed to guide your focus, not as a pass/fail evaluation.\n")

    for category, data in results.items():
        print(f"  - {category}: {data['score']}% ({data['proficiency']} Proficiency)")

    print("\n" + "=" * 50)
    print(f"\nYour strongest area appears to be: ** {strongest_category} **\n")

    proficiency_of_strongest = results[strongest_category]['proficiency']
    
    if strongest_category in recommendations and proficiency_of_strongest in recommendations[strongest_category]:
        rec = recommendations[strongest_category][proficiency_of_strongest]

        print("Based on this result, here is a potential path for you to explore:")
        print(f"\n**Focus On:** {rec['Focus On']}")
        print("\n**Certifications & Skills to Explore:**")
        for cert in rec['Certifications & Skills to Explore']:
            print(f"  - {cert}")
        print("\n**Job Titles to Target:**")
        for title in rec['Job Titles to Target']:
            print(f"  - {title}")
    else:
        print("Could not retrieve recommendations for your strongest category.")


    print("\n" + "=" * 50)
    print("\nThank you for taking the test!")
    input("\nPress Enter to exit.") # Add input to keep window open at the end


# --- Main Execution ---
if __name__ == "__main__":
    all_questions = load_json_data(QUESTIONS_FILE)
    all_recommendations = load_json_data(RECOMMENDATIONS_FILE)
    
    clear_screen()
    print("Welcome to the Technology Aptitude Test v1.06!")
    print(f"This is a {len(all_questions)}-question multiple-choice test.")
    print("It will help identify your strengths across six key areas of technology.")
    input("\nPress Enter to begin...")
    
    final_scores = run_test(all_questions)
    final_results, strongest = calculate_results(final_scores)
    display_report(final_results, strongest, all_recommendations)
