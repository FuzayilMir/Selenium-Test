# Selenium Automation with BrowserStack

## Overview
This project automates scraping articles from the Opinion section of *El País* using Selenium, translates article titles to English using a translation API, analyzes repeated words, and runs tests on BrowserStack with parallel cross-browser execution.

## Features
- Navigate El País in Spanish
- Scrape first 5 Opinion articles (title and content)
- Download article cover images (if available)
- Translate titles from Spanish to English
- Identify words repeated more than twice
- Execute tests on BrowserStack using 5 parallel threads

## Tech Stack
- Python
- Selenium 
- BrowserStack SDK
- Translation API

## How to Run
```bash
venv\Scripts\Activate
pip install -r requirements.txt
browserstack-sdk python3 main.py
