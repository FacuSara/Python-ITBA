# Programa Final, Certificación Profesional Python


##  Programa


El objetivo del programa es poder obtener datos de una base de datos de finanzas, mantenerlos en una base de datos propia y graficarlos temporalmente. La aplicación grafica los valores diarios junto con el volumen, las bandas Bollinger superior e inferior.
 
### ¿Cómo correr el programa?


1. Descargar `API_finanzas.py`, `tickers.db` y `requirements.txt` en una misma carpeta de su computadora.
2. Abrir el *Símbolo del sistema* y tipear `pip install -r requirements.txt` para instalar los paquetes necesarios.
3. Ejecutar desde la carpeta donde descargó los archivos, `python API_finanzas.py`


### ¿Cómo usarlo?
1. Al inicializar, se tendrá que elegir una opción, según lo que se quiera hacer:
     - 1- Actualización de datos
     - 2- Visualización de datos
     - 3- Salir

```
 ******************************************************
        Te damos la Bienvenida. API de Finanzas
                Certificación Python ITBA
    ******************************************************
    MENU PRINCIPAL:
    1- Actualización de datos
    2- Visualización de datos
    3- Salir

¿Cuál opción desea elegir?:
```

Si se ingresa `1`, se va a ingresar al menú de **Actualización de datos**.
Debe ingresar el nombre del **Ticker** a cargar en la base de datos junto al rango de **fechas** requerido, utilizando el formato `año-mes-día` . Si alguna fecha requerida ya se encuentra cargada en la base de datos, no la cargará nuevamente.
Si el nombre del ticker no existe o no se tiene información en la base de datos de la API, va a pedir que se ingrese un nuevo Ticker.

Ejemplo:
```
¿Cuál opción desea elegir?:1


ACTUALIZACIÓN DE DATOS.


Ingrese ticker a pedir y luego apriete <enter>.

Ticker:AAPL


Ingrese fecha de inicio [AAAA-MM-DD]:
 2021-02-03


Ingrese fecha de fin [AAAA-MM-DD]:
 2022-02-03
 
 ERROR - No tenemos información de ese ticker. Elija otro

ACTUALIZACIÓN DE DATOS.


Ingrese ticker a pedir y luego apriete <enter>.

Ticker:

```

Si se ingresa `2`, se va a ingresar al menú de **Visualización de datos**:

 Se tendrá que elegir una opción, según lo que se quiera ver:
  - 1- Resumen: donde verá los Tickers, junto a su rango de fechas pedido por el usuario.
  - 2- Gráfico de ticker: podrá visualizar la gráfica de los valores diarios del Ticker junto con el volumen y las bandas Bollinger superior e inferior.

```
¿Cuál opción desea elegir?:2



 VISUALIZACIÓN DE DATOS:
      1- Resumen
      2- Gráfico de ticker
      3- Volver al MENÚ Principal

¿Cuál opción desea elegir?:
```

Al finalizar cada opción, se va a poder regresar al menú para elegir una nueva opción.

## Desarrollo
 
La aplicación se realizó en *[Python 3](https://www.python.org/downloads/)*.

Para el desarrollo y prueba de la base de datos, se utilizó *[Sqlite3](https://www.sqlite.org/index.html)*, en donde se crea dos tablas con la siguiente estructura:
-  Datos *(Nombre del ticker, fecha, volumen operado, valor medio, valor de apertura, valor de cierre, mayor valor, menor valor y timestamp)*.
- Tickers *(Nombre del ticker, fecha de inicio de los datos, fecha de fin de los datos)*.

En la tabla ***datos*** se guarda la información recibida de la API de finanzas y en la tabla ***tickers*** los requests recibidos del usuario.
