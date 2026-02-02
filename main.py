from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.button import MDFillRoundFlatIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem, MDList
from kivymd.uix.textfield import MDTextField
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from datetime import date
import requests

# Windows size setup
try:
    Window.size = (380, 650)
except:
    pass

store = JsonStore('currency_cache.json')

KV = '''
MDScreen:
    md_bg_color: [0.96, 0.97, 1, 1]

    MDBoxLayout:
        orientation: 'vertical'
        
        MDBoxLayout:
            size_hint_y: None
            height: "120dp"
            md_bg_color: [0.12, 0.15, 0.35, 1]
            radius: [0, 0, 40, 40]
            padding: "20dp"
            orientation: 'vertical'
            
            MDLabel:
                text: "GLOBAL"
                halign: "center"
                font_style: "H4"
                bold: True
                theme_text_color: "Custom"
                text_color: [1, 0.76, 0.03, 1]
                
            MDLabel:
                text: "CURRENCY HUB"
                halign: "center"
                font_style: "Button"
                letter_spacing: "5sp"
                theme_text_color: "Custom"
                text_color: [1, 1, 1, 1]
                
        MDBoxLayout:
            orientation: 'vertical'
            padding: ["20dp", "10dp", "20dp", "20dp"]
            spacing: "15dp"
            
            MDCard:
                orientation: 'vertical'
                padding: "25dp"
                spacing: "20dp"
                radius: [30, 30, 30, 30]
                elevation: 4
                md_bg_color: [1, 1, 1, 1]
                size_hint_y: None
                height: "440dp"
                pos_hint: {"center_x": .5}

                MDLabel:
                    text: "SMART UNLIMITED CONVERSION"
                    halign: "center"
                    theme_text_color: "Secondary"
                    font_style: "Caption"
                    bold: True

                MDTextField:
                    id: amount_input
                    hint_text: "Amount to Convert"
                    mode: "rectangle"
                    input_filter: "float"
                    size_hint_x: 1
                    pos_hint: {"center_x": .5}
                    font_size: "20sp"

                MDBoxLayout:
                    spacing: "15dp"
                    adaptive_height: True
                    
                    MDFillRoundFlatIconButton:
                        id: from_btn
                        text: "USD"
                        icon: "chevron-down"
                        size_hint_x: 0.5
                        md_bg_color: [0.22, 0.35, 0.7, 1]
                        on_release: app.show_currency_picker("from")
                    
                    MDFillRoundFlatIconButton:
                        id: to_btn
                        text: "KES"
                        icon: "chevron-down"
                        size_hint_x: 0.5
                        md_bg_color: [0, 0.5, 0.35, 1]
                        on_release: app.show_currency_picker("to")

                MDLabel:
                    id: result_label
                    text: "0.00"
                    halign: "center"
                    font_style: "H3"
                    bold: True
                    theme_text_color: "Primary"

                MDFillRoundFlatButton:
                    text: "CONVERT NOW"
                    size_hint_x: 1
                    font_size: "20sp"
                    md_bg_color: [0.12, 0.15, 0.35, 1]
                    on_release: app.convert()

            MDLabel:
                text: "Developed by Md. Saidul Islam Sakil"
                halign: "center"
                theme_text_color: "Hint"
                font_style: "Caption"
                italic: True
'''

class CurrencyApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        # 4টি ভ্যালিড ব্যাকআপ API Keys
        self.api_keys = [
            "ce1c713ea1bffbc692d5349b", # Sakil's 1st Key
            "047805167f2b1736b46851b9", # Sakil's 2nd Key
            "8449626359f140d343997232", # Extra Backup 1
            "549887167f2b1736b46852c0"  # Extra Backup 2
        ] 
        self.from_val = "USD"
        self.to_val = "KES"
        self.all_codes = []
        self.dialog = None
        Clock.schedule_once(self.fetch_codes, 0.5)
        return Builder.load_string(KV)

    def fetch_codes(self, dt):
        if store.exists('currency_codes'):
            self.all_codes = store.get('currency_codes')['data']
        
        for key in self.api_keys:
            try:
                r = requests.get(f"https://v6.exchangerate-api.com/v6/{key}/codes", timeout=5)
                if r.status_code == 200:
                    self.all_codes = [f"{c[0]} - {c[1]}" for c in r.json().get('supported_codes', [])]
                    store.put('currency_codes', data=self.all_codes)
                    break
            except: continue
        if not self.all_codes:
            self.all_codes = ["USD - US Dollar", "KES - Kenyan Shilling", "BDT - Bangladeshi Taka"]

    def show_currency_picker(self, picker_type):
        self.active_type = picker_type
        content = MDBoxLayout(orientation="vertical", spacing="10dp", size_hint_y=None, height="400dp")
        self.search_field = MDTextField(hint_text="Search currency (e.g. BDT)", mode="fill")
        self.search_field.bind(text=self.filter_list) 
        self.list_container = MDList()
        self.update_list(self.all_codes)
        scroll = ScrollView()
        scroll.add_widget(self.list_container)
        content.add_widget(self.search_field)
        content.add_widget(scroll)
        self.dialog = MDDialog(
            title="Select Currency",
            type="custom",
            content_cls=content,
            buttons=[MDFlatButton(text="CLOSE", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()

    def update_list(self, items):
        self.list_container.clear_widgets()
        for item in items[:40]:
            self.list_container.add_widget(
                OneLineListItem(text=item, on_release=lambda x: self.select_currency(x.text))
            )

    def filter_list(self, instance, value):
        search_term = value.lower()
        filtered = [c for c in self.all_codes if search_term in c.lower()]
        self.update_list(filtered)

    def select_currency(self, text):
        code = text.split(" - ")[0]
        if self.active_type == "from":
            self.from_val = code
            self.root.ids.from_btn.text = code
        else:
            self.to_val = code
            self.root.ids.to_btn.text = code
        self.dialog.dismiss()

    def convert(self):
        amt = self.root.ids.amount_input.text
        if not amt: return
        today = str(date.today())
        cache_key = f"{self.from_val}_{self.to_val}"
        
        if store.exists(cache_key):
            cached_data = store.get(cache_key)
            if cached_data['date'] == today:
                res = float(amt) * cached_data['rate']
                self.root.ids.result_label.text = f"{res:,.2f}"
                return

        success = False
        for key in self.api_keys:
            url = f"https://v6.exchangerate-api.com/v6/{key}/pair/{self.from_val}/{self.to_val}"
            try:
                r = requests.get(url, timeout=5).json()
                if r.get('result') == 'success':
                    rate = r.get('conversion_rate')
                    res = float(amt) * rate
                    self.root.ids.result_label.text = f"{res:,.2f}"
                    store.put(cache_key, date=today, rate=rate)
                    success = True
                    break
            except: continue
        
        if not success:
            self.root.ids.result_label.text = "Connection Error"

if __name__ == "__main__":
    CurrencyApp().run()