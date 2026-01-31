import pygame
import sys
import csv
import os
from button import Button, OptionButton
from user import User
from question_ui import Question
from constants import *
from quiz_questions import QuizQuestions

# Try to import JeopardyBoard, use fallback if not available
try:
    from jeopardy_board import JeopardyBoard

    JEOPARDY_AVAILABLE = True
except ImportError:
    JEOPARDY_AVAILABLE = False
    print("Warning: jeopardy_board.py not found. Jeopardy mode will be disabled.")


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
        self.question_source = 'auto'  # 'api', 'csv', or 'auto'
        self.is_islamic_subject = False  # Track if Islamic category selected
        self.use_points_difficulty = False  # For Jeopardy-style point selection
        self.jeopardy_mode = False  # Track if using interactive board
        self.jeopardy_board = None  # Will hold JeopardyBoard instance
        self.current_selected_category = None  # For board mode
        self.current_selected_points = None  # For board mode

        # Initialize API
        self.api_questions = QuizQuestions()

        # Fonts (must be created BEFORE JeopardyBoard)
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.large_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)

        # Initialize Jeopardy board if available (AFTER fonts are created)
        if JEOPARDY_AVAILABLE:
            self.jeopardy_board = JeopardyBoard(screen, self.font, self.small_font)
        else:
            self.jeopardy_board = None

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
        # General subjects (work with API and CSV)
        self.subject_buttons = pygame.sprite.Group(
            Button(150, 150, 200, 50,
                   'General Knowledge', self.font, RED, BLACK, 'General Knowledge'),
            Button(150, 210, 200, 50,
                   'Science', self.font, ORANGE, WHITE, 'Science'),
            Button(150, 270, 200, 50,
                   'History', self.font, YELLOW, BLACK, 'History'),
            Button(150, 330, 200, 50,
                   'Entertainment', self.font, GREEN, BLACK, 'Entertainment'),
            Button(150, 390, 200, 50,
                   'Geography', self.font, BLUE, WHITE, 'Geography'),
            Button(150, 450, 200, 50,
                   'Sports', self.font, CYAN, BLACK, 'Sports'),
        )

        # Islamic subjects (CSV only)
        islamic_button_list = [
            Button(850, 150, 200, 50,
                   'Quran', self.font, PURPLE, WHITE, 'Quran'),
            Button(850, 210, 200, 50,
                   'Seerah', self.font, VIOLET, BLACK, 'Seerah'),
            Button(850, 270, 200, 50,
                   'Dua And Dhikr', self.font, GREEN, BLACK, 'Dua And Dhikr'),
            Button(850, 330, 200, 50,
                   'Salah', self.font, BLUE, WHITE, 'Salah'),
            Button(850, 390, 200, 50,
                   'Prophets', self.font, BRIGHT_COLOR, BLACK, 'Prophets'),
        ]

        # Only add Jeopardy Board button if available
        if JEOPARDY_AVAILABLE:
            islamic_button_list.append(
                Button(850, 450, 200, 50,
                       'Jeopardy Board', self.font, RED, WHITE, 'jeopardy_board')
            )

        self.islamic_buttons = pygame.sprite.Group(*islamic_button_list)

        self.difficulty_buttons = pygame.sprite.Group(
            Button(SCREEN_WIDTH // 2 - 100, 250, 200, 50,
                   'Easy', self.font, GREEN, BLACK, 'easy'),
            Button(SCREEN_WIDTH // 2 - 100, 350, 200, 50,
                   'Medium', self.font, ORANGE, BLACK, 'medium'),
            Button(SCREEN_WIDTH // 2 - 100, 450, 200, 50,
                   'Hard', self.font, RED, WHITE, 'hard')
        )

        # Points-based difficulty buttons (for Islamic categories)
        self.points_buttons = pygame.sprite.Group(
            Button(200, 200, 120, 50, '100', self.font, GREEN, BLACK, '100'),
            Button(350, 200, 120, 50, '200', self.font, GREEN, BLACK, '200'),
            Button(500, 200, 120, 50, '300', self.font, YELLOW, BLACK, '300'),
            Button(650, 200, 120, 50, '400', self.font, YELLOW, BLACK, '400'),
            Button(800, 200, 120, 50, '500', self.font, ORANGE, BLACK, '500'),
            Button(200, 280, 120, 50, '600', self.font, RED, WHITE, '600'),
            Button(350, 280, 120, 50, '700', self.font, RED, WHITE, '700'),
            Button(500, 280, 180, 50, 'Mixed', self.font, PURPLE, WHITE, 'mixed'),
        )

        # Source selection buttons
        self.source_buttons = pygame.sprite.Group(
            Button(SCREEN_WIDTH // 2 - 250, 600, 150, 40,
                   'API', self.small_font, BLUE, WHITE, 'api'),
            Button(SCREEN_WIDTH // 2 - 75, 600, 150, 40,
                   'CSV', self.small_font, PURPLE, WHITE, 'csv'),
            Button(SCREEN_WIDTH // 2 + 100, 600, 150, 40,
                   'Auto', self.small_font, GREEN, BLACK, 'auto')
        )

    def render_text(self, text, font, color, surface, x, y):
        """Helper method to render text on surface."""
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect(topleft=(x, y))
        surface.blit(text_obj, text_rect)

    def display_score(self, score, points):
        """Display current score and points on screen."""
        self.render_text(f'Correct: {score}', self.font, WHITE,
                         self.screen, SCREEN_WIDTH - 200, 20)
        self.render_text(f'Points: {points}', self.font, BRIGHT_COLOR,
                         self.screen, SCREEN_WIDTH - 200, 55)

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

        # General subjects section
        self.render_text('General Topics', self.font, CYAN,
                         self.screen, 150, 110)
        for button in self.subject_buttons:
            button.draw(self.screen)

        # Islamic subjects section
        self.render_text('Islamic Topics (CSV Only)', self.font, BRIGHT_COLOR,
                         self.screen, 850, 110)
        for button in self.islamic_buttons:
            button.draw(self.screen)

        # Display question source selector
        self.render_text('Question Source:', self.font, BRIGHT_COLOR,
                         self.screen, SCREEN_WIDTH // 2 - 100, 560)

        for button in self.source_buttons:
            # Highlight selected source
            if button.action == self.question_source:
                pygame.draw.rect(self.screen, BRIGHT_COLOR,
                                 button.rect.inflate(8, 8), 3)
            button.draw(self.screen)

        # Show CSV status
        csv_exists = os.path.exists(self.api_questions.csv_file)
        csv_status = "CSV Available ✓" if csv_exists else "CSV Not Found ✗"
        csv_color = GREEN if csv_exists else RED
        self.render_text(csv_status, self.small_font, csv_color,
                         self.screen, SCREEN_WIDTH // 2 - 80, 660)

    def select_difficulty(self):
        """Display difficulty selection screen."""
        self.screen.blit(self.background, (0, 0))

        if self.is_islamic_subject:
            # Points-based selection for Islamic subjects
            self.render_text('Select Point Value (Jeopardy Style)', self.large_font, WHITE,
                             self.screen, SCREEN_WIDTH // 2 - 300, 50)
            self.render_text(f'Subject: {self.subject_name}', self.font, BRIGHT_COLOR,
                             self.screen, SCREEN_WIDTH // 2 - 150, 120)
            self.render_text('Choose specific point values or Mixed for all', self.small_font, CYAN,
                             self.screen, SCREEN_WIDTH // 2 - 200, 160)

            for button in self.points_buttons:
                button.draw(self.screen)

            # Legend
            self.render_text('Green: 100-200 (Easier)', self.small_font, GREEN,
                             self.screen, SCREEN_WIDTH // 2 - 250, 380)
            self.render_text('Yellow: 300-400 (Medium)', self.small_font, YELLOW,
                             self.screen, SCREEN_WIDTH // 2 - 250, 410)
            self.render_text('Orange: 500 (Hard)', self.small_font, ORANGE,
                             self.screen, SCREEN_WIDTH // 2 - 250, 440)
            self.render_text('Red: 600-700 (Expert)', self.small_font, RED,
                             self.screen, SCREEN_WIDTH // 2 - 250, 470)
        else:
            # Regular difficulty for general subjects
            self.render_text('Select Difficulty Level', self.large_font, WHITE,
                             self.screen, SCREEN_WIDTH // 2 - 250, 50)
            self.render_text(f'Subject: {self.subject_name}', self.font, BRIGHT_COLOR,
                             self.screen, SCREEN_WIDTH // 2 - 150, 150)
            self.render_text(f'Source: {self.question_source.upper()}', self.small_font, CYAN,
                             self.screen, SCREEN_WIDTH // 2 - 100, 180)

            for button in self.difficulty_buttons:
                button.draw(self.screen)

    def fetch_single_question(self, category, points):
        """Fetch a single question for Jeopardy board mode."""
        questions = self.api_questions.get_questions(
            category=category,
            difficulty=None,
            question_type='multiple',
            source='csv',
            points_value=str(points)
        )

        if questions and len(questions) > 0:
            # Just get the first question (there should only be one at this point value)
            return questions[0]
        else:
            print(f"No question found for {category} at {points} points")
            return None

    def fetch_questions(self):
        """Fetch questions from selected source and start game."""
        # Force CSV mode for Islamic subjects
        source = 'csv' if self.is_islamic_subject else self.question_source

        if self.is_islamic_subject and source != 'csv':
            print("Islamic categories only available in CSV mode. Switching to CSV...")

        questions = self.api_questions.get_questions(
            category=self.subject,
            difficulty=self.difficulty_level,
            question_type='multiple',
            source=source
        )

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

                # In Jeopardy mode, return to board instead of next question
                if self.jeopardy_mode and self.jeopardy_board:
                    if self.jeopardy_board.is_board_complete():
                        self.game_state = 'score'
                    else:
                        self.game_state = 'jeopardy_board'
                elif self.current_question >= len(self.questions):
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
            # Show question with points value
            current_q = self.questions[self.current_question]
            points_value = current_q.get('points', 100)

            # Display points value and category (if in board mode)
            if self.jeopardy_mode:
                self.render_text(f'Category: {current_q.get("category", "Unknown")}',
                                 self.font, BRIGHT_COLOR,
                                 self.screen, 20, 20)
                self.render_text(f'Value: {points_value} points',
                                 self.font, YELLOW,
                                 self.screen, 20, 60)
            else:
                self.render_text(f'Question Value: {points_value} points',
                                 self.font, BRIGHT_COLOR,
                                 self.screen, 20, 60)

            question_sprite = Question(current_q, self.font, 20, 100)
            self.screen.blit(question_sprite.image, question_sprite.rect)

            # Create answer buttons
            self.answer_buttons.empty()
            for idx, option in enumerate(current_q["options"]):
                button = OptionButton(
                    100, 350 + 70 * idx, SCREEN_WIDTH - 200, 60,
                    f"{chr(65 + idx)}. {option}", self.font,
                    BUTTON_BG_COLOR, BUTTON_TEXT_COLOR, BUTTON_HOVER_COLOR)
                self.answer_buttons.add(button)

            self.answer_buttons.update(pygame.mouse.get_pos())
            self.answer_buttons.draw(self.screen)

            self.display_score(self.user.get_score(), self.user.get_points())
            self.display_timer(time_left)

    def check_answer(self, selected_option):
        """Check if selected answer is correct."""
        current_q = self.questions[self.current_question]
        correct_answer = current_q['correct_answer']
        points_value = current_q.get('points', 100)

        if selected_option == correct_answer:
            if self.correct_sound:
                self.correct_sound.play()
            self.user.increase_score(points_value)
        else:
            if self.wrong_sound:
                self.wrong_sound.play()

        # Mark as answered on board if in Jeopardy mode
        if self.jeopardy_mode and self.jeopardy_board and self.current_selected_category and self.current_selected_points:
            self.jeopardy_board.mark_answered(self.current_selected_category, self.current_selected_points)

        self.showing_answer = True
        self.answer_display_start_time = pygame.time.get_ticks()

    def display_score_screen(self):
        """Display final score and statistics."""
        self.screen.blit(self.background, (0, 0))

        if self.jeopardy_mode and self.jeopardy_board:
            # Special display for Jeopardy board completion
            total_questions = self.jeopardy_board.get_total_questions()
            answered = self.jeopardy_board.get_questions_answered()
        else:
            total_questions = len(self.questions)
            answered = self.user.get_score()

        score = self.user.get_score()
        points = self.user.get_points()
        percentage = (score / total_questions) * 100 if total_questions > 0 else 0

        # Calculate possible points
        if self.jeopardy_mode:
            # All categories, all point values (100-700)
            possible_points = 5 * (100 + 200 + 300 + 400 + 500 + 600 + 700)  # 5 categories
        else:
            possible_points = sum(q.get('points', 100) for q in self.questions)

        # Display results
        if self.jeopardy_mode:
            self.render_text("Jeopardy Board Complete!", self.large_font, BRIGHT_COLOR,
                             self.screen, SCREEN_WIDTH // 2 - 250, 120)
        else:
            self.render_text("Quiz Complete!", self.large_font, BRIGHT_COLOR,
                             self.screen, SCREEN_WIDTH // 2 - 150, 120)

        if not self.jeopardy_mode:
            self.render_text(f"Subject: {self.subject_name}", self.font, WHITE,
                             self.screen, SCREEN_WIDTH // 2 - 150, 220)

            # Show difficulty or points value
            if self.use_points_difficulty:
                diff_text = f"Point Value: {self.difficulty_level}"
                if self.difficulty_level == 'mixed':
                    diff_text = "Point Value: Mixed (100-700)"
            else:
                diff_text = f"Difficulty: {self.difficulty_level.capitalize()}"

            self.render_text(diff_text, self.font, WHITE,
                             self.screen, SCREEN_WIDTH // 2 - 150, 260)
            self.render_text(f"Source: {self.question_source.upper()}",
                             self.font, CYAN, self.screen, SCREEN_WIDTH // 2 - 150, 300)
        else:
            self.render_text("Islamic Trivia - All Categories", self.font, CYAN,
                             self.screen, SCREEN_WIDTH // 2 - 200, 220)

        # Score display
        y_offset = 350 if not self.jeopardy_mode else 280

        self.render_text(f"Correct Answers: {score} / {total_questions}",
                         self.font, GREEN, self.screen, SCREEN_WIDTH // 2 - 150, y_offset)
        self.render_text(f"Total Points: {points} / {possible_points}",
                         self.large_font, BRIGHT_COLOR,
                         self.screen, SCREEN_WIDTH // 2 - 150, y_offset + 40)
        self.render_text(f"Percentage: {percentage:.1f}%", self.font, YELLOW,
                         self.screen, SCREEN_WIDTH // 2 - 150, y_offset + 100)

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
                         self.screen, SCREEN_WIDTH // 2 - 150, y_offset + 170)

        self.render_text("Click anywhere to return to menu", self.small_font, GRAY,
                         self.screen, SCREEN_WIDTH // 2 - 200, 650)

    def save_results(self):
        """Save game results to CSV file."""
        headers = ['Subject', 'Difficulty/Points', 'Source', 'Correct', 'Total Questions', 'Points', 'Possible Points',
                   'Percentage']
        file_name = 'trivia_results.csv'

        if self.jeopardy_mode and self.jeopardy_board:
            total_questions = self.jeopardy_board.get_total_questions()
            subject_display = "Islamic Board (All)"
            diff_display = "Jeopardy Mode"
            possible_points = 5 * (100 + 200 + 300 + 400 + 500 + 600 + 700)
        else:
            total_questions = len(self.questions)
            subject_display = self.subject_name
            # Format difficulty/points display
            if self.use_points_difficulty:
                diff_display = f"{self.difficulty_level} pts" if self.difficulty_level != 'mixed' else "Mixed"
            else:
                diff_display = self.difficulty_level.capitalize()
            possible_points = sum(q.get('points', 100) for q in self.questions)

        score = self.user.get_score()
        points = self.user.get_points()
        percentage = (score / total_questions) * 100 if total_questions > 0 else 0

        player_data = [
            subject_display,
            diff_display,
            self.question_source.upper(),
            score,
            total_questions,
            points,
            possible_points,
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
                        # Check source buttons
                        for button in self.source_buttons:
                            if button.is_clicked(pos):
                                self.question_source = button.action

                        # Check general subject buttons
                        for button in self.subject_buttons:
                            if button.is_clicked(pos):
                                self.subject_name = button.action
                                self.subject = SUBJECTS.get(button.action)
                                self.is_islamic_subject = False
                                self.game_state = 'selecting_difficulty'

                        # Check Islamic subject buttons
                        for button in self.islamic_buttons:
                            if button.is_clicked(pos):
                                from constants import ISLAMIC_SUBJECTS

                                # Special handling for Jeopardy Board mode
                                if button.action == 'jeopardy_board':
                                    if JEOPARDY_AVAILABLE and self.jeopardy_board:
                                        self.jeopardy_mode = True
                                        self.is_islamic_subject = True
                                        self.jeopardy_board.reset_board()
                                        self.user.reset_score()
                                        self.game_state = 'jeopardy_board'
                                    else:
                                        print("Jeopardy board not available - missing jeopardy_board.py")
                                else:
                                    self.subject_name = button.action
                                    self.subject = ISLAMIC_SUBJECTS.get(button.action)
                                    self.is_islamic_subject = True
                                    self.jeopardy_mode = False
                                    self.game_state = 'selecting_difficulty'

                    # Jeopardy Board state
                    elif self.game_state == 'jeopardy_board':
                        if self.jeopardy_board:
                            clicked = self.jeopardy_board.get_clicked_question(pos)
                            if clicked:
                                category, points = clicked
                                self.current_selected_category = category
                                self.current_selected_points = points

                                # Fetch single question for this category/points
                                question = self.fetch_single_question(category, points)
                                if question:
                                    self.questions = [question]
                                    self.current_question = 0
                                    self.start_time = pygame.time.get_ticks()
                                    self.game_state = 'game'

                    # Difficulty selection
                    elif self.game_state == 'selecting_difficulty':
                        if self.is_islamic_subject:
                            # Check points buttons for Islamic subjects
                            for button in self.points_buttons:
                                if button.is_clicked(pos):
                                    self.difficulty_level = button.action
                                    self.use_points_difficulty = True
                                    self.fetch_questions()
                        else:
                            # Check regular difficulty buttons
                            for button in self.difficulty_buttons:
                                if button.is_clicked(pos):
                                    self.difficulty_level = button.action
                                    self.use_points_difficulty = False
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
                        self.jeopardy_mode = False  # Reset for next game
                        self.game_state = 'menu'

            # Render appropriate screen
            if self.game_state == 'menu':
                self.select_subject()
            elif self.game_state == 'jeopardy_board':
                self.screen.blit(self.background, (0, 0))
                if self.jeopardy_board:
                    self.jeopardy_board.draw_board(pygame.mouse.get_pos())
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