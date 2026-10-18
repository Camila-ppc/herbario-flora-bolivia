import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { handleDbError } from '../common/db-errors';
import { CreateAvistamientoDto } from './dto/create-avistamiento.dto';
import { QueryAvistamientosDto } from './dto/query-avistamientos.dto';
import { UpdateAvistamientoDto } from './dto/update-avistamiento.dto';
import { Avistamiento } from './entities/avistamiento.entity';

@Injectable()
export class AvistamientosService {
  constructor(
    @InjectRepository(Avistamiento)
    private readonly repo: Repository<Avistamiento>,
  ) {}

  async create(dto: CreateAvistamientoDto): Promise<Avistamiento> {
    try {
      const saved = await this.repo.save(this.repo.create(dto));
      return await this.findOne(saved.id);
    } catch (e) {
      handleDbError(e);
    }
  }

  findAll(query: QueryAvistamientosDto): Promise<Avistamiento[]> {
    const where: Record<string, unknown> = {};
    if (query.plantaId) where.plantaId = query.plantaId;
    if (query.departamento) where.departamento = query.departamento;
    return this.repo.find({
      where,
      relations: { planta: true },
      order: { fecha: 'DESC', id: 'DESC' },
    });
  }

  async findOne(id: number): Promise<Avistamiento> {
    const item = await this.repo.findOne({ where: { id }, relations: { planta: true } });
    if (!item) throw new NotFoundException(`Avistamiento ${id} no encontrado`);
    return item;
  }

  async update(id: number, dto: UpdateAvistamientoDto): Promise<Avistamiento> {
    const item = await this.findOne(id);
    try {
      const merged = Object.assign(item, dto);
      delete merged.planta; // usar plantaId actualizado
      await this.repo.save(merged);
      return await this.findOne(id);
    } catch (e) {
      handleDbError(e);
    }
  }

  async remove(id: number): Promise<void> {
    const item = await this.findOne(id);
    await this.repo.remove(item);
  }
}
