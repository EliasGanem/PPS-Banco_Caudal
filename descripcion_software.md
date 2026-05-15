# Descripción del software

Este código se encarga de controlar por USB COM un banco de caudal, que se utiliza para hacer ensayos de calibración de caudalimetros. Para ello recibe y envía información al banco de caudal a traves de USB COM. Además utiliza una camara de fotos a través de usb para tomar imágenes en diferentes momentos.

# Descripción de interfaz de usuario

## Estilo Visual
- Tema: Modo oscuro (Dark Mode), con un estilo técnico, industrial o de panel de control de laboratorio.
- Colores Principales:
    - Fondo principal: Gris oscuro (#242424)
    - Fondo de los inputs/cajas: Gris claro mate.
- Texto: Blanco o gris muy claro para una alta legibilidad.
- Texto inputs: gris o negro para una alta legibilidad
- Tipografía: Limpia, sin remates (sans-serif),moderna.

## Estructura de Contenedores:
La interfaz está dividida en cuatro bloques horizontales principales. Cada bloque tendrá un fondo de color gris más claro (#2b2b2b) y el título de cada sección está incrustado en la línea superior del marco (estilo fieldset y legend en HTML).

Diseño y Disposición (Layout) por Secciones
1. Panel Superior: "Configuración de Puertos"
    - Estructura: Ocupa todo el ancho de la interfaz.
    - Elementos:
        - A la izquierda: Un texto que dice "Banco de Caudal" seguido de un menú desplegable (dropdown/select). A la derecha de este menú, un indicador visual tipo LED de color rojo cuando no hay conexión y verde cuando está conectado.
        - A la derecha de lo anterior, con un espaciado suficiente como para distinguir que se tratan de opciones distintas, u texto que dice "Cámara" seguido de un menú desplegable (dropdown/select). A la derecha de este menú, un indicador visual tipo LED de color rojo cuando no hay conexión y verde cuando está conectado.
        - Luego de estas opciones, con un espaciado suficiente, un botón circular con el ícono de actualizar, el cual sirve para actualizar los puertos COM de la cámara y el banco de caudal. 

2. Panel Central: está dividido en dos columnas.
    - Columna Izquierda (1/3 del total): está dividida en tres secciones horizontales:
        1. Primera sección horizontal posee los siguientes elementos de entrada:
            - "Duración Ensayo [s]” Al lado de este texto debe haber un recuadro que es un campo numérico donde se ingresará la duración del ensayo.
            - "Densidad del Fluido [kg/m³]” Al lado de este texto debe haber un recuadro que es un campo numérico donde se ingresará la densidad.
        2. Segunda sección horizontal posee el siguiente botón de accion:
            - Un botón grande que ocupa el ancho de la columna con el texto "Iniciar Ensayo".
            - Estado del botón: Está deshabilitado (disabled), se ve opaco/oscurecido.
        3. Tercera sección horizontal posee los siguientes botones de accion:
            - Un botón que ocupa un poco menos de la mitad del ancho de la columna con el texto "Iniciar Retorno".
            - A la derecha del anterior, a una distancia suficiente, un botón que ocupa el espacio restante de la columna con el texto "Finalizar Retorno".

    - Columna Derecha: está dividida en dos secciones horizontales
        1. Primera sección horizontal tiene el título“Mediciones”
            - Estructura: Una lista de dos campos que son botones de acción alineados verticalmente a la izquierda. A la derecha de cada uno de botones, hay un recuadro que es un campo numérico que mostrará el valor de la variable indicada.
            - Campos:   
                - "Peso Inicial [kg]" 
                - "Peso Final [kg]" 
        2. Segunda sección horizontal tiene el título “Resultados”, el cual es un botón de acción para calcular los caudales.
            - Estructura: Una lista de cuatro campos alineados verticalmente a la izquierda. Tienen el título a la izquierda y el valor dentro de un recuadro que es un campo numérico que mostrará el valor de la variable indicada.
            - Campos: 
                - "Tiempo [s]” 
                - "Peso Neto [kg]" 
                - "Caudal Másico [kg/s]" 
                - "Caudal Volumétrico [m³/s]" 
3. Tercer Panel: "Imágenes del Ensayo"
    - Estructura: Ocupa todo el ancho de la interfaz.
    - Elementos: Una galería horizontal (grid de 1 fila y 6 columnas) con contenedores tipo "marcadores de posición" (placeholders).
    - Diseño de cada marcador:
        - Tienen forma cuadrada con esquinas redondeadas.
        - Fondo gris claro
        - En el centro tienen el ícono de una cámarafotográfica.
        - Debajo del cuadro, un texto que numera cada cuadro de izquierda a derecha: "Imagen 1","Imagen2", "Imagen 3", "Imagen 4", "Imagen 5" y "Imagen 6".

4. Cuarto Panel: "Terminal"
    - Estructura: Ocupa todo el ancho de la interfaz. Es un desplegable que se habilita con contraseña. Acá irá la terminal serial.

## Paleta de colores para los botones:
1. Botones de Acción Principal (Arranque / Iniciar / OK)
    - Color Base (Reposo): #388E3C (Un verde sólido, no tan brillante que canse la vista).
    - Color Hover (Al pasar el mouse): #4CAF50 (Un tono más claro para dar feedback de interacción).
2. Botones Críticos o de Parada (Detener / Abortar / Error)
    - Color Base (Reposo): #D32F2F (Un rojo profundo y serio).
    - Color Hover (Al pasar el mouse): #F44336 (Rojo vibrante).
3. Botones de Advertencia o Transición (Pausa / Precaución)
    - Color Base (Reposo): #F57C00 (Naranja oscuro/ámbar).
    - Color Hover (Al pasar el mouse): #FFB300 (Amarillo ámbar brillante).
4. Botones Secundarios o de Configuración (Neutros)
    - Color Base (Reposo): #1976D2 (Azul técnico) o #424242 (Gris medio).
    - Color Hover (Al pasar el mouse): #2196F3 (Azul claro) o #545454 (Gris más claro).

Para los textos que vayan dentro de estos botones (especialmente los de colores saturados como rojo, verde y azul), te recomiendo usar blanco puro (#FFFFFF) o un blanco apenas roto (#F5F5F5).

## Imagen
Ténes una imagen que se llama IU.png que usaras de guía.

# Descripción de funcionamiento

La comunicación con el banco de caudal es a través de usb com, se envían comandos y se reciben datos. Tanto los datos como los comandos son cadenas de caracteres, donde el ultimo caracter es un terminador configurable por código (macros separadas para envío y recepción).
Cuando se inicia el programa se intenta establecer comunicación con el banco de caudal y con la cámara.

Al presionar el boton de "iniciar ensayo" se envia el comando "INICIAR ENSAYO" al banco de caudal. La duración del ensayo se obtiene del valor ingresado por el usuario en el recuadro correspondiente, el valor por defecto de la duración del ensayo es de 10 segundos (este valor debe estar parametrizado para los diseñadores puedas modificarlo en el codigo). Para saber cuanto tiempo transcurrió se utiliza el reloj de la computadora. Se debe verificar que  el tiempo transcurrido desde que inicio el ensayo coincida con la duración del ensayo, cuando esto sucede se envía el comando FINALIZAR ENSAYO. Luego de enviar el comando espera a que el banco de caudal le envie la duración del ensayo. Se utiliza este valor para determinar el tiempo final del ensayo y calcular los caudales. 

Al iniciar el ensayo se toma la primera imagen de la camara y las 5 imágenes restantes se toman cada una quinta parte del tiempo de ensayo. Por ejemplo, si el tiempo de ensayo son 25 segundos, las imágenes se tomarán a los 0, 5, 10, 15, 20 y 25 segundos. Estas imagenes se mostraran en orden cronológico en los recuadros correspondientes.

Cuando no se esta ensayando y se presiona el botón "peso inicial" o "peso final" se debe enviar el comando MEDICION BALANZA, luego se espera recibir el valor del peso el cual se debe mostrar en el indicador correspondiente. 

Una vez finalizado el ensayo se debe calcular el caudal a partir de los datos de tiempo final, peso inicial y peso final obtenidos. El calculo y la indicacion se realizan una vez presionado el boton "calcular caudal", solo cuando se haya presionado el boton "peso final".

Al precionar el boton "iniciar retorno" se envia el comando "INICIAR RETORNO" al banco de caudal. Cuando esto pasa el programa debe enviar al banco de caudal el comando "MEDICION BALANZA" cada un tiempo configurable con una macro y a partir del valor recibido debe controlar que el peso no sea menor a un valor configurable con una macro. Estas macros son congifurables poer el programador desde el código. Si el valor que devuelve el banco de caudal es menor o igual al valor minimo o si se presiona el boton "finalizar retorno" se debe enviar el comando FINALIZAR RETORNO al banco de caudal.

No se puede presionar "iniciar ensayo" sin antes haber presionado el boton "peso inicial".

Se debe tener un selector de puerto para elegir que camara usar. Este selector debe mostrar todas las camaras disponibles. En caso de no tener una camara conectada el programa seguira funcionando sin tomar las fotos. El indicador de camara conectada debe cumplir su funcion.

Aunque la selección del puerto al que esta conectado el banco de caudal es automatico, debe haber un selector para poder elegir otro puerto com en caso de ser necesario. Y debe mostrar que puerto com esta seleccionado. Es decir, al inicio aparece el puerto com que se determino automaticamente, pero se puede hacer click y se debe desplegar una barra con las distintas opciones de puertos para elegir.

Las imagenes se guardarán en una carpeta llamada ensayos_banco_caudal. Las imagenes corrspondientes a cada ensayo se guardan dentro de otras carpeta cuyo nombre es la fecha y hora del ensayo, y estas estaran dentro de la carpeta ensayo_banco_caudal. El nombre de las fotos sera un nuemero segun el orden cronologico en que se tomaron, la primera será la img_1. 

Ademas en la carpeta del ensayo debe generarse un archivo .csv con los datos de las mediciones, donde la primera columna tiene el nombre de la variable con sus respectivas unidades y la segunda el valor. Las variables que debe guarfar son:
- fecha y hora [hh:mm:ss - dd/mm/aaaa]
- Tiempo de ensayo [s]
- Peso inicial [kg]
- Peso final [kg]
- Peso neto [kg]
- Caudal másico [kg/s]
- Caudal volumétrico [m3/s]
- Densidad [kg/m3]

Se debe tener un parámetro de densidad que será ingresado por el usuario en la interfaz de usuario, este debe ser mostrado. No se puede iniciar el ensayo a menos que se tenga el haya ingresado el valor de densidad. 

# Otras especificaciones
1.  Comunicación usb com 
    - Parámetros: 115200 baudios, 8 bits de datos, sin paridad y un bit de stop.
    - Puerto: se elige automaticamente a partir del vendor id y del produc id, los cuales deben estar parametrizados.
    - Formato de datos recibidos según el comando enviado:
        - MEDICION BALANZA: viene en un string donde los mas significativos son la parte entera luego viene un punto y despues la parte decimal. La longitud del string es de 7 caractes mas el terminador configurado.
        - MEDICION RELOJ: viene en un string donde los mas significativos son la parte entera luego viene un punto y despues la parte decimal. La longitud del string es de 8 caractes mas el terminador configurado.
        - MEDICION COMPLETA: en este caso se reciben dos string con el mismo formato que los anteriores. Pero primero llega el peso y luego el tiempo.
    - Formato de los datos enviados: es un string de longitud variable seguido del terminador configurado. 
        - INICIAR ENSAYO: longitud 15 caracteres mas el terminador configurado.
        - FINALIZAR ENSAYO: longitud 16 caracteres mas el terminador configurado.
        - MEDICION BALANZA: longitud 17 caracteres mas el terminador configurado.
        - MEDICION RELOJ: longitud 16 caracteres mas el terminador configurado.
        - MEDICION COMPLETA: longitud 17 caracteres mas el terminador configurado.

2. No se debe bloquear la UI: la usb com y la captura de fotos corran en un hilo (thread) separado para que se pueda utilizar la camara, el banco de caudal y el resto del programa de forma simultanea.

3. Libreria para el control de la camára: se debe usar OpenCV (cv2).

4. Polling de MEDICION RELOJ se realiza cada 100 milisegundos.

5. Cálculo de caudal masico: el caudal se calcula: (peso final - peso inicial)/(Tiempo). Debe ser mostrado en el indicador correspondiente una vez presionado el boton calcular caudar. Las unidades en SIMELA serían kg/s.

6. Cálculo de caudal volumetrico: el caudal se calcula: (peso final - peso inicial)/(Tiempo*densidad). Debe ser mostrado en el indicador correspondiente una vez presionado el boton calcular caudar. Las unidades serían m^3/s.

7. Utilizá las unidades del SIMELA.

8. Utilizá la librería CustomTkinter para la interfaz gráfica y threading para que la comunicación serial con el banco y la captura de imágenes con OpenCV no bloqueen la interfaz. Nota los hilos secundarios no deben actualizar la interfaz de ususario.

9. Debajo del cuadro donde aparece cada imagen debe decir: "Imagen #" donde # es el numero de imagen según el orden cronológico en que se tomaron. Por ejemplo, en el primer cuadro debe aparecer "Imagen 1" y así sucesivamente.

10. En los cuadros desplegables de selección de puertos COM se debe indicar a que corresponde. Es decir, si corresponde a la camara o al banco de caudal.