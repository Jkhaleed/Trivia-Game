import requests
import random
import csv
import os
from html import unescape


class QuizQuestions:
    """Fetches trivia questions from API or CSV file."""

    def __init__(self):
        self.token_url = 'https://opentdb.com/api_token.php'
        self.question_url = 'https://opentdb.com/api.php'
        self.token = None
        self.csv_file = 'Islamic_questions.csv'

    def get_token(self):
        """Request a session token from the API to avoid duplicate questions."""
        parameters = {'command': 'request'}

        try:
            response = requests.get(self.token_url, params=parameters)
            if response.status_code == 200:
                token_data = response.json()
                if token_data['response_code'] == 0:
                    self.token = token_data['token']
                    return self.token
                else:
                    print('Error: Unable to retrieve token.')
                    return None
            else:
                print(f'Got status code {response.status_code}')
                return None
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            return None

    def get_questions_from_api(self, category, difficulty, question_type):
        """
        Fetch trivia questions from the API.

        Args:
            category: Subject category ID
            difficulty: 'easy', 'medium', or 'hard'
            question_type: 'multiple' or 'boolean'

        Returns:
            List of question dictionaries or None if error
        """
        # Get or refresh token
        if not self.token:
            self.token = self.get_token()

        parameters = {
            'amount': 10,
            'category': category,
            'difficulty': difficulty,
            'type': question_type,
        }

        if self.token:
            parameters['token'] = self.token

        try:
            response = requests.get(self.question_url, params=parameters)

            if response.status_code == 200:
                question_data = response.json()

                if question_data['response_code'] == 0:
                    questions = []
                    for data in question_data['results']:
                        # Shuffle options so correct answer isn't always in same position
                        options = data['incorrect_answers'] + [data['correct_answer']]
                        random.shuffle(options)

                        question = {
                            'question': unescape(data['question']),
                            'correct_answer': unescape(data['correct_answer']),
                            'options': [unescape(opt) for opt in options],
                            'difficulty': difficulty,
                            'category': category,
                        }
                        questions.append(question)
                    return questions

                elif question_data['response_code'] == 1:
                    print('Error: No questions found for this category/difficulty.')
                    return None

                elif question_data['response_code'] == 4:
                    print('Token expired. Refreshing...')
                    self.token = self.get_token()
                    return self.get_questions_from_api(category, difficulty, question_type)

                else:
                    print(f'Error: Response code {question_data["response_code"]}')
                    return None
            else:
                print(f'Error: Status code {response.status_code}')
                return None

        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            return None

    def get_questions_from_csv(self, category=None, difficulty=None, points_value=None):
        """
        Load questions from CSV file.

        CSV Format:
        question,correct_answer,option1,option2,option3,option4,difficulty,category,points

        Args:
            category: Filter by category (optional)
            difficulty: Filter by difficulty (optional)
            points_value: Filter by specific point value or 'mixed' (optional)

        Returns:
            List of question dictionaries or None if error
        """
        if not os.path.exists(self.csv_file):
            print(f"CSV file '{self.csv_file}' not found.")
            return None

        questions = []

        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)

                print(f"DEBUG: Looking for category='{category}', difficulty='{difficulty}', points='{points_value}'")

                for row in csv_reader:
                    # Filter by category if specified
                    if category and row.get('category', '').strip().lower() != category.strip().lower():
                        continue

                    # Filter by difficulty if specified (for non-Islamic)
                    if difficulty and not points_value and row.get('difficulty',
                                                                   '').strip().lower() != difficulty.strip().lower():
                        continue

                    # Filter by points value if specified (for Islamic categories)
                    if points_value and points_value != 'mixed':
                        try:
                            question_points = int(row.get('points', 100))
                            target_points = int(points_value)
                            if question_points != target_points:
                                continue
                        except ValueError:
                            continue

                    # Collect all options (skip empty ones)
                    options = []
                    for i in range(1, 5):
                        option_key = f'option{i}'
                        if option_key in row and row[option_key].strip():
                            options.append(row[option_key].strip())

                    # Add correct answer if not already in options
                    correct_answer = row['correct_answer'].strip()
                    if correct_answer not in options:
                        options.append(correct_answer)

                    # Shuffle options
                    random.shuffle(options)

                    question = {
                        'question': row['question'].strip(),
                        'correct_answer': correct_answer,
                        'options': options,
                        'difficulty': row.get('difficulty', 'medium').strip(),
                        'category': row.get('category', 'General').strip(),
                        'points': int(row.get('points', 100)) if row.get('points', '').strip() else 100,
                    }
                    questions.append(question)

            if not questions:
                print(f"DEBUG: No questions found. Checked {csv_reader.line_num - 1} rows.")
                print(f"DEBUG: Filters - category: {category}, difficulty: {difficulty}, points: {points_value}")
                return None

            # Shuffle and limit to 10 questions
            random.shuffle(questions)
            return questions[:10]

        except Exception as e:
            print(f"Error reading CSV: {e}")
            return None

    def get_questions(self, category, difficulty, question_type, source='api', points_value=None):
        """
        Get questions from specified source.

        Args:
            category: Subject category
            difficulty: 'easy', 'medium', or 'hard'
            question_type: 'multiple' or 'boolean' (API only)
            source: 'api', 'csv', or 'auto' (tries CSV first, then API)
            points_value: Specific point value for filtering (CSV only, for Islamic categories)

        Returns:
            List of question dictionaries or None if error
        """
        if source == 'csv':
            return self.get_questions_from_csv(category, difficulty, points_value)

        elif source == 'api':
            return self.get_questions_from_api(category, difficulty, question_type)

        elif source == 'auto':
            # Try CSV first, fallback to API
            questions = self.get_questions_from_csv(category, difficulty, points_value)
            if questions:
                print("Loaded questions from CSV")
                return questions
            else:
                print("CSV not available, fetching from API...")
                return self.get_questions_from_api(category, difficulty, question_type)

        else:
            print(f"Unknown source: {source}")
            return None

    def create_sample_csv(self):
        """Create a sample CSV file with example questions."""
        headers = ['question', 'correct_answer', 'option1', 'option2', 'option3', 'option4', 'difficulty', 'category',
                   'points']

        sample_questions = [
            {
                'question': 'What is the capital of France?',
                'correct_answer': 'Paris',
                'option1': 'London',
                'option2': 'Berlin',
                'option3': 'Madrid',
                'option4': 'Rome',
                'difficulty': 'easy',
                'category': 'Geography',
                'points': 100
            },
            {
                'question': 'Who painted the Mona Lisa?',
                'correct_answer': 'Leonardo da Vinci',
                'option1': 'Pablo Picasso',
                'option2': 'Vincent van Gogh',
                'option3': 'Michelangelo',
                'option4': 'Rembrandt',
                'difficulty': 'easy',
                'category': 'Art',
                'points': 100
            },
            {
                'question': 'What is the largest planet in our solar system?',
                'correct_answer': 'Jupiter',
                'option1': 'Saturn',
                'option2': 'Neptune',
                'option3': 'Earth',
                'option4': 'Mars',
                'difficulty': 'easy',
                'category': 'Science',
                'points': 100
            },
            {
                'question': 'In what year did World War II end?',
                'correct_answer': '1945',
                'option1': '1943',
                'option2': '1944',
                'option3': '1946',
                'option4': '1947',
                'difficulty': 'medium',
                'category': 'History',
                'points': 200
            },
            {
                'question': 'What is the chemical symbol for gold?',
                'correct_answer': 'Au',
                'option1': 'Go',
                'option2': 'Gd',
                'option3': 'Ag',
                'option4': 'Fe',
                'difficulty': 'medium',
                'category': 'Science',
                'points': 200
            },
        ]

        try:
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(sample_questions)
            print(f"Sample CSV created: {self.csv_file}")
            return True
        except Exception as e:
            print(f"Error creating sample CSV: {e}")
            return False


# Test the class
if __name__ == "__main__":
    quiz = QuizQuestions()

    # Create sample CSV if it doesn't exist
    if not os.path.exists(quiz.csv_file):
        print("Creating sample CSV file...")
        quiz.create_sample_csv()

    # Test CSV loading
    print("\n--- Testing CSV Questions ---")
    csv_questions = quiz.get_questions(category='Science', difficulty='easy',
                                       question_type='multiple', source='csv')
    if csv_questions:
        print(f"Loaded {len(csv_questions)} questions from CSV")
        print(f"First question: {csv_questions[0]['question']}")

    # Test API loading
    print("\n--- Testing API Questions ---")
    api_questions = quiz.get_questions(category='9', difficulty='easy',
                                       question_type='multiple', source='api')
    if api_questions:
        print(f"Loaded {len(api_questions)} questions from API")
        print(f"First question: {api_questions[0]['question']}")