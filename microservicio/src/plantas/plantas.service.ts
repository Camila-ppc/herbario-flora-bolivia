import { BadRequestException, Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Avistamiento } from '../avistamientos/entities/avistamiento.entity';
import { handleDbError } from '../common/db-errors';
import { CreatePlantaDto } from './dto/create-planta.dto';
import { QueryPlantasDto } from './dto/query-plantas.dto';
import { UpdatePlantaDto } from './dto/update-planta.dto';
import { Planta } from './entities/planta.entity';

@Injectable()
export class PlantasService {
  constructor(
    @InjectRepository(Planta)
    private readonly repo: Repository<Planta>,
    @InjectRepository(Avistamiento)
    private readonly avistamientosRepo: Repository<Avistamiento>,
  ) {}

  private validarAltitud(min?: number, max?: number) {
    if (min !== undefined && max !== undefined && min > max) {
      throw new BadRequestException('altitudMin no puede ser mayor que altitudMax');
    }
  }

  async create(dto: CreatePlantaDto): Promise<Planta> {
    this.validarAltitud(dto.altitudMin, dto.altitudMax);
    try {
      const saved = await this.repo.save(this.repo.create(dto));
      return await this.findOne(saved.id);
    } catch (e) {
      handleDbError(e);
    }
  }

  findAll(query: QueryPlantasDto): Promise<Planta[]> {
    const qb = this.repo
      .createQueryBuilder('p')
      .leftJoinAndSelect('p.familia', 'familia')
      .orderBy('p.nombreCientifico', 'ASC');

    if (query.familiaId) qb.andWhere('p.familia_id = :familiaId', { familiaId: query.familiaId });
    if (query.ecorregion) qb.andWhere('p.ecorregion ILIKE :eco', { eco: query.ecorregion });
    if (query.estado) qb.andWhere('p.estado_conservacion = :estado', { estado: query.estado });
    if (query.q) {
      qb.andWhere('(p.nombre_cientifico ILIKE :q OR p.nombre_comun ILIKE :q)', {
        q: `%${query.q}%`,
      });
    }
    return qb.getMany();
  }

  async findOne(id: number): Promise<Planta> {
    const planta = await this.repo.findOne({ where: { id } });
    if (!planta) throw new NotFoundException(`Planta ${id} no encontrada`);
    return planta;
  }

  async findAvistamientos(id: number): Promise<Avistamiento[]> {
    await this.findOne(id);
    return this.avistamientosRepo.find({
      where: { plantaId: id },
      order: { fecha: 'DESC' },
    });
  }

  async update(id: number, dto: UpdatePlantaDto): Promise<Planta> {
    const planta = await this.findOne(id);
    const merged = Object.assign(planta, dto);
    this.validarAltitud(merged.altitudMin, merged.altitudMax);
    try {
      // Se quita la relación cargada para que TypeORM use familiaId actualizado
      delete merged.familia;
      await this.repo.save(merged);
      return await this.findOne(id);
    } catch (e) {
      handleDbError(e);
    }
  }

  async remove(id: number): Promise<void> {
    const planta = await this.findOne(id);
    try {
      await this.repo.remove(planta);
    } catch (e) {
      handleDbError(e);
    }
  }
}
