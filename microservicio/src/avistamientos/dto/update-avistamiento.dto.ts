import { PartialType } from '@nestjs/swagger';
import { CreateAvistamientoDto } from './create-avistamiento.dto';

export class UpdateAvistamientoDto extends PartialType(CreateAvistamientoDto) {}
