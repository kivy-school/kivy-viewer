from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory as F
from kivy.lang import Builder
import kivy_widgets
Window.always_on_top = True

kv = Builder.load_string("""
#:import KivyLexer kivy.extras.highlight.KivyLexer
                         
#:import global_idmap kivy.lang.global_idmap
#:set tailwind_colors [eval(i) for i in global_idmap if '_' in i and i.endswith('0')]

BoxLayout:
    id: reactive_layout
    reloader: reloader
    language_box: language_box
    orientation: 'vertical' if self.width < self.height else 'horizontal'

    Splitter:
        id: editor_pane
        max_size: (reactive_layout.height if self.vertical else \
                         reactive_layout.width) - self.strip_size
        min_size: dp(30) + self.strip_size
        vertical: 1 if reactive_layout.width < reactive_layout.height else 0
        sizable_from: 'bottom' if self.vertical else 'right'
        size_hint: (1, None) if self.vertical else (None, 1)
        size: dp(400), dp(400)
        on_vertical:
            mid_size = self.max_size/2
            if args[1]: self.height = mid_size
            if not args[1]: self.width = mid_size
        ScrollView:
            id: sv
            effect_cls: "ScrollEffect"
            CodeInput:
                id: language_box
                auto_indent: True
                lexer: KivyLexer()
                size_hint: 1, None
                height: max(sv.height, self.minimum_height)
                valign: "top"
                text: ""
                on_text: app.schedule_reload(self.text)
    Screen:
        id: reloader
""")


class ReloaderApp(App):
    kv_content = F.StringProperty()

    def on_kv_content(self, *args):
        self.root.language_box.text = self.kv_content

    def build(self):
        Clock.schedule_interval(self.check_kv_content, 1 / 10)
        return kv

    def check_kv_content(self, dt):
        with open('reloader.kv', 'r') as f:
            text = f.read()

            if text != self.kv_content:
                print('reloading')
                self.kv_content = text
                self.schedule_reload(text)

    def schedule_reload(self, text):
        if 'reloader' not in self.__dict__:
            self.reloader = self.root.reloader

        with open('reloader.kv', 'w') as f:
            f.write(text)
        try:
            Builder.unload_file('reloader.kv')
            kv = Builder.load_file('reloader.kv')
            self.reloader.clear_widgets()
            self.reloader.add_widget(kv)
        except Exception as e:
            print(e)
            if not self.reloader.children:
                self.reloader.add_widget(F.Label(text=str(e)))


if __name__ == '__main__':
    ReloaderApp().run()
