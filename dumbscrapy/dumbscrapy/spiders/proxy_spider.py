from pathlib import Path
import base64
import scrapy
import time


class ProxySpider(scrapy.Spider):
    name = "proxy"
    start_urls = [
        "http://free-proxy.cz/en/",
        "http://free-proxy.cz/en/proxylist/main/2",
        "http://free-proxy.cz/en/proxylist/main/3",
        "http://free-proxy.cz/en/proxylist/main/4",
        "http://free-proxy.cz/en/proxylist/main/5",
    ]

    local_files = [
        "proxy-.html",
        "proxy-2.html",
        "proxy-3.html",
        "proxy-4.html",
        "proxy-5.html",
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

    def start_requests(self):
        for file in self.local_files:
            yield scrapy.Request(
                url=f"file://{Path(file).absolute()}", callback=self.parse_local
            )

    def parse_local(self, response):
        # page = response.url.split("/")[-1]
        # filename = f"proxy-{page}.html"
        # local_file = local_file.append(filename)
        # Path(filename).write_bytes(response.body)
        selector = scrapy.Selector(text=response.body.decode("utf-8"))

        proxies = selector.css("table#proxy_list tbody tr")
        for proxy in proxies:
            encoded = proxy.css("td:nth-child(1) script::text").get()
            if encoded and "Base64.decode" in encoded:
                encoded_ip = encoded.split('"')[1]
                decoded_ip = base64.b64decode(encoded_ip).decode("utf-8")
            port = proxy.css("td:nth-child(2) ::text").get()
            protocl = proxy.css("td:nth-child(3) ::text").get()

            if decoded_ip and port:
                yield {
                    "ip": decoded_ip,
                    "port": port,
                    "protocol": protocl,
                }


class TorCheckSpider(scrapy.Spider):
    name = "tor_check"
    start_urls = ["https://check.torproject.org"]

    def parse(self, response):
        if "Congratulations. This browser is configured to use Tor." in response.text:
            self.log("Tor is working!")
        else:
            self.log("Tor is NOT working.")
