# # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                   #
#   Name: Prakash bhatiya                           #
#   Date: 24/05/2023                                #
#   Desc: Scraping Etsy Catalogue Details           #
#   Email: bhatiyaprakash991@gmail.com              #
#                                                   #
# # # # # # # # # # # # # # # # # # # # # # # # # # #
from utils import save_response
import time, os, json
from playwright.sync_api import sync_playwright


class Etsy:
    """ Etsy Class
    """
    # >> just for decoration
    def intro(self):
      print()
      print('  # # # # # # # # # # # # #  # # # # # # # #')
      print('  #                                        #')
      print('  #     SCRAPER FOR Amazon Products        #')
      print('  #           By: PRAKASH BHATIYA          #')
      print('  #             Dt: 24-05-2023             #')
      print('  #      bhatiyaprakash991@gmail.com       #')
      print('  #                                        #')
      print('  # # # # # # # # # # # # #  # # # # # # # #')
      print()

    @staticmethod
    def form_product_url(product_code: str) -> str:
        """ Static method return configure URl"""
        return f"https://www.etsy.com/in-en/listing/{product_code}"

    def get_category(self) -> None:
        """ This method for gettng categories
        """
        categories = []
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        url = "https://www.etsy.com"
        page = context.new_page()
        page.goto(url)
        time.sleep(3)
        categories_list = page.query_selector_all("xpath=//li[contains(@class, 'top-nav-item wt-pb-xs-2 wt-mr-xs-2 wt-display-flex-xs wt-align-items-center')]//a[contains(@class, 'wt-text-link-no-underline')]")
        for cat in categories_list:
            category_dict = {}
            try:
                title = cat.inner_text()
            except Exception:
                title = None
            if "Sellers' Sales Hub" in title and "Gift" in title:
                continue
            cat_url = f"https://www.etsy.com{cat.get_attribute('href')}"
            category_dict['category'] = title
            category_dict['url'] = cat_url
            category_dict['subcategory'] = []

            page2 = context.new_page()
            page2.goto(cat_url)
            time.sleep(3)
            subcat = page2.query_selector_all("xpath=//div[contains(@class, 'wt-block-grid__item wt-text-center-xs wt-break-word wt-pl-xs-1 wt-pr-xs-1 wt-mb-xs-3')]//a")

            for sub in subcat:
                sub_cat_title = sub.inner_text()
                sub_cat_url = sub.get_attribute('href')
                page3 = context.new_page()
                page3.goto(sub_cat_url)
                time.sleep(3)
                sub_cat_dict =  {
                    "category": sub_cat_title,
                    "url": sub_cat_url,
                    "subcategory": []
                }
                subcat2 = page3.query_selector_all("xpath=//div[contains(@class, 'wt-block-grid__item wt-text-center-xs wt-break-word wt-pl-xs-1 wt-pr-xs-1 wt-mb-xs-3')]//a")

                for sub2 in subcat2:
                    sub2_cat_title = sub2.inner_text()
                    sub_cat_url2 = sub2.get_attribute('href')
                    page4 = context.new_page()
                    page4.goto(sub_cat_url2)
                    sub2_cat_dict = {
                        "category": sub2_cat_title,
                        "url": sub_cat_url2,
                        "product": []
                    }
                    sub_cat_dict['subcategory'].append(sub2_cat_dict)
                    page4.close()
                category_dict['subcategory'].append(sub_cat_dict)
                page3.close()
            categories.append(category_dict)
            save_response(categories, "category_list.json", "Data/etsy/")
            page2.close()
        page.close()
        browser.close()

    def get_product_code(self, product_url: str, shop_name: str) ->list:
        """ This method for Product code and return list dict data

        Args:
            product_url (str): String
            shop_name (str): name of the shop

        Returns:
            list: Product code list
        """
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        if product_url:
            url = product_url
        else:
            url = shop_name
        page.goto(url)
        time.sleep(3)
        url = page.query_selector_all("xpath=//a[contains(@class, 'listing-link wt-display-inline-block')]")
        product_code_list = []
        count2 = 0
        for u in url:
            if count2 == 4:
                break
            count2 += 1
            href = u.get_attribute('href')
            product_code = href.split('listing/')[1].split('/70')[0].split('/')[0]
            product_code_list.append({
                "product_code": product_code,
            })
        page.close()
        return product_code_list

    def get_product_detail(self, product_url: str) -> list:
        """ This method to get product details based Url passed on param

        Args:
            product_url (str): String

        Returns:
            list: Product Details
        """
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        product_list = []
        page = context.new_page()
        page.goto(product_url)
        time.sleep(3)
        try:
            title = page.query_selector("xpath=//h1[contains(@class, 'wt-text-body-01 wt-line-height-tight wt-break-word wt-mt-xs-1')]").inner_text()
        except Exception:
            title = None
        try:
            price = page.query_selector("xpath=//p[contains(@class, 'wt-text-title-03 wt-mr-xs-1')]").inner_text().split('\n')[1]
        except Exception:
            price = None
        try:
            shop_name = page.query_selector("xpath=//div[contains(@data-action, 'follow-shop-listing-header')]//span").inner_text()
        except Exception:
            shop_name = None
        try:
            details = page.query_selector_all("xpath=//ul[contains(@class, 'wt-text-body-01 jewelry-attributes wt-pl-xs-3')]//li")
            detail_list = []
            for detail in details:
                detail_list.append(detail.inner_text())
        except Exception:
            detail_list = []
        try:
            description = page.query_selector("xpath=//div[contains(@data-id, 'description-text')]//p").inner_text()
        except Exception:
            description = None
        try:
            image_link = page.query_selector_all("xpath=//img[contains(@class, 'wt-animated wt-max-width-full wt-width-full wt-animated--appear-01')]")
            image_urls = []
            for link in image_link:
                image_urls.append(link.get_attribute('src'))
        except Exception:
            image_urls = None
        try:
            order_list = page.query_selector_all("xpath=//p[contains(@class, 'wt-mt-xs-2 wt-text-black wt-text-caption-title wt-line-height-tight')]")
            order_details = []
            order_details.append({
                "order_place": order_list[0].inner_text(),
                "order_dispatched": order_list[1].inner_text(),
                "order_delivered": order_list[2].inner_text(),
            })
        except Exception:
            order_details = []
        try:
            reviews = self.get_product_reviews(product_url)
        except Exception as e:
            reviews = []

        product_list.append({
            "title": title,
            "price": price,
            "shop_name": shop_name,
            "details": detail_list,
            "description": description,
            "image_urls": image_urls,
            "order_details": order_details,
            "reviews": reviews
        })
        page.close()
        return product_list

    def get_product_reviews(self, product_url: str) -> dict:
        """ This method to get product reviews

        Args:
            product_url (str): string

        Returns:
            dict: reviews of product
        """
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(product_url)
        time.sleep(3)
        review_list = []
        product_name = page.query_selector("xpath=//h1[contains(@class, 'wt-text-body-01 wt-line-height-tight wt-break-word wt-mt-xs-1')]").inner_text()
        total_reviews = page.query_selector("xpath=//div[contains(@id, 'reviews')]//h2").inner_text()
        reviews = page.query_selector_all("xpath=//div[contains(@class, 'wt-grid__item-xs-12')]//p[contains(@class, 'wt-text-truncate--multi-line')]")
        if not reviews:
            page.close()
            return
        reviewer_name = page.query_selector_all("xpath=//div[contains(@class, 'wt-display-flex-xs wt-align-items-center wt-pt-xs-1')]//p")
        helpful = page.query_selector_all("xpath=//div[contains(@data-action, 'helpful-voting-button')]")
        for i in range(0, 4):
            profile = reviewer_name[i].inner_text().split(" ", 1)
            date = profile[1]
            review_list.append({
                "profile": profile[0],
                "date": date,
                "review":reviews[i].inner_text(),
                "helpful": helpful[i].inner_text()
                })
        try:
            star_rating = page.query_selector("xpath=//div[contains(@class, 'wt-display-inline-flex-xs wt-align-items-center wt-flex-wrap')]//span[contains(@class, 'wt-screen-reader-only')]").inner_text()
        except Exception as e:
            star_rating = None
        try:
            star_ratings_list = []
            star_ratings = page.query_selector_all("xpath=//div[contains(@class, 'histogram-rating wt-align-self-center wt-text-right-md')]")
            star_ratings_list.append({
                "five star": star_ratings[0].inner_text(),
                "four star": star_ratings[1].inner_text(),
                "three star": star_ratings[2].inner_text(),
                "two star": star_ratings[3].inner_text(),
                "one star": star_ratings[4].inner_text(),
            })
        except Exception as e:
            star_ratings_list = []
        review_dict = {
            "product_name": product_name,
            "total_reviews": total_reviews,
            "star_rating": star_rating,
            "types_of_rating": star_ratings_list,
            "reviews": review_list,
        }
        page.close()
        return review_dict

    def get_category_tree(self) -> None:
        """ This method to get category tree
        """
        json_path = os.path.join(os.path.dirname(__file__), "Data/etsy/")
        with open(os.path.join(json_path, "category_list.json"), "r", encoding="utf-8") as category:
            data = json.load(category)
        for x in data:
            for i in x['subcategory']:
                for j in i['subcategory']:
                    code_list = self.get_product_code(j['url'], "")
                    for code in code_list:
                        product_url = self.form_product_url(code['product_code'])
                        code["product_details"] = self.get_product_detail(product_url)
                    j['product'] = code_list
                    save_response(data, "category_list.json", "Data/etsy/")

    def scrape_shop(self, shop_url: str) -> list:
        """ This method for scrape shop details

        Args:
            shop_url (str): string

        Returns:
            list: code list
        """
        product_codes = etsy.get_product_code("", shop_url)
        for product_code in product_codes:
            product_code["product_details"] = self.get_product_detail(self.form_product_url(product_code['product_code']))
        return product_codes

    # >> Revie Not Done Yet
    # def scrape_reviews(self) -> :
    #     json_path = os.path.join(os.path.dirname(__file__), "Data/etsy/")
    #     with open(os.path.join(json_path, "category_list.json"), "r", encoding="utf-8") as category:
    #         data = json.load(category)
    #     browser = p.chromium.launch(headless=False)
    #     context = browser.new_context()
    #     for x in data:
    #         for x in data:
    #             for i in x['subcategory']:
    #                 for j in i['subcategory']:
    #                     for k in j['product']:
    #                         review = {}
    #                         review['title'] = k['title']
    #                         page = context.new_page()
    #                         page.goto(k['url'])
    #                         time.sleep(3)
    #                         review['total_reviews'] = page.query_selector("xpath=////div[contains(@id, 'reviews')]//h2").inner_text()
    #                         review['reviews'] = []



if __name__ == '__main__':
    etsy = Etsy()
    with sync_playwright() as p:
        etsy.intro()
        etsy.get_category_tree()
        etsy.scrape_shop("https://www.etsy.com/in-en/shop/LielandLentz")