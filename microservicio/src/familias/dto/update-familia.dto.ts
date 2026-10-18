import { PartialType } from '@nestjs/swagger';
import { CreateFamiliaDto } from './create-familia.dto';

export class UpdateFamiliaDto extends PartialType(CreateFamiliaDto) {}
