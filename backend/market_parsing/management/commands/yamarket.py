import os
from django.core.management.base import BaseCommand
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from core.settings import BASE_DIR, DIV_CLASS, EMAIL_HOST_USER
from ...models import *
from django.contrib.auth.models import User
from django.core.mail import send_mail


class Command(BaseCommand):
    help = "Парсер цены товара с Яндекс.Маркета"

    def handle(self, *args, **kwargs):
        self.stdout.write("Начат процесс парсинга")
        url = [
            "https://market.yandex.ru/product--super-alkaline-aaa/344134477?sku=100993502710&uniqueId=762288&do-waremd5=c_kQnrCBOq-jrxyNTiR45A&businessId=762288&clid=605&utm_source=762288",
            "https://market.yandex.ru/product--super-alkaline-aa/344135325?sku=100965281506&uniqueId=762288&do-waremd5=OkLRSAKWMxfPDIkZkvqlbA&businessId=762288&clid=605&utm_source=762288",
            "https://market.yandex.ru/product--super-alkaline-aa/344135325?sku=100965448135&uniqueId=762288&do-waremd5=mpynPa_RY7M_YZB4FJqgPA&businessId=762288&clid=605&utm_source=762288",
            "https://market.yandex.ru/product--super-alkaline-aaa/344134477?sku=100604541874&uniqueId=762288&do-waremd5=QSwn1tXxQWuTiDeeNrXQzQ&sponsored=1",
            "https://market.yandex.ru/product--batereika-gp-gp-24aupa21-2crsb4-40-320-4/265322396?sku=103238532080&uniqueId=914247",
        ]

        """ for z in range(1, 10):
            for i in range(len(url)):
                 Link.objects.create(user_id=2, link=url[i])
            print("------------------") """

        def create_driver():
            options = Options()
            options.add_argument(
                f"user-data-dir=/Users/timonen/Library/Application Support/Google/Chrome/Default"
            )  # Путь до профиля можно найти введя в адресную строку Chrome - chrome://version/
            # driver = webdriver.Chrome(executable_path='YOUR_PATH_CHROMEDRIVER', chrome_options=options)
            # options.add_argument(f"user-data-dir={BASE_DIR}/Market_Parser")
            options.add_argument(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
            )
            """ options.add_argument("--headless")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--v=99")
            options.add_argument("--no-sandbox") """
            driver = webdriver.Chrome(
                executable_path="/usr/local/bin/chromedriver", chrome_options=options
            )
            return driver

        def parser_yandex_market(link):
            driver = create_driver()
            driver.get(link)
            time.sleep(3)
            try:
                price = driver.find_element_by_class_name(DIV_CLASS)

                price = price.text
                # print(price)
                # pars_price = price[0].split(" ₽")[0].replace(" ", "")
                pars_price = (
                    price.replace("Цена с картой Яндекс Пэй:", "")
                    .replace(" ₽", "")
                    .replace("/n", "")
                    .strip()
                )

                # print(pars_price)
                driver.quit()

                return pars_price
            except Exception as e:
                print(f"Ошибка парсинга {e}")
                driver.quit()
                return f"error {e}"

        links = Link.objects.all()

        print("Основа")
        for obj in links:
            print(parser_yandex_market(obj.link))
            # email = User.objects.get(username=obj.user).email
            quetstion_func = parser_yandex_market(obj.link)
            if "error" in quetstion_func:
                print(quetstion_func)
                # subject, message = "Ошибка парсинга", f"Ошибка при парсинге ссылки: {obj.link} \n Лог ошибки {quetstion_func}"
                # send_mail( subject,message, EMAIL_HOST_USER, [EMAIL_HOST_USER], fail_silently=False,)
            else:
                last_price = PriceLink.objects.filter(price_link_id=obj.id)
                if len(last_price) != 0:
                    if (
                        int(last_price[len(last_price) - 1].price)
                        != int(quetstion_func)
                    ) == True:
                        # subject, message = "Изменение цены", f"Изменилась цена товара по ссылке: {obj.link}\nБыла {last_price[len(last_price)-1].price}₽, стала {pars_price}₽"
                        # send_mail( subject,message, EMAIL_HOST_USER, [email], fail_silently=False,)
                        PriceLink.objects.create(
                            price_link_id=obj.id, price=quetstion_func
                        )
                else:
                    # subject, message = "Добавление товара на парсинг", f"Добавлен товар на парсинг: {obj.link}\nТекущая цена {pars_price}₽"
                    # send_mail( subject,message, EMAIL_HOST_USER, [email], fail_silently=False,)
                    PriceLink.objects.create(price_link_id=obj.id, price=quetstion_func)

        print("Аналогичные товары")
        links = AnalogLink.objects.all()
        for obj in links:
            # print(parser_yandex_market(obj.link))
            quetstion_func = parser_yandex_market(obj.link)
            if "error" in quetstion_func:
                print(quetstion_func)
                # subject, message = "Ошибка парсинга", f"Ошибка при парсинге ссылки: {obj.link} \n Лог ошибки {quetstion_func}"
                # send_mail( subject,message, EMAIL_HOST_USER, [EMAIL_HOST_USER], fail_silently=False,)
            else:
                last_price = AnalogLinkPrice.objects.filter(analog_link_price_id=obj.id)
                if len(last_price) != 0:
                    if (
                        int(last_price[len(last_price) - 1].analog_price)
                        != int(quetstion_func)
                    ) == True:
                        # subject, message = "Изменение цены", f"Изменилась цена товара по ссылке: {obj.link}\nБыла {last_price[len(last_price)-1].price}₽, стала {pars_price}₽"
                        # send_mail( subject,message, EMAIL_HOST_USER, [email], fail_silently=False,)
                        AnalogLinkPrice.objects.create(
                            analog_link_price_id=obj.id, analog_price=quetstion_func
                        )
                else:
                    # subject, message = "Добавление товара на парсинг", f"Добавлен товар на парсинг: {obj.link}\nТекущая цена {pars_price}₽"
                    # send_mail( subject,message, EMAIL_HOST_USER, [email], fail_silently=False,)
                    AnalogLinkPrice.objects.create(
                        analog_link_price_id=obj.id, analog_price=quetstion_func
                    )
        self.stdout.write("Закончен процесс парсинга")
