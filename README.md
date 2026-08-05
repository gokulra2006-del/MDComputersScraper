# MDComputers Web Scraper

## Project Description
A Python-based web scraping utility designed to dynamically extract product details from [MDComputers.in](https://mdcomputers.in) based on a user-defined search keyword. 

**Important Note on Anti-Bot Protection:** 
MDComputers employs bot-protection mechanisms (such as Cloudflare) that block standard HTTP requests (returning a `403 Forbidden` error). To overcome this, this scraper automatically utilizes **Selenium WebDriver** to render the JavaScript and mimic legitimate browser behavior.

## Features
- Dynamically builds the search URL based on user input.
- Bypasses basic bot protection using Selenium and Chrome WebDriver.
- Extracts key product information including:
  - Product Name
  - Price
  - Product URL
  - Availability (In Stock / Out of Stock)
  - Brand (if available)
- Handles missing fields gracefully.
- Saves all extracted data to a cleanly formatted `output.csv`.
- Displays the scraped products in an elegant tabular format in the console.

## Folder Structure
```
mdcomputers-scraper/
│
├── scraper.py          # The main web scraping Python script
├── requirements.txt    # List of required Python dependencies
├── README.md           # Project documentation
├── output.csv          # Exported product data (sample included)
├── .gitignore          # Git ignore rules for Python projects
└── screenshots/        # Directory to store evaluation screenshots
```

## Required Packages
- `pandas` - For data manipulation and CSV export.
- `beautifulsoup4` - For parsing the HTML DOM.
- `selenium` - For browser automation and handling JavaScript/anti-bot protection.
- `webdriver-manager` - For automatic installation and management of ChromeDriver binaries.
- `tabulate` - For displaying clean tables in the CLI.

## Installation

1. **Clone or Download the Repository**
2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   ```
3. **Activate the Virtual Environment:**
   - **Windows:** 
     ```bash
     venv\Scripts\activate
     ```
   - **Mac/Linux:** 
     ```bash
     source venv/bin/activate
     ```
4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the script from your terminal:
```bash
python scraper.py
```
You will be prompted to enter a search keyword. For example: `external harddrive`.

## Example Output
```text
==================================================
   MDComputers Web Scraper (Selenium Edition)
==================================================

Enter search keyword (e.g., external harddrive): external harddrive

[*] Starting scrape for 'external harddrive'...

[*] Navigating to URL: https://mdcomputers.in/?route=product/search&search=external%20harddrive
[*] Launching browser (this bypasses bot-protection)...
[*] Waiting for the page to load completely (5 seconds)...
[*] Page loaded. Parsing products...

[*] Successfully scraped 10 products.
[*] Data saved to 'output.csv'.

====================================================================================================
SCRAPED RESULTS
====================================================================================================
+-----------------------------------------------+-----------+-----------------------------------------------+-------+--------------+
| Product Name                                  | Price     | Product URL                                   | Brand | Availability |
+===============================================+===========+===============================================+=======+==============+
| Seagate Expansion 1TB Portable External H...  | ₹4,799    | https://mdcomputers.in/seagate-expansion-1... | N/A   | In Stock     |
+-----------------------------------------------+-----------+-----------------------------------------------+-------+--------------+
| Western Digital Elements 1.5TB Portable ...   | ₹4,650    | https://mdcomputers.in/western-digital-ele... | N/A   | In Stock     |
+-----------------------------------------------+-----------+-----------------------------------------------+-------+--------------+
...
```

## How to Verify It's Working
1. Run the script and enter a term like `processor` or `harddrive`.
2. Observe the Chrome browser briefly open, navigate to the search page, and close once the HTML is captured.
3. Check the console for the tabular output.
4. Open `output.csv` to ensure the data is properly formatted and stored.
5. **Screenshots for Assignment:** Take a screenshot of the script running in the terminal with the table displayed, and a screenshot of the generated `output.csv` opened in Excel or Notepad. Place these screenshots in the `screenshots/` directory before submission.

## Limitations
- **Dynamic Classes:** If MDComputers drastically changes their website theme or HTML structure, the CSS selectors in `BeautifulSoup` will need to be updated.
- **Advanced CAPTCHAs:** If the site triggers an advanced CAPTCHA, the script leaves the browser non-headless so the user can manually solve it before the 5-second wait expires (or the script timeout can be increased).

## Future Improvements
- Add proxy support to scrape large volumes without triggering rate limits.
- Implement pagination to scrape multiple pages of search results.
- Incorporate `undetected-chromedriver` for even more robust anti-bot evasion.
