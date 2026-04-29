#include "app_rs232_task.h"
#include "board_config.h"
#include "../hal/hal_uart.h"
#include "../hal/hal_gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"

static SemaphoreHandle_t rs232_mutex;

void App_RS232_Init(void) {
    rs232_mutex = xSemaphoreCreateMutex();
}

bool App_RS232_ReadBalanza(char* out_buffer) {
    if (xSemaphoreTake(rs232_mutex, portMAX_DELAY) == pdTRUE) {
        // Seleccionar Balanza
        HAL_GPIO_Write(PIN_SELECTOR_UART, VAL_SEL_UART_BALANZA);
        HAL_GPIO_Write(PIN_HAB_MUX, LOGIC_HAB_MUX_ACTIVE);
        
        // Limpiar buffer y esperar trama
        HAL_UART_Flush(HAL_UART_PORT_RS232);
        
        // La balanza envía continuamente de a 8 bytes "SPPPPPPC" donde C es '\r'
        bool success = false;
        uint8_t c;
        int frame_idx = 0;
        uint8_t frame[8];
        size_t bytes_read = 0;
        
        // Sincronizar y leer frame válido (timeout 1000ms)
        uint32_t start_time = xTaskGetTickCount() * portTICK_PERIOD_MS;
        while ((xTaskGetTickCount() * portTICK_PERIOD_MS - start_time) < 1000) {
            if (HAL_UART_Read(HAL_UART_PORT_RS232, &c, 1, &bytes_read, 50) == HAL_UART_SUCCESS && bytes_read == 1) {
                frame[frame_idx++] = c;
                if (c == '\r') {
                    if (frame_idx == 8) {
                        // Frame válido
                        out_buffer[0] = frame[1];
                        out_buffer[1] = frame[2];
                        out_buffer[2] = frame[3];
                        out_buffer[3] = frame[4];
                        out_buffer[4] = '.';
                        out_buffer[5] = frame[5];
                        out_buffer[6] = frame[6];
                        out_buffer[7] = '\0';
                        success = true;
                        break;
                    } else {
                        // Desincronizado, reiniciar frame
                        frame_idx = 0;
                    }
                }
                if (frame_idx >= 8) {
                    // Llegamos a 8 bytes sin \r, descartar todo
                    frame_idx = 0;
                }
            }
        }
        
        xSemaphoreGive(rs232_mutex);
        return success;
    }
    return false;
}

bool App_RS232_ReadReloj(uint8_t* out_buffer) {
    if (xSemaphoreTake(rs232_mutex, portMAX_DELAY) == pdTRUE) {
        // Seleccionar Reloj
        HAL_GPIO_Write(PIN_SELECTOR_UART, VAL_SEL_UART_RELOJ);
        HAL_GPIO_Write(PIN_HAB_MUX, LOGIC_HAB_MUX_ACTIVE);
        
        HAL_UART_Flush(HAL_UART_PORT_RS232);
        
        // Enviar comando PEDIR TIEMPO (entero 100 = 0x64)
        uint8_t cmd = 100;
        HAL_UART_Write(HAL_UART_PORT_RS232, &cmd, 1);
        
        // Leer 2 bytes
        size_t bytes_read = 0;
        bool success = false;
        
        if (HAL_UART_Read(HAL_UART_PORT_RS232, out_buffer, 2, &bytes_read, 500) == HAL_UART_SUCCESS) {
            if (bytes_read == 2) {
                success = true;
            }
        }
        
        xSemaphoreGive(rs232_mutex);
        return success;
    }
    return false;
}
