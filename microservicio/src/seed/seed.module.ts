import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Avistamiento } from '../avistamientos/entities/avistamiento.entity';
import { Familia } from '../familias/entities/familia.entity';
import { Planta } from '../plantas/entities/planta.entity';
import { SeedService } from './seed.service';

@Module({
  imports: [TypeOrmModule.forFeature([Familia, Planta, Avistamiento])],
  providers: [SeedService],
})
export class SeedModule {}
