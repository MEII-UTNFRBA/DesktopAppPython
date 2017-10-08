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
from kivy.uix.textinput import TextInput
import visa
import serial
import math
from si_prefix import si_format
from kivy.config import Config
from main_popups import ArduinoConnectPopup,VNAConnectPopup,NewStubPopup

Config.set('graphics', 'resizable', False)              # Para que no se deforme por resizear
Config.set('kivy', 'exit_on_escape', '0')               # Para que no se cierre cuando se toca "Esc"


class Main(FloatLayout):

    vna_conectado = StringProperty()
    vna_showname = StringProperty()
    arduino_conectado = StringProperty()
    ang_sel = 0
    start = 0
    modulo_out = StringProperty()
    angulo_out = StringProperty()
    z_out = StringProperty()
#    frec_ol = ["First thing", "Second thing", "Third thing"]
    stub_sel = StringProperty()                         # Va a ser el stub que vaya a elegir
    stubs = ""                                          # Para listar los stubs guardados
    mode_state = 0                                      # Modo en el que nos encontramos:
                                                            # 0: Calibracion precisa
                                                            # 1: Calibracion rapida
                                                            # 2: Lazo abierto preciso
                                                            # 3: Lazo abierto rapido
                                                            # 4: Ninguno

    def __init__(self):
        super(Main, self).__init__()
        self.vna_conectado = "Desconectado"             # Indica cual vna esta conectado (o dc si no hay)
        self.arduino_conectado = "Desconectado"         # Indica en cual port esta conectado el arduino (o dc si no hay)
        self.vna_showname = "Desconectado"              # El nombre que muestra (asi aparece solo fabr y modelo)
        self.vna_status = 0                             # Para saber si esta algo conectado o no
        self.arduino_status = 0                         # Lo mismo pero para arduino
        Clock.schedule_interval(self.threadloop,0.1)    # Me "interrumpe" cada 100 mseg
        self.rm = visa.ResourceManager()                # rm es un "tipo" visa
        self.start = 0                                  # Para los botones "Comenzar" y "Detener"
        self.modulo_out=str("MOD= ")                    # String que indica en pantalla lo dicho
        self.angulo_out=str("ANG= ")                    # String que indica en pantalla lo dicho
        self.z_out = str("COMP: ")                      # String que indica en pantalla lo dicho
        self.ids.stub_sel_id.values = ['Nuevo']         # Deberia leer los stubs existentes y listarlos aca

########################################################################################################################
### Loop cada 100ms ####################################################################################################

    def threadloop(self, dt):
        self.ModeSel_check()                            # En base al modo elegido, habilita o deshabilita widgets
        self.ArduinoTestConnection()                    # Chequea el estado del conexion del arduino
        self.VNATestConnection()                        # Chequea el estado de conexion del vna
        if self.vna_status == 1 and self.start == 1:
            self.vna_lectura()                          # Se ejecuta solo si comenzo y si esta seleccionado el vna
        if self.arduino_status == 1 and self.start == 1:
            pass
#            self.arduino_lectura()

