import scrapy

class AgribegriSpider(scrapy.Spider):
    name = "agribegri"
    allowed_domains = ["agribegri.com"]

    def start_requests(self):
        # Loop through the first 50 pages
        for page in range(1, 51):  # Pages 1 to 50
            url = f"https://agribegri.com/get_result_lazy.php?page={page}"
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Loop through each product container
        for product in response.css('div.bg-effect-cls'):
            # Extract product details
            product_name = product.css('h4.title-pdt.tp1.product_name_cls.product-name-english.product_name_lazy::text').get()
            quantity = product.css('big.unit_text_cls::text').get()
            notes = product.css('small.product_notes_cls::text').get()
            
            # Extract price details
            final_price = product.css('p.price-pdt.tp5 strong::text').get()
            if not final_price:
                final_price = product.xpath("//p[contains(@class, 'price-pdt tp5')]/strong/text()").get()
            
            original_price = product.css('p.price-pdt.tp5 span i + s::text').get()
            
            # Extract discount
            discount_texts = product.css('p.product_discount.price-pdt.tp5.dark-orange::text').getall()
            discount = ''.join([text.strip() for text in discount_texts if text.strip().isdigit()])
            
            # Extract product URL
            product_url = product.css('a::attr(href)').get()
            
            yield {
                'name': product_name.strip() if product_name else None,
                'quantity': quantity.strip() if quantity else None,
                'notes': notes.strip() if notes else None,
                'final_price': final_price.strip() if final_price else None,
                'original_price': original_price.strip() if original_price else None,
                'discount': discount if discount else None,
                'url': product_url.strip() if product_url else None,
            }
