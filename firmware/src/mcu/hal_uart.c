#include "mcu/hal_uart.h"
#include "utils/circular_buffer.h"
#include "main.h"

extern UART_HandleTypeDef huart1;

#define UART_RX_BUFFER_SIZE 128
static uint8_t rx_buffer_memory[UART_RX_BUFFER_SIZE];
static circular_buffer_t rx_buffer;

void hal_uart_init(void) {
    cb_init(&rx_buffer, rx_buffer_memory, UART_RX_BUFFER_SIZE);
    
    // Enable UART RX Interrupt
    __HAL_UART_ENABLE_IT(&huart1, UART_IT_RXNE);
}

void hal_uart_clear_rx_buffer(void) {
    __disable_irq(); // Avoid concurrent modification
    cb_clear(&rx_buffer);
    __enable_irq();
}

bool hal_uart_read_byte(uint8_t *data) {
    bool result = false;
    __disable_irq();
    result = cb_pop(&rx_buffer, data);
    __enable_irq();
    return result;
}

void hal_uart_isr_callback(void) {
    if (__HAL_UART_GET_FLAG(&huart1, UART_FLAG_RXNE) != RESET &&
        __HAL_UART_GET_IT_SOURCE(&huart1, UART_IT_RXNE) != RESET) {
        
        uint8_t data = (uint8_t)(huart1.Instance->DR & (uint8_t)0x00FF);
        cb_push(&rx_buffer, data);
    }
}
