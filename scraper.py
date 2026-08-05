import sys
import time
import urllib.parse
import argparse
import logging
import csv
from typing import List, Dict

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium.common.exceptions import TimeoutException, WebDriverException

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class MDComputersScraper:
    """
    A professional web scraper for MDComputers.in.
    
    Utilizes Selenium WebDriver to bypass Cloudflare/bot-protection 
    by rendering JavaScript, and BeautifulSoup for efficient DOM parsing.
    """
    
    BASE_URL = "https://mdcomputers.in/?route=product/search&search="
    
    def __init__(self, headless: bool = False):
        """
        Initializes the scraper with specific Chrome configurations.
        
        Args:
            headless (bool): Whether to run the browser in headless mode. 
                             Defaults to False to prevent bot detection.
        """
        self.headless = headless
        self.driver = self._initialize_driver()
        
    def _initialize_driver(self) -> webdriver.Chrome:
        """Sets up and returns the Selenium Chrome WebDriver."""
        logger.info("Initializing Selenium WebDriver...")
        options = Options()
        
        if self.headless:
            options.add_argument("--headless=new")
            
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
        options.add_argument('--ignore-certificate-errors')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        try:
            # Selenium 4.6+ has a built-in Selenium Manager.
            # We remove webdriver_manager to fix the corrupted [WinError 193] caching issue.
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(45)
            return driver
        except WebDriverException as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            sys.exit(1)

    def scrape_keyword(self, keyword: str) -> List[Dict[str, str]]:
        """
        Scrapes products matching the given keyword.
        
        Args:
            keyword (str): The search term.
            
        Returns:
            List[Dict[str, str]]: A list of dictionaries containing product details.
        """
        encoded_keyword = urllib.parse.quote(keyword)
        target_url = f"{self.BASE_URL}{encoded_keyword}"
        
        logger.info(f"Navigating to URL: {target_url}")
        
        try:
            self.driver.get(target_url)
            logger.info("Waiting for page load and potential anti-bot checks (5s)...")
            time.sleep(5)  # Allow time for Cloudflare interstitial to pass
            
            html_source = self.driver.page_source
            return self._parse_html(html_source)
            
        except TimeoutException:
            logger.error("Page load timed out.")
            return []
        except Exception as e:
            logger.error(f"An error occurred during scraping: {e}")
            return []
            
    def _parse_html(self, html_source: str) -> List[Dict[str, str]]:
        """
        Parses the HTML source code to extract product details.
        
        Args:
            html_source (str): The raw HTML of the page.
            
        Returns:
            List[Dict[str, str]]: Extracted product records.
        """
        logger.info("Parsing DOM structure using BeautifulSoup...")
        soup = BeautifulSoup(html_source, 'html.parser')
        products = []
        
        # MDComputers utilizes various layout classes depending on the theme
        product_containers = soup.find_all('div', class_='product-layout')
        if not product_containers:
            product_containers = soup.find_all('div', class_='product-thumb')
        if not product_containers:
            product_containers = soup.find_all('div', class_='product-grid-item')
            
        logger.info(f"Found {len(product_containers)} product containers on the page.")
        
        for container in product_containers:
            product_data = self._extract_product_data(container)
            if product_data.get("Product Name") != "N/A":
                products.append(product_data)
                
        return products

    def _extract_product_data(self, container: BeautifulSoup) -> Dict[str, str]:
        """
        Extracts specific attributes from a single product container.
        
        Args:
            container (BeautifulSoup): The HTML element containing the product.
            
        Returns:
            Dict[str, str]: The structured product data.
        """
        product_data = {
            "Product Name": "N/A",
            "Price": "N/A",
            "Product URL": "N/A",
            "Brand": "N/A",
            "Availability": "N/A"
        }
        
        # 1. Product Name & URL
        title_elem = container.find('h4')
        if not title_elem:
            title_elem = container.find('h3', class_='product-entities-title')
            
        if title_elem and title_elem.find('a'):
            a_tag = title_elem.find('a')
            product_data["Product Name"] = a_tag.text.strip()
            product_data["Product URL"] = a_tag.get('href', 'N/A')

        # 2. Price
        price_elem = container.find('p', class_='price') or container.find('div', class_='price') or container.find('span', class_='price')
        if price_elem:
            price_ins = price_elem.find('span', class_='ins')
            price_new = price_elem.find('span', class_='price-new')
            if price_ins and price_ins.find(class_='amount'):
                product_data["Price"] = price_ins.find(class_='amount').text.strip()
            elif price_new:
                product_data["Price"] = price_new.text.strip()
            else:
                amount = price_elem.find(class_='amount')
                if amount:
                    product_data["Price"] = amount.text.strip()
                else:
                    price_text = price_elem.text.strip().split('\n')[0].strip()
                    product_data["Price"] = price_text
                    
        # Fix Windows console encoding issues with the Rupee symbol
        if "Price" in product_data and product_data["Price"]:
            product_data["Price"] = product_data["Price"].replace('₹', 'Rs. ')

        # 3. Availability
        button_group = container.find('div', class_='button-group') or container.find('div', class_='product-add-btn')
        if button_group:
            cart_btn = button_group.find('button')
            if cart_btn:
                btn_text = cart_btn.text.strip().lower()
                product_data["Availability"] = "Out of Stock" if "out of stock" in btn_text else "In Stock"

        # 4. Brand
        brand_elem = container.find('p', class_='brand')
        if brand_elem:
            product_data["Brand"] = brand_elem.text.strip()
        elif product_data["Product Name"] != "N/A":
            # Best effort to extract brand from the first word of the product name
            product_data["Brand"] = product_data["Product Name"].split()[0]

        return product_data

    def close(self):
        """Terminates the WebDriver session safely."""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver session closed.")


