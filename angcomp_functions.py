from general_popups import PopupError

########################################################################################################################
### Funciones correspondientes al ang/comp elegido estando en lazo abierto #############################################

# Funcion que verifica el valor ingresado como angulo
def ang_sel_fnc(aux):
    error = 0                                   # Usado para avisar de que hubo un error con el angulo ingresado

    # Me fijo si el numero sin coma ni signo corresponde a un digito valido, ademas de que sea menor a 360 en modulo
    if aux.lstrip('-').replace('.', '', 1).isdigit():
        aux_ang = float(aux)
        if float(aux.lstrip('-')) <= 360:
        # Si es un digito valido, le sumo 360 en caso que sea negativo, sino queda positivo
            if aux_ang < 0:
                c = 360 + float(aux)
            else:
                c = float(aux)
            if c == 360:                # Como 360 es lo mismo que 0, lo dejamos en 0
                c = 0
        else:
            error = 1
    else:
        error = 1                   # Si esta en 1, va a avisar el popup, haciendo que no se cargue el valor
    # Si no es angulo valido, tira error (tiene que ser entre -360 y 360)
    if error:
        txt = 'Angulo no valido.\n Tiene que ser entre -360 y 360 grados'
        PopupError(txt)
        return -1
    return c

# Funcion que verifica el valor ingresado como capacidad


def capa_sel_fnc(aux):
    if aux.replace('.', '', 1).isdigit():
        c = aux                                                 # Hacer algo con esto
    else:
        txt = 'Capacitor no valido'
        PopupError(txt)
        return -1
    return c

# Funcion que verifica el valor ingresado como inductancia


def inductor_sel_fnc(aux):
    if aux.replace('.', '', 1).isdigit():
        c = aux                                                 # Hacer algo con esto
    else:
        txt = 'Inductancia no valida'
        PopupError(txt)
        return -1
    return c
