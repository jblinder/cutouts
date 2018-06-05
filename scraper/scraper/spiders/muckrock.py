import scrapy


class FestivalSpider(scrapy.Spider):
    name = 'music_festivals'

    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 3,
        "HTTPCACHE_ENABLED": True
    }

    start_urls = [
        'https://www.musicfestivalwizard.com/festival-guide/us-festivals/',
        'https://www.musicfestivalwizard.com/festival-guide/canada-festivals/'
    ]

    def parse(self, response):
        # Extract the links to the individual festival pages
        # Follow pagination links and repeat