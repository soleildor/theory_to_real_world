# Amazon US Pipeline

Seven Colab notebooks that take a set of search keywords to a clean, ASIN-level product
table with ranks, specs and sales estimates.

| # | Notebook | Input → Output |
|---|---|---|
| 01 | `01_search_results_crawler.ipynb` | Keywords → product cards per keyword (ASIN, title, brand, price, rating, reviews, sponsored flag) + third-party price history |
| 02a | `02a_append_sheets_across_files.ipynb` | Several keyword workbooks → one workbook, same-named sheets stacked with `source_file` |
| 02b | `02b_merge_keywords_one_sheet.ipynb` | Parent + sub-keyword results → one row per ASIN, de-duplicated price history, all matching keywords recorded |
| 03 | `03_product_page_html_collector.ipynb` | ASIN list → product-page HTML; status per ASIN, blocked pages never retried |
| 04 | `04_product_detail_parser.ipynb` | HTML → BSR (main + sub-category), "bought in past month", specs (incl. unit count), ingredients |
| 05 | `05_bsr_sales_estimator_lumaiscope.ipynb` | BSR + price → monthly units / revenue (central, low, high) via LumaiScope's public endpoint |
| 06 | `06_merge_by_asin.ipynb` | Two outputs → outer join on ASIN with `BOTH / FILE1_ONLY / FILE2_ONLY` status |

Feed the final table into [`../market-sizing/`](../market-sizing/) for market size, growth
and positioning.

## Notes

- Paths use `/content/drive/MyDrive/YOUR_PROJECT_FOLDER/...` — set your own folder first.
- 01–05 keep the original Korean comments and console messages; 02a and 06 were rewritten
  in English. Column names in the output workbooks are Korean (e.g. `제품분석` = product
  analysis, `가격이력` = price history, `가격요약` = price summary).
- 03 uses a real browser and is slow by design (one page at a time with pauses).
- Read Amazon's and the price tracker's terms before running 01 or 03. See the
  [disclaimer](../README.md#disclaimer).
