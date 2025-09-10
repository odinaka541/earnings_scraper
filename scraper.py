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