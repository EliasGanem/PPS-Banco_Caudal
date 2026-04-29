#include "app_usb_task.h"
#include "app_control.h"
#include "board_config.h"
#include "../hal/hal_uart.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <string.h>

#define USB_RX_BUF_SIZE 128

static void app_usb_rx_task(void *pvParameters);

void App_USB_Init(void) {
    // La inicialización del HAL_UART debe hacerse en el main, 
    // pero aquí creamos la tarea que lo lee.
    xTaskCreate(app_usb_rx_task, "USB_RX_TASK", 4096, NULL, 5, NULL);
}

void App_USB_SendString(const char* str) {
    HAL_UART_Write(HAL_UART_PORT_USB, (const uint8_t*)str, strlen(str));
}

void App_USB_SendBytes(const uint8_t* data, size_t len) {
    HAL_UART_Write(HAL_UART_PORT_USB, data, len);
}

static void app_usb_rx_task(void *pvParameters) {
    uint8_t rx_buffer[USB_RX_BUF_SIZE];
    uint16_t rx_index = 0;

    while (1) {
        uint8_t c;
        size_t read_bytes = 0;
        // Leer 1 byte de forma bloqueante (utiliza la interrupción y cola interna de ESP-IDF)
        hal_uart_status_t status = HAL_UART_Read(HAL_UART_PORT_USB, &c, 1, &read_bytes, portMAX_DELAY);

        if (status == HAL_UART_SUCCESS && read_bytes > 0) {
            if (c == CMD_TERMINATOR) {
                rx_buffer[rx_index] = '\0'; // Asegurar terminador nulo internamente

                // Parseo del comando
                app_cmd_t cmd = CMD_DESCONOCIDO;
                if (strcmp((char*)rx_buffer, "INICIAR ENSAYO") == 0) {
                    cmd = CMD_INICIAR_ENSAYO;
                } else if (strcmp((char*)rx_buffer, "INICIAR RETORNO") == 0) {
                    cmd = CMD_INICIAR_RETORNO;
                } else if (strcmp((char*)rx_buffer, "FINALIZAR ENSAYO") == 0) {
                    cmd = CMD_FINALIZAR_ENSAYO;
                } else if (strcmp((char*)rx_buffer, "FINALIZAR RETORNO") == 0) {
                    cmd = CMD_FINALIZAR_RETORNO;
                } else if (strcmp((char*)rx_buffer, "MEDICION BALANZA") == 0) {
                    cmd = CMD_MEDICION_BALANZA;
                } else if (strcmp((char*)rx_buffer, "MEDICION RELOJ") == 0) {
                    cmd = CMD_MEDICION_RELOJ;
                } else if (strcmp((char*)rx_buffer, "MEDICION COMPLETA") == 0) {
                    cmd = CMD_MEDICION_COMPLETA;
                }

                // Enviar comando a la cola de la tarea de control
                if (cmd != CMD_DESCONOCIDO) {
                    App_Control_SendCmd(cmd);
                }

                // Limpiar buffer
                rx_index = 0;
            } else {
                if (rx_index < USB_RX_BUF_SIZE - 1) {
                    rx_buffer[rx_index++] = c;
                } else {
                    // Overflow de buffer, descartar todo
                    rx_index = 0;
                }
            }
        }
    }
}
