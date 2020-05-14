import time

from kivy.app import runTouchApp
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.uix.screenmanager import Screen, ScreenManager

from support_files.rss_parser import Parser
from support_files.dtos import Item

screen_manager = ScreenManager()


class ItemScreen(Screen):
    def __init__(self, item: Item, rss_url, **kwargs):
        super().__init__(**kwargs)
        self.item = item
        self.rss_url = rss_url
        self.main_content = main_content = Builder.load_file('layouts/item_screen/main.kv')
        main_content.title_label.text = item.title
        img_links = item.img_links
        try:
            img_links[0]
        except IndexError:
            img_links = [
                "https://lh3.googleusercontent.com/proxy/IDewKjtSRFq4JXcNwZJwSKxI5m70p5T-j5ImFoVBiH5Xw109aTK491K1iP46b1uDnMpNbbNBKEZSJgbkCsbS6sf5gSK_TJMEFTtVcjGiZBtUoCpj6VYDA6Vdg1fWs8A49ZOf_mq8u7E3IeMnXEdxzSoh5nk"]
        for img_link in img_links:
            image = AsyncImage(
                source=img_link)
            image.size = image.image_ratio * 200, 200
            main_content.image.add_widget(image)
        main_content.description_label.text = item.description
        main_content.author_label.text = f"Author: {item.author}"
        main_content.time_label.text = f"Published time: {time.asctime(item.published_parsed)}"
        main_content.url_label.text = f"Link: {item.link}"
        self.add_widget(main_content)

    def on_back(self):
        screen_manager.switch_to(
            MainScreen(name='main', rss_url=self.rss_url)
        )


class ItemButton(Button):
    def __init__(self, item, rss_url, **kwargs):
        super().__init__(**kwargs)
        self.item = item
        self.rss_url = rss_url
        self.size_hint_y = None
        self.height = 400
        self.on_press = self.update_screen
        self.text_size = [350, None]
        self.halign = 'center'
        self.valign = 'middle'
        self.font_size = '15sp'

    def update_screen(self):
        screen_manager.switch_to(ItemScreen(item=self.item, rss_url=self.rss_url), direction='left')


class MainScreen(Screen):
    def __init__(self, rss_url="", **kwargs):
        super().__init__(**kwargs)
        self.rss_url = rss_url
        self.main_content = main_content = Builder.load_file('layouts/main_screen/main.kv')
        main_content.grid_layout.bind(minimum_height=main_content.grid_layout.setter('height'))
        self._load_content()
        self.add_widget(main_content)

    def _load_content(self):
        try:
            for item in Parser.parse_feed(self.rss_url).items:
                try:
                    img_link = item.img_links[0]
                except IndexError:
                    img_link = "https://lh3.googleusercontent.com/proxy/IDewKjtSRFq4JXcNwZJwSKxI5m70p5T-j5ImFoVBiH5Xw109aTK491K1iP46b1uDnMpNbbNBKEZSJgbkCsbS6sf5gSK_TJMEFTtVcjGiZBtUoCpj6VYDA6Vdg1fWs8A49ZOf_mq8u7E3IeMnXEdxzSoh5nk"
                image = AsyncImage(
                    source=img_link)
                image.size = image.image_ratio * 200, 200
                self.main_content.grid_layout.add_widget(image)
                self.main_content.grid_layout.add_widget(
                    ItemButton(text=item.title, item=item, rss_url=self.rss_url))
            self.main_content.text_input.text = self.rss_url
        except ConnectionError:
            self.main_content.text_input.text = "Woops, something happened with url :("

    def load_content(self):
        self.rss_url = self.main_content.text_input.text
        self._load_content()


if __name__ == '__main__':
    import certifi
    import os

    os.environ['SSL_CERT_FILE'] = certifi.where()
    screen_manager.add_widget(MainScreen(name='main'))
    runTouchApp(screen_manager)
