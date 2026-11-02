### Feature 2

- **Question:** Who does the work on the project, do frequent commenters also
  label or close issues, and how concentrated are first replies on a few people?
- **Run:**
  ```
  python run.py --feature 2               # project-wide view
  python run.py --feature 2 --user abn    # one contributor (case-insensitive)
  ```
- **Method:** every event is classified as a comment, a label action
  (labeled/unlabeled) or a close, and counted per contributor. Bots and unknown
  users are excluded, and labels or closes made by the reporter on their own
  issue are not counted as triage (issue templates apply labels in the
  reporter's name). Spearman rank correlations relate the measures. For every
  issue, the first reply by a human other than the reporter is found, and the
  share handled by the top 1 / 3 / 10 responders is computed overall and per year.
- **Output (no `--user`):** the top 10 contributors, rank correlations between
  comments and triage actions, a written finding, a first-reply concentration
  table by year (a "bus factor" view), and three charts: a grouped bar chart
  of the top contributors, a scatter plot of comments vs. triage actions, and
  the top-responder share by year.
- **Output (`--user`):** that contributor's comments, label actions, closes,
  rank, share of all activity and share of first replies, a finding comparing
  their triage share with the top 10, and a bar chart next to the average of
  the top 10. If the user does not exist, similar names are suggested and the
  program exits cleanly.
- **Limitations:**
  - The provided subset (`poetry_issues.json`) is not representative over time,
    so concentration figures differ from those of the full file
    (`poetry_issues_all.json`); always state which file a number comes from.
  - "Frequent commenter" means at least 10 comments, a small group in the
    subset, so percentages for that group rest on few people.
  - Years with fewer than 10 answered issues are left out of the concentration
    table and chart. Correlations describe the data and do not show cause.
- **Differences from the Milestone 1 design:** the analysis also prints a written
  finding after the correlations, computes first-reply concentration (extra table
  and third chart), and prints a message and exits when the requested user does
  not exist. It also imports `model.py` (for `Issue`), which the component
  diagram does not show.



### Shengjie Liu
- **Implementation:** Feature 2, contributor activity analysis (`contributor_activity_analysis.py`).
- **Shared code:** helpers in `model.py` (`is_human`, `closed_date`, `days_to_close`, `human_comments`), a clear error in `data_loader.py` when the data file is missing, and `numpy` in `requirements.txt` (pull request #2).
