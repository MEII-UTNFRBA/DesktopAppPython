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
from puerto_serie import serial_ports

rm = visa.ResourceManager()


class Main(FloatLayout):
    pass


class VNAConnectPopup(Popup):

    global rm

    def __init__(self, *args):
        super(VNAConnectPopup, self).__init__(*args)
        a=ObjectProperty()
        a = rm.list_resources()
        if len(a)>0:
            box = BoxLayout(orientation='vertical')
            for i in [len(a)]:
                box.add_widget(Button(
                    text=str(a[i-1]),
                    on_press = lambda *args: VNAConnectPopup.hola(self,a[i-1])))
            self.title = 'Seleccione un equipo'
            self.content=box
            self.size_hint=(0.4, 0.4)
        else:
            box = BoxLayout(orientation='vertical')
            box.add_widget(Label(text='No hay equipo conectado'))
            self.title = 'Error'
            self.content=box
            self.size_hint=(0.4, 0.4)
        box.add_widget(Button(
            text="Cancelar",
            on_press=lambda *args: VNAConnectPopup.chau(self)))
#        box.add_widget(SubWidget())
#        box.add_widget(SubWidget())
#        box.add_widget(SubWidget())
#        box.add_widget(SubWidget())
        self.auto_dismiss=False
        self.open()

    @staticmethod
    def chau(self):
        self.dismiss()

    def hola(self,*args):
        print(args)


class ArduinoConnectPopup(Popup):

    def __init__(self, *args):
        super(ArduinoConnectPopup, self).__init__(*args)
        a=serial_ports()
        if len(a) > 0:
            box = BoxLayout(orientation='vertical')
            for i in [len(a)]:
                box.add_widget(Button(
                    text=str(a[i - 1]),
                    on_press=lambda *args: ArduinoConnectPopup.hola(self,a[i - 1])))
            self.title = 'Seleccione un equipo'
            self.content = box
            self.size_hint = (0.4, 0.4)
        else:
            box = BoxLayout(orientation='vertical')
            box.add_widget(Label(text='No hay equipo conectado'))
            self.title = 'Error'
            self.content = box
            self.size_hint = (0.4, 0.4)

        box.add_widget(Button(
            text="Cancelar",
            on_press=lambda *args: ArduinoConnectPopup.chau(self)))
        self.auto_dismiss = False
        self.open()

    @staticmethod
    def chau(self):
        self.dismiss()

    def hola(self,*args):
        print(args)


class MainApp(App):
    def build(self):
        return Main()


if __name__ == '__main__':
    MainApp().run()
