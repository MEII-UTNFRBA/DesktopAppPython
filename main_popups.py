from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from puerto_serie import serial_ports
from kivy.uix.textinput import TextInput
import visa

########################################################################################################################
### Popups #############################################################################################################

# Popup para agregar un nuevo stub


class NewStubPopup(Popup):

    def __init__(self,callback,mode):
        super(NewStubPopup, self).__init__()
        box = BoxLayout(orientation='vertical')
        if mode > 1:
            box.add_widget(Label(
                    text="No permitido para este modo"))
            self.title = 'Error'
            self.content = box
            self.size_hint = (0.4, 0.4)
            box.add_widget(Button(
                text="OK",
                on_press=lambda *args: NewStubPopup.on_enter(self,callback,1)))
        else:
            box.add_widget(Label(
                    text="Ingrese nombre del stub y presione 'Enter'"))
            self.title = 'Stub nuevo'
            self.content = box
            self.size_hint = (0.4, 0.4)
            self.txtimput = TextInput(multiline=False,on_text_validate=lambda *args: NewStubPopup.on_enter(self,callback,0))
            box.add_widget(self.txtimput)
            box.add_widget(Button(
                text="Cancelar",
                on_press=lambda *args: NewStubPopup.cancel(self,callback)))
        self.auto_dismiss = False
        self.open()

    def cancel(self,callback):
        callback(str("Seleccionar"))
        self.dismiss()

    def on_enter(self,callback,error):
        if error:
            callback("Seleccionar")
        else:
            callback(str(self.txtimput.text))
        self.dismiss()


# Popup para elegir el vna al cual conectarse


class VNAConnectPopup(Popup):

    vna_elegido = StringProperty()
    rm = visa.ResourceManager()

    def __init__(self,callback):
        super(VNAConnectPopup, self).__init__()
        self.vna_elegido = "Desconectado"               #HAY QUE SACARLO, esta solo para que no rompa Cancelar
        a = ObjectProperty()
        a = self.rm.list_resources(query=u'USB?*')
#        a = self.rm.list_resources()
        print(a)
        test = []
        inst_aux = []
        if len(a) > 0:
            for i in range(0,len(a)):
                test.append(1)
                try:
                    inst_test = self.rm.open_resource(str(a[i]))
                    var_aux = str(inst_test.query("*IDN?"))
                    inst_test.close()
                except visa.VisaIOError:
                    test[i] = 0

            for i in range(0,len(a)):
                if test[i] == 1:
                    inst_aux.append(a[i])
        if len(inst_aux) > 0:
            box = BoxLayout(orientation='vertical')
            for i in range(0, len(inst_aux)):
                inst = self.rm.open_resource(str(inst_aux[i]))
                var = str(inst.query("*IDN?"))
                texto = []
                haycoma = 0
                for j in range(0,len(var)):
                    if var[j] == ',':
                        haycoma = haycoma + 1
                    if haycoma == 2:
                        break
                    else:
                        texto.append(var[j])
                texto=''.join(texto)
                box.add_widget(Button(
                    text=texto,
                    on_press = lambda *args: VNAConnectPopup.vnasel(self, callback, inst_aux[i],1,texto)))
                inst.close()
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
            on_press=lambda *args: VNAConnectPopup.cancel(self,callback)))
        self.auto_dismiss = False
        self.open()

    def cancel(self,callback):
        self.dismiss()

    def vnasel(self,callback,vna_sel,status,showname):
        self.vna_elegido = vna_sel
        callback(self.vna_elegido,status,showname)               #Hay que ver si se rompe por esto
#        inst = rm.open_resource(str(vna_elegido))      #Hay que ver como hacer para que no se rompa
#        print(str(self.vna_elegido))
#        inst = self.rm.open_resource(str(self.vna_elegido))
#        print(inst.query("*IDN?"))
#        inst.write("INST:SEL 'NA'")
#        inst.write("CALC:FORM SMIT")
#        inst.write("CALC:PAR:COUN 1")
#        inst.write("CALC:PAR1:DEF S22")
#        inst.write("FREQ:STAR 1E9")
#        inst.write("FREQ:STOP 1E9")
#        inst.write("CALC:MARK1 NORM")
#        inst.write(":FREQ:CENT 803000")          #Para el DSA815 (SA)
#        inst.close()
        self.dismiss()


# Popup para elegir el puerto de arduino al cual conectarse


class ArduinoConnectPopup(Popup):

    puerto_arduino = StringProperty()

    def __init__(self,callback):
        super(ArduinoConnectPopup, self).__init__()
        self.puerto_arduino = "Mongo"
        a=serial_ports()
        if len(a) > 0:
            box = BoxLayout(orientation='vertical')
            for i in range(0, len(a)):
                box.add_widget(Button(
                    text=str(a[i]),
                    on_press=lambda *args: ArduinoConnectPopup.comsel(self, callback, a[i],1)))
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
            on_press=lambda *args: ArduinoConnectPopup.cancel(self, callback)))
        self.auto_dismiss = False
        self.open()

    def cancel(self,callback):
        self.dismiss()

    def comsel(self,callback,port_sel,status):
        self.puerto_arduino = port_sel          #Esta en caso de necesitarlo luego
        callback(self.puerto_arduino,status)
        self.dismiss()