########################################################################################################################
### Chequea el modo elegido y, en base a eso, habilita o deshabilita widgets ###########################################

    def ModeSel_check(self):
        if self.start == 0:                                     # Para que cuando salga del start vuelva esto
            self.ids.operation_text.disabled = False
            self.ids.calibracionprecision_checkbox.disabled = False
            self.ids.calibracionprecision_text.disabled = False
            self.ids.calibracionrapida_checkbox.disabled = False
            self.ids.calibracionrapida_text.disabled = False
            self.ids.openloopprecision_checkbox.disabled = False
            self.ids.openloopprecision_text.disabled = False
            self.ids.openlooprapido_checkbox.disabled = False
            self.ids.openlooprapido_text.disabled = False

            if self.ids.calibracionprecision_checkbox.active:
                self.mode_state = 0                             # Para indicar que estoy en este modo

                # Deshabilito el Comenzar y Detener
                self.ids.start.disabled = False
                self.ids.stop.disabled = False

                # Activo lo que tenga que ver con el vna
                self.ids.vna_connect.disabled = False
                self.ids.vna_text.disabled = False
                self.ids.calibracion_puerto_text.disabled = False
                self.ids.calibracion_seteo_puerto1.disabled = False
                self.ids.calibracion_seteo_puerto1_text.disabled = False
                self.ids.calibracion_seteo_puerto2.disabled = False
                self.ids.calibracion_seteo_puerto2_text.disabled = False

                #Dejo solo la seleccion de frecuencia como input
                self.ids.freq_text.disabled = False
                self.ids.freq_input.disabled = False
                self.ids.freq_text_unidad.disabled = False
                self.ids.frec_precision.disabled = True

                # Deshabilito el seteo de componente o angulo
                self.ids.angcomp_text.disabled = True
                self.ids.angcomp_input.disabled = True
                self.ids.angcomp_seteo_angulo.disabled = True
                self.ids.angcomp_seteo_angulo_text.disabled = True
                self.ids.angcomp_seteo_capacitor.disabled = True
                self.ids.angcomp_seteo_c_text.disabled = True
                self.ids.angcomp_seteo_inductor.disabled = True
                self.ids.angcomp_seteo_l_text.disabled = True

            elif self.ids.calibracionrapida_checkbox.active:
                self.mode_state = 1                             # Para indicar que estoy en este modo

                # Deshabilito el Comenzar y Detener
                self.ids.start.disabled = False
                self.ids.stop.disabled = False

                # Activo lo que tenga que ver con el vna
                self.ids.vna_connect.disabled = False
                self.ids.vna_text.disabled = False
                self.ids.calibracion_puerto_text.disabled = False
                self.ids.calibracion_seteo_puerto1.disabled = False
                self.ids.calibracion_seteo_puerto1_text.disabled = False
                self.ids.calibracion_seteo_puerto2.disabled = False
                self.ids.calibracion_seteo_puerto2_text.disabled = False

                #Saco lo que tenga que ver con seleccion de frecuencia
                self.ids.freq_text.disabled = True
                self.ids.freq_input.disabled = True
                self.ids.freq_text_unidad.disabled =True
                self.ids.frec_precision.disabled = True

                # Deshabilito el seteo de componente o angulo
                self.ids.angcomp_text.disabled = True
                self.ids.angcomp_input.disabled = True
                self.ids.angcomp_seteo_angulo.disabled = True
                self.ids.angcomp_seteo_angulo_text.disabled = True
                self.ids.angcomp_seteo_capacitor.disabled = True
                self.ids.angcomp_seteo_c_text.disabled = True
                self.ids.angcomp_seteo_inductor.disabled = True
                self.ids.angcomp_seteo_l_text.disabled = True

            elif self.ids.openloopprecision_checkbox.active:
                self.mode_state = 2                             # Para indicar que estoy en este modo

                # Deshabilito el Comenzar y Detener
                self.ids.start.disabled = False
                self.ids.stop.disabled = False

                # Desactivo lo que tenga que ver con el vna
                self.ids.vna_connect.disabled = True
                self.ids.vna_text.disabled = True
                self.ids.calibracion_puerto_text.disabled = True
                self.ids.calibracion_seteo_puerto1.disabled = True
                self.ids.calibracion_seteo_puerto1_text.disabled = True
                self.ids.calibracion_seteo_puerto2.disabled = True
                self.ids.calibracion_seteo_puerto2_text.disabled = True

                # Dejo solo la seleccion de frecuencia como seleccion especifica
                self.ids.freq_text.disabled = False
                self.ids.freq_input.disabled = True
                self.ids.freq_text_unidad.disabled = True
                self.ids.frec_precision.disabled = False

                # Habilito el seteo de componente o angulo
                self.ids.angcomp_text.disabled = False
                self.ids.angcomp_input.disabled = False
                self.ids.angcomp_seteo_angulo.disabled = False
                self.ids.angcomp_seteo_angulo_text.disabled = False
                self.ids.angcomp_seteo_capacitor.disabled = False
                self.ids.angcomp_seteo_c_text.disabled = False
                self.ids.angcomp_seteo_inductor.disabled = False
                self.ids.angcomp_seteo_l_text.disabled = False

            elif self.ids.openlooprapido_checkbox.active:
                self.mode_state = 3                             # Para indicar que estoy en este modo

                # Deshabilito el Comenzar y Detener
                self.ids.start.disabled = False
                self.ids.stop.disabled = False

                # Desactivo lo que tenga que ver con el vna
                self.ids.vna_connect.disabled = True
                self.ids.vna_text.disabled = True
                self.ids.calibracion_puerto_text.disabled = True
                self.ids.calibracion_seteo_puerto1.disabled = True
                self.ids.calibracion_seteo_puerto1_text.disabled = True
                self.ids.calibracion_seteo_puerto2.disabled = True
                self.ids.calibracion_seteo_puerto2_text.disabled = True

                # Dejo solo la seleccion de frecuencia como input
                self.ids.freq_text.disabled = False
                self.ids.freq_input.disabled = False
                self.ids.freq_text_unidad.disabled = False
                self.ids.frec_precision.disabled = True

                # Habilito el seteo de componente o angulo
                self.ids.angcomp_text.disabled = False
                self.ids.angcomp_input.disabled = False
                self.ids.angcomp_seteo_angulo.disabled = False
                self.ids.angcomp_seteo_angulo_text.disabled = False
                self.ids.angcomp_seteo_capacitor.disabled = False
                self.ids.angcomp_seteo_c_text.disabled = False
                self.ids.angcomp_seteo_inductor.disabled = False
                self.ids.angcomp_seteo_l_text.disabled = False

            else:
                self.mode_state = 4                             # Para indicar que estoy en este modo

                # Desactivo lo que tenga que ver con el vna
                self.ids.vna_connect.disabled = True
                self.ids.calibracion_puerto_text.disabled = True
                self.ids.calibracion_seteo_puerto1.disabled = True
                self.ids.calibracion_seteo_puerto1_text.disabled = True
                self.ids.calibracion_seteo_puerto2.disabled = True
                self.ids.calibracion_seteo_puerto2_text.disabled = True

                # Desactivo lo de frecuencia
                self.ids.freq_text.disabled = True
                self.ids.freq_input.disabled = True
                self.ids.freq_text_unidad.disabled = True
                self.ids.frec_precision.disabled = True

                # Deshabilito el seteo de componente o angulo
                self.ids.angcomp_text.disabled = True
                self.ids.angcomp_input.disabled = True
                self.ids.angcomp_seteo_angulo.disabled = True
                self.ids.angcomp_seteo_angulo_text.disabled = True
                self.ids.angcomp_seteo_capacitor.disabled = True
                self.ids.angcomp_seteo_c_text.disabled = True
                self.ids.angcomp_seteo_inductor.disabled = True
                self.ids.angcomp_seteo_l_text.disabled = True

                # Deshabilito el Comenzar y Detener
                self.ids.start.disabled = True
                self.ids.stop.disabled = True

