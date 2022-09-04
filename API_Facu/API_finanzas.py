#!/usr/bin/env python

import sqlite3
import requests

#para recorrer fechas
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
from pandas.tseries.offsets import CustomBusinessDay

#importamos los feriados de pandas que nos interesan
from pandas.tseries.holiday import nearest_workday, \
    AbstractHolidayCalendar, Holiday, \
    USMartinLutherKingJr, USPresidentsDay, GoodFriday, \
    USMemorialDay, USLaborDay, USThanksgivingDay


#creamos nuestra propia lista de feriados, los que toma la bolsa de USA
class USTradingHolidaysCalendar(AbstractHolidayCalendar):
    rules = [
        Holiday(
            'NewYearsDay',
            month=1,
            day=1,
            observance=nearest_workday
        ),
        USMartinLutherKingJr,
        USPresidentsDay,
        GoodFriday,
        USMemorialDay,
        Holiday(
            'Juneteenth National Independence Day',
            month=6,
            day=19,
            start_date='2021-06-18',
            observance=nearest_workday,
        ),
        Holiday(
            'USIndependenceDay',
            month=7,
            day=4,
            observance=nearest_workday
        ),
        USLaborDay,
        USThanksgivingDay,
        Holiday(
            'Christmas',
            month=12,
            day=25,
            observance=nearest_workday
        ),
    ]


cal = USTradingHolidaysCalendar()

#valor para loop
salir=2

#iniciamos la interfaz del usuario en loop
while salir != 0:
    print("""
    ******************************************************
        Te damos la Bienvenida. API de Finanzas
                Certificación Python ITBA
    ******************************************************
    MENU PRINCIPAL:
    1- Actualización de datos
    2- Visualización de datos
    """)

    option = input('¿Cuál opción desea elegir?:')
    print("\n ")
    if option == "1":
    #inicio opcion 1
            print("ACTUALIZACIÓN DE DATOS.")
            print("\n ")
            print("Ingrese ticker a pedir y luego apriete <enter>.\n ")
            ticker = input('Ticker:')
            print("\n ")
            f_inicial = input('Ingrese fecha de inicio [AAAA-MM-DD]:\n ')
            print("\n ")
            f_final = input('Ingrese fecha de fin [AAAA-MM-DD]:\n ')
            print("\n ")
            print("Pidiendo datos ...\n ")

            #Creamos la API key con los valores propuestos
            pedido= ("https://api.polygon.io/v2/aggs/ticker/{t}/range/1/day/{fi}/{ff}?adjusted=true&sort=asc&apiKey=Hl28_xet0aqM7JlJ8rMwSoa7rVqhC_uo"
            .format(t=ticker,
                    fi=f_inicial,
                    ff=f_final,
                    )
                    )

            #realizamos el pedido a la pagina de la API
            json_file = requests.get(pedido)

            #mostramos los resultados
            print("Contendio en JSON:\n", json_file.json())

            print(json_file.text)

            json_obj = json_file.json() # Parseo a Diccionario de Python

            ticker = json_obj["ticker"]
            value = json_obj["results"]

            print(ticker)
            print(value)

            print(f"Ticker: {ticker} - {value[0]['v']}")

            #cargamos el calendario de feriados junto a los dias habiles
            us_bd = CustomBusinessDay(calendar=cal)

            f_pedidas = []
            #con panda, recorro todos los dias desde mi dia inicial al final, filtrando por mi calendario
            ser = pd.date_range(start=f_inicial, end=f_final, freq=us_bd)
            #cargo mi dataframe a una lista
            f_pedidas = ser.strftime('%Y-%m-%d').tolist()
            print (f_pedidas)
            print(f'Cantidad de fechas tomada ={len(f_pedidas)}, fechas API= {int(json_obj["queryCount"])}')

            startDate = datetime.strptime(f_inicial, '%Y-%m-%d').date()
            endDate = datetime.strptime(f_final, '%Y-%m-%d').date()

            # Creamos una conexión con la base de datos
            con = sqlite3.connect('tickers.db')
            # Creamos el cursor para interactuar con los datos
            cursor = con.cursor()

            #cargamos pedido realizado
            cursor.execute( '''INSERT INTO ticker (
            nombre,
            f_inicio,
            f_fin
                )
            VALUES ( ?, ?, ?)''',
             (ticker, startDate, endDate))

            con.commit()
            print(cursor.rowcount, "datos guardados correctamente en ticker.")

