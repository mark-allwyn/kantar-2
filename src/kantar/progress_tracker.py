"""
Progress tracking utilities for synthetic data generation.

Provides progress bars and ETA estimates for long-running operations.
"""

from typing import Optional, Dict, Any
from tqdm import tqdm
from datetime import datetime, timedelta
import time


class GenerationProgressTracker:
    """
    Tracks progress during synthetic respondent generation.

    Features:
    - Progress bar with ETA
    - Respondent generation rate
    - Time estimates
    - Real-time cost tracking (optional)
    """

    def __init__(self,
                 total_respondents: int,
                 description: str = "Generating respondents",
                 show_cost: bool = False,
                 cost_per_respondent: Optional[float] = None):
        """
        Initialize progress tracker.

        Args:
            total_respondents: Total number of respondents to generate
            description: Description for progress bar
            show_cost: Whether to show cost estimates
            cost_per_respondent: Estimated cost per respondent
        """
        self.total_respondents = total_respondents
        self.description = description
        self.show_cost = show_cost
        self.cost_per_respondent = cost_per_respondent or 0.01  # Default estimate

        self.start_time = None
        self.completed = 0

        # Create progress bar
        self.pbar = tqdm(
            total=total_respondents,
            desc=description,
            unit="resp",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )

    def start(self):
        """Start tracking progress."""
        self.start_time = time.time()

    def update(self, n: int = 1, **kwargs):
        """
        Update progress bar.

        Args:
            n: Number of respondents completed
            **kwargs: Additional info to display in postfix
        """
        self.completed += n

        # Calculate stats
        if self.start_time:
            elapsed = time.time() - self.start_time
            rate = self.completed / elapsed if elapsed > 0 else 0

            postfix = {
                "rate": f"{rate:.2f} resp/s"
            }

            if self.show_cost:
                cost_so_far = self.completed * self.cost_per_respondent
                total_cost = self.total_respondents * self.cost_per_respondent
                postfix["cost"] = f"${cost_so_far:.2f}/${total_cost:.2f}"

            # Add custom postfix
            postfix.update(kwargs)

            self.pbar.set_postfix(postfix)

        self.pbar.update(n)

    def close(self):
        """Close progress bar."""
        self.pbar.close()

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class ValidationProgressTracker:
    """
    Tracks progress during validation calculations.
    """

    def __init__(self, total_questions: int, description: str = "Validating questions"):
        """
        Initialize validation progress tracker.

        Args:
            total_questions: Total number of questions to validate
            description: Description for progress bar
        """
        self.total_questions = total_questions
        self.description = description

        self.pbar = tqdm(
            total=total_questions,
            desc=description,
            unit="q",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
        )

    def update(self, n: int = 1, **kwargs):
        """Update progress."""
        if kwargs:
            self.pbar.set_postfix(kwargs)
        self.pbar.update(n)

    def close(self):
        """Close progress bar."""
        self.pbar.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def format_time_remaining(seconds: float) -> str:
    """
    Format time remaining in human-readable format.

    Args:
        seconds: Number of seconds

    Returns:
        Formatted string (e.g., "2m 30s", "1h 15m")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"


def estimate_generation_time(num_respondents: int,
                             concepts_per_respondent: int = 3,
                             questions_per_concept: int = 10,
                             seconds_per_question: float = 0.5) -> Dict[str, Any]:
    """
    Estimate time required for generation.

    Args:
        num_respondents: Number of respondents to generate
        concepts_per_respondent: Concepts each respondent tests
        questions_per_concept: Questions per concept
        seconds_per_question: Average time per question (LLM call)

    Returns:
        Dictionary with time estimates
    """
    total_questions = num_respondents * concepts_per_respondent * questions_per_concept
    total_seconds = total_questions * seconds_per_question

    # Add overhead for persona generation, formatting, etc (20%)
    total_seconds *= 1.2

    return {
        "total_questions": total_questions,
        "estimated_seconds": total_seconds,
        "estimated_formatted": format_time_remaining(total_seconds),
        "estimated_datetime": datetime.now() + timedelta(seconds=total_seconds)
    }