def save_and_display_results(products: List[Dict[str, str]], filename: str = "output.csv"):
    """
    Saves the extracted products to a CSV using Python's built-in csv module, 
    and prints a clean text-based table to the CLI.
    """
    if not products:
        return
        
    # Save to CSV
    keys = products[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(products)
        
    logger.info(f"Successfully saved {len(products)} records to '{filename}'.")
    
    # CLI Display natively without pandas/tabulate to avoid large dependencies
    print("\n" + "="*110)
    print(" SCRAPED RESULTS ".center(110))
    print("="*110)
    
    # Print header
    header_format = "{:<45} | {:<10} | {:<15} | {:<20}"
    print(header_format.format("Product Name (Truncated)", "Price", "Availability", "Product URL (Truncated)"))
    print("-" * 110)
    
    for p in products:
        # Truncate for display
        name = p["Product Name"]
        if len(name) > 42:
            name = name[:39] + "..."
            
        url = p["Product URL"]
        if len(url) > 17:
            url = url[:14] + "..."
            
        print(header_format.format(name, p["Price"], p["Availability"], url))
        
    print("="*110 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Professional MDComputers Web Scraper.")
    parser.add_argument('-k', '--keyword', type=str, help="Search keyword (e.g., 'external harddrive')")
    parser.add_argument('--headless', action='store_true', help="Run browser in headless mode")
    
    args = parser.parse_args()
    keyword = args.keyword
    
    if not keyword:
        # Fallback to interactive input if no argument provided
        print("="*50)
        print(" MDComputers Web Scraper (Professional Edition)".center(50))
        print("="*50)
        keyword = input("\nEnter search keyword (e.g., external harddrive): ").strip()
        
    if not keyword:
        logger.error("Keyword cannot be empty. Exiting.")
        sys.exit(1)
        
    scraper = MDComputersScraper(headless=args.headless)
    try:
        products = scraper.scrape_keyword(keyword)
        
        if not products:
            logger.warning("No products found. The site layout may have changed, or a CAPTCHA blocked access.")
        else:
            save_and_display_results(products)
            
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
