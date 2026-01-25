import pygame
import sys
import csv
import os
from button import Button, OptionButton
from user import User
from question_ui import Question
from constants import *
from quiz_questions import QuizQuestions


class TriviaGame:
    """Main game class managing all game states and logic."""

    def __init__(self, screen):
        self.screen = screen
        self.user = User()
        self.current_question = 0
        self.questions = []
        self.start_time = 0
        self.game_state = 'menu'
        self.difficulty_level = None
        self.subject = None
        self.subject_name = None
        self.showing_answer = False
        self.answer_display_start_time = 0

        # Initialize API
        self.api_questions = QuizQuestions()

        # Fonts
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.large_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)

        # Load assets
        self.load_assets()

        # Button groups
        self.create_buttons()

        # Answer buttons (created dynamically)
        self.answer_buttons = pygame.sprite.Group()

    def load_assets(self):
        """Load images and sounds."""
        try:
            self.background = pygame.image.load('Background [MConverter.eu].png')
            self.background = pygame.transform.scale(
                self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            # Create default background if image not found
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill((20, 20, 40))

        try:
            self.frame_image = pygame.image.load('Frame.png')
            self.frame_image = pygame.transform.scale(
                self.frame_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.frame_image = None

        # Load sounds
        try:
            self.correct_sound = pygame.mixer.Sound('correct-6033.wav')
            self.wrong_sound = pygame.mixer.Sound('buzzer-or-wrong-answer-20582.wav')
            self.timer_sound = pygame.mixer.Sound('timer-with-chime-101253.wav')
            pygame.mixer.music.load('ethereal-ambient-music-55115.wav')
            pygame.mixer.music.play(-1)
        except:
            print("Warning: Some audio files not found. Game will run without sound.")
            self.correct_sound = None
            self.wrong_sound = None
            self.timer_sound = None

    def create_buttons(self):
        """Create menu and difficulty selection buttons."""
        self.subject_buttons = pygame.sprite.Group(
            Button(SCREEN_WIDTH // 2 - 100, 150, 200, 50,
                   'General Knowledge', self.font, RED, BLACK, 'General Knowledge'),
            Button(SCREEN_WIDTH // 2 - 100, 230, 200, 50,
                   'Science', self.font, ORANGE, WHITE, 'Science'),
            Button(SCREEN_WIDTH // 2 - 100, 310, 200, 50,
                   'History', self.font, YELLOW, BLACK, 'History'),
            Button(SCREEN_WIDTH // 2 - 100, 390, 200, 50,
                   'Entertainment', self.font, GREEN, BLACK, 'Entertainment'),
            Button(SCREEN_WIDTH // 2 - 100, 470, 200, 50,
                   'Geography', self.font, BLUE, WHITE, 'Geography'),
            Button(SCREEN_WIDTH // 2 - 100, 550, 200, 50,
                   'Sports', self.font, CYAN, BLACK, 'Sports'),
        )

        self.difficulty_buttons = pygame.sprite.Group(
            Button(SCREEN_WIDTH // 2 - 100, 250, 200, 50,
                   'Easy', self.font, GREEN, BLACK, 'easy'),
            Button(SCREEN_WIDTH // 2 - 100, 350, 200, 50,
                   'Medium', self.font, ORANGE, BLACK, 'medium'),
            Button(SCREEN_WIDTH // 2 - 100, 450, 200, 50,
                   'Hard', self.font, RED, WHITE, 'hard')
        )

    def render_text(self, text, font, color, surface, x, y):
        """Helper method to render text on surface."""
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect(topleft=(x, y))
        surface.blit(text_obj, text_rect)

    def display_score(self, score):
        """Display current score on screen."""
        self.render_text(f'Score: {score}', self.font, WHITE,
                         self.screen, SCREEN_WIDTH - 200, 20)

    def display_timer(self, time_left):
        """Display remaining time on screen."""
        seconds = max(0, time_left // 1000)
        color = RED if seconds <= 3 else WHITE
        self.render_text(f'Time: {seconds}s', self.font, color,
                         self.screen, SCREEN_WIDTH // 2 - 50, 20)

    def select_subject(self):
        """Display subject selection screen."""
        self.screen.blit(self.background, (0, 0))
        self.render_text('Choose Your Subject', self.large_font, WHITE,
                         self.screen, SCREEN_WIDTH // 2 - 200, 50)

        for button in self.subject_buttons:
            button.draw(self.screen)

    def select_difficulty(self):
        """Display difficulty selection screen."""
        self.screen.blit(self.background, (0, 0))
        self.render_text('Select Difficulty Level', self.large_font, WHITE,
                         self.screen, SCREEN_WIDTH // 2 - 250, 50)
        self.render_text(f'Subject: {self.subject_name}', self.font, BRIGHT_COLOR,
                         self.screen, SCREEN_WIDTH // 2 - 150, 150)

        for button in self.difficulty_buttons:
            button.draw(self.screen)

    def fetch_questions(self):
        """Fetch questions from API and start game."""
        questions = self.api_questions.get_questions(
            self.subject, self.difficulty_level, 'multiple')

        if questions:
            self.questions = questions
            self.current_question = 0
            self.user.reset_score()
            self.start_time = pygame.time.get_ticks()
            self.game_state = 'game'
        else:
            print("Error fetching questions. Returning to menu.")
            self.game_state = 'menu'

    def display_game(self):
        """Main game display logic."""
        self.screen.blit(self.background, (0, 0))
        if self.frame_image:
            self.screen.blit(self.frame_image, (0, 0))

        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time
        time_left = TIME_LIMIT - elapsed_time

        # Display correct answer feedback
        if self.showing_answer:
            if current_time - self.answer_display_start_time > ANSWER_DISPLAY_TIME:
                self.showing_answer = False
                self.current_question += 1
                self.start_time = current_time

                if self.current_question >= len(self.questions):
                    self.game_state = 'score'
                return
            else:
                self.screen.blit(self.background, (0, 0))
                self.render_text('Correct Answer:', self.large_font, BRIGHT_COLOR,
                                 self.screen, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50)
                self.render_text(
                    self.questions[self.current_question]['correct_answer'],
                    self.font, GREEN, self.screen,
                    SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 20)
                return

        # Time's up
        if time_left <= 0:
            if self.wrong_sound:
                self.wrong_sound.play()
            self.current_question += 1
            self.start_time = current_time

            if self.current_question >= len(self.questions):
                self.game_state = 'score'
            return

        # Display question
        if self.current_question < len(self.questions):
            question_sprite = Question(
                self.questions[self.current_question],
                self.font, 20, 100)
            self.screen.blit(question_sprite.image, question_sprite.rect)

            # Create answer buttons
            self.answer_buttons.empty()
            for idx, option in enumerate(self.questions[self.current_question]["options"]):
                button = OptionButton(
                    100, 350 + 70 * idx, SCREEN_WIDTH - 200, 60,
                    f"{chr(65 + idx)}. {option}", self.font,
                    BUTTON_BG_COLOR, BUTTON_TEXT_COLOR, BUTTON_HOVER_COLOR)
                self.answer_buttons.add(button)

            self.answer_buttons.update(pygame.mouse.get_pos())
            self.answer_buttons.draw(self.screen)

            self.display_score(self.user.get_score())
            self.display_timer(time_left)

    def check_answer(self, selected_option):
        """Check if selected answer is correct."""
        correct_answer = self.questions[self.current_question]['correct_answer']

        if selected_option == correct_answer:
            if self.correct_sound:
                self.correct_sound.play()
            self.user.increase_score()
        else:
            if self.wrong_sound:
                self.wrong_sound.play()

        self.showing_answer = True
        self.answer_display_start_time = pygame.time.get_ticks()

    def display_score_screen(self):
        """Display final score and statistics."""
        self.screen.blit(self.background, (0, 0))

        total_questions = len(self.questions)
        score = self.user.get_score()
        percentage = (score / total_questions) * 100 if total_questions > 0 else 0

        # Display results
        self.render_text("Quiz Complete!", self.large_font, BRIGHT_COLOR,
                         self.screen, SCREEN_WIDTH // 2 - 150, 150)
        self.render_text(f"Subject: {self.subject_name}", self.font, WHITE,
                         self.screen, SCREEN_WIDTH // 2 - 150, 250)
        self.render_text(f"Difficulty: {self.difficulty_level.capitalize()}",
                         self.font, WHITE, self.screen, SCREEN_WIDTH // 2 - 150, 300)
        self.render_text(f"Score: {score} / {total_questions}", self.font, GREEN,
                         self.screen, SCREEN_WIDTH // 2 - 150, 350)
        self.render_text(f"Percentage: {percentage:.1f}%", self.font, BRIGHT_COLOR,
                         self.screen, SCREEN_WIDTH // 2 - 150, 400)

        # Grade
        if percentage >= 90:
            grade = "Excellent! 🌟"
        elif percentage >= 70:
            grade = "Good Job! 👍"
        elif percentage >= 50:
            grade = "Not Bad! 📚"
        else:
            grade = "Keep Practicing! 💪"

        self.render_text(grade, self.large_font, YELLOW,
                         self.screen, SCREEN_WIDTH // 2 - 150, 480)

        self.render_text("Click anywhere to return to menu", self.small_font, GRAY,
                         self.screen, SCREEN_WIDTH // 2 - 200, 650)

    def save_results(self):
        """Save game results to CSV file."""
        headers = ['Subject', 'Difficulty', 'Score', 'Total Questions', 'Percentage']
        file_name = 'trivia_results.csv'

        total_questions = len(self.questions)
        score = self.user.get_score()
        percentage = (score / total_questions) * 100 if total_questions > 0 else 0

        player_data = [
            self.subject_name,
            self.difficulty_level.capitalize(),
            score,
            total_questions,
            f"{percentage:.1f}%"
        ]

        file_exists = os.path.exists(file_name)

        try:
            with open(file_name, 'a', newline='') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(headers)
                writer.writerow(player_data)
        except Exception as e:
            print(f"Error saving results: {e}")

    def run(self):
        """Main game loop."""
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    # Menu state
                    if self.game_state == 'menu':
                        for button in self.subject_buttons:
                            if button.is_clicked(pos):
                                self.subject_name = button.action
                                self.subject = SUBJECTS.get(button.action)
                                self.game_state = 'selecting_difficulty'

                    # Difficulty selection
                    elif self.game_state == 'selecting_difficulty':
                        for button in self.difficulty_buttons:
                            if button.is_clicked(pos):
                                self.difficulty_level = button.action
                                self.fetch_questions()

                    # Game state - answer selection
                    elif self.game_state == 'game' and not self.showing_answer:
                        for idx, button in enumerate(self.answer_buttons):
                            if button.is_clicked(pos):
                                selected = self.questions[self.current_question]['options'][idx]
                                self.check_answer(selected)

                    # Score screen
                    elif self.game_state == 'score':
                        self.save_results()
                        self.game_state = 'menu'

            # Render appropriate screen
            if self.game_state == 'menu':
                self.select_subject()
            elif self.game_state == 'selecting_difficulty':
                self.select_difficulty()
            elif self.game_state == 'game':
                self.display_game()
            elif self.game_state == 'score':
                self.display_score_screen()

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()