#itero hasta cubrir todos los diccionarios con queryCount parseado, que es la cantidad de datos que tengo
            for k in range(int(json_obj["queryCount"])):
                    cursor.execute( '''INSERT INTO datos (
                    nombre,
                    fechas,
                    close,
                    high,
                    low,
                    n,
                    open,
                    timestamp,
                    vol,
                    val_w                )
                    VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (ticker, str(f_pedidas[k]), value[k]['c'], value[k]['h'], value[k]['l'], value[k]['n'], value[k]['o'], value[k]['t'], value[k]['v'],value[k]['vw']))

                    con.commit()
            print(cursor.rowcount, "datos guardados correctamente en datos.")
            # Cerramos la conexión
            con.close()

            #manejo de menu
            print("\n ")
            input1 = input('Si quiere salir entre 0, de lo contrario ingrese 1:')
            salir = int(input1)

    #inicio de la opcion 2
    elif option == "2":
        fin=0
        #mantengo el bucle de la opción 2
        while fin == 0:
            print("""
 VISUALIZACIÓN DE DATOS:
      1- Resumen
      2- Gráfico de ticker
            """)

            option1 = input('¿Cuál opción desea elegir?:')
            if option1 == "1":
                #inicio opcion 1 - RESUMEN
                        # Creamos una conexión con la base de datos
                        con = sqlite3.connect('tickers.db')
                        # Creamos el cursor para interactuar con los datos
                        cursor = con.cursor()


                        # Pedimos parametros al SQL
                        res = cursor.execute(f'''
                            SELECT nombre, f_inicio, f_fin
                            FROM ticker
                            ORDER BY nombre DESC
                            ''')

                        #imprimimos los datos pedidos
                        print("Los tickers guardados en la base de datos son:\n ")
                        for row in res:
                            print(f'{row[0]} - {row[1]} <-> {row[2]}')

                        # Cerramos la conexión
                        con.close()
                        fin=1
                        print("\n ")
                        input1 = input('Si quiere salir entre 0, de lo contrario ingrese 1:')
                        salir = int(input1)


            #inicio de la opcion 2 - GRAFICO
            elif option1 == "2":
                    print("Gráfico de ticker - No lo hice aún")

                    tickerAGraficar = input('¿Que Ticker desea graficar?:')

                    # Creamos una conexión con la base de datos
                    con = sqlite3.connect('tickers.db')
                    # Creamos el cursor para interactuar con los datos
                    cursor = con.cursor()

                    # Pedimos parametros al SQL
                    res = cursor.execute(f'''
                        SELECT nombre, fechas, vol, val_w, high, low
                        FROM datos
                        WHERE nombre = ?
                        ORDER BY nombre DESC
                        ''',(tickerAGraficar,))

                    # Construimos un Pandas Data Frame
                    records = pd.DataFrame(cursor.fetchall())
                    records.columns=['Ticker', 'Date', 'Vol', 'Val_W', 'High', 'Low']
                    records["Date"] = pd.to_datetime(records["Date"])
                    records.sort_values(by='Date', ascending=True)

                    print(records)

                    # Cerramos la conexión
                    con.close()

                    # Graficamos los datos
                    fig, ax1 = plt.subplots()
                    records.plot(ax=ax1, x='Date', y='Val_W', label='Val_W', color='blue')
                    records.plot(ax=ax1, x='Date', y='High', label='High', color='red')
                    records.plot(ax=ax1, x='Date', y='Low', label='Low', color='green')
                    plt.title('Stock Evolution')
                    plt.xticks(rotation=45)
                    plt.xlabel('Dates')
                    plt.ylabel('Price')
                    plt.legend()
                    plt.show(block=False)

                    records.plot(x='Date', y='Vol', label='Val_W', color='blue')
                    plt.title('Operated Volume')
                    plt.xticks(rotation=45)
                    plt.xlabel('Dates')
                    plt.ylabel('Value')
                    plt.legend()
                    plt.show()


           #si ingresó cualquier numero le pide que ingrese 1 o 2 en el menu
            else:
                print(f'        ERROR - Ingresó {option1}. Ingrese la opción 1 o 2')


    else:
        print(f'        ERROR - Ingresó {option}. Ingrese la opción 1 o 2')
