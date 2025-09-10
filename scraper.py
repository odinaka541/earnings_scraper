# 541

"""
production-grade selenium webscraper with:
- anti-detection measures
- robust error handling
- data processing and export
- logging and monitoring

"""

import os, json, random, logging, time
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from dataclasses import dataclass, asdict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException,
    ElementNotInteractableException
)
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@dataclass
class EarningsEvent:
    """
    data structure for earnings events
    using dataclass for clean, type-safe data handling
    """
    symbol: str
    company_name: str
    earnings_date: str
    earnings_time: str  # "BMO", "AMC", or specific time
    eps_estimate: Optional[float] = None
    revenue_estimate: Optional[str] = None
    market_cap: Optional[str] = None
    sector: Optional[str] = None
    scraped_timestamp: Optional[str] = None

    def __post_init__(self):
        """add timestamp when object is created """
        if not self.scraped_timestamp:
            self.scraped_timestamp = datetime.now().isoformat()


class AntiDetectionSystem:
    """
    scraper looks and "acts" humaan
    """

    # real browser user agents
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
    ]

    @classmethod
    def get_stealth_chrome_options(cls) -> Options:
        """
        configure Chrome to avoid detection
        """
        options = Options()

        # basic stealth options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # random user agent to look like different users
        user_agent = random.choice(cls.USER_AGENTS)
        options.add_argument(f'--user-agent={user_agent}')

        # additional stealth measures
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")

        # window size randomization
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        options.add_argument(f"--window-size={width},{height}")

        return options

    @staticmethod
    def human_like_delay(min_seconds: float = 0.5, max_seconds: float = 3.0):
        """
        random delays that mimic human reading/thinking time

        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    @staticmethod
    def random_mouse_movement(driver):
        """
        move mouse randomly to simulate human behavior

        """
        try:
            actions = ActionChains(driver)

            # get page dimensions
            page_width = driver.execute_script("return document.body.scrollWidth")
            page_height = driver.execute_script("return document.body.scrollHeight")

            # random mouse movements
            for _ in range(random.randint(1, 3)):
                x = random.randint(100, min(page_width - 100, 1200))
                y = random.randint(100, min(page_height - 100, 800))

                actions.move_by_offset(
                    x - actions._get_center_of_element(driver.find_element(By.TAG_NAME, "body"))[0],
                    y - actions._get_center_of_element(driver.find_element(By.TAG_NAME, "body"))[1]
                )
                actions.pause(random.uniform(0.1, 0.5))

            actions.perform()
        except:
            pass


class EarningsCalendarScraper:
    """
    gathers real-world financial data

    """

    def __init__(self, headless: bool = True, debug: bool = False):
        self.headless = headless
        self.debug = debug
        self.driver = None
        self.wait = None
        self.logger = self._setup_logging()
        self.scraped_events: List[EarningsEvent] = []
        self.session_stats = {
            'pages_scraped': 0,
            'events_found': 0,
            'errors_encountered': 0,
            'start_time': None
        }

    def _setup_logging(self) -> logging.Logger:
        """
        cnfigure comprehensive logging
        """
        #
        os.makedirs('logs', exist_ok=True)

        #
        logging.basicConfig(
            level=logging.INFO if not self.debug else logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/earnings_scraper_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )

        logger = logging.getLogger(__name__)
        logger.info("Earnings scraper initialized")
        return logger

    def initialize_driver(self):
        """
        this is where the magic happens...

        """
        try:
            self.logger.info("!!! Initializing WebDriver with stealth configuration !!!")

            #
            options = AntiDetectionSystem.get_stealth_chrome_options()

            if self.headless:
                options.add_argument("--headless")
                self.logger.info("Running in headless mode")

            # init driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 15)

            #stealth scripts to remove webdriver traces
            stealth_js = """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });

            window.chrome = {
                runtime: {},
            };
            """

            self.driver.execute_script(stealth_js)

            self.logger.info("WebDriver initialized successfully with anti-detection measures")
            self.session_stats['start_time'] = datetime.now()

        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def scrape_yahoo_earnings_calendar(self, target_date: str) -> List[EarningsEvent]:
        """
        core calendar scraper
        """
        events = []
        url = f"https://finance.yahoo.com/calendar/earnings?from={target_date}&to={target_date}&size=100"

        try:
            self.logger.info(f"Scraping Yahoo Finance earnings calendar for {target_date}")
            self.logger.debug(f"URL: {url}")

            #
            self.driver.get(url)
            AntiDetectionSystem.human_like_delay(2, 4)

            #
            self.logger.debug("!!! Waiting for earnings calendar table to load...")

            # in case Yahoo changes their HTML...
            table_selectors = [
                "table[data-test='earnings-calendar-table']",
                "table",
                "[data-testid='earnings-table']",
                ".earnings-table"
            ]

            earnings_table = None
            for selector in table_selectors:
                try:
                    earnings_table = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    self.logger.debug(f"!!! Found table using selector: {selector}")
                    break
                except TimeoutException:
                    continue

            if not earnings_table:
                self.logger.warning("!!! Could not find earnings table with any known selector")
                return events

            # extracting table rows
            rows = earnings_table.find_elements(By.TAG_NAME, "tr")
            self.logger.info(f"Found {len(rows)} rows in earnings table")

            #
            data_rows = rows[1:] if len(rows) > 1 else []

            for i, row in enumerate(data_rows):
                try:
                    event = self._parse_earnings_row(row, target_date)
                    if event:
                        events.append(event)
                        self.logger.debug(f"Successfully parsed: {event.symbol} - {event.company_name}")

                except Exception as e:
                    self.logger.warning(f"Failed to parse row {i}: {e}")
                    self.session_stats['errors_encountered'] += 1
                    continue

            self.logger.info(f"Successfully extracted {len(events)} earnings events")
            self.session_stats['pages_scraped'] += 1
            self.session_stats['events_found'] += len(events)

            # imp!!! random mouse movement
            AntiDetectionSystem.random_mouse_movement(self.driver)

        except TimeoutException:
            self.logger.error(f"Timeout waiting for earnings calendar page to load for {target_date}")
        except Exception as e:
            self.logger.error(f"Unexpected error scraping {target_date}: {e}")
            self.session_stats['errors_encountered'] += 1

        return events

    def _parse_earnings_row(self, row, date: str) -> Optional[EarningsEvent]:
        try:
            cells = row.find_elements(By.TAG_NAME, "td")

            if len(cells) < 4:  #at least symbol, time, eps, revenue
                return None

            # symbol and company name
            symbol_cell = cells[0]
            symbol = symbol_cell.text.strip()

            if not symbol:
                return None

            # fetching company name from link title or nearby elements
            company_name = symbol  # fallback
            try:
                company_link = symbol_cell.find_element(By.TAG_NAME, "a")
                company_name = (
                        company_link.get_attribute("title") or
                        company_link.get_attribute("aria-label") or
                        symbol
                )
            except:
                pass

            # earnings time (BMO = Before Market Open, AMC = After Market Close)
            earnings_time = cells[1].text.strip() if len(cells) > 1 else "N/A"

            # extracting EPS estimate (handle various formats)
            eps_estimate = None
            if len(cells) > 2:
                eps_text = cells[2].text.strip()
                eps_estimate = self._parse_financial_number(eps_text)

            #
            revenue_estimate = None
            if len(cells) > 3:
                revenue_text = cells[3].text.strip()
                revenue_estimate = revenue_text if revenue_text != "N/A" else None

            # ceate earnings event
            event = EarningsEvent(
                symbol=symbol,
                company_name=company_name,
                earnings_date=date,
                earnings_time=earnings_time,
                eps_estimate=eps_estimate,
                revenue_estimate=revenue_estimate
            )

            return event

        except Exception as e:
            self.logger.debug(f"!!! Error parsing earnings row: {e}")
            return None

    def _parse_financial_number(self, text: str) -> Optional[float]:
        """
        parsing financial numbers in various formats
        Handles: $1.23, (1.23), 1.23B, N/A, etc.
        """
        if not text or text.upper() in ['N/A', 'TBD', '--', '']:
            return None

        try:
            #
            cleaned = text.replace('$', '').replace(',', '').replace('(', '-').replace(')', '')

            # handling multipliers
            multiplier = 1
            if cleaned.upper().endswith('B'):
                multiplier = 1e9
                cleaned = cleaned[:-1]
            elif cleaned.upper().endswith('M'):
                multiplier = 1e6
                cleaned = cleaned[:-1]
            elif cleaned.upper().endswith('K'):
                multiplier = 1e3
                cleaned = cleaned[:-1]

            #
            number = float(cleaned.strip()) * multiplier
            return number

        except (ValueError, AttributeError):
            return None

    def enrich_with_company_details(self, events: List[EarningsEvent], max_enrich: int = 10) -> List[EarningsEvent]:
        """
        extra information about the company
        """
        self.logger.info(f"Enriching up to {max_enrich} events with company details")

        enriched = 0
        for event in events[:max_enrich]: # has to be limited though to avoid detection
            try:
                self.logger.debug(f"Enriching data for {event.symbol}")

                profile_url = f"https://finance.yahoo.com/quote/{event.symbol}/profile"
                self.driver.get(profile_url)
                AntiDetectionSystem.human_like_delay(1, 2)

                # sector??
                try:
                    sector_element = self.driver.find_element(By.CSS_SELECTOR, "[data-test='SECTOR']")
                    event.sector = sector_element.text.strip()
                except NoSuchElementException:
                    pass

                # mc??
                try:
                    market_cap_element = self.driver.find_element(By.CSS_SELECTOR, "[data-test='MARKET_CAP-value']")
                    event.market_cap = market_cap_element.text.strip()
                except NoSuchElementException:
                    pass

                enriched += 1
                AntiDetectionSystem.human_like_delay(0.5, 1.5)

            except Exception as e:
                self.logger.warning(f"Failed to enrich {event.symbol}: {e}")
                continue

        self.logger.info(f"!!! Successfully added {enriched} events")
        return events

    def run_multi_day_scrape(self, start_date: str = None, days: int = 5, enrich_data: bool = False) -> List[
        EarningsEvent]:
        """
        !!!

        """
        try:
            self.logger.info(f"Starting {days}-day earnings scraping job")

            # init
            self.initialize_driver()

            # 'today' by default
            if not start_date:
                start_date = datetime.now().strftime("%Y-%m-%d")

            current_date = datetime.strptime(start_date, "%Y-%m-%d")
            all_events = []

            #
            for day_num in range(days):
                date_str = current_date.strftime("%Y-%m-%d")
                weekday = current_date.weekday()

                # skipping weekends, because why?
                if weekday < 5:  # Monday=0, Sunday=6
                    self.logger.info(f"Scraping day {day_num + 1}/{days}: {date_str}")

                    daily_events = self.scrape_yahoo_earnings_calendar(date_str)

                    if daily_events:
                        all_events.extend(daily_events)
                        self.logger.info(f"Found {len(daily_events)} events for {date_str}")
                    else:
                        self.logger.info(f"No earnings events found for {date_str}")

                    #
                    if day_num < days - 1:  # Don't delay after last day
                        AntiDetectionSystem.human_like_delay(3, 8)
                else:
                    self.logger.info(f"Skipping weekend: {date_str}")

                current_date += timedelta(days=1)

            #
            if enrich_data and all_events:
                self.logger.info("Enriching events with company details...")
                all_events = self.enrich_with_company_details(all_events)

            self.scraped_events = all_events

            #
            self._log_session_stats()

            return all_events

        except Exception as e:
            self.logger.error(f"!!! Multi-day scraping job failed: {e}")
            return []

        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("!!! WebDriver session closed!!!")

    def _log_session_stats(self):
        """logs *** """
        if self.session_stats['start_time']:
            duration = datetime.now() - self.session_stats['start_time']
            self.session_stats['duration_minutes'] = duration.total_seconds() / 60

        self.logger.info("=" * 50)
        self.logger.info("SCRAPING SESSION COMPLETE")
        self.logger.info("=" * 50)
        self.logger.info(f"Pages scraped: {self.session_stats['pages_scraped']}")
        self.logger.info(f"Events found: {self.session_stats['events_found']}")
        self.logger.info(f"Errors encountered: {self.session_stats['errors_encountered']}")
        self.logger.info(f"Duration: {self.session_stats.get('duration_minutes', 0):.1f} minutes")
        self.logger.info(
            f"Success rate: {(1 - self.session_stats['errors_encountered'] / max(1, self.session_stats['pages_scraped'])) * 100:.1f}%")

    def save_to_json(self, filename: str = None) -> str:
        """saving scraped data to readable json """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/earnings_calendar_{timestamp}.json"

        #
        os.makedirs('data', exist_ok=True)

        #
        export_data = {
            'metadata': {
                'scrape_timestamp': datetime.now().isoformat(),
                'total_events': len(self.scraped_events),
                'session_stats': self.session_stats,
                'version': '1.0'
            },
            'earnings_events': [asdict(event) for event in self.scraped_events]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Data saved to {filename}")
        return filename

    def save_to_csv(self, filename: str = None) -> str:
        """ saving to csv"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/earnings_calendar_{timestamp}.csv"

        #
        os.makedirs('data', exist_ok=True)

        #
        df = pd.DataFrame([asdict(event) for event in self.scraped_events])

        #
        if not df.empty:
            df['has_eps_estimate'] = df['eps_estimate'].notna()
            df['has_revenue_estimate'] = df['revenue_estimate'].notna()
            df['earnings_day_of_week'] = pd.to_datetime(df['earnings_date']).dt.day_name()

        df.to_csv(filename, index=False)

        self.logger.info(f"CSV saved to {filename}")
        return filename

    def generate_summary_report(self) -> Dict:
        """ ***"""
        if not self.scraped_events:
            return {"error": "No data to analyze"}

        df = pd.DataFrame([asdict(event) for event in self.scraped_events])

        report = {
            'total_events': len(self.scraped_events),
            'unique_companies': df['symbol'].nunique(),
            'date_range': {
                'start': df['earnings_date'].min(),
                'end': df['earnings_date'].max()
            },
            'earnings_timing': df['earnings_time'].value_counts().to_dict(),
            'events_with_eps_estimates': df['eps_estimate'].notna().sum(),
            'events_with_revenue_estimates': df['revenue_estimate'].notna().sum(),
            'sectors_represented': df['sector'].value_counts().to_dict() if 'sector' in df.columns else {},
            'top_companies_by_market_cap': df.nlargest(10, 'market_cap')[
                ['symbol', 'company_name', 'market_cap']].to_dict('records') if 'market_cap' in df.columns else []
        }

        return report


