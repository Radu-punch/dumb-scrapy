from pathlib import Path

import scrapy
import time


class QuotesSpider(scrapy.Spider):
    name = "read"

    start_urls = [
        "http://free-proxy.cz/en/",
        "http://free-proxy.cz/en/proxylist/main/2",
        "http://free-proxy.cz/en/proxylist/main/3",
        "http://free-proxy.cz/en/proxylist/main/4",
        "http://free-proxy.cz/en/proxylist/main/5",
    ]

    def open_spider(self, spider):
        self.start_time = time.time()

    def close_spider(self, spider):
        end_time = time.time()
        elapsed_time = end_time - self.start_time

        # Convert elapsed time to hh:mm:ss format
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_time = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

        self.log(f"Spider execution time: {formatted_time}")

    def parse(self, response):
        page = response.url.split("/")[-1]
        filename = f"proxy-{page}.html"
        Path(filename).write_bytes(response.body)
