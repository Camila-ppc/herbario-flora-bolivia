import { ConflictException } from '@nestjs/common';
import { QueryFailedError } from 'typeorm';

/**
 * Traduce errores de PostgreSQL a respuestas HTTP 409 legibles.
 *  - 23505: violación de UNIQUE
 *  - 23503: violación de llave foránea (registro referenciado o referencia inexistente)
 */
export function handleDbError(error: unknown): never {
  if (error instanceof QueryFailedError) {
    const code = (error as any).driverError?.code;
    if (code === '23505') {
      throw new ConflictException('Ya existe un registro con esos datos únicos.');
    }
    if (code === '23503') {
      throw new ConflictException(
        'Operación inválida por relaciones: el registro referenciado no existe o aún tiene registros asociados.',
      );
    }
  }
  throw error;
}