########################################################################################################################
### Test connections para ambos instrumentos (se hacen en el loop constantemente) ######################################

    def ArduinoTestConnection(self):
        if self.arduino_conectado != "Desconectado":        # Si esta desconectado, no hace falta chequear conn
            try:
                s = serial.Serial(self.arduino_conectado)
                s.close()
            except (OSError, serial.SerialException):       # En caso que no pueda conectarme con el arduino
                self.arduino_conectado = "Desconectado"
                if self.start == 1:                         # Si habia comenzado, salta un popup diciendo que se
                                                            #desconecto el arduino
                    self.start_error(1,0)                   # arg1: Arduino
                    self.start = 0
                self.arduino_status = 0
        elif self.start == 1:                               # Si esta dc, no tendria ni que estar activo!
                self.start_error(1,0)                       # arg1: Arduino
                self.start = 0
                self.arduino_status = 0

    def VNATestConnection(self):                            # Mismo principio que el de arduino
        if self.vna_conectado != "Desconectado":
            try:
                inst_test = self.rm.open_resource(self.vna_conectado)
                inst_test.close()
            except visa.VisaIOError:
                self.vna_conectado = "Desconectado"
                self.vna_showname = "Desconectado"
                if self.start == 1:
                    self.start_error(0,1)                   # arg2: VNA
                    self.start = 0
                self.vna_status = 0
        elif self.start == 1:
                self.start_error(0,1)                       # arg2: VNA
                self.start = 0
                self.vna_status = 0

