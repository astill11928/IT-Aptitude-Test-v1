import json
import os
import textwrap
import sys
import random
from datetime import datetime

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
ALL_CATEGORIES = [
    "IT Operations & Support",
    "Network Engineering",
    "Cybersecurity",
    "Cloud Engineering",
    "Software Development",
    "Web Development"
]
DIFFICULTY_LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert"]
QUESTIONS_PER_CATEGORY = 16
ADAPTIVE_BASELINE_COUNT = 2

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
        input("Press Enter to exit.")
        exit()
    except json.JSONDecodeError:
        print(f"Error: Could not decode the JSON from '{filename}'.")
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

def get_user_selection(prompt_message, selection_list, allow_all=False):
    """Generic function to get user's numbered selection from a list."""
    while True:
        clear_screen()
        print(prompt_message)
        for i, item in enumerate(selection_list, 1):
            print(f"  {i}) {item}")
        
        print("\nEnter the numbers of your choices, separated by commas (e.g., 1,3,5).")
        if allow_all:
            print("Or, type 'all' to select all.")

        user_input = input("\nYour selection: ").lower().strip()

        if allow_all and user_input == 'all':
            return selection_list

        selected_indices = []
        try:
            parts = user_input.split(',')
            if not parts or parts == ['']:
                 raise ValueError
            for part in parts:
                index = int(part.strip())
                if 1 <= index <= len(selection_list):
                    selected_indices.append(index - 1)
                else:
                    raise ValueError
            
            if selected_indices:
                unique_indices = sorted(list(set(selected_indices)))
                return [selection_list[i] for i in unique_indices]
            else:
                print("Invalid input. Please enter numbers from the list.")
                input("Press Enter to try again...")

        except ValueError:
            print("Invalid input. Please enter valid numbers from the list, separated by commas.")
            input("Press Enter to try again...")

def run_test(questions, scores):
    """Core test-taking loop for a given list of questions."""
    total_questions_count = len(questions)
    for i, q_data in enumerate(questions, 1):
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
            # --- New Feature: Display Explanation ---
            if 'explanation' in q_data and q_data['explanation']:
                print(f"Explanation: {q_data['explanation']}")

        input("\nPress Enter to continue to the next question...")
    return scores

def calculate_results(scores):
    """Calculates final percentages and identifies the strongest and second strongest areas."""
    results = {}
    for category, data in scores.items():
        if data['total'] > 0:
            percentage = (data['correct'] / data['total']) * 100
            results[category] = {
                'score': round(percentage),
                'proficiency': get_proficiency_level(percentage)
            }
        else:
            results[category] = {'score': 0, 'proficiency': 'Beginner'}
    
    if not results:
        return {}, None, None

    sorted_categories = sorted(results.items(), key=lambda item: item[1]['score'], reverse=True)
    
    strongest_category = sorted_categories[0][0] if sorted_categories else None
    second_strongest_category = sorted_categories[1][0] if len(sorted_categories) > 1 else None
    
    return results, strongest_category, second_strongest_category

def generate_report_text(results, strongest_category, second_strongest_category, recommendations, user_interests):
    """Generates the full report text as a string."""
    report_lines = []
    report_lines.append("=" * 30)
    report_lines.append("  Technology Aptitude Report  ")
    report_lines.append("=" * 30)
    
    if not results:
        report_lines.append("\nNo test sections were completed.")
        return "\n".join(report_lines)

    report_lines.append("\nThis report highlights your areas of strongest aptitude based on your answers.")
    report_lines.append("It is designed to guide your focus, not as a pass/fail evaluation.\n")

    for category, data in results.items():
        report_lines.append(f"  - {category}: {data['score']}% ({data['proficiency']} Proficiency)")

    report_lines.append("\n" + "=" * 50)
    report_lines.append("\nInterest vs. Aptitude Analysis:")
    if strongest_category in user_interests:
        report_lines.append(f"Great news! Your strongest aptitude in '{strongest_category}' aligns with your stated interests.")
        report_lines.append("This is a strong indicator that you should focus your career development in this area.")
    else:
        report_lines.append(f"Your results show a strong aptitude for '{strongest_category}'.")
        report_lines.append(f"While this differs from your stated interest(s) in {', '.join(user_interests)},")
        report_lines.append("it highlights a potential natural talent you could explore further.")
    
    report_lines.append("\n" + "=" * 50)
    report_lines.append(f"\nPrimary Recommendation (Based on your strongest aptitude: {strongest_category})\n")

    proficiency_of_strongest = results[strongest_category]['proficiency']
    
    if strongest_category in recommendations and proficiency_of_strongest in recommendations[strongest_category]:
        rec = recommendations[strongest_category][proficiency_of_strongest]
        report_lines.append(f"**Focus On:** {rec['Focus On']}")
        report_lines.append("\n**Certifications & Skills to Explore:**")
        for cert in rec['Certifications & Skills to Explore']:
            report_lines.append(f"  - {cert}")
        report_lines.append("\n**Job Titles to Target:**")
        for title in rec['Job Titles to Target']:
            report_lines.append(f"  - {title}")
    else:
        report_lines.append("Could not retrieve recommendations for your strongest category.")

    if second_strongest_category:
        report_lines.append("\n" + "=" * 50)
        report_lines.append("\nYour Secondary Strength & Complementary Skills\n")
        report_lines.append(f"Your results also show a strong aptitude for '{second_strongest_category}'.")
        report_lines.append("Skills in this area often complement your primary strength and can lead to powerful career combinations.")
        report_lines.append("Consider exploring this as a future specialization or as a way to enhance your primary skill set.")

    if 'hybrid_roles' in recommendations:
        hybrid_recommendations = []
        for role in recommendations['hybrid_roles']:
            is_match = True
            if not all(cat in results for cat in role['required_categories']):
                is_match = False
                continue
            for req_cat in role['required_categories']:
                if results[req_cat]['score'] < role['score_threshold']:
                    is_match = False
                    break
            if is_match:
                hybrid_recommendations.append(role)
        
        if hybrid_recommendations:
            report_lines.append("\n" + "=" * 50)
            report_lines.append("\nPotential Hybrid Roles\n")
            report_lines.append("Your scores indicate a strong aptitude for the following hybrid roles:")
            for role in hybrid_recommendations:
                report_lines.append(f"\n--- {role['name']} ---")
                report_lines.append(f"Description: {role['description']}")
                rec = role['recommendation']
                report_lines.append(f"\n**Focus On:** {rec['Focus On']}")
                report_lines.append("\n**Certifications & Skills to Explore:**")
                for cert in rec['Certifications & Skills to Explore']:
                    report_lines.append(f"  - {cert}")
                report_lines.append("\n**Job Titles to Target:**")
                for title in rec['Job Titles to Target']:
                    report_lines.append(f"  - {title}")

    taken_categories = set(results.keys())
    all_test_categories = set(ALL_CATEGORIES)
    not_taken_categories = all_test_categories - taken_categories

    if not_taken_categories:
        report_lines.append("\n" + "=" * 50)
        report_lines.append("\nOther Areas to Explore:")
        report_lines.append("Consider taking these sections in the future to discover other strengths:")
        for category in sorted(list(not_taken_categories)):
            report_lines.append(f"  - {category}")

    report_lines.append("\n" + "=" * 50)
    report_lines.append("\nThank you for taking the test!")
    return "\n".join(report_lines)

