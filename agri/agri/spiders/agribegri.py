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

            # Follow the product URL to scrape additional details
            yield scrapy.Request(url=product_url, callback=self.parse_product_details, meta={
                'product_name': product_name,
                'quantity': quantity,
                'notes': notes,
                'final_price': final_price,
                'original_price': original_price,
                'discount': discount,
                'url': product_url,
            })

    def parse_product_details(self, response):
        # Extract additional product details from the individual product page

        # Extract product description
        description = response.css('div.prod_desc p span::text').getall()
        description = " ".join([desc.strip() for desc in description])

        # Extract company/manufacturer name and URL
        company_name = response.css('div.manufacture_box a::text').get().strip() if response.css('div.manufacture_box a::text').get() else None
        company_url = response.css('div.manufacture_box a::attr(href)').get()

        # Extract product image URL
        image_url = response.css('div.zoom-rt-box a img::attr(src)').get()

        # Extract product units (21)
        product_units = response.css('div.units_label::text').get()

        # Extract product quantity options
        product_quantity_options = response.css('div#divUnitscroll br::text').getall()
        product_quantity_option_number = " / ".join([option.strip() for option in product_quantity_options if option.strip()])

        # Yield the final result with all data
        yield {
            'name': response.meta['product_name'],
            'quantity': response.meta['quantity'],
            'notes': response.meta['notes'],
            'final_price': response.meta['final_price'],
            'original_price': response.meta['original_price'],
            'discount': response.meta['discount'],
            'url': response.meta['url'],
            'description': description,
            'company_name': company_name,
            'company_url': company_url,
            'image_url': image_url,
            'product_units': product_units,
            'product_quantity_option_number': product_quantity_option_number
        }
