#ifndef HAL_UART_H
#define HAL_UART_H

#include <stdint.h>
#include <stdbool.h>

void hal_uart_init(void);
void hal_uart_clear_rx_buffer(void);
bool hal_uart_read_byte(uint8_t *data);
void hal_uart_isr_callback(void); // To be called from USART1_IRQHandler

#endif /* HAL_UART_H */
