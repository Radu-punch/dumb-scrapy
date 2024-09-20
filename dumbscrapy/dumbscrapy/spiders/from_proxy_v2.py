import scrapy
import json
import random


class FormScrapy(scrapy.Spider):
    name = "form2"

    file_path = "./proxy.json"

    def start_requests(self):
        self.logger.info("Starting")
        with open(self.file_path, "r") as file:
            self.proxy_data = json.load(file)
            if not isinstance(self.proxy_data, list):
                self.logger.error("Proxy data is not a list.")
                return
            self.logger.info(f"Loaded {len(self.proxy_data)} proxies.")

        if not hasattr(self, "proxy_data"):
            self.logger.error("Proxy data is not loaded.")
            return

        total_proxies = len(self.proxy_data)
        self.logger.info(f"Total proxies to process: {total_proxies}")

        for i in range(0, total_proxies, 10):
            proxy_batch = self.proxy_data[i : i + 10]
            if len(proxy_batch) < 3 and i == total_proxies - 1:
                self.logger.error("Last batch contains less than 3 proxies. Skipping.")
                continue

            proxy_list = [f"{proxy['ip']}:{proxy['port']}" for proxy in proxy_batch]
            self.logger.info(f"Processing batch: {proxy_list}")
            url = "https://test-rg8.ddns.net/api/get_token"

            delay = random.uniform(1, 5)

            yield scrapy.Request(
                url=url,
                method="GET",
                callback=self.get_form_token,
                errback=self.req_error,
                cb_kwargs={"proxy_list": proxy_list},
                dont_filter=True,
                meta={"download_delay": delay},
            )

    def get_form_token(self, response, proxy_list):
        try:
            cookies = response.headers.getlist("Set-Cookie")
            form_token = None
            for cookie in cookies:
                if b"form_token" in cookie:
                    form_token = cookie.decode().split(";")[0].split("=")[1]
                    break

            if form_token:
                self.logger.info(
                    f"Extracted form_token: {form_token} for batch: {proxy_list}"
                )
                return self.post_request(form_token, proxy_list)
            else:
                self.logger.error(f"form_token not found for batch: {proxy_list}")
        except Exception as e:
            self.logger.error(f"Error in get_form_token: {e}")

    def post_request(self, form_token, proxy_list):
        try:
            data = {
                "user_id": "t_b2e64f55",
                "len": len(proxy_list),
                "proxies": ", ".join(proxy_list),
            }
            url = "https://test-rg8.ddns.net/api/post_proxies"

            headers = {
                "Content-Type": "application/json",
            }
            cookies = {"form_token": form_token, "x-user_id": "t_b2e64f55"}
            delay = random.uniform(3, 5)
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
                meta={"download_delay": delay},
            )
        except Exception as e:
            self.logger.error(f"Error in post_request: {e}")

    def req_response(self, response, proxy_list):
        try:
            self.logger.info(f"Response: {response.text}")
            save_id = response.json().get("save_id")
            if save_id is None:
                self.logger.error(
                    f"save_id not found in response for batch: {proxy_list}"
                )
                return

            saved_data = {save_id: proxy_list}
            filename = "./result.json"

            try:
                with open(filename, "r") as file:
                    existing_data = json.load(file)
            except FileNotFoundError:
                existing_data = {}
            except json.JSONDecodeError:
                self.logger.error(f"Error decoding JSON from {filename}")
                existing_data = {}

            existing_data.update(saved_data)
            with open(filename, "w") as f:
                json.dump(existing_data, f)
        except Exception as e:
            self.logger.error(f"Error in req_response: {e}")

    def req_error(self, failure):
        if failure.value.response.status == 429:
            self.logger.error(
                f"Rate limit reached, will retry...{failure.value.response}"
            )
            # Optionally implement a backoff strategy
            raise scrapy.exceptions.IgnoreRequest()
        else:
            self.logger.error(f"Request error: {failure}")
