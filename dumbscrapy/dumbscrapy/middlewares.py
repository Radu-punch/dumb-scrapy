# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals, Request

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
import time
from scrapy.downloadermiddlewares.retry import RetryMiddleware


class TooManyRequestsRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        if response.status == 429 or response.status == 403:
            retry_after = response.headers.get("retry-after", None)

            if retry_after:
                retry_after = int(retry_after)
                spider.logger.warning(
                    f"429 error received. Retrying after {retry_after} seconds."
                )
                time.sleep(retry_after)

            token_url = "https://test-rg8.ddns.net/api/get_token"

            new_token_request = Request(
                url=token_url,
                method="GET",
                callback=self.retry_with_fresh_token,
                errback=self.handle_error,
                cb_kwargs={"original_request": request},
                meta={"retrying_spider": spider},
                dont_filter=True,
            )
            return new_token_request

        return response

    def retry_with_fresh_token(self, response, original_request):
        try:
            cookies = response.headers.getlist("Set-Cookie")
            form_token = None
            for cookie in cookies:
                if b"form_token" in cookie:
                    form_token = cookie.decode().split(";")[0].split("=")[1]
                    break

            if form_token:
                spider = response.meta.get("retrying_spider")
                spider.logger.info(f"Fetched new form_token: {form_token}")

                original_request.cookies["form_token"] = form_token

                return (
                    self._retry(original_request, response, spider) or original_request
                )
            else:
                spider = response.meta.get("retrying_spider")
                spider.logger.error("Unable to fetch form_token during retry")
                return original_request
        except Exception as e:
            spider = response.meta.get("retrying_spider")
            spider.logger.error(f"Error fetching fresh token: {e}")
            return original_request

    def handle_error(self, failure):
        spider = failure.request.meta["spider"]
        spider.logger.error(f"Error during retry with fresh token: {failure}")


class DumbscrapySpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class DumbscrapyDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
