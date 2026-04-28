---
trigger: always_on
---

# Buenas Prácticas y Arquitectura de Firmware en C

Este documento establece las reglas y estándares para el desarrollo de sistemas embebidos modulares, escalables y agnósticos al hardware.

## 1. Arquitectura de Capas (Decoupling)
El firmware debe estructurarse para que la lógica de aplicación no dependa de los registros del microcontrolador (MCU).

| Capa | Descripción | Acceso al Hardware |
| :--- | :--- | :--- |
| **Application** | Logica de aplicación. | Prohibido. |
| **Services / PAL** | Capa de Abstracción de Plataforma. Traduce servicios. | Indirecto (vía HAL). |
| **HAL (Hardware Abstraction Layer)** | Drivers de periféricos (UART, I2C, SPI) con nombres genéricos. | Solo a través de APIs del SDK. |
| **LL (Low Level) / Target** | Configuración de registros, vectores de interrupción y startup. | Acceso total. |

## 2. Orientación a Objetos en C (Encapsulamiento)

Usar el patrón de "Objeto" para manejar múltiples instancias de un periférico. Reglas de Diseño:

1. Opaque Pointers (Encapsulamiento real): Define el struct en el .c y solo expón un typedef en el .h. Esto evita que el usuario manipule los campos internos.
2. El puntero self: Todas las funciones de un módulo deben recibir como primer argumento un puntero a la estructura de control.

## 3.Modularidad y Hardware Abstraction Layer (HAL)

El driver debe recibir punteros a funciones (callbacks) para realizar las operaciones de lectura/escritura durante su inicialización.

Está prohibido usar int, long o short. Se debe usar exclusivamente <stdint.h> (uint8_t, int32_t, uintptr_t, etc.). 

Excepción: float y double son aceptables si el hardware tiene FPU (Floating Point Unit).

## 4. Gestión de Memoria y Rendimiento
### 4.1. Prohibición de Memoria Dinámica

Regla: No se permite el uso de malloc(), calloc() o free() en el firmware principal.

Razón: La fragmentación del Heap y el indeterminismo temporal pueden provocar fallos críticos impredecibles.

Alternativa: Usa asignación estática (variables globales/static) o Pools de memoria de tamaño fijo.

### 4.2. Ubicación de Datos (Const y Volatile)

Const: Todo dato que no deba cambiar en tiempo de ejecución (tablas de búsqueda, configuraciones de pines) debe marcarse como const. Esto ahorra RAM al mantener los datos en la Flash.

Volatile: Obligatorio para variables modificadas dentro de una ISR o para punteros que apuntan a registros de hardware.

## 5. Control de Hardware y Registros

### 5.1. Manipulación de Bits

Regla: Evita el uso de bit-fields en estructuras para mapear registros, ya que el orden de los bits depende del compilador y la arquitectura (Endians).

Práctica Experta: Usa máscaras de bits y desplazamientos explícitos.

### 5.2. Estados de Retorno

Regla: Ninguna función que interactúe con el hardware debe ser de tipo void. Siempre deben devolver un status_t (Enum) que indique éxito, timeout o error de hardware.

## 6. Documentación y Estilo (Clean Code)

### 6.1. Estándar Doxygen
Todos los archivos .h deben estar documentados siguiendo el formato Doxygen para permitir la generación automática de manuales técnicos.

### 6.2. Reglas para nombres

Archivos: modulo_nombre.c y modulo_nombre.h.

Funciones: Prefijo_Sustantivo_Verbo() (Ej: UART_Buffer_Flush).

Macros: Siempre en MAYUSCULAS_CON_SNAKE_CASE.

Utilizar el idioma español.

## 7. Estructura de Archivos Recomendada

Para mantener el proyecto organizado y facilitar la migración de microcontrolador:

/src

  ├── /app            # Lógica de la aplicación (100% Portable)

  ├── /drivers        # Componentes externos (Sensores, Displays, etc.)

  ├── /mcu            # CAPA NO PORTABLE

  │     ├── /xx1     # Implementación específica para el microcontrolador 1

  │     └── /xx2    # Implementación específica para el microcontrolador 2

  ├── /utils          # Librerías generales (Buffer Circular, Matemáticas)
  
  └── main.c          # Punto de entrada (Setup y Loop principal)
/inc
 ├──  # donde estan los archivos punto H.