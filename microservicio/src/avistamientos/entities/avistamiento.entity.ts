import { Column, Entity, JoinColumn, ManyToOne, PrimaryGeneratedColumn } from 'typeorm';
import { Departamento } from '../../common/enums';
import { Planta } from '../../plantas/entities/planta.entity';

@Entity('avistamientos')
export class Avistamiento {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ name: 'planta_id' })
  plantaId: number;

  @ManyToOne(() => Planta, (planta) => planta.avistamientos, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'planta_id' })
  planta?: Planta;

  @Column({ length: 150 })
  localidad: string;

  @Column({ type: 'enum', enum: Departamento })
  departamento: Departamento;

  @Column({ type: 'double precision', nullable: true })
  latitud?: number;

  @Column({ type: 'double precision', nullable: true })
  longitud?: number;

  /** Fecha del avistamiento, formato YYYY-MM-DD */
  @Column({ type: 'date' })
  fecha: string;

  @Column({ length: 120 })
  observador: string;

  @Column({ type: 'text', nullable: true })
  notas?: string;
}
