import { Type } from 'class-transformer';
import { IsEnum, IsInt, IsOptional, IsString } from 'class-validator';
import { EstadoConservacion } from '../../common/enums';

export class QueryPlantasDto {
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  familiaId?: number;

  @IsOptional()
  @IsString()
  ecorregion?: string;

  @IsOptional()
  @IsEnum(EstadoConservacion)
  estado?: EstadoConservacion;

  /** Búsqueda por nombre científico o común (coincidencia parcial) */
  @IsOptional()
  @IsString()
  q?: string;
}
