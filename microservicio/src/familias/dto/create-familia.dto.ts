import { IsNotEmpty, IsOptional, IsString, MaxLength } from 'class-validator';

export class CreateFamiliaDto {
  @IsString()
  @IsNotEmpty()
  @MaxLength(100)
  nombre: string;

  @IsOptional()
  @IsString()
  descripcion?: string;
}
