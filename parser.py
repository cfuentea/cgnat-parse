#!/usr/bin/env python3
# main developers: @rat2k4, @cfuentea
# Inspiration: OBM Corp <3

import re
import json
from datetime import datetime


# Genera diccionario a partir de los campos extraidos

def to_dict(date_log, timestamp, nodo, accion, ip_interna, ip_externa, puerto_inicio, puerto_fin):
    reg = {"timestamp": timestamp,
    "date_log": date_log,
    "nodo": nodo,
    "accion": accion,
    "ip_interna": ip_interna,
    "ip_externa": ip_externa,
    "puerto_inicio": puerto_inicio,
    "puerto_fin": puerto_fin
           }
    return reg

# Determina que tipo de log esta procesado

def procesar_registro(registro):
    if re.search('.*NAT44.*', registro):
        tipo = 'Cisco'
        return cisco_nat44_log(registro)

    elif re.search('.*jservices-nat.*', registro):
        tipo = 'Juniper'
        return (juniper_nat44_log(registro))

# Cisco entrega formato de fecha "especial", transforma a mes a numero con padding.

def month_to_number(month):
    return str(datetime.strptime(month,'%b').month).rjust(2, '0')

# Procesa log de Cisco

def cisco_nat44_log(log_line):
    try:
        partes = log_line.split(' - NAT44 - ')
        parte_comun = partes[0].strip()
        entradas_nat44 = partes[1]

        # Dividir la parte común en campos individuales
        campos_comun = parte_comun.split(maxsplit=8)
        campos_comun[6] = month_to_number(campos_comun[6])
        campos_comun[7] = campos_comun[7].rjust(2, '0')
        timestamp = ' '.join(campos_comun[:3])
        nodo_red = campos_comun[3]
        timestamp_evento = '-'.join(campos_comun[5:8])
        hora_cisco = " ".join(campos_comun[8:]).strip(' -')
        timestamp_evento = f"{timestamp_evento} {hora_cisco}"

        entradas = entradas_nat44.split('][')
        entradas = [entrada.strip('[]') for entrada in entradas]

        nuevas_lineas = []
        for entrada in entradas:
            nueva_linea = extraer_datos_cisco(timestamp, nodo_red, timestamp_evento, entrada)
            if nueva_linea:
                nuevas_lineas.append(nueva_linea)
        return nuevas_lineas
    except Exception as e:
        print(f"Error procesando el registro: {log_line}\nError: {e}")
        return []


# Procesa logs de juniper mediante una expresion regular

def juniper_nat44_log(log_line):
    # Patron regular para extraer los campos
    pattern = (r'(\w+ \d{2} \d{2}:\d{2}:\d{2}) (\d{4}-\d{2}-\d{2} \d{2}: \d{2}:\d{2}): (.*?)\{.*\}\[(.*?)\]: (.*): (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) -> (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})-(\d{1,5})(.*)')
    match = re.match(pattern, log_line)

    if match:
        # Extraer los campos
        timestamp = match.group(1)
        date_time = match.group(2).replace(": ", ":")
        device_name = match.group(3)
        device_action = match.group(5)
        if device_action == "JSERVICES_NAT_PORT_BLOCK_ALLOC":
            device_action = "Add"
        elif device_action == "JSERVICES_NAT_PORT_BLOCK_RELEASE":
            device_action = "Remove"
        ip_interna = match.group(6)
        ip_externa = match.group(7)
        puerto_ini = match.group(8)
        puerto_fin = match.group(9)
        return [to_dict(
            timestamp,
            date_time,
            device_name,
            device_action,
            ip_interna,
            ip_externa,
            puerto_ini,
            puerto_fin
        )]
    else:
        return None


def extraer_datos_cisco(timestamp, nodo_red, timestamp_evento, entrada):
    try:
        campos_nat44 = entrada.split(' - ')
        accion = campos_nat44[0]
        if accion == "UserbasedA":
            accion = "Add"
        elif accion == "UserbasedW":
            accion = "Remove"
        ip_privada = campos_nat44[1].split()[0]
        ip_publica = campos_nat44[2] if len(campos_nat44) > 2 else '-'
        puertos = campos_nat44[3].split() if len(campos_nat44) > 3 else ['-', '-']
        puerto_inicio = puertos[0]
        puerto_fin = puertos[1] if len(puertos) > 1 else '-'

        return to_dict(timestamp, timestamp_evento, nodo_red, accion, ip_privada, ip_publica, puerto_inicio, puerto_fin)
    except Exception as e:
        print(f"Error extrayendo datos: entrada={entrada}\nError: {e}")
        return None

# Genera archivo con json, una linea por entrada terminada en \n

def procesar_archivo(registro, archivo_salida):
    try:
        with open(archivo_salida, 'w') as salida:
           for linea in registro:
                 salida.writelines(f"{json.dumps(linea)}\n")
    except Exception as e:
        print(f"Error procesando el archivo: {archivo_salida}\nError: {e}")


archivo_entrada = 'logs/00.log'
archivo_salida = 'logs/00-limpio.txt'
lineas_a_grabar = []

# Procesar el archivo
try:
    with open(archivo_entrada, 'r') as entrada:
        for registro in entrada:
            registro = registro.strip()
            if registro:
                prueba = procesar_registro(registro)
                for lineas in prueba:
                    lineas_a_grabar.append(lineas)
    procesar_archivo(lineas_a_grabar, archivo_salida)
except Exception as e:
    print(f"Error procesando el archivo: {archivo_salida}\nError: {e}")