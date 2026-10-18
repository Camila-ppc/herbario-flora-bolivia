import { Type } from 'class-transformer';
import { IsEnum, IsInt, IsOptional } from 'class-validator';
import { Departamento } from '../../common/enums';

export class QueryAvistamientosDto {
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  plantaId?: number;

  @IsOptional()
  @IsEnum(Departamento)
  departamento?: Departamento;
}
