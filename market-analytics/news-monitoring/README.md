# News Monitoring

Tracks new-product launches in a category from news coverage.

| # | Notebook | What it does |
|---|---|---|
| 01 | `01_launch_news_trend_analysis.ipynb` | Parses pasted news search results for a keyword, removes near-duplicate articles (TF-IDF cosine similarity + fuzzy title matching), groups them into issues and tags brand, category, USP and issue type |
| 02 | `02_product_issue_visualization.ipynb` | Turns the issue table into a chart pack (issue types, top brands, categories, USPs, daily trend, brand × issue heatmap, top issues, keywords) and a summary workbook |

## Notes

- 01 works on text you paste from a news search, not on automated requests.
- 01 keeps the original Korean comments; 02 was rewritten in English and maps the Korean
  output columns of 01 to English names at the top of the notebook.
- See the [disclaimer](../README.md#disclaimer).
