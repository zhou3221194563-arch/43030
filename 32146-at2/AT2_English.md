# Visual Analysis of Historical Wimbledon Championship Data

## Abstract

This report analyses the performance of top players, gender differences in match duration, and the nationalities of champions and runners-up in Wimbledon final data from 1877 to 2026. The dataset contains 271 finals: 139 men's finals and 132 women's finals. The report focuses on comparing players with at least five titles and on changes in men's and women's match duration over time. National comparisons are used as supporting evidence of the concentration of championship success.

## 1. Data, Formats and Processing Methods

The data comprise three worksheets:

- `wimbledons_champions`: 271 final records and 25 fields, including year, gender, champion and runner-up, nationality, seed, score, games in each set, and match duration.
- `Parallel_Coordinates`: championship wins, runner-up appearances, win rate, average seed, average duration, and normalised values for 17 players with at least five titles.
- `Nationality_Comparison`: champion and runner-up counts by country.

The dataset contains 271 final records and 25 fields, including year, gender, champion and runner-up, nationality, seed, score, games in each set, and match duration. Year, seed, duration, and set-game values are numeric fields; player, nationality, country, gender, and score are text or categorical fields. Match duration is available for 206 matches and missing for 65, so duration averages, trends, and outliers use recorded durations only. Champion and runner-up seed values each contain 85 blanks, and `U` (unseeded or unknown) must not be treated as a numeric seed. The scores also include one walkover in the 1931 men's final and one retirement in the 1911 men's final; these are treated as special records when interpreting duration and sets.

To support comparison, championship wins were aggregated by champion name and used to select the 17 players with at least five titles. Champion and runner-up totals were aggregated by country. Win rate was calculated as `Champion Wins / (Champion Wins + Runner-up Count)`. Average seed and average duration use valid numeric values only, and the comparison measures were normalised to a 0–1 scale. Recorded durations were grouped by decade using `floor(Year / 10) × 10`. Missing durations remain blank rather than being replaced with zero.

## 2. Chart Descriptions

![Figure 1: Champion Nationality Map](output/pngs/Champion%20Nationality%20Map.png)

**Figure 1: Champion Nationality Map.** Country location provides the geographic context and colour intensity represents the number of championships. The United States is darkest, with the legend reaching 90. The map provides a quick view of the geographic concentration of championship success.

![Figure 2: Top Players Treemap](output/pngs/Top%20Players%20Treemap.png)

**Figure 2: Top Players Treemap.** Each rectangle represents a player with at least five titles. Area encodes championship wins, while blue and orange distinguish men's and women's players. Area encoding makes it possible to compare many players' title counts in limited space.

![Figure 3: Top Players Parallel Coordinates](output/pngs/Top%20Players%20Parallel%20Coordinates.png)

**Figure 3: Top Players Parallel Coordinates.** Lines show the positions of top players across championship wins, runner-up appearances, win rate, average seed, and average duration, with colour indicating gender. The multi-axis comparison makes performance differences beyond a single title ranking visible at the same time.

![Figure 4: Match Duration Scatter](output/pngs/Match%20Duration%20Scatter.png)

**Figure 4: Match Duration Scatter.** The horizontal axis is year, the vertical axis is minutes, and colour distinguishes gender. Each point represents one final with a recorded duration. The scatter plot retains the distribution and outliers of individual matches.

![Figure 5: Match Duration Trend by Year](output/pngs/Match%20Duration%20Trend.png)

**Figure 5: Match Duration Trend by Year.** The annual line shows variation in recorded duration over time. Gaps indicate unavailable duration data, not years in which the tournament was not held.

![Figure 6: Champion versus Runner-up Countries](output/pngs/Champion%20vs%20Runner-up%20Countries.png)

**Figure 6: Champion versus Runner-up Countries.** The paired horizontal bar chart shows champion and runner-up counts for each country on the same scale. It supports comparison between countries that frequently reach finals and those that convert final appearances into championships.

## 3. Discussion and Findings

### 3.1 Top-Player Performance

Only 17 players have won at least five titles, showing that Wimbledon titles are concentrated among a small group of players. In the treemap, M. Navratilova leads with nine titles, while R. Federer and H.W. Moody have eight each. Several players form a close second tier with seven titles. Area and gender colour allow readers to identify both title rankings and the distribution of men's and women's players without reading a data table row by row.

Championship totals are not the only measure of performance; the following groups cover all 17 top players.

