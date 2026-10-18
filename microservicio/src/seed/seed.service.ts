import { Injectable, Logger, OnApplicationBootstrap } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Avistamiento } from '../avistamientos/entities/avistamiento.entity';
import { Departamento, EstadoConservacion } from '../common/enums';
import { Familia } from '../familias/entities/familia.entity';
import { Planta } from '../plantas/entities/planta.entity';

/**
 * Carga datos de ejemplo la primera vez que arranca el sistema (tablas vacías).
 * Se desactiva con SEED_DATA=false. Los estados de conservación son ilustrativos.
 */
@Injectable()
export class SeedService implements OnApplicationBootstrap {
  private readonly logger = new Logger(SeedService.name);

  constructor(
    private readonly config: ConfigService,
    @InjectRepository(Familia) private readonly familias: Repository<Familia>,
    @InjectRepository(Planta) private readonly plantas: Repository<Planta>,
    @InjectRepository(Avistamiento) private readonly avistamientos: Repository<Avistamiento>,
  ) {}

  async onApplicationBootstrap() {
    if (this.config.get('SEED_DATA', 'true') !== 'true') return;
    if ((await this.familias.count()) > 0) return;

    const fam = await this.familias.save(
      ['Rosaceae', 'Bromeliaceae', 'Lecythidaceae', 'Nymphaeaceae', 'Amaranthaceae'].map((nombre) =>
        this.familias.create({ nombre }),
      ),
    );
    const byName = Object.fromEntries(fam.map((f) => [f.nombre, f.id]));

    const plantas = await this.plantas.save([
      this.plantas.create({
        nombreCientifico: 'Polylepis besseri',
        nombreComun: 'Queñua',
        ecorregion: 'Altiplano y valles altoandinos',
        altitudMin: 2800,
        altitudMax: 4500,
        estadoConservacion: EstadoConservacion.VULNERABLE,
        descripcion: 'Árbol de corteza laminada que forma bosques de altura.',
        familiaId: byName['Rosaceae'],
      }),
      this.plantas.create({
        nombreCientifico: 'Puya raimondii',
        nombreComun: 'Titanka',
        ecorregion: 'Puna',
        altitudMin: 3200,
        altitudMax: 4800,
        estadoConservacion: EstadoConservacion.EN_PELIGRO,
        descripcion: 'Bromelia gigante que florece una sola vez al final de su vida.',
        familiaId: byName['Bromeliaceae'],
      }),
      this.plantas.create({
        nombreCientifico: 'Bertholletia excelsa',
        nombreComun: 'Castaña',
        ecorregion: 'Amazonía',
        altitudMin: 100,
        altitudMax: 400,
        estadoConservacion: EstadoConservacion.VULNERABLE,
        descripcion: 'Árbol emergente de la Amazonía, productor de la nuez de castaña.',
        familiaId: byName['Lecythidaceae'],
      }),
      this.plantas.create({
        nombreCientifico: 'Victoria amazonica',
        nombreComun: 'Victoria regia',
        ecorregion: 'Llanos de Moxos',
        altitudMin: 100,
        altitudMax: 300,
        estadoConservacion: EstadoConservacion.PREOCUPACION_MENOR,
        descripcion: 'Planta acuática de hojas circulares gigantes.',
        familiaId: byName['Nymphaeaceae'],
      }),
      this.plantas.create({
        nombreCientifico: 'Chenopodium quinoa',
        nombreComun: 'Quinua',
        ecorregion: 'Altiplano',
        altitudMin: 2500,
        altitudMax: 4000,
        estadoConservacion: EstadoConservacion.PREOCUPACION_MENOR,
        descripcion: 'Pseudocereal andino de alto valor nutricional.',
        familiaId: byName['Amaranthaceae'],
      }),
    ]);

    const p = Object.fromEntries(plantas.map((x) => [x.nombreCientifico, x.id]));
    await this.avistamientos.save([
      this.avistamientos.create({
        plantaId: p['Puya raimondii'],
        localidad: 'Cordillera del Tunari',
        departamento: Departamento.COCHABAMBA,
        latitud: -17.3,
        longitud: -66.2,
        fecha: '2026-03-14',
        observador: 'Equipo de campo UCB',
        notas: 'Ejemplares en floración, zona de pajonal.',
      }),
      this.avistamientos.create({
        plantaId: p['Bertholletia excelsa'],
        localidad: 'Riberalta',
        departamento: Departamento.BENI,
        latitud: -11.0,
        longitud: -66.1,
        fecha: '2026-05-02',
        observador: 'Equipo de campo UCB',
      }),
    ]);

    this.logger.log('Datos de ejemplo cargados (5 familias, 5 plantas, 2 avistamientos)');
  }
}
