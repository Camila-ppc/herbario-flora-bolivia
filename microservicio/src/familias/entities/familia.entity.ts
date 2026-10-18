import { Column, Entity, OneToMany, PrimaryGeneratedColumn } from 'typeorm';
import { Planta } from '../../plantas/entities/planta.entity';

@Entity('familias')
export class Familia {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ length: 100, unique: true })
  nombre: string;

  @Column({ type: 'text', nullable: true })
  descripcion?: string;

  @OneToMany(() => Planta, (planta) => planta.familia)
  plantas?: Planta[];
}