########################################################################################################################
### Lectura del vna cuando esta corriendo el programa ##################################################################

    def vna_lectura(self):
        try:
            inst = self.rm.open_resource(self.vna_conectado)
            measure = inst.query_ascii_values("CALC:SEL:DATA:SDAT?")        # Para leer real imag
            inst.close()
        except visa.VisaIOError:                                            # Si no se puede hacer, es que se dc o algo
            self.vna_status = 0
            return

        measure_real = []
        measure_img = []
        for i in range(0, len(measure)):                                    # Lo separo en real e img
            if (i % 2) == 1:
                measure_img.append(measure[i])
            else:
                measure_real.append(measure[i])

        prom_measure_real = sum(measure_real) / len(measure_real)           # Hago el promedio de ambas partes
        prom_measure_img = sum(measure_img) / len(measure_img)
        div = prom_measure_img / prom_measure_real                          # Hago la div de ambas
        ang1 = round(math.degrees(math.atan(div)), 2)                       # Calculo el angulo
        if prom_measure_real > 0 and prom_measure_img > 0:                  # Correccion del angulo para tenerlo de
                                                                            #0 a 360 grados
            ang = ang1
        elif prom_measure_real < 0 < prom_measure_img:
            ang = 180 + ang1
        elif prom_measure_real < 0 and prom_measure_img < 0:
            ang = 180 + ang1
        else:
            ang = 360 + ang1

        mod = round(math.sqrt(math.pow(prom_measure_real, 2) + math.pow(prom_measure_img, 2)), 2)   # Calculo modulo
        self.angulo_out = str("ANG= %s" % round(ang))                       # Lo que va a imprimir con el angulo
        self.modulo_out = str("MOD= %s" % mod)                              # Lo que va a imprimir con el modulo
        #        self.angulo_out = str("Re: %s" % prom_mongo_real)
        #        self.modulo_out = str("Im: %s" % prom_mongo_img)
        self.move_point(round(prom_measure_real * 120, 0), round(prom_measure_img * 120, 0))    # Mueve el punto

        #        if (round(ang)/float(self.ang_sel)) > 1:
        #            s = serial.Serial(self.arduino_conectado)
        #            s.write('S')
        #            s.close()

        s_complex = complex(prom_measure_real, prom_measure_img)            # Paso la medicion a compleja
        z_aux = (1 + s_complex) / (1 - s_complex) * 50                      # Calculo la impedancia
        if prom_measure_img < 0:                                            # Imprime la L o C en base a la freq
            z_posta = -1 / (z_aux.imag * 2 * 3.14159 * pow(10, 9))
            self.z_out = str("COMP: C = %sF" % si_format(z_posta, precision=2))
        else:
            z_posta = z_aux.imag / (2 * 3.14159 * pow(10, 9))
            self.z_out = str("COMP: L = %sH" % si_format(z_posta, precision=2))

########################################################################################################################
### Lectura del arduino cuando esta corriendo el programa ##############################################################

    def arduino_lectura(self):
        pass

########################################################################################################################
### Error en caso de que estaba corriendo el programa y se desconecto algun equipo #####################################

    def start_error(self, arduino, vna):
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

########################################################################################################################
### Funcion para mover el punto dentro del smith #######################################################################

    def move_point(self, x, y):                             # Le paso la pos x,y que quiero (Esta referido al centro del
                                                            #diagrama de smith utilizado)
        self.punto.posicion_x = x
        self.punto.posicion_y = y
        self.punto.move(self.ids.smith_img.parent.center)   # Como bien lo dice, mueve el punto a la pos x,y

########################################################################################################################
### Llaman a los popups para conectarse tanto con arduino como con el vna ##############################################

    def vna_popup(self):
        VNAConnectPopup(self.vna_popup_cb)

    def arduino_popup(self):
        ArduinoConnectPopup(self.arduino_popup_cb)


########################################################################################################################
### Callbacks de las funciones de popup ################################################################################

    def vna_popup_cb(self, vna_sel, status, showname):
        self.vna_showname = showname                    # El nombre que va a mostrar en la pantalla del equipo
        self.vna_conectado = vna_sel                    # Aca esta guardado el comando que se usa para abrir el vna
        self.vna_status = status                        # Activa el vna

    def arduino_popup_cb(self, ar_sel, status):
        self.arduino_conectado = ar_sel                 # Sirve tanto como para mostar el nombre como para llamarlo
        self.arduino_status = status                    # Activa el arduino

        # Mueve el stub a alguno de los dos extremos, o sea, los fines de carrera para tener una referencia.
        s = serial.Serial(self.arduino_conectado)
        s.write('I20000U\n')
        print(s.readline())
        s.close()

