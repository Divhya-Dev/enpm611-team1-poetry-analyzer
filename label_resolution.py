```python
from collections import defaultdict
from statistics import median
import matplotlib.pyplot as plt

from data_loader import DataLoader
from model import State


"""
Feature 1: Label Resolution Analysis
"""


class LabelResolutionAnalysis:

    def __init__(self):
        self.issues = DataLoader().get_issues()

    def get_resolution_date(self, issue):
        """Find the date the issue was closed."""

        closing_events = []

        for event in issue.events:
            if (
                event.event_type
                and "clos" in event.event_type.lower()
                and event.event_date is not None
            ):
                closing_events.append(event.event_date)

        if not closing_events:
            return None

        return max(closing_events)

    def calculate_resolution_times(self):
        """Group issue resolution times by label."""

        label_resolution_times = defaultdict(list)

        closed_issues = 0
        missing_close_dates = 0

        for issue in self.issues:

            if issue.state != State.closed:
                continue

            closed_issues += 1

            if issue.created_date is None:
                continue

            close_date = self.get_resolution_date(issue)

            if close_date is None:
                missing_close_dates += 1
                continue

            resolution_days = (
                close_date - issue.created_date
            ).total_seconds() / 86400

            if resolution_days < 0:
                continue

            for label in issue.labels:

                if isinstance(label, str) and label.strip():
                    label_resolution_times[label].append(
                        resolution_days
                    )

        print(f"\nTotal issues: {len(self.issues)}")
        print(f"Closed issues: {closed_issues}")
        print(
            f"Closed issues without a closing event: "
            f"{missing_close_dates}"
        )

        return label_resolution_times

    def run(self):

        label_data = self.calculate_resolution_times()

        if not label_data:
            print(
                "\nNo issues with usable resolution dates "
                "and labels were found."
            )
            return

        results = {}

        for label, resolution_times in label_data.items():

            if len(resolution_times) >= 5:
                results[label] = {
                    "median": median(resolution_times),
                    "count": len(resolution_times)
                }

        if not results:
            print(
                "\nNo labels have at least 5 resolved issues."
            )
            return

        # Sort labels by median resolution time.
        sorted_results = sorted(
            results.items(),
            key=lambda item: item[1]["median"]
        )

        # Display the analysis question, methodology, and findings.
        print("\n" + "=" * 60)
        print("LABEL RESOLUTION ANALYSIS")
        print("=" * 60)

        print("\nQUESTION:")
        print(
            "Which types of issues, grouped by label, take the "
            "longest to resolve in the Poetry project?"
        )

        print("\nMETHOD:")
        print(
            "1. Identify closed issues with valid creation dates "
            "and recorded closing events."
        )
        print(
            "2. Calculate the resolution time in days by subtracting "
            "the issue creation date from its closing date."
        )
        print(
            "3. Group resolution times by issue label."
        )
        print(
            "4. Calculate the median resolution time for each label."
        )
        print(
            "5. Include only labels with at least 5 resolved issues."
        )
        print(
            "6. Sort labels by median resolution time and compare "
            "the results using a bar chart."
        )

        print("\nFINDING:")

        longest_label, longest_data = sorted_results[-1]
        shortest_label, shortest_data = sorted_results[0]

        print(
            f"The label with the longest median resolution time "
            f"is '{longest_label}' at "
            f"{longest_data['median']:.2f} days, based on "
            f"{longest_data['count']} issues."
        )

        print(
            f"The label with the shortest median resolution time "
            f"is '{shortest_label}' at "
            f"{shortest_data['median']:.2f} days, based on "
            f"{shortest_data['count']} issues."
        )

        print(
            "\nThese results compare resolution times across labels "
            "and show which issue categories take longer to resolve."
        )

        # display the detailed results.
        print("\nDETAILED RESULTS")
        print("-" * 65)

        for label, data in sorted_results:
            print(
                f"{label:<35} "
                f"Median: {data['median']:>8.2f} days "
                f"Issues: {data['count']}"
            )

        # generate the bar chart for the analysis.
        labels = [
            item[0] for item in sorted_results
        ]

        resolution_days = [
            item[1]["median"] for item in sorted_results
        ]

        plt.figure(figsize=(12, 6))

        plt.bar(labels, resolution_days)

        plt.title("Median Issue Resolution Time by Label")
        plt.xlabel("Issue Label")
        plt.ylabel("Median Days to Close")

        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        plt.show()
```
