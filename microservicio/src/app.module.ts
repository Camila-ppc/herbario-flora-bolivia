import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AvistamientosModule } from './avistamientos/avistamientos.module';
import { FamiliasModule } from './familias/familias.module';
import { HealthController } from './health/health.controller';
import { PlantasModule } from './plantas/plantas.module';
import { SeedModule } from './seed/seed.module';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    TypeOrmModule.forRootAsync({
      inject: [ConfigService],
      useFactory: (config: ConfigService) => ({
        type: 'postgres' as const,
        host: config.get<string>('DB_HOST', 'localhost'),
        port: parseInt(config.get<string>('DB_PORT', '5432'), 10),
        username: config.get<string>('DB_USER', 'herbario'),
        password: config.get<string>('DB_PASSWORD', 'herbario123'),
        database: config.get<string>('DB_NAME', 'herbario_db'),
        autoLoadEntities: true,
        // Para el alcance académico se crean las tablas automáticamente.
        // En producción real se usarían migraciones.
        synchronize: config.get<string>('DB_SYNC', 'true') === 'true',
        retryAttempts: 10,
        retryDelay: 3000,
      }),
    }),
    FamiliasModule,
    PlantasModule,
    AvistamientosModule,
    SeedModule,
  ],
  controllers: [HealthController],
})
export class AppModule {}
