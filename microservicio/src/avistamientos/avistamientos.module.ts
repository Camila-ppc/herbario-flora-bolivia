import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AvistamientosController } from './avistamientos.controller';
import { AvistamientosService } from './avistamientos.service';
import { Avistamiento } from './entities/avistamiento.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Avistamiento])],
  controllers: [AvistamientosController],
  providers: [AvistamientosService],
})
export class AvistamientosModule {}
