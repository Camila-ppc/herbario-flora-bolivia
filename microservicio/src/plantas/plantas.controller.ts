import {
  Body,
  Controller,
  Delete,
  Get,
  HttpCode,
  Param,
  ParseIntPipe,
  Patch,
  Post,
  Query,
} from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import { CreatePlantaDto } from './dto/create-planta.dto';
import { QueryPlantasDto } from './dto/query-plantas.dto';
import { UpdatePlantaDto } from './dto/update-planta.dto';
import { PlantasService } from './plantas.service';

@ApiTags('plantas')
@Controller('plantas')
export class PlantasController {
  constructor(private readonly service: PlantasService) {}

  @Post()
  create(@Body() dto: CreatePlantaDto) {
    return this.service.create(dto);
  }

  @Get()
  findAll(@Query() query: QueryPlantasDto) {
    return this.service.findAll(query);
  }

  @Get(':id')
  findOne(@Param('id', ParseIntPipe) id: number) {
    return this.service.findOne(id);
  }

  @Get(':id/avistamientos')
  findAvistamientos(@Param('id', ParseIntPipe) id: number) {
    return this.service.findAvistamientos(id);
  }

  @Patch(':id')
  update(@Param('id', ParseIntPipe) id: number, @Body() dto: UpdatePlantaDto) {
    return this.service.update(id, dto);
  }

  @Delete(':id')
  @HttpCode(204)
  remove(@Param('id', ParseIntPipe) id: number) {
    return this.service.remove(id);
  }
}
