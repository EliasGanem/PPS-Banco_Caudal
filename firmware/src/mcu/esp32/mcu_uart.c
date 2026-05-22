#include "../../hal/hal_uart.h"
#include "driver/uart.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

#define BUF_SIZE 1024

static uart_port_t get_esp_uart_num(hal_uart_port_t port) {
    if (port == HAL_UART_PORT_USB) return UART_NUM_0;
    if (port == HAL_UART_PORT_RS232) return UART_NUM_2;
    return UART_NUM_MAX;
}

hal_uart_status_t HAL_UART_Init(hal_uart_port_t port, uint32_t baudrate, void** event_queue_out) {
    uart_port_t uart_num = get_esp_uart_num(port);
    if (uart_num == UART_NUM_MAX) return HAL_UART_ERROR;

    uart_config_t uart_config = {
        .baud_rate = baudrate,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_DEFAULT,
    };

    if (uart_param_config(uart_num, &uart_config) != ESP_OK) {
        return HAL_UART_ERROR;
    }

    // Configuración de pines según el hardware
    if (port == HAL_UART_PORT_USB) {
        if (uart_set_pin(uart_num, 1, 3, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE) != ESP_OK) {
            return HAL_UART_ERROR;
        }
    } else if (port == HAL_UART_PORT_RS232) {
        // Pines 17 (TX) y 16 (RX) para el UART2
        if (uart_set_pin(uart_num, 17, 16, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE) != ESP_OK) {
            return HAL_UART_ERROR;
        }
    }

    QueueHandle_t uart_queue = NULL;
    int queue_size = (event_queue_out != NULL) ? 20 : 0;

    if (uart_driver_install(uart_num, BUF_SIZE * 2, BUF_SIZE * 2, queue_size, (event_queue_out != NULL) ? &uart_queue : NULL, 0) != ESP_OK) {
        return HAL_UART_ERROR;
    }

    if (event_queue_out != NULL) {
        *event_queue_out = (void*)uart_queue;
    }

    return HAL_UART_SUCCESS;
}

hal_uart_status_t HAL_UART_Write(hal_uart_port_t port, const uint8_t* data, size_t length) {
    uart_port_t uart_num = get_esp_uart_num(port);
    if (uart_num == UART_NUM_MAX) return HAL_UART_ERROR;

    int written = uart_write_bytes(uart_num, (const char*)data, length);
    if (written < 0) {
        return HAL_UART_ERROR;
    }
    return HAL_UART_SUCCESS;
}

hal_uart_status_t HAL_UART_Read(hal_uart_port_t port, uint8_t* buffer, size_t length, size_t* read_bytes, uint32_t timeout_ms) {
    uart_port_t uart_num = get_esp_uart_num(port);
    if (uart_num == UART_NUM_MAX) return HAL_UART_ERROR;

    int len = uart_read_bytes(uart_num, buffer, length, pdMS_TO_TICKS(timeout_ms));
    if (len < 0) {
        return HAL_UART_ERROR;
    }
    if (read_bytes != NULL) {
        *read_bytes = (size_t)len;
    }
    if (len == 0 && timeout_ms > 0) {
        return HAL_UART_TIMEOUT;
    }
    return HAL_UART_SUCCESS;
}

hal_uart_status_t HAL_UART_Flush(hal_uart_port_t port) {
    uart_port_t uart_num = get_esp_uart_num(port);
    if (uart_num == UART_NUM_MAX) return HAL_UART_ERROR;

    if (uart_flush_input(uart_num) != ESP_OK) {
        return HAL_UART_ERROR;
    }
    return HAL_UART_SUCCESS;
}
