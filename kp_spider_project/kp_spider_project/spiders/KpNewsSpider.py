from collections.abc import Iterable

import scrapy
from parsel import Selector
from playwright.async_api import Page
from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.http import Response

from ..items import KpNewsItem


def should_abort_request(request):
    return "yandex" in request.url or "ya" in request.url or "google" in request.url or "smi2" in request.url


def validate_necessary_field(value):
    if value is None:
        raise DropItem("Field is required")
    return value


class KpNewsSpider(scrapy.Spider):
    name = "kp_news"
    allowed_domains = ["kp.ru"]
    required_articles_count = 1000
    total_scanned_articles = 0

    custom_settings = {
        "PLAYWRIGHT_ABORT_REQUEST": should_abort_request,
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": False},
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
    }

    def start_requests(self) -> Iterable[Request]:
        yield scrapy.Request(
            url="https://www.kp.ru/online/",
            meta={"playwright": True, "playwright_include_page": True},
        )

    async def parse(self, response: Response):
        page: Page = response.meta["playwright_page"]
        while self.total_scanned_articles < self.required_articles_count:
            page_selector = Selector(await page.content())
            articles = page_selector.xpath("//a[contains(@class, 'sc-1tputnk-2')]/@href").getall()
            articles = articles[-25:]
            for article in articles:
                yield scrapy.Request(
                    url=response.urljoin(article),
                    meta={"playwright": True},
                    callback=self.parse_article
                )
            await page.locator(selector="button.sc-abxysl-0.cdgmSL").click(position={"x": 176, "y": 26.5})
            await page.wait_for_timeout(10000)
            self.total_scanned_articles += len(articles)
            print(self.total_scanned_articles)
            del articles
        await page.close()


    async def parse_article(self, response: Response):
        title = response.xpath("//h1[contains(@class, 'sc-j7em19-3')]/text()").get()
        description = response.xpath("//div[contains(@class, 'sc-j7em19-4')]/text()").get()
        article_text = ''.join(response.xpath("//*[contains(@class, 'sc-1wayp1z')]/text()").getall())
        publication_datetime = response.xpath("//span[contains(@class, 'sc-j7em19-1')]/text()").get()
        header_photo_url = response.xpath("//img[contains(@class, 'sc-foxktb-1')]/@src").get()
        keywords = response.xpath("//a[contains(@class, 'sc-1vxg2pp-0')]/text()").getall()
        authors = response.xpath("//span[contains(@class, 'sc-1jl27nw-1')]/text()").getall()
        source_url = response.url

        item = KpNewsItem()

        item["title"] = validate_necessary_field(title)
        item["description"] = validate_necessary_field(description)
        item["article_text"] = validate_necessary_field(article_text)
        item["publication_datetime"] = validate_necessary_field(publication_datetime)
        item["header_photo_url"] = header_photo_url
        item["keywords"] = validate_necessary_field(keywords)
        item["authors"] = validate_necessary_field(authors)
        item["source_url"] = validate_necessary_field(source_url)

        yield item

