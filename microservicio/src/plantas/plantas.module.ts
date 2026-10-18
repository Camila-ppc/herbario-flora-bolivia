import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Avistamiento } from '../avistamientos/entities/avistamiento.entity';
import { Planta } from './entities/planta.entity';
import { PlantasController } from './plantas.controller';
import { PlantasService } from './plantas.service';

@Module({
  imports: [TypeOrmModule.forFeature([Planta, Avistamiento])],
  controllers: [PlantasController],
  providers: [PlantasService],
  exports: [TypeOrmModule],
})
export class PlantasModule {}
