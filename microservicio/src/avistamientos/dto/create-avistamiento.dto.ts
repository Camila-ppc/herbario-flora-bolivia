import {
  IsDateString,
  IsEnum,
  IsInt,
  IsNotEmpty,
  IsNumber,
  IsOptional,
  IsPositive,
  IsString,
  Max,
  MaxLength,
  Min,
} from 'class-validator';
import { Departamento } from '../../common/enums';

export class CreateAvistamientoDto {
  @IsInt()
  @IsPositive()
  plantaId: number;

  @IsString()
  @IsNotEmpty()
  @MaxLength(150)
  localidad: string;

  @IsEnum(Departamento)
  departamento: Departamento;

  @IsOptional()
  @IsNumber()
  @Min(-90)
  @Max(90)
  latitud?: number;

  @IsOptional()
  @IsNumber()
  @Min(-180)
  @Max(180)
  longitud?: number;

  /** YYYY-MM-DD */
  @IsDateString({ strict: true })
  fecha: string;

  @IsString()
  @IsNotEmpty()
  @MaxLength(120)
  observador: string;

  @IsOptional()
  @IsString()
  notas?: string;
}
