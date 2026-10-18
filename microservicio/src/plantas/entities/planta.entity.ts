import {
  Column,
  Entity,
  JoinColumn,
  ManyToOne,
  OneToMany,
  PrimaryGeneratedColumn,
} from 'typeorm';
import { EstadoConservacion } from '../../common/enums';
import { Avistamiento } from '../../avistamientos/entities/avistamiento.entity';
import { Familia } from '../../familias/entities/familia.entity';

@Entity('plantas')
export class Planta {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ name: 'nombre_cientifico', length: 150, unique: true })
  nombreCientifico: string;

  @Column({ name: 'nombre_comun', length: 150, nullable: true })
  nombreComun?: string;

  @Column({ type: 'text', nullable: true })
  descripcion?: string;

  @Column({ length: 80, nullable: true })
  ecorregion?: string;

  @Column({ name: 'altitud_min', type: 'int', nullable: true })
  altitudMin?: number;

  @Column({ name: 'altitud_max', type: 'int', nullable: true })
  altitudMax?: number;

  @Column({
    name: 'estado_conservacion',
    type: 'enum',
    enum: EstadoConservacion,
    default: EstadoConservacion.PREOCUPACION_MENOR,
  })
  estadoConservacion: EstadoConservacion;

  @Column({ name: 'familia_id' })
  familiaId: number;

  @ManyToOne(() => Familia, (familia) => familia.plantas, {
    onDelete: 'RESTRICT',
    eager: true,
  })
  @JoinColumn({ name: 'familia_id' })
  familia?: Familia;

  @OneToMany(() => Avistamiento, (a) => a.planta)
  avistamientos?: Avistamiento[];
}
