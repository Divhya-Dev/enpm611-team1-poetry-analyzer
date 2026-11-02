"""Analyze discussion activity in Poetry GitHub issues."""

from collections import defaultdict
from datetime import datetime, timezone
from statistics import median
from typing import Dict, List, Tuple

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from data_loader import DataLoader
from model import Event, Issue


class DiscussionTrendAnalysis:
    """Summarize issue discussion patterns and save trend visualizations."""


    @staticmethod
    def _count_comments(issue: Issue) -> int:
        """Count comment events once, excluding non-comment timeline events."""
        events: List[Event] = issue.events or []
        return sum(
            1
            for event in events
            if event is not None and event.event_type == 'commented'
        )


@staticmethod
def _parse_event_date(date_value):
    """Convert a datetime or ISO timestamp string into a UTC datetime."""
    if date_value is None:
        return None

    try:
        if isinstance(date_value, str):
            date_value = datetime.fromisoformat(
                date_value.replace('Z', '+00:00')
            )

        if not isinstance(date_value, datetime):
            return None

        if date_value.tzinfo is None:
            return date_value.replace(tzinfo=timezone.utc)

        return date_value.astimezone(timezone.utc)

    except (ValueError, TypeError):
        return None