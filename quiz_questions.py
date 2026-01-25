import requests
import random
from html import unescape


class QuizQuestions:
    """Fetches trivia questions from the Open Trivia Database API."""

    def __init__(self):
        self.token_url = 'https://opentdb.com/api_token.php'
        self.question_url = 'https://opentdb.com/api.php'
        self.token = None

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

    def get_questions(self, category, difficulty, question_type):
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
                    return self.get_questions(category, difficulty, question_type)

                else:
                    print(f'Error: Response code {question_data["response_code"]}')
                    return None
            else:
                print(f'Error: Status code {response.status_code}')
                return None

        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            return None