# Agrega el stub nuevo a la lista
    def stub_new_popup_cb(self, stub_name):
        if stub_name == "Seleccionar":
            self.ids.stub_sel_id.text = "Seleccionar"
        else:
            a = []
            for i in range(0, len(self.ids.stub_sel_id.values)):
                if i == (len(self.ids.stub_sel_id.values)-1):
                    a.append(str(stub_name))
                a.append(self.ids.stub_sel_id.values[i])
            self.ids.stub_sel_id.values = a
            self.ids.stub_sel_id.text = stub_name

########################################################################################################################
### Funcion que se llama al elegir un stub #############################################################################

    def on_stub_selected(self):
        if self.ids.stub_sel_id.text == "Nuevo":
            NewStubPopup(self.stub_new_popup_cb,self.mode_state)

########################################################################################################################
### Seleccion del angulo (el recuadro) #################################################################################

    def ang_sel_fnc(self):
        a = self.ids.ang_input_text.text.lstrip('-').replace('.','',1)      # Le saco al numero el signo y la coma
        b = self.ids.ang_input_text.text.lstrip('-')                        # A este solo le saco el signo
        if a.isdigit():                                                     # Me fijo si el numero pelado corresponde
                                                                            #a un digito valido
            c = float(b)                                                    # De ser asi lo guardo en c
        else:
            c = 1000
        if not((a.isdigit()) and (c <= 360)):                               # Si no es angulo valido, tira error (tiene
                                                                            #que ser entre 0 y 360)
            content = BoxLayout(orientation='vertical')
            popup = Popup(title='Error',content=content,size_hint=(None,None),size=(200,200),auto_dismiss=False)
            content.add_widget(Label(text='Angulo no valido'))
            content.add_widget(Button(text='Cerrar',on_press=popup.dismiss))
            popup.content=content
            popup.open()

########################################################################################################################
### Funcion correspondiente al boton "Detener# #########################################################################

    def stop_fnc(self):
        self.start = 0

########################################################################################################################
### Funcion correspondiente al boton "Comenzar" ########################################################################

    def start_fnc(self):                                                    # Se hace lo mismo que con el ok de angsel
        a = self.ids.ang_input_text.text.lstrip('-').replace('.','',1)
        b = self.ids.ang_input_text.text.lstrip('-')
        if a.isdigit():
            c = float(b)
        else:
            c = 1000
        if not((a.isdigit()) and (c <= 360)):                               #Para ver si es num o no
            content = BoxLayout(orientation='vertical')
            popup = Popup(title='Error',content=content,size_hint=(None,None),size=(200,200),auto_dismiss=False)
            content.add_widget(Label(text='Angulo no valido'))
            content.add_widget(Button(text='Cerrar',on_press=popup.dismiss))
            popup.content=content
            popup.open()
            return
        self.ang_sel = self.ids.ang_input_text.text                         # Carga el valor del angulo
        self.start = 1                                                      # Hace que comience el programa
        self.ArduinoTestConnection()                                        # Checks profilacticos
        self.VNATestConnection()
        if self.vna_status == 1 and self.start == 1:                        # Por si las moscas tambien
            inst = self.rm.open_resource(str(self.vna_conectado))
            print(inst.query("*IDN?"))
            inst.write("INST:SEL 'NA'")
            inst.write("CALC:FORM SMIT")
            #        inst.write("DISP:MARK:LARG:A:DEF:TRAC1:MEAS S22")
            inst.write("CALC:PAR:COUN 1")

            # Estos habria que ponerlos para que se puedan ajustar despues
            inst.write("CALC:PAR1:DEF S22")
            inst.write("FREQ:STAR 1E9")
            inst.write("FREQ:STOP 1E9")
            ##############################################################
            inst.write("CALC:MARK1 NORM")
            inst.close()

            s = serial.Serial(self.arduino_conectado)
            s.write('DU\n')
            s.write(str(c/360*15000))
            s.close()
            #        inst.write(":FREQ:CENT 803000")          #Para el DSA815 (SA)

########################################################################################################################
### Para graficar el punto #############################################################################################


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
