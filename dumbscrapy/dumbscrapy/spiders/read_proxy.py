from pathlib import Path

import scrapy


class QuotesSpider(scrapy.Spider):
    name = "read"

    start_urls = [
        "http://free-proxy.cz/en/",
        "http://free-proxy.cz/en/proxylist/main/2",
        "http://free-proxy.cz/en/proxylist/main/3",
        "http://free-proxy.cz/en/proxylist/main/4",
        "http://free-proxy.cz/en/proxylist/main/5",
    ]

    def parse(self, response):
        page = response.url.split("/")[-1]
        filename = f"proxy-{page}.html"
        Path(filename).write_bytes(response.body)
