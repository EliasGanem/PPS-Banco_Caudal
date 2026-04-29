#include "driver/uart.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdio.h>
#include <string.h>


// Usamos el UART0 que es el que está conectado al chip USB-Serie
#define UART_NUM UART_NUM_0
#define BUF_SIZE (1024)

static const char *TAG = "USB_TEST";

void app_main(void) {
  /* 1. Configuración del UART */
  uart_config_t uart_config = {
      .baud_rate = 115200,
      .data_bits = UART_DATA_8_BITS,
      .parity = UART_PARITY_DISABLE,
      .stop_bits = UART_STOP_BITS_1,
      .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
      .source_clk = UART_SCLK_DEFAULT,
  };

  // Instalamos el driver (Puerto, buffer RX, buffer TX, cola, etc)
  ESP_ERROR_CHECK(uart_driver_install(UART_NUM, BUF_SIZE * 2, 0, 0, NULL, 0));
  ESP_ERROR_CHECK(uart_param_config(UART_NUM, &uart_config));

  ESP_LOGI(TAG, "Comunicación USB-Serial Iniciada.");
  ESP_LOGI(TAG, "Escribe algo en la terminal y el ESP32 lo repetirá...");

  // Buffer para recibir datos
  uint8_t *data = (uint8_t *)malloc(BUF_SIZE);

  while (1) {
    // 2. Leer datos desde el USB (UART0)
    // Esta función se bloquea hasta que recibe algo o pasa el timeout (20ms)
    int len =
        uart_read_bytes(UART_NUM, data, BUF_SIZE, 20 / portTICK_PERIOD_MS);

    if (len > 0) {
      // 3. Escribir de vuelta lo recibido (Echo)
      ESP_LOGI(TAG, "He recibido %d bytes", len);
      uart_write_bytes(UART_NUM, (const char *)data, len);

      // Limpiamos el buffer para la siguiente lectura
      memset(data, 0, BUF_SIZE);
    }

    // Un pequeño delay para no saturar el Watchdog de FreeRTOS
    vTaskDelay(pdMS_TO_TICKS(10));
  }
}