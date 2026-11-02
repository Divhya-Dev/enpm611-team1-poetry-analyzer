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



    @staticmethod
    def _group_monthly_activity(
        issue_comment_counts: List[Tuple[Issue, int]]
    ) -> Dict[datetime, Dict[str, int]]:
        """Group issue counts and their comments by issue creation month."""
        activity = defaultdict(lambda: {'issues': 0, 'comments': 0})

        for issue, comment_count in issue_comment_counts:
            created_date = issue.created_date

            if not isinstance(created_date, datetime):
                continue

            month = datetime(created_date.year, created_date.month, 1)
            activity[month]['issues'] += 1
            activity[month]['comments'] += comment_count

        return dict(sorted(activity.items()))


    def run(self) -> None:
            """Load issues, report discussion patterns, and display charts."""
            issues: List[Issue] = DataLoader().get_issues() or []
    
            issue_comment_counts = [
                (issue, self._count_comments(issue))
                for issue in issues
            ]
    
            total_comments = sum(
                comment_count for _, comment_count in issue_comment_counts
            )
    
            monthly_activity = self._group_monthly_activity(
                issue_comment_counts
            )

    
    
if __name__ == '__main__':
        DiscussionTrendAnalysis().run()
    