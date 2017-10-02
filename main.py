from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from puerto_serie import serial_ports
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.clock import Clock
import visa
import serial
import math


class Main(FloatLayout):

    vna_conectado = StringProperty()
    vna_showname = StringProperty()
    arduino_conectado = StringProperty()
    ang_sel = 0
    start = 0
    modulo_out = StringProperty()
    angulo_out = StringProperty()

    def __init__(self):
        super(Main, self).__init__()
        self.vna_conectado = "Desconectado"             #Indica cual vna esta conectado (o dc si no hay)
        self.arduino_conectado = "Desconectado"         #Indica en cual port esta conectado el arduino (o dc si no hay)
        self.vna_showname = "Desconectado"
        self.vna_status = 0                          #Para saber si esta algo conectado o no
        self.arduino_status = 0                      #Lo mismo pero para arduino
        self.flag = 0                                   #Solo para pruebas
        Clock.schedule_interval(self.threadloop,0.1)   #Me "interrumpe" cada 2 seg
        self.rm = visa.ResourceManager()
        self.start = 0
        self.modulo_out=str("MOD: ")
        self.angulo_out=str("ANG: ")

### Loop cada 100ms ####################################################################################################
    def threadloop(self, dt):
        if self.flag == 0:
            self.move_point(20,20)
            self.flag = 1
        else:
            self.flag = 0
            self.move_point(00,00)
        self.ArduinoTestConnection()
        self.VNATestConnection()
        if self.vna_status == 1 and self.start == 1:
            self.vna_lectura()
        if self.arduino_status == 1 and self.start == 1:
            pass
#            self.arduino_lectura()

########################################################################################################################

### Test connections para ambos instrumentos (se hacen en el loop constantemente) ######################################

    def ArduinoTestConnection(self):
        if self.arduino_conectado != "Desconectado":
            try:
                s = serial.Serial(self.arduino_conectado)
                s.close()
            except (OSError, serial.SerialException):
                self.arduino_conectado = "Desconectado"
                if self.start == 1:
                    self.start_error(1,0)        # arg1: Arduino
                    self.start = 0
                self.arduino_status = 0
        elif self.start == 1:
                self.start_error(1,0)        # arg1: Arduino
                self.start = 0
                self.arduino_status = 0


    def VNATestConnection(self):
        if self.vna_conectado != "Desconectado":
            try:
                inst_test = self.rm.open_resource(self.vna_conectado)
                inst_test.close()
            except visa.VisaIOError:
                self.vna_conectado = "Desconectado"
                self.vna_showname = "Desconectado"
                if self.start == 1:
                    self.start_error(0,1)        # arg2: VNA
                    self.start = 0
                self.vna_status = 0
        elif self.start == 1:
                self.start_error(0,1)        # arg2: VNA
                self.start = 0
                self.vna_status = 0


########################################################################################################################

    def move_point(self, x, y):               #Deberia llevarlo a cualquier punto, no estaria andando
        self.punto.posicion_x = x
        self.punto.posicion_y = y
        self.punto.move(self.ids.mongoimg.parent.center)

    def vna_popup(self):
        VNAConnectPopup(self.vna_popup_cb)

    def arduino_popup(self):
        ArduinoConnectPopup(self.arduino_popup_cb)


### Callbacks de las funciones de popup para elegir instrumentos #######################################################

    def vna_popup_cb(self, vna_sel, status, showname):
        self.vna_showname = showname
        self.vna_conectado = vna_sel
        self.vna_status = status

    def arduino_popup_cb(self, ar_sel, status):
        self.arduino_conectado = ar_sel
        self.arduino_status = status

########################################################################################################################

### Seleccion del angulo (el recuadro) #################################################################################
    def ang_sel_fnc(self):
        a = self.ids.ang_input_text.text.lstrip('-').replace('.','',1)
        b = self.ids.ang_input_text.text.lstrip('-')
        if a.isdigit():
            c = float(b)
        else:
            c = 1000
        if not((a.isdigit()) and (c <= 360)):        #Para ver si es num o no
            content = BoxLayout(orientation='vertical')
            popup = Popup(title='Error',content=content,size_hint=(None,None),size=(200,200),auto_dismiss=False)
            content.add_widget(Label(text='Angulo no valido'))
            content.add_widget(Button(text='Cerrar',on_press=popup.dismiss))
            popup.content=content
            popup.open()

