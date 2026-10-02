# Coupang Pipeline

Four Colab notebooks for Coupang (Korea) competitor analysis, from saved search-result
page source to an AI-enriched product table.

| # | Notebook | Input → Output |
|---|---|---|
| 01 | `01_search_page_product_extractor.ipynb` | Saved search-page source → products with list price, discount rate and `vendorItemId`, joined to price history; competitor workbook |
| 02 | `02_keyword_append.ipynb` | Several keyword workbooks → one dataset with keyword priority and ID de-duplication |
| 03 | `03_product_detail_ocr_ai.ipynb` | Saved detail-page source → detail images → OCR → Gemini structured attributes added as new columns |
| 04 | `04_price_history_filter.ipynb` | Workbook → price history / summary restricted to the confirmed product list |

## Notes

- Pages are saved manually (view-source → save) and uploaded; the notebooks parse files,
  they do not browse Coupang themselves.
- 03 needs a Gemini API key in Colab Secrets as `GEMINI_API_KEY`. OCR text is sent to the
  API, so do not run it on content you are not allowed to share with a third party.
- 01–03 keep the original Korean comments; 04 was rewritten in English. Sheet names in the
  workbooks are Korean (`제품분석`, `가격이력`, `가격요약`, `시장요약` = market summary).
- See the [disclaimer](../README.md#disclaimer).