def save_report_to_file(report_text):
    """Saves the report text to a timestamped file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Aptitude_Report_{timestamp}.txt"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"\nReport successfully saved as {filename}")
    except Exception as e:
        print(f"\nAn error occurred while saving the report: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    all_questions = load_json_data(QUESTIONS_FILE)
    all_recommendations = load_json_data(RECOMMENDATIONS_FILE)
    
    selection_prompt = (
        "Please select the categories you are interested in.\n"
        "NOTE: You will be tested on the sections you choose."
    )
    user_selections = get_user_selection(selection_prompt, ALL_CATEGORIES, allow_all=True)
    user_interests = user_selections
    user_selected_categories = user_selections
    
    test_modes = ["Full Assessment (All difficulties)", "Targeted Difficulty (You choose levels)", "Adaptive Assessment (Starts at Intermediate and adjusts)"]
    chosen_mode = get_user_selection("Next, choose your test mode.", test_modes, allow_all=False)[0]

    scores = {category: {'correct': 0, 'total': 0} for category in user_selected_categories}
    questions_to_ask = []

    if "Full Assessment" in chosen_mode:
        questions_to_ask = [q for q in all_questions if q['category'] in user_selected_categories]

    elif "Targeted Difficulty" in chosen_mode:
        selected_difficulties = get_user_selection("Which difficulty levels would you like?", DIFFICULTY_LEVELS, allow_all=True)
        questions_to_ask = [q for q in all_questions if q['category'] in user_selected_categories and q['difficulty'] in selected_difficulties]

    elif "Adaptive Assessment" in chosen_mode:
        baseline_questions = [q for q in all_questions if q['category'] in user_selected_categories and q['difficulty'] == "Intermediate"]
        final_baseline = []
        for cat in user_selected_categories:
            cat_questions = [q for q in baseline_questions if q['category'] == cat]
            random.shuffle(cat_questions)
            final_baseline.extend(cat_questions[:ADAPTIVE_BASELINE_COUNT])
        
        print(f"\nStarting with a baseline of {len(final_baseline)} Intermediate questions...")
        input("Press Enter to begin the adaptive assessment...")
        
        scores = run_test(final_baseline, scores)
        
        total_correct = sum(scores[cat]['correct'] for cat in user_selected_categories)
        total_asked = sum(scores[cat]['total'] for cat in user_selected_categories)
        performance_percent = (total_correct / total_asked) * 100 if total_asked > 0 else 0

        additional_questions = []
        if performance_percent > 50:
            print("\nYou're doing great! Let's try some more advanced questions.")
            difficulties = ["Advanced", "Expert"]
            additional_questions = [q for q in all_questions if q['category'] in user_selected_categories and q['difficulty'] in difficulties]
        else:
            print("\nLet's review some fundamentals.")
            difficulties = ["Beginner"]
            additional_questions = [q for q in all_questions if q['category'] in user_selected_categories and q['difficulty'] in difficulties]
        
        input("Press Enter to continue...")
        scores = run_test(additional_questions, scores)

    if "Adaptive Assessment" not in chosen_mode:
        question_count = len(questions_to_ask)
        clear_screen()
        print(f"You have selected a test with {question_count} questions.")
        input("\nPress Enter to begin...")
        scores = run_test(questions_to_ask, scores)

    final_results, strongest, second_strongest = calculate_results(scores)
    
    # Generate the report text first
    report_string = generate_report_text(final_results, strongest, second_strongest, all_recommendations, user_interests)
    
    # Display the report on screen
    clear_screen()
    print(report_string)

    # --- New Feature: Save Report ---
    while True:
        save_choice = input("\nWould you like to save this report to a text file? (y/n): ").lower().strip()
        if save_choice in ['y', 'yes']:
            save_report_to_file(report_string)
            break
        elif save_choice in ['n', 'no']:
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    input("\nPress Enter to exit.")
