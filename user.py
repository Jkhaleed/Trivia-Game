class User:
    """Manages user score for the trivia game."""

    def __init__(self):
        self.score = 0
        self.points = 0  # Track points separately

    def increase_score(self, points=1):
        """Increment the user's score by 1 and add points."""
        self.score += 1
        self.points += points

    def get_score(self):
        """Return the current score (number of correct answers)."""
        return self.score

    def get_points(self):
        """Return the current points total."""
        return self.points

    def reset_score(self):
        """Reset both score and points to 0."""
        self.score = 0
        self.points = 0