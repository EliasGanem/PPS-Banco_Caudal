#include "stm32f1xx_hal.h"

// --- Definiciones para CLK ---
#define LED_PIN GPIO_PIN_13
#define LED_PORT GPIOC

// Definición del handle para la UART
UART_HandleTypeDef huart1;

// Prototipos de funciones
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART1_UART_Init(void);

int main(void) {
  // 1. Inicialización de la librería HAL
  HAL_Init();

  // 2. Configuración del reloj del sistema
  SystemClock_Config();

  // 3. Inicialización de periféricos configurados
  MX_GPIO_Init();
  MX_USART1_UART_Init();

  uint8_t rxData; // Variable para almacenar el byte recibido
  HAL_GPIO_WritePin(LED_PORT, LED_PIN, GPIO_PIN_SET);

  while (1) {

    // HAL_GPIO_TogglePin(LED_PORT, LED_PIN);
    // HAL_Delay(500);
    //  Recibir 1 byte por UART1 (espera infinita HAL_MAX_DELAY)
    if (HAL_UART_Receive(&huart1, &rxData, 1, HAL_MAX_DELAY) == HAL_OK) {
      // Transmitir el mismo byte de vuelta (Eco)
      HAL_UART_Transmit(&huart1, &rxData, 1, HAL_MAX_DELAY);
    }
  }
}

// Configuración de UART1
static void MX_USART1_UART_Init(void) {
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 9600;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart1) != HAL_OK) {
    // Error de inicialización
    while (1)
      ;
  }
}

// Inicialización de bajo nivel (MSP) - Relojes y Pines
void HAL_UART_MspInit(UART_HandleTypeDef *huart) {
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  if (huart->Instance == USART1) {
    // Habilitar relojes
    __HAL_RCC_USART1_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    /** Configuración de pines:
    PA9  ------> USART1_TX (Alternate Function Push-Pull)
    PA10 ------> USART1_RX (Input Floating o Pull-up)
    */
    GPIO_InitStruct.Pin = GPIO_PIN_9;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    GPIO_InitStruct.Pin = GPIO_PIN_10;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
  }
}

static void MX_GPIO_Init(void) {
  // 1. Habilitar el reloj del puerto A y C
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();

  GPIO_InitTypeDef GPIO_InitStruct = {0};

  // 2. Configuración para el CLK
  GPIO_InitStruct.Pin = LED_PIN;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LED_PORT, &GPIO_InitStruct);
}

void SystemClock_Config(void) {
  // Configuración por defecto para HSI (8MHz) si no se usa cristal externo
}

void SysTick_Handler(void) { HAL_IncTick(); }