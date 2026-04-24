#include "banco_caudal.h"
#include <string.h>
#include <stdio.h>
#include "stm32f1xx_hal.h" // Necesario para HAL_GetTick()

typedef enum {
    ESTADO_ESPERA,
    ESTADO_EN_CURSO
} estado_ensayo_t;

// Definición real de la estructura (Opaque Pointer)
struct banco_caudal_s {
    hal_comm_t* comm;
    estado_ensayo_t estado;
    uint32_t start_tick;
    uint32_t last_tick;
    uint32_t simulated_weight_g;
    uint8_t rx_buffer[64];
    uint16_t rx_index;
};

// Instancia única (asignación estática, sin malloc)
static struct banco_caudal_s instance;

banco_caudal_t* BancoCaudal_GetInstance(void) {
    return &instance;
}

void BancoCaudal_Init(banco_caudal_t* self, hal_comm_t* comm) {
    if (self == NULL) return;
    self->comm = comm;
    self->estado = ESTADO_ESPERA;
    self->start_tick = 0;
    self->last_tick = HAL_GetTick();
    self->simulated_weight_g = 50000; // Inicia en 50kg (50000g)
    self->rx_index = 0;
    memset(self->rx_buffer, 0, sizeof(self->rx_buffer));
}

static void BancoCaudal_EnviarRespuesta(banco_caudal_t* self, const char* str, uint16_t len) {
    // Intentamos enviar repetidas veces si está BUSY (comportamiento bloqueante simple)
    while (self->comm->transmit((const uint8_t*)str, len) == STATUS_BUSY);
}

static void BancoCaudal_ProcesarComando(banco_caudal_t* self, const char* cmd) {
    char resp[32];
    uint32_t current_tick = HAL_GetTick();
    uint32_t elapsed_ms = 0;
    
    if (self->estado == ESTADO_EN_CURSO) {
        elapsed_ms = current_tick - self->start_tick;
    }

    uint32_t secs = elapsed_ms / 1000;
    uint32_t ms = elapsed_ms % 1000;
    
    // Obtenemos el peso simulado actual
    uint32_t weight_int = self->simulated_weight_g / 1000; 
    uint32_t weight_frac = self->simulated_weight_g % 1000;        

    if (strcmp(cmd, "INICIAR ENSAYO") == 0) {
        self->estado = ESTADO_EN_CURSO;
        self->start_tick = HAL_GetTick();
    } 
    else if (strcmp(cmd, "FINALIZAR ENSAYO") == 0) {
        self->estado = ESTADO_ESPERA;
        // Envía tiempo total
        sprintf(resp, "%04lu.%03lu", secs, ms);
        BancoCaudal_EnviarRespuesta(self, resp, 9); // 8 chars + '\0'
    } 
    else if (strcmp(cmd, "MEDICION RELOJ") == 0) {
        sprintf(resp, "%04lu.%03lu", secs, ms);
        BancoCaudal_EnviarRespuesta(self, resp, 9); // 8 chars + '\0'
    } 
    else if (strcmp(cmd, "MEDICION BALANZA") == 0) {
        sprintf(resp, "%03lu.%03lu", weight_int, weight_frac);
        BancoCaudal_EnviarRespuesta(self, resp, 8); // 7 chars + '\0'
    } 
    else if (strcmp(cmd, "MEDICION COMPLETA") == 0) {
        // Envia peso
        sprintf(resp, "%03lu.%03lu", weight_int, weight_frac);
        BancoCaudal_EnviarRespuesta(self, resp, 8);
        
        // Envia tiempo
        sprintf(resp, "%04lu.%03lu", secs, ms);
        BancoCaudal_EnviarRespuesta(self, resp, 9);
    }
}

void BancoCaudal_Process(banco_caudal_t* self) {
    if (self == NULL || self->comm == NULL) return;

    // Actualizar simulación de peso
    uint32_t current_tick = HAL_GetTick();
    uint32_t delta_ms = current_tick - self->last_tick;
    self->last_tick = current_tick;
    
    if (self->estado == ESTADO_EN_CURSO) {
        self->simulated_weight_g += delta_ms; // 1g por ms = 1kg por s
    }

    uint8_t temp_buf[16];
    uint16_t bytes_read = 0;
    
    if (self->comm->receive(temp_buf, sizeof(temp_buf), &bytes_read) == STATUS_OK && bytes_read > 0) {
        for (uint16_t i = 0; i < bytes_read; i++) {
            if (self->rx_index < sizeof(self->rx_buffer) - 1) {
                self->rx_buffer[self->rx_index++] = temp_buf[i];
                if (temp_buf[i] == '\0') {
                    // Se encontró un comando completo terminado en null
                    BancoCaudal_ProcesarComando(self, (char*)self->rx_buffer);
                    self->rx_index = 0; // Resetea buffer para próximo comando
                }
            } else {
                // Buffer lleno y no se encontró terminador null, se resetea para evitar overflow
                self->rx_index = 0;
            }
        }
    }
}
