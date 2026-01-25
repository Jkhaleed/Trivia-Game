class User:
    """Manages user score for the trivia game."""

    def __init__(self):
        self.score = 0

    def increase_score(self):
        """Increment the user's score by 1."""
        self.score += 1

    def get_score(self):
        """Return the current score."""
        return self.score

    def reset_score(self):
        """Reset the score to 0."""
        self.score = 0