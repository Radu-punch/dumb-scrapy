import scrapy
import json


class FormScrpay(scrapy.Spider):
    name = "form"

    file_path = "./proxy.json"

    def start_requests(self):
        self.logger.info(f"Starting")
        url = "https://test-rg8.ddns.net/api/get_token"
        self.logger.info(f"Request {url} for form_token")
        yield scrapy.Request(
            url=url,
            method="GET",
            callback=self.get_form_token,
            errback=self.req_error,
            dont_filter=True,
        )

    def get_form_token(self, response):
        cookies = response.headers.getlist("Set-Cookie")
        form_token = None
        for cookie in cookies:
            if b"form_token" in cookie:
                form_token = cookie.decode().split(";")[0].split("=")[1]
                break
        if form_token:
            self.logger.info(f"Extract form_token: {form_token}")
            return self.post_request(form_token)
        else:
            self.logger.error("not found")

    def post_request(self, form_token):
        try:
            with open(self.file_path, "r") as file:
                proxy_data = json.load(file)
                self.logger.info(f"Loaded {len(proxy_data)} proxy.")
        except FileNotFoundError:
            self.logger.error(f"{self.file_path} not found")
            return

        proxy_list = [f"{proxy['ip']}:{proxy['port']}" for proxy in proxy_data[:10]]

        if len(proxy_list) < 3:
            self.logger.error("less than 3 proxies.")
            return
        elif len(proxy_list) > 10:
            self.logger.error("more than 10 proxies.")
            return

        proxies_string = ", ".join(proxy_list)

        data = {
            "user_id": "t_b2e64f55",
            "len": len(proxy_list),
            "proxies": proxies_string,
        }
        url = "https://test-rg8.ddns.net/api/post_proxies"

        headers = {
            "Content-Type": "application/json",
        }
        cookies = {"form_token": form_token, "x-user_id": "t_b2e64f55"}
        self.logger.info("I am HEre")

        yield scrapy.Request(
            url=url,
            method="POST",
            headers=headers,
            cookies=cookies,
            body=json.dumps(data),
            callback=self.req_response,
            cb_kwargs={"proxy_list": proxy_list},
            errback=self.req_error,
            dont_filter=True,
        )

    def req_response(self, response, proxy_list):
        self.logger.info(f"Response: {response.text}")
        save_id = response.json().get("save_id")
        saved_data = {save_id: proxy_list}
        filename = "./result.json"
        try:
            with open(filename, "r") as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = {}

        existing_data.update(saved_data)
        with open(filename, "w") as f:
            json.dump(existing_data, f)

    def req_error(self, failure):
        self.logger.error(f"Req error: {failure}")