# -----------------------------------------
def main():

    print("Financial Earnings Calendar Automation System")
    print("=" * 60)

    # init
    scraper = EarningsCalendarScraper(
        headless=False,  # T, prod
        debug=True
    )

    try:
        #
        events = scraper.run_multi_day_scrape(
            days=1, # 1 def, abeg
            enrich_data=False  #
        )

        if events:
            print(f"\nSuccessfully scraped {len(events)} earnings events!")

            json_file = scraper.save_to_json()
            csv_file = scraper.save_to_csv()

            report = scraper.generate_summary_report()
            print(f"\n SUMMARY REPORT:")
            print(f"Total events: {report['total_events']}")
            print(f"Unique companies: {report['unique_companies']}")
            print(f"Date range: {report['date_range']['start']} to {report['date_range']['end']}")

            #
            print(f"\n SAMPLE EVENTS:")
            for i, event in enumerate(events[:5]):
                print(f"{i + 1}. {event.symbol} ({event.company_name}) - {event.earnings_date} {event.earnings_time}")

            print(f"\n Files saved:")
            print(f"   JSON: {json_file}")
            print(f"   CSV: {csv_file}")

        else:
            print(" No earnings events found. Check logs for details.")

    except Exception as e:
        print(f" Scraping failed: {e}")

    print("\n Scraping complete!")


if __name__ == "__main__":
    main()