########################################################################################################################

    def stop_fnc(self):
        self.start = 0

    def start_fnc(self):
        a = self.ids.ang_input_text.text.lstrip('-').replace('.','',1)
        b = self.ids.ang_input_text.text.lstrip('-')
        if a.isdigit():
            c = float(b)
        else:
            c = 1000
        if not((a.isdigit()) and (c <= 360)):        #Para ver si es num o no
            content = BoxLayout(orientation='vertical')
            popup = Popup(title='Error',content=content,size_hint=(None,None),size=(200,200),auto_dismiss=False)
            content.add_widget(Label(text='Angulo no valido'))
            content.add_widget(Button(text='Cerrar',on_press=popup.dismiss))
            popup.content=content
            popup.open()
            return
        self.ang_sel = self.ids.ang_input_text.text
        self.start = 1

    def vna_lectura(self):
        try:
            inst = self.rm.open_resource(self.vna_conectado)
            mongo2 = inst.query_ascii_values("CALC:SEL:DATA:SDAT?")             #Para leer real imag
            inst.close()
        except visa.VisaIOError:
            self.vna_status = 0
            return

        mongo_real = []
        mongo_img = []
        for i in range(0,len(mongo2)):
            if (i % 2) == 1:
                mongo_img.append(mongo2[i])
            else:
                mongo_real.append(mongo2[i])

        prom_mongo_real = sum(mongo_real) / len(mongo_real)
#        print("Parte real: %s" % prom_mongo_real)
        prom_mongo_img = sum(mongo_img) / len(mongo_img)
#        print("Parte imaginaria: %s" % prom_mongo_img)
        div = prom_mongo_img / prom_mongo_real
#        if prom_mongo_real*prom_mongo_img < 0:
#            print('Angulo: %s' % (180+math.degrees(math.atan(div))))
#        elif (prom_mongo_real*prom_mongo_img < 0) and (prom_mongo_real >0):
#            print('Angulo: %s' % (-180+math.degrees(math.atan(div))))
#        else:
#            print('Angulo:', (math.degrees(math.atan(div))))
#         print('Angulo:', max(inst.query_ascii_values("CALC:DATA:FDAT?")))
#        print('Mag:', math.sqrt(math.pow(prom_mongo_real, 2) + math.pow(prom_mongo_img, 2)))
#        self.start = 0
        self.angulo_out = str("ANG: %s" % round(math.degrees(math.atan(div)),2))
        self.modulo_out = str("MOD: %s" % round(math.sqrt(math.pow(prom_mongo_real, 2) + math.pow(prom_mongo_img, 2)),2))


    def arduino_lectura(self):
        pass

    def start_error(self,arduino,vna):
        content = BoxLayout(orientation='vertical')
        popup = Popup(title='Error', content=content, size_hint=(None, None), size=(200, 200), auto_dismiss=False)
        if arduino == 1:
            content.add_widget(Label(text='Arduino desconectado'))
        elif vna == 1:
            content.add_widget(Label(text='VNA desconectado'))
        content.add_widget(Button(text='Cerrar', on_press=popup.dismiss))
        popup.content = content
        popup.open()
        self.start = 0


class VNAConnectPopup(Popup):

    vna_elegido = StringProperty()
    rm = visa.ResourceManager()

    def __init__(self,callback):
        super(VNAConnectPopup, self).__init__()
        self.vna_elegido = "Desconectado"               #HAY QUE SACARLO, esta solo para que no rompa Cancelar
        a = ObjectProperty()
#        a = rm.list_resources(query=u'USB?*')
        a = self.rm.list_resources()
        test = []
        inst_aux = []
        if len(a) > 0:
            for i in range(0,len(a)):
                test.append(1)
                try:
                    inst_test = self.rm.open_resource(str(a[i]))
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
        print(str(self.vna_elegido))
        inst = self.rm.open_resource(str(self.vna_elegido))
        print(inst.query("*IDN?"))
        inst.write("INST:SEL 'NA'")
        inst.write("CALC:FORM SMIT")
#        inst.write("DISP:MARK:LARG:A:DEF:TRAC1:MEAS S22")
        inst.write("CALC:PAR:COUN 1")
        inst.write("CALC:PAR1:DEF S22")
        inst.write("FREQ:STAR 1E9")
        inst.write("FREQ:STOP 1E9")
        inst.write("CALC:MARK1 NORM")
#        inst.write(":FREQ:CENT 803000")          #Para el DSA815 (SA)
        inst.close()
        self.dismiss()


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


class PuntoEnGrafico(Widget):

    # El grafico del smith utilizado tiene 240 "pasos" de diametro
    posicion_x = NumericProperty(0)
    posicion_y = NumericProperty(0)
    posicion = ReferenceListProperty(posicion_x, posicion_y)

    def move(self,args):
        self.pos = Vector(self.posicion) + args - (3,3)


class MainApp(App):

    def build(self):
        return Main()


if __name__ == '__main__':
    MainApp().run()
