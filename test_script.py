import json
import os
import textwrap
import sys

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
QUESTIONS_FILE = resource_path('questions.json')
RECOMMENDATIONS_FILE = resource_path('recommendations.json')
PROFICIENCY_LEVELS = {
    'Beginner': (0, 25),
    'Intermediate': (26, 50),
    'Advanced': (51, 75),
    'Expert': (76, 100)
}
# All available categories
ALL_CATEGORIES = [
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
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        print("This can happen if the JSON files were not bundled correctly.")
        input("Press Enter to exit.")
        exit()
    except json.JSONDecodeError:
        print(f"Error: Could not decode the JSON from '{filename}'.")
        print("Please check the file for formatting errors.")
        input("Press Enter to exit.")
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

def select_categories():
    """Allows the user to select which categories to be tested on."""
    while True:
        clear_screen()
        print("Please select the categories you would like to be tested on.")
        for i, category in enumerate(ALL_CATEGORIES, 1):
            print(f"  {i}) {category}")
        print("\nEnter the numbers of the categories, separated by commas (e.g., 1,3,5).")
        print("Or, type 'all' to take the full test.")
        
        user_input = input("\nYour selection: ").lower().strip()

        if user_input == 'all':
            return ALL_CATEGORIES

        selected_indices = []
        try:
            parts = user_input.split(',')
            for part in parts:
                index = int(part.strip())
                if 1 <= index <= len(ALL_CATEGORIES):
                    selected_indices.append(index - 1)
                else:
                    raise ValueError
            
            if selected_indices:
                # Remove duplicates and sort
                unique_indices = sorted(list(set(selected_indices)))
                return [ALL_CATEGORIES[i] for i in unique_indices]
            else:
                print("Invalid input. Please enter numbers from the list.")
                input("Press Enter to try again...")

        except ValueError:
            print("Invalid input. Please enter numbers from the list, separated by commas.")
            input("Press Enter to try again...")


def run_test(questions, selected_categories):
    """Main function to run the selected sections of the aptitude test."""
    # Filter questions based on selected categories
    test_questions = [q for q in questions if q['category'] in selected_categories]
    
    # Initialize scores for selected categories only
    scores = {category: {'correct': 0, 'total': 0} for category in selected_categories}
    total_questions_count = len(test_questions)

    for i, q_data in enumerate(test_questions, 1):
        clear_screen()
        display_question(q_data, i, total_questions_count)
        user_answer = get_user_answer(q_data['options'])

        category = q_data['category']
        scores[category]['total'] += 1
        if user_answer == q_data['answer'].lower():
            scores[category]['correct'] += 1
            print("\nCorrect!")
        else:
            print(f"\nIncorrect. The correct answer was {q_data['answer'].upper()}.")

        input("\nPress Enter to continue to the next question...")

    return scores

def calculate_results(scores):
    """Calculates the final percentages and identifies the strongest area from the taken sections."""
    results = {}
    for category, data in scores.items():
        if data['total'] > 0:
            percentage = (data['correct'] / QUESTIONS_PER_CATEGORY) * 100
            results[category] = {
                'score': round(percentage),
                'proficiency': get_proficiency_level(percentage)
            }
        else:
            # This case should not happen with the new logic, but is kept for safety
            results[category] = {'score': 0, 'proficiency': 'Beginner'}
    
    if not results:
        return {}, None

    # Determine the strongest category among the ones taken
    strongest_category = max(results, key=lambda cat: results[cat]['score'])
    return results, strongest_category

def display_report(results, strongest_category, recommendations):
    """Displays the final aptitude report and recommendations."""
    clear_screen()
    print("=" * 30)
    print("  Technology Aptitude Report  ")
    print("=" * 30)
    
    if not results:
        print("\nNo test sections were completed.")
        return

    print("\nThis report highlights your areas of strongest aptitude based on your answers.")
    print("It is designed to guide your focus, not as a pass/fail evaluation.\n")

    for category, data in results.items():
        print(f"  - {category}: {data['score']}% ({data['proficiency']} Proficiency)")

    print("\n" + "=" * 50)
    print(f"\nBased on the sections you took, your strongest area appears to be: ** {strongest_category} **\n")

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

    # New Feature: Suggest other areas to explore if not all sections were taken
    taken_categories = set(results.keys())
    all_test_categories = set(ALL_CATEGORIES)
    not_taken_categories = all_test_categories - taken_categories

    if not_taken_categories:
        print("\n" + "=" * 50)
        print("\nOther Areas to Explore:")
        print("Consider taking these sections in the future to discover other strengths:")
        for category in sorted(list(not_taken_categories)):
            print(f"  - {category}")


    print("\n" + "=" * 50)
    print("\nThank you for taking the test!")
    input("\nPress Enter to exit.")


# --- Main Execution ---
if __name__ == "__main__":
    all_questions = load_json_data(QUESTIONS_FILE)
    all_recommendations = load_json_data(RECOMMENDATIONS_FILE)
    
    # New step: Let the user select categories
    user_selected_categories = select_categories()
    
    clear_screen()
    print("Welcome to the Technology Aptitude Test!")
    question_count = len(user_selected_categories) * QUESTIONS_PER_CATEGORY
    print(f"You have selected {len(user_selected_categories)} section(s) for a total of {question_count} questions.")
    print("This test will help identify your strengths in your chosen domains.")
    input("\nPress Enter to begin...")
    
    final_scores = run_test(all_questions, user_selected_categories)
    final_results, strongest = calculate_results(final_scores)
    display_report(final_results, strongest, all_recommendations)