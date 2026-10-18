import {
  IsEnum,
  IsInt,
  IsNotEmpty,
  IsOptional,
  IsPositive,
  IsString,
  MaxLength,
  Min,
} from 'class-validator';
import { EstadoConservacion } from '../../common/enums';

export class CreatePlantaDto {
  @IsString()
  @IsNotEmpty()
  @MaxLength(150)
  nombreCientifico: string;

  @IsOptional()
  @IsString()
  @MaxLength(150)
  nombreComun?: string;

  @IsOptional()
  @IsString()
  descripcion?: string;

  @IsOptional()
  @IsString()
  @MaxLength(80)
  ecorregion?: string;

  @IsOptional()
  @IsInt()
  @Min(0)
  altitudMin?: number;

  @IsOptional()
  @IsInt()
  @Min(0)
  altitudMax?: number;

  @IsOptional()
  @IsEnum(EstadoConservacion)
  estadoConservacion?: EstadoConservacion;

  @IsInt()
  @IsPositive()
  familiaId: number;
}
