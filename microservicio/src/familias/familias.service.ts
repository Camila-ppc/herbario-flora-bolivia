import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { handleDbError } from '../common/db-errors';
import { CreateFamiliaDto } from './dto/create-familia.dto';
import { UpdateFamiliaDto } from './dto/update-familia.dto';
import { Familia } from './entities/familia.entity';

@Injectable()
export class FamiliasService {
  constructor(
    @InjectRepository(Familia)
    private readonly repo: Repository<Familia>,
  ) {}

  async create(dto: CreateFamiliaDto): Promise<Familia> {
    try {
      return await this.repo.save(this.repo.create(dto));
    } catch (e) {
      handleDbError(e);
    }
  }

  findAll(): Promise<Familia[]> {
    return this.repo.find({ order: { nombre: 'ASC' } });
  }

  async findOne(id: number): Promise<Familia> {
    const familia = await this.repo.findOne({ where: { id } });
    if (!familia) throw new NotFoundException(`Familia ${id} no encontrada`);
    return familia;
  }

  async update(id: number, dto: UpdateFamiliaDto): Promise<Familia> {
    const familia = await this.findOne(id);
    try {
      return await this.repo.save(Object.assign(familia, dto));
    } catch (e) {
      handleDbError(e);
    }
  }

  async remove(id: number): Promise<void> {
    const familia = await this.findOne(id);
    try {
      await this.repo.remove(familia);
    } catch (e) {
      handleDbError(e);
    }
  }
}
