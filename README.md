# USports Hoops Scraper

## Introduction

This package makes getting data from https://usportshoops.ca/ easy. Provided in the package are web scraping methods to quickly pull individual game or season box scores.

## Example Code
```python
from USports_Scraper import scrape_season_box
print(scrape_season_box.scrape_season("Queens", "2022-23", "print"))
```