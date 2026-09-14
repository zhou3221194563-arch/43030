# AT2 Tableau interactive visualisation TODO

## 0. Prepare the data source

- [ ] Use the processed Excel workbook only after checking the `Mins` values: retain unknown durations as blank, rather than inventing zero.
- [ ] In Tableau, assign appropriate data types (Year/date, Mins/number, seed/number, gender and nationality/dimensions).
- [ ] Create documented calculated fields only where needed: match outcome role (champion/runner-up), top-player flag (`championship wins >= 5`), and decade.
- [ ] Keep a short record of each transformation for the PDF report.

## 1. Build required worksheets

- [ ] **Champions by nationality map** — filled/symbol map showing championship wins by country; colour or filter by gender and decade.
- [ ] **Top players treemap** — player-sized tiles by championship wins for players with at least five wins; colour by gender or nationality.
- [ ] **Top-player parallel coordinates** — compare the five-plus-win players across wins, runner-up appearances, win rate, average seed, and average match duration. Use player as the detail line.
- [ ] **Match-duration scatter plot** — Year on x-axis, Mins on y-axis; colour by gender and optionally show champion/runner-up, exposing unusually long or short finals and changes over time.
- [ ] **Long-term trend chart** — championships and/or average final duration by year or decade, split by gender.
- [ ] **Champion vs runner-up comparison** — compare nationality, seed, and match-result patterns using a clearly labelled bar chart or heatmap.

## 2. Make the workbook genuinely interactive

- [ ] Create a main dashboard for broad historical patterns: map, trend chart, and duration scatter plot.
- [ ] Create a dedicated top-player dashboard: treemap, parallel coordinates, and player comparison view.
- [ ] Add global filters for gender, year/decade, nationality, and player where they make sense.
- [ ] Add dashboard actions: selecting a country filters the timeline and scatter plot; selecting a player filters the top-player comparison views.
- [ ] Use useful tooltips: player, year, gender, seed, opponent, score, and known duration; label unavailable duration as unavailable.
- [ ] Add a reset-filters control and concise on-dashboard instructions for exploration.

## 3. Check visual design and evidence

- [ ] Use consistent colours for gender and the same units/labels across all sheets.
- [ ] Avoid misleading map colour scales, truncated axes, unreadable parallel lines, or overloaded tooltips.
- [ ] Verify that each required chart answers a stated question, not merely that it exists.
- [ ] Record one defensible insight and any important limitation for every dashboard.

## 4. Produce the submission material

- [ ] Export selected dashboard views to the PDF report; explain the data, transformations, findings, visual-design choices, Tableau advantages/disadvantages, and conclusion.
- [ ] Keep the PDF within 15 pages including graphs.
- [ ] Save the Tableau deliverable as a packaged workbook: `Student_ID_A2.twbx`.
- [ ] Submit the final PDF, Excel workbook, and packaged Tableau workbook using the required Student ID filenames.
