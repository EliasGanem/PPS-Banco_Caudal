#ifndef STATUS_H
#define STATUS_H

/**
 * @brief Tipos de estado devueltos por las funciones del sistema.
 */
typedef enum {
    STATUS_OK = 0,      /**< Operación completada con éxito */
    STATUS_ERROR = 1,   /**< Error genérico en la operación */
    STATUS_BUSY = 2,    /**< El recurso se encuentra ocupado */
    STATUS_TIMEOUT = 3  /**< Se agotó el tiempo de espera */
} status_t;

#endif // STATUS_H
