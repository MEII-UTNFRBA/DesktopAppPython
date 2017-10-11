from general_popups import ErrorPopup

########################################################################################################################
### Funciones correspondientes al ang/comp elegido estando en lazo abierto #############################################

# Funcion que verifica el valor ingresado como angulo


def ang_sel_fnc(args):

    c = 0                                           # Valor inicial
    # Me fijo si el numero sin coma ni signo corresponde a un digito valido
    if args.lstrip('-').replace('.', '', 1).isdigit():
        aux_ang = float(args)
        # Esto es para que el angulo insertado quede entre -360 y 360 grados
        if float(aux_ang) > 360:
            while aux_ang > 360:
                aux_ang -= 360
        elif float(aux_ang) < -360:
            while aux_ang < -360:
                aux_ang += 360
        # Esto es para que el angulo insertado quede entre 0 y 360 grados
        if aux_ang < 0:
            c = 360 + aux_ang
        else:
            c = aux_ang
        if c == 360:                # Como 360 es lo mismo que 0, lo dejamos en 0
            c = 0
    # En caso que no sea un digito valido
    else:
        txt = 'Angulo no valido'
        ErrorPopup(txt)
        c = -1                      # Hubo un error
    return c

# Funcion que verifica el valor ingresado como capacidad


def capa_sel_fnc(aux):
    if aux.replace('.', '', 1).isdigit():
        c = aux                                                 # Hacer algo con esto
    else:
        txt = 'Capacitor no valido'
        ErrorPopup(txt)
        return -1
    return c

# Funcion que verifica el valor ingresado como inductancia


def inductor_sel_fnc(aux):
    if aux.replace('.', '', 1).isdigit():
        c = aux                                                 # Hacer algo con esto
    else:
        txt = 'Inductancia no valida'
        ErrorPopup(txt)
        return -1
    return c
