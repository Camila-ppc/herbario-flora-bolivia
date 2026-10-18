import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Familia } from './entities/familia.entity';
import { FamiliasController } from './familias.controller';
import { FamiliasService } from './familias.service';

@Module({
  imports: [TypeOrmModule.forFeature([Familia])],
  controllers: [FamiliasController],
  providers: [FamiliasService],
  exports: [TypeOrmModule],
})
export class FamiliasModule {}
