---
trigger: manual
---

# Estilo y Legibilidad (El "Pythonic Way")

El código se lee mucho más de lo que se escribe. Un experto sigue las convenciones para que cualquier otro desarrollador (o vos mismo en 6 meses) entienda todo a primera vista.
    * PEP 8 al pie de la letra: Es el estándar de la industria. Usá snake_case para funciones/variables y PascalCase para clases.
    * Type Hinting (Tipado estático): Python es dinámico, pero un profesional usa Type Hints para evitar errores de lógica y mejorar el autocompletado.
Además mantené una coherencia en el lenguaje. Utilizá español tanto para documentar como para el nombre de variables, funciones, etc. No mezclés español e inglés.


# Arquitectura y Estructura de Proyecto

Para que un software sea expandible, la estructura debe ser predecible. Un "experto" no pone todo en un solo archivo main.py.
* Separación de Preocupaciones (SoC): Dividí el código en capas:
    * Core/Logic: La lógica de negocio pura (no sabe nada de bases de datos ni de hardware).
    * Drivers/Adapters: Módulos que hablan con el mundo exterior (USB, APIs, archivos).
    * UI/CLI: La interfaz que interactúa con el usuario.
* Paquetes Iniciadores: Usá archivos __init__.py para definir qué funciones o clases se exponen al exterior de cada carpeta, manteniendo el resto como "privado".
* Alta Cohesión y Bajo Acoplamiento: Cada módulo o clase debe hacer una sola cosa y tener la menor dependencia posible de otros módulos.
* Inyección de Dependencias: No instancies clases pesadas dentro de otras funciones. Pasalas como argumentos. Esto facilita enormemente el testing.


# Reglas de Oro para Multiplataforma (Linux & Windows)

Escribir código que corra en ambos sistemas requiere evitar supuestos sobre el sistema de archivos o la consola.

## Manejo de Rutas (El error más común)
* Prohibido: Usar strings manuales como "C:\\datos\\file.txt" o "/home/user/file.txt".
* Regla: Usar siempre la librería pathlib. Se encarga de usar / o \ según el SO automáticamente.

## Codificación de Archivos
Windows suele usar cp1252 y Linux utf-8. Para evitar errores de caracteres raros, siempre especificá el encoding al abrir archivos:

## Comandos de Sistema
Si necesitás ejecutar comandos externos con subprocess, evitá shell=True siempre que sea posible, ya que los comandos de consola varían (ej: ls vs dir). Usá abstracciones de Python (os o shutil) antes que llamadas al sistema.


# Código Limpio y Mantenible

Un software experto es legible para humanos, no solo para máquinas.
* Tipado Estático (Type Hinting): Obligatorio para proyectos grandes. Permite que el IDE te avise si estás pasando un dato erróneo antes de ejecutar.
* Principios SOLID: 
    * S (Single Responsibility): Una clase debe tener una única razón para cambiar. Una función hace una sola cosa. Si tiene más de 20-30 líneas, probablemente deba dividirse.
    * O (Open/Closed): El código debe estar abierto a la extensión pero cerrado a la modificación. (Usá herencia o composición). Usá clases abstractas (abc.ABC) para definir comportamientos. Si mañana querés cambiar un driver de comunicación, solo creás una nueva clase que herede de la abstracta sin tocar el resto del programa.
    * L (Liskov Substitution): Las subclases deben poder sustituir a las clases base sin romper nada.
    * I (Interface Segregation): Es mejor muchas interfaces específicas que una general (en Python usamos Protocols o Abstract Base Classes - ABC).
    * D (Dependency Inversion): Dependé de abstracciones, no de implementaciones concretas.
* Inyección de Dependencias: No crees objetos pesados dentro de otros. Pasalos como parámetros. Esto permite que en los tests puedas pasar un objeto "de juguete" (Mock) fácilmente.

# Gestión de Errores y Diagnóstico
* Logging Profesional: No uses print(), usá el módulo logging. Configurá un rotador de archivos para que los logs no pesen gigas en el disco. Permite categorizar mensajes (DEBUG, INFO, ERROR) y redirigirlos a archivos sin ensuciar la consola del usuario.
* Excepciones Específicas: Nunca captures un Exception genérico. Capturá el error exacto (ValueError, ConnectionError, etc.).
* Lanzá errores temprano: Si un parámetro es inválido, hacé que falle apenas entra a la función (fail-fast), no 50 líneas después.


# Tooling y Ecosistema

Un entorno profesional está automatizado. Usá estas herramientas para que el software no se degrade con el tiempo:
| Herramienta | Propósito |
|-------------|-----------|
| Ruff | Linter ultrarrápido que reemplaza a Flake8 y detecta errores de estilo y bugs potenciales. |
| Black | Formateador de código. Mantiene el estilo idéntico en todo el proyecto automáticamente. |
| Pytest | Para escribir tests. Si el software es expandible, cada nueva función debe tener su test. |
| Poetry | Gestión de dependencias. Asegura que las librerías sean las mismas en Windows y Linux. |
| Mypy | Verificador de tipos estáticos para asegurar que los Type Hints se cumplan. |


# Documentación "Viva"

* Docstrings: Usá el formato Google o NumPy.
* README.md: Debe explicar cómo instalar el entorno (venv), cómo correr los tests y qué dependencias de sistema (como drivers USB o librerías C++) se necesitan en cada SO.