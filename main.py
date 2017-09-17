from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
import visa


class Main(ScreenManager):
    pass


class Gil(FloatLayout):
    pass


class Monguito(Popup):

    def __init__(self, *args):
        super(Monguito, self).__init__(*args)
        box = BoxLayout()
        for i in range(5):
            box.add_widget(Button(
                text = "Yes",
                on_press = lambda *args: Monguito.hola(self)))
        box.add_widget(Button(
                text = "Exit",
                on_press = lambda *args: Monguito.chau(self)))

#        box.add_widget(SubWidget())
#        box.add_widget(SubWidget())
#        box.add_widget(SubWidget())
#        box.add_widget(SubWidget())
        self.title='Test popup'
        self.content=box
        self.size_hint=(0.7, 0.7)
        self.auto_dismiss=False
        self.open()

    @staticmethod
    def chau(self):
        self.dismiss()

    def hola(self):
        pass


class Trabajador(FloatLayout):
    pass
#    def instr_connect(self):
#        global rm
#        print(rm.list_resources())


class Mongo(Popup):
    pass


class SubWidget(Button):

    h = 'Mongo4'

    def press_action(self):
        print('esta entrando')
        return lambda *args: Monguito.chau(Monguito.__self__)


class MyWidget(Popup):

    def __init__(self, *args):
        super(MyWidget, self).__init__(*args)
        self._create_widget()

    def _create_widget(self):
        box=BoxLayout()
        box.add_widget(SubWidget(text='mongo1'))
        box.add_widget(SubWidget(text='mongo2'))
        box.add_widget(SubWidget(text='mongo3'))
        box.add_widget(SubWidget(text='mongo4'))
#        if self.widget is not None:
#            self.remove_widget(self.widget)
#        self.widget = SubWidget()
#        self.add_widget(self.widget)
#        self.widget = SubWidget()
#        self.add_widget(self.widget)
#        self.widget = SubWidget()
#        self.add_widget(self.widget)
#        popup = Popup(title='Test popup', content=box, size_hint=(None, None), size=(400, 400),auto_dismiss=False)


class MainApp(App):
    def build(self):
#        return Gil()
        return Gil()


if __name__ == '__main__':
    MainApp().run()
