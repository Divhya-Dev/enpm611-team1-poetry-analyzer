"""Analyze discussion activity in Poetry GitHub issues."""

"""
Feature 3: Discussion Trend Analysis
"""
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
        """Convert a date value into a UTC datetime."""

        if date_value is None:
            return None

        try:
            if isinstance(date_value, datetime):
                parsed_date = date_value
            else:
                parsed_date = datetime.fromisoformat(
                    date_value.replace("Z", "+00:00")
                )

            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)

            return parsed_date.astimezone(timezone.utc)

        except (ValueError, TypeError):
            return None


    def _group_monthly_activity(self, issues: List[Issue]) -> Dict[datetime, Dict[str, int]]:
        """Group issue creation and comment activity by month."""

        monthly_activity = defaultdict(lambda: {
            "issues": 0,
            "comments": 0
        })

        for issue in issues:

            # Count issues by their creation month
            issue_date = self._parse_event_date(issue.created_date)

            if issue_date:
                month = datetime(
                    issue_date.year,
                    issue_date.month,
                    1,
                    tzinfo=timezone.utc
                )
                monthly_activity[month]["issues"] += 1

            # Count comments by the actual comment event date
            for event in issue.events:
                if event.event_type == "commented":

                    comment_date = self._parse_event_date(event.event_date)

                    if comment_date:
                        month = datetime(
                            comment_date.year,
                            comment_date.month,
                            1,
                            tzinfo=timezone.utc
                        )
                        monthly_activity[month]["comments"] += 1

        return dict(sorted(monthly_activity.items()))
    

    @staticmethod
    def _get_intensity_distribution(
        issue_comment_counts: List[Tuple[Issue, int]]
    ) -> Dict[str, int]:
        """
        Categorize issues based on their number of comments.

        Low (0-2): Represents minimal discussion or interaction.
        Medium (3-10): Represents a moderate level of discussion.
        High (>10): Represents extensive discussion that may indicate
        complex issues or greater contributor involvement.

        These fixed thresholds provide simple and consistent
        categories for comparing discussion activity across issues.
        """
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
        """
        Identify issues with unusually high discussion activity.

        The hotspot threshold is set to twice the median number
        of comments across all issues.

        The median is used because it is less sensitive to extreme
        values than the mean. Multiplying it by two provides a
        simple benchmark for identifying issues that receive
        substantially more discussion than a typical issue.

        If the median is zero, any issue with at least one comment
        is considered a hotspot.
        """
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
        monthly_activity: Dict[datetime, Dict[str, int]],
        metric: str
    ) -> str:
        """Compare the average monthly activity in two time periods."""

        months = list(monthly_activity.values())

        if len(months) < 2:
            return 'stable (not enough monthly data to compare)'

        counts = [values[metric] for values in months]

        midpoint = len(counts) // 2

        earlier_average = sum(counts[:midpoint]) / midpoint
        later_average = sum(counts[midpoint:]) / len(counts[midpoint:])

        overall_average = sum(counts) / len(counts)

        tolerance = overall_average * 0.1
        difference = later_average - earlier_average

        if difference > tolerance:
            return 'increasing'

        if difference < -tolerance:
            return 'decreasing'

        return 'relatively stable'


    def _show_monthly_activity_chart(self, monthly_activity):

        months = list(monthly_activity.keys())

        issue_counts = [
            monthly_activity[month]["issues"]
            for month in months
        ]

        comment_counts = [
            monthly_activity[month]["comments"]
            for month in months
        ]

        fig, ax = plt.subplots(figsize=(15, 7))

        ax.plot(
            months,
            issue_counts,
            marker="o",
            markersize=3,
            linewidth=1.5,
            label="Issues Created"
        )

        ax.plot(
            months,
            comment_counts,
            marker="o",
            markersize=3,
            linewidth=1.5,
            label="Comments Posted"
        )

        ax.set_title(
            f"Monthly Issue and Comment Activity "
            f"({months[0].year}–{months[-1].year})"
)
        ax.set_xlabel("Month")
        ax.set_ylabel("Number of Activities")

        # Automatically select readable date labels
        ax.xaxis.set_major_locator(
            mdates.MonthLocator(interval=3)
        )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%b %Y")
        )
        ax.legend()
        ax.grid(True, alpha=0.3)

        fig.autofmt_xdate()
        fig.tight_layout()


    def _show_intensity_chart(
        self, distribution: Dict[str, int]
    ) -> None:
        """Display the issue discussion-intensity distribution."""
        figure, axis = plt.subplots(figsize=(8, 6))

        categories = ['Low', 'Medium', 'High']
        counts = [distribution[category] for category in categories]

        bars = axis.bar(
            categories,
            counts,
            color=['#76b7b2', '#f2cf5b', '#e17c72']
        )

        axis.set_title('Discussion Intensity Distribution')
        axis.set_xlabel('Discussion category')
        axis.set_ylabel('Number of issues')
        axis.bar_label(bars, padding=3)
        axis.set_ylim(0, max(counts, default=0) * 1.1 + 1)

        figure.tight_layout()


    @staticmethod
    def _print_report(
        issue_comment_counts: List[Tuple[Issue, int]],
        monthly_activity: Dict[datetime, Dict[str, int]],
        distribution: Dict[str, int],
        top_issues: List[Tuple[Issue, int]],
        total_comments: int,
    ) -> None:
        """Print the requested totals, breakdowns, and interpretation."""

        total_issues = len(issue_comment_counts)

        average_comments = (
            total_comments / total_issues if total_issues else 0.0
        )

        print('\nDiscussion Trend Analysis')
        print('=' * 27)

        print(f'Total issues analyzed: {total_issues}')
        print(f'Total comments analyzed: {total_comments}')
        print(f'Average comments per issue: {average_comments:.2f}')

        print(
            'Monthly activity (issues grouped by creation date, '
            'comments grouped by comment event date):'
        )

        if monthly_activity:
            for month, values in monthly_activity.items():
                print(
                    f'  {month:%B %Y}: {values["issues"]} issues, '
                    f'{values["comments"]} comments'
                )

            highest_count = max(
                values['comments'] for values in monthly_activity.values()
            )

            lowest_count = min(
                values['comments'] for values in monthly_activity.values()
            )

            highest_months = [
                month.strftime('%B %Y')
                for month, values in monthly_activity.items()
                if values['comments'] == highest_count
            ]

            lowest_months = [
                month.strftime('%B %Y')
                for month, values in monthly_activity.items()
                if values['comments'] == lowest_count
            ]

            issue_trend = DiscussionTrendAnalysis._describe_trend(
                monthly_activity, 'issues'
            )

            comment_trend = DiscussionTrendAnalysis._describe_trend(
                monthly_activity, 'comments'
            )

            print(f'Issue creation trend: {issue_trend}.')
            print(f'Comment activity trend: {comment_trend}.')

            print(
                f'Highest comment activity: {", ".join(highest_months)} '
                f'({highest_count} comments)'
            )

            print(
                f'Lowest comment activity: {", ".join(lowest_months)} '
                f'({lowest_count} comments)'
            )

        else:
            print('  No valid monthly activity data available.')
            print('Discussion activity trend: unavailable.')

        print('Discussion intensity:')

        for category, count in distribution.items():
            percentage = (
                count / total_issues * 100 if total_issues else 0.0
            )

            print(
                f'  {category}: {count} issues ({percentage:.1f}%)'
            )

        print('Most-discussed issues (ties at fifth place are included):')

        if top_issues:
            for issue, comment_count in top_issues:
                title = issue.title or 'Untitled issue'

                print(
                    f'  #{issue.number}: {title} '
                    f'({comment_count} comments)'
                )
        else:
            print('  No issues to report.')

        if total_issues:
            high_share = distribution['High'] / total_issues * 100

            print(
                f'Interpretation: {high_share:.1f}% of issues generated '
                f'more than 10 comments; the monthly comparison above shows '
                'whether comment volume is shifting over time.'
            )
        else:
            print('Interpretation: no issue data was available to analyze.')

    
    
    def _print_additional_insights(self, median_comments, hotspots):
        print("\n" + "=" * 60)
        print("ADDITIONAL DISCUSSION INSIGHTS")
        print("=" * 60)

        print(f"\nMedian comments per issue: {median_comments:.2f}")

        if median_comments == 0:
            print("Hotspot threshold: More than 0 comments")
        else:
            print(
                f"Hotspot threshold: At least {2 * median_comments:.2f} comments"
            )

        print(f"Number of discussion hotspots: {len(hotspots)}")

        if hotspots:
            print("\nMost active discussion hotspots:")
            for issue, comment_count in hotspots[:10]:
                print(
                    f"Issue #{issue.number}: {issue.title} "
                    f"({comment_count} comments)"
                )
        else:
            print("No discussion hotspots found.")


    def run(self) -> None:
        """Load issues, report discussion patterns, and display charts."""
        issues: List[Issue] = DataLoader().get_issues() or []

        #print("Total issues:", len(issues))
        issue_comment_counts = [
            (issue, self._count_comments(issue))
            for issue in issues
        ]

        total_comments = sum(
            comment_count for _, comment_count in issue_comment_counts
        )

        monthly_activity = self._group_monthly_activity(
            issues
        )

        distribution = self._get_intensity_distribution(
            issue_comment_counts
        )

        top_issues = self._get_top_discussed_issues(
            issue_comment_counts
        )

        median_comments, hotspots = self._get_discussion_hotspots(
            issue_comment_counts
        )

        
        print("\n" + "=" * 60)
        print("DISCUSSION TREND ANALYSIS")
        print("=" * 60)

        print("\nQUESTION:")
        print(
            "How has issue creation and discussion activity changed "
            "over time in the Poetry project, and which issues attract "
            "the most discussion?"
        )

        print("\nMETHOD:")
        print(
            "1. Count comment events for each issue."
        )
        print(
            "2. Group issues by their creation month and comments "
            "by their actual event dates."
        )
        print(
            "3. Classify issues into Low (0-2), Medium (3-10), "
            "and High (more than 10) discussion categories."
        )
        print(
            "4. Rank issues by comment count, including ties at "
            "the fifth position."
        )
        print(
            "5. Identify discussion hotspots using twice the median "
            "comment count as the threshold."
        )
        print(
            "6. Compare monthly activity across the observation period "
            "to identify trends."
        )

        print("\nFINDING:")

        self._print_report(
            issue_comment_counts,
            monthly_activity,
            distribution,
            top_issues,
            total_comments,
        )

        self._print_additional_insights(median_comments, hotspots)
        self._show_monthly_activity_chart(monthly_activity)
        self._show_intensity_chart(distribution)
        print("Number of open figures:", plt.get_fignums())

        plt.show(block=True)
    
    
if __name__ == '__main__':
    DiscussionTrendAnalysis().run()