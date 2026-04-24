#ifndef BANCO_CAUDAL_H
#define BANCO_CAUDAL_H

#include "hal_comm.h"

/**
 * @brief Opaque Pointer para la estructura de control del banco de caudal.
 */
typedef struct banco_caudal_s banco_caudal_t;

/**
 * @brief Obtiene la instancia única del banco de caudal.
 * @return banco_caudal_t* Puntero a la instancia.
 */
banco_caudal_t *BancoCaudal_GetInstance(void);

/**
 * @brief Inicializa el módulo del banco de caudal.
 * @param self Puntero a la instancia.
 * @param comm Puntero a la interfaz de comunicaciones a utilizar.
 */
void BancoCaudal_Init(banco_caudal_t *self, hal_comm_t *comm);

/**
 * @brief Procesa la lógica de recepción de comandos y la máquina de estados.
 * Debe ser llamada periódicamente en el bucle principal.
 * @param self Puntero a la instancia.
 */
void BancoCaudal_Process(banco_caudal_t *self);

#endif // BANCO_CAUDAL_H
