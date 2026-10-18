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
import { AvistamientosService } from './avistamientos.service';
import { CreateAvistamientoDto } from './dto/create-avistamiento.dto';
import { QueryAvistamientosDto } from './dto/query-avistamientos.dto';
import { UpdateAvistamientoDto } from './dto/update-avistamiento.dto';

@ApiTags('avistamientos')
@Controller('avistamientos')
export class AvistamientosController {
  constructor(private readonly service: AvistamientosService) {}

  @Post()
  create(@Body() dto: CreateAvistamientoDto) {
    return this.service.create(dto);
  }

  @Get()
  findAll(@Query() query: QueryAvistamientosDto) {
    return this.service.findAll(query);
  }

  @Get(':id')
  findOne(@Param('id', ParseIntPipe) id: number) {
    return this.service.findOne(id);
  }

  @Patch(':id')
  update(@Param('id', ParseIntPipe) id: number, @Body() dto: UpdateAvistamientoDto) {
    return this.service.update(id, dto);
  }

  @Delete(':id')
  @HttpCode(204)
  remove(@Param('id', ParseIntPipe) id: number) {
    return this.service.remove(id);
  }
}
