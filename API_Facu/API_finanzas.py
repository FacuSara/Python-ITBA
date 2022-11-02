#!/usr/bin/env python

import sqlite3
import requests

#para recorrer fechas
from datetime import datetime

import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt

print("""
******************************************************
    Te damos la Bienvenida. API de Finanzas
            Certificación Python ITBA
******************************************************
""")
#iniciamos la interfaz del usuario en loop
while True:
    print("""
    MENU PRINCIPAL:
    1- Actualización de datos
    2- Visualización de datos
    3- Salir
    """)

    option = input('¿Cuál opción desea elegir?:')
    print("\n ")
    if option == "1":
            z=0
            while z == 0:

            #inicio opcion 1
                print("ACTUALIZACIÓN DE DATOS.")
                print("\n ")
                print("Ingrese ticker a pedir y luego apriete <enter>.\n ")
                ticker = input('Ticker:')
                print("\n ")
                #verificamos que ingresen una fecha correcta
                while True:
                    try:
                        f_inicial = input('Ingrese fecha de inicio [AAAA-MM-DD]:\n ')
                        #llevamos a la fecha inicial a formato datetime
                        startDate = datetime.strptime(f_inicial, '%Y-%m-%d').date()
                        break
                    except ValueError:
                        print("Fecha inválida - Ingresa una fecha válida \n")
                print("\n ")
                while True:
                    try:
                        f_final = input('Ingrese fecha de fin [AAAA-MM-DD]:\n ')
                        endDate = datetime.strptime(f_final, '%Y-%m-%d').date()
                        if startDate > endDate:
                            print(f'Ingrese una fecha mayor a la de inicio: {f_inicial}\n')
                        else:
                            break
                    except ValueError:
                        print("Fecha inválida - Ingresa una fecha válida\n")
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
                # print("Contendio en JSON:\n", json_file.json())

                print(json_file.text)

                json_obj = json_file.json() # Parseo a Diccionario de Python

                z = int(json_obj["queryCount"])
                if z == 0:
                    print('\n')
                    print('ERROR - No tenemos información de ese ticker. Elija otro \n')

            print('Terminó el loop')

            #cargo a una lista el nombre del ticker y los datos de la API
            ticker = json_obj["ticker"]
            value = json_obj["results"]


            #tomo la parte del timestamp de los resultados de la API, lo tranformo en tipo fecha datetime (esta en milisegundos por eso lo divido por 1000) y lo guardo en la lista "fechas" para compararlo con "datos_cargados2" luego
            #no comparo el timestamp directamente porque tiene la parte de la hora también y es complejo coincidir en hora. Es mas facil comparar solo dias.
            fechas = []
            for k in range(int(json_obj["queryCount"])):
                fechas_normal = str(datetime.fromtimestamp(value[k]['t']//1000.0).strftime('%Y-%m-%d'))
                fechas.append(fechas_normal)

            print(f'ESTAS SON LAS FECHAS de API : {fechas}\n')



            #MANEJO DE BASE DE DATOS
            con = sqlite3.connect('tickers.db')
            # Creamos el cursor para interactuar con los datos
            cursor = con.cursor()

            # Pedimos parametros al SQL para ver qué fechas tenemos en la DB del ticker pedido
            res = cursor.execute(f'''
                SELECT nombre, fechas
                FROM datos
                WHERE nombre = ?
                ORDER BY nombre, fechas
                ''',(ticker,))

            records = cursor.fetchall()

            con.close()

            #usamos datos_cargados para cargar en una lista las fechas desde la fecha inical pedida hasta la final y luego compararla con las fechas que nos da la API
            datos_cargados=[]
            #f es para conocer el el punto de lista donde la fecha pedida es igual a la fecha en la base de datos
            f=-1
            f_loop = f_inicial
            for word in records:
                print(f'{word[1]}')
                f+=1
                if f_loop == word[1]:
                      print("Encontramos una fecha igual!!!")
                      datos_cargados = records[f:]
                      break
                elif f_loop < word[1]:
                    print("MENOR")
                    datos_cargados = records[f:]
                    break

            #uso datos cargados 2 para quedarme solo con la parte de la fecha, sin el nombre del ticker
            datos_cargados2=[]
            for data in datos_cargados:
                datos_cargados2.append(data[1])

            print(f'ESTAS SON LAS FECHAS DE DB: {datos_cargados2}\n')


            # Creamos una conexión con la base de datos
            con = sqlite3.connect('tickers.db')
            # Creamos el cursor para interactuar con los datostemp
            cursor = con.cursor()

            #cargamos pedido realizado en la tabla ticker, que luego se usa para visualizar los pedidos datos_cargados
            cursor.execute( '''INSERT INTO ticker (
            nombre,
            f_inicio,
            f_fin
                )
            VALUES ( ?, ?, ?)''',
             (ticker, startDate, endDate))

            con.commit()
            print(cursor.rowcount, "datos guardados correctamente en ticker.")

            #comparo las fechas de DB "datos_cargados2" Con la de API "fechas" y me quedo con las fechas que no existen en datos_cargados2.
            #Las guardo en temp3 que seria mi lista de fechas a cargar en la base de datos considerando lo guardado anteriormente, en otra sesión
            temp3 = []
            for element in fechas:
                if element not in datos_cargados2:
                     temp3.append(element)

            print(f'DATOS a cargar:{temp3}\n')
            print(f'DATOS cargados:')

            #itero hasta cubrir todos los datos de la API con queryCount parseado, que es la cantidad de datos que me brinda la API. Antes de cargar en la DB comparo la fecha date1 de la API, si está en temp3, cargo la fecha, sino, no.
            for k in range(int(json_obj["queryCount"])):
                date1 = str(datetime.fromtimestamp(value[k]['t']//1000.0).strftime('%Y-%m-%d'))
                if date1 in temp3:
                        print(date1)
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
                         (ticker, date1 , value[k]['c'], value[k]['h'], value[k]['l'], value[k]['n'], value[k]['o'], value[k]['t'], value[k]['v'],value[k]['vw']))

            con.commit()
            print(cursor.rowcount, "datos guardados correctamente en datos.")
            # Cerramos la conexión
            con.close()

    #inicio de la opcion 2
    elif option == "2":
        fin=0
        #mantengo el bucle de la opción 2
        while fin == 0:
            print("""
 VISUALIZACIÓN DE DATOS:
      1- Resumen
      2- Gráfico de ticker
      3- Volver al MENÚ Principal
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



            #inicio de la opcion 2 - GRAFICO
            elif option1 == "2":
                    print("Gráfico de ticker")

                    while True:

                        tickerAGraficar = input('¿Que Ticker desea graficar?:')

                        # Creamos una conexión con la base de datos
                        con = sqlite3.connect('tickers.db')
                        # Creamos el cursor para interactuar con los datos
                        cursor = con.cursor()

                        # Pedimos parametros al SQL
                        try:
                            res = cursor.execute(f'''
                            SELECT nombre, fechas, vol, val_w, high, low
                            FROM datos
                            WHERE nombre = ?
                            ORDER BY nombre DESC
                            ''',(tickerAGraficar,))


                            # Construimos un Pandas Data Frame
                            records = pd.DataFrame(cursor.fetchall())
                            records.columns = ['Ticker', 'Date', 'Vol', 'Val_W', 'High', 'Low']
                            records["Date"] = pd.to_datetime(records["Date"])
                            records.sort_values(by='Date', ascending=True)
                            indicator_bb = ta.bbands(close=records["Val_W"], window=20, window_dev=2)
                            print(indicator_bb)
                            records = pd.concat([records, indicator_bb], ignore_index=True, axis=1)
                            records.columns = ['Ticker', 'Date', 'Vol', 'Val_W', 'High', 'Low', 'BBL_5_2.0', 'BBM_5_2.0', 'BBU_5_2.0', 'BBB_5_2.0', 'BBP_5_2.0']
                            print(records)

                            # Cerramos la conexión
                            con.close()

                            # Graficamos los datos
                            # fig, (ax1, ax2) = plt.subplots(2)
                            fig = plt.figure(constrained_layout=True)
                            ax = fig.add_gridspec(3, 1)
                            ax1 = fig.add_subplot(ax[0:2, 0])
                            ax2 = fig.add_subplot(ax[2, 0])
                            records.plot(ax=ax1, x='Date', y='Val_W', label='Val_W', color='blue')
                            records.plot(ax=ax1, x='Date', y='BBL_5_2.0', label='BOLU', color='red')
                            records.plot(ax=ax1, x='Date', y='BBM_5_2.0', label='BOLD', color='green')
                            plt.title('Stock Evolution')
                            plt.xticks(rotation=45)
                            plt.xlabel('Dates')
                            plt.ylabel('Price')
                            plt.show(block=False)

                            records.plot(ax=ax2, x='Date', y='Vol', label='Vol', color='blue')
                            records.plot
                            plt.title('Operated Volume')
                            plt.xticks(rotation=45)
                            plt.xlabel('Dates')
                            plt.ylabel('Value')
                            plt.show()

                            break


                        except ValueError:
                            print(f'        ERROR - El Ticker {tickerAGraficar} no existe en la base de datos. Elija otro\n')

            #si ingreso 3, vuelvo al menu principal
            elif option1 == "3":
                fin=1

           #si ingresó cualquier numero le pide que ingrese 1 o 2 en el menu
            else:
                print(f'        ERROR - Ingresó {option1}. Ingrese la opción 1, 2 o 3')

    elif option == "3":
        break
    else:
        print(f'        ERROR - Ingresó {option}. Ingrese la opción 1, 2 o 3 para salir')
