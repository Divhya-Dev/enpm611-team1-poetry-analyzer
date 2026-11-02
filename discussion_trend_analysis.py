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


    @staticmethod
    def _get_intensity_distribution(
        issue_comment_counts: List[Tuple[Issue, int]]
    ) -> Dict[str, int]:
        """Classify issues by their number of comment events."""
        distribution = {'Low': 0, 'Medium': 0, 'High': 0}

        for _, comment_count in issue_comment_counts:
            if comment_count <= 2:
                distribution['Low'] += 1
            elif comment_count <= 10:
                distribution['Medium'] += 1
            else:
                distribution['High'] += 1

        return distribution


    @staticmethod
    def _get_top_discussed_issues(
        issue_comment_counts: List[Tuple[Issue, int]], limit: int = 5
    ) -> List[Tuple[Issue, int]]:
        """Return the top issues, including every issue tied at the cutoff."""
        ranked_issues = sorted(
            issue_comment_counts,
            key=lambda item: (
                -item[1],
                item[0].number,
                item[0].title or '',
            ),
        )

        if not ranked_issues or limit <= 0:
            return []

        if len(ranked_issues) <= limit:
            return ranked_issues

        cutoff_count = ranked_issues[limit - 1][1]

        return [
            item for item in ranked_issues if item[1] >= cutoff_count
        ]
    

    @staticmethod
    def _get_discussion_hotspots(
        issue_comment_counts: List[Tuple[Issue, int]]
    ) -> Tuple[float, List[Tuple[Issue, int]]]:
        """Identify issues with unusually high discussion activity."""
        if not issue_comment_counts:
            return 0.0, []

        comment_counts = [
            count for _, count in issue_comment_counts
        ]

        median_comments = float(median(comment_counts))

        if median_comments == 0:
            hotspots = [
                (issue, count)
                for issue, count in issue_comment_counts
                if count > 0
            ]
        else:
            threshold = median_comments * 2

            hotspots = [
                (issue, count)
                for issue, count in issue_comment_counts
                if count >= threshold
            ]

        hotspots.sort(
            key=lambda item: (-item[1], item[0].number)
        )

        return median_comments, hotspots


    @staticmethod
    def _describe_trend(
        monthly_activity: Dict[datetime, Dict[str, int]]
    ) -> str:
        """Compare average monthly comments in the first and second halves."""
        months = list(monthly_activity.items())

        if len(months) < 2:
            return 'relatively stable (not enough monthly data to compare)'

        midpoint = len(months) // 2

        earlier_average = (
            sum(values['comments'] for _, values in months[:midpoint])
            / midpoint
        )

        later_months = months[midpoint:]

        later_average = (
            sum(values['comments'] for _, values in later_months)
            / len(later_months)
        )

        overall_average = (
            sum(values['comments'] for _, values in months) / len(months)
        )

        tolerance = overall_average * 0.1
        difference = later_average - earlier_average

        if difference > tolerance:
            return 'increasing'

        if difference < -tolerance:
            return 'decreasing'

        return 'relatively stable'


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

            distribution = self._get_intensity_distribution(
                issue_comment_counts
            )
            
            top_issues = self._get_top_discussed_issues(
                issue_comment_counts
            )        

    
    
if __name__ == '__main__':
        DiscussionTrendAnalysis().run()
    