- M. Navratilova leads with nine titles, three runner-up appearances, a 75.0% win rate, an average seed of 1.58, and an average duration of 84.5 minutes. She represents the player with the highest title count and consistently leading seed positions.
- H.W. Moody and R. Federer both have eight titles, but Moody's final record of eight wins and one runner-up appearance gives an 88.9% win rate and a 38.3-minute average duration. Federer has four runner-up appearances, a 66.7% win rate, and a much higher average duration of 193.7 minutes.
- Among the seven-title men, P. Sampras has seven wins and no runner-up appearances for a 100.0% win rate. N. Djokovic has seven titles, two runner-up appearances, a 77.8% win rate, and an average duration of 188.1 minutes, while W.C. Renshaw has seven titles, one runner-up appearance, and an 87.5% win rate.
- Among the seven-title women, S.M. Graf has seven titles, two runner-up appearances, and a 77.8% win rate. S. Williams and D.L. Chambers both have seven titles and four runner-up appearances, for 63.6% win rates; Williams has an average seed of 5.18 and an average duration of 86.2 minutes, while Chambers has a recorded-duration average of 18.8 minutes.
- In the six-title group, L.W. King has six titles, two runner-up appearances, a 75.0% win rate, and an average duration of 69.6 minutes. S.R.F. Lenglen has six titles with no runner-up appearances and a 100.0% win rate, whereas G.W. Hillyard has six titles but seven runner-up appearances and a 46.2% win rate.
- Among the five-title men, B.R. Borg and H.L. Doherty each have five titles, one runner-up appearance, and an 83.3% win rate. Borg's average duration is 169.3 minutes, substantially higher than Doherty's 46.3 minutes.
- Among the five-title women, C. Dod has five titles with no runner-up appearances and a 100.0% win rate. C.R. Cooper has five titles and six runner-up appearances for a 45.5% win rate, while V.E.S. Williams has five titles, four runner-up appearances, a 55.6% win rate, an average seed of 7.67, and an average duration of 98.3 minutes.
- For early players, average seed or average duration values of zero indicate that no numeric records are available; they do not mean a seed of zero or a match lasting zero minutes. These fields are therefore compared only where records are available.

The parallel-coordinates chart places championship wins, runner-up appearances, win rate, average seed, and average duration in one comparison view. Gender colour distinguishes players' trajectories and avoids treating the most titles as evidence that every performance measure is highest.

### 3.2 Gender, Match Duration and Change over Time

The scatter plot shows that men's final durations range from 37 to 297 minutes, compared with 23 to 166 minutes for women's finals. The groups overlap at shorter durations, but the men's data contain more high-duration matches. The men's maximum is 297 minutes in 2019 and the women's maximum is 166 minutes in 2005. These peaks are clear outliers, and a scatter plot preserves such match-level differences better than averages alone.

The annual trend indicates that men's finals moved into a higher duration range after the 1970s. The decade average for recorded men's matches rose from about 88 minutes in the 1960s to about 140 minutes in the 1970s and 164 minutes in the 1980s. It fell to about 142 minutes in the 1990s before rising to about 179 minutes in the 2000s. Women's durations changed more gradually: about 79 minutes in the 1970s, about 100 minutes in both the 1990s and 2000s, about 77 minutes in the 2010s, and about 104 minutes in the 2020s. The gender gap therefore became more apparent after the 1970s, especially in the higher values and greater variation of modern men's finals. Early decades and the 2020s contain fewer valid records, and 65 matches have no duration, so these findings describe the available data rather than the cause of the change.

Match results and seed values also require interpretation alongside missing data. The 1931 walkover and the 1911 retirement should not be compared directly with completed matches for duration or sets. Blank seed values and `U` should be excluded from average-seed calculations to prevent special records and non-numeric seeds from distorting top-player and gender comparisons.

### 3.3 National Comparison

National results are a supporting finding rather than the main focus of the report. The United States has the most championships (90) and 73 runner-up appearances. The United Kingdom has 73 championships but the most runner-up appearances (79). The map shows that titles are concentrated in a small number of countries, while the bar chart shows that the United States is particularly strong in championship conversion and the United Kingdom also reaches finals more frequently.

### 3.4 Graphic Techniques, Readability and Tableau

Each chart is used for the task it suits best: the map presents geographic concentration, the treemap shows part-to-whole title distribution, parallel coordinates compare multiple top-player measures, the scatter plot identifies the range and outliers of gendered match duration, the trend line locates change over time, and the bar chart directly compares champion and runner-up counts. Consistent blue for men and orange for women are used across the treemap, parallel-coordinates chart, scatter plot, and trend plot. Clear titles, legends, axes, and captions reduce the effort required to move between charts.

Tableau can place these views in one dashboard and provide filters, highlighting, and tooltips so readers can investigate results by gender, decade, country, or player without losing the overall comparison. Its limitations are that maps can be visually misleading because country area is not proportional to count, parallel-coordinate charts can become crowded with many lines, and static PNGs cannot show filters or tooltips. Missing durations, special matches, and non-numeric seed values must also be handled explicitly before analysis.

## 4. Conclusion

Wimbledon final history shows that titles are concentrated among a small number of countries and top players. The comparison of top players shows that championship wins, win rate, seed, final appearances, and average duration do not create a single ranking. Men's and women's match durations show a clearer difference after the 1970s, with higher values and greater variation among men. Together, the map, treemap, parallel coordinates, scatter plot, trend line, and bar chart place broad distribution, player performance, and change over time within one readable comparison framework.
