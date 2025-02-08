# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class KpNewsItem(scrapy.Item):
    title = scrapy.Field()  # Заголовок статьи
    description = scrapy.Field()  # Краткое описание
    article_text = scrapy.Field()  # Текст статьи
    publication_datetime = scrapy.Field()  # Дата и время публикации
    header_photo_url = scrapy.Field()  # URL обложки
    keywords = scrapy.Field()  # Ключевые слова
    authors = scrapy.Field()  # Автор(ы)
    source_url = scrapy.Field()  # Ссылка на источник
    header_photo_base64 = scrapy.Field()  # Базовая64-кодированная картинка обложки