'use client';

import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { PetCharacteristics } from '@/types';

interface PetCharacteristicsFormProps {
  onChange: (characteristics: PetCharacteristics) => void;
  value: Partial<PetCharacteristics>;
}

export function PetCharacteristicsForm({ onChange, value }: PetCharacteristicsFormProps) {
  const handleChange = (field: keyof PetCharacteristics, fieldValue: string) => {
    onChange({
      ...value as PetCharacteristics,
      [field]: fieldValue,
    });
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="species">Species</Label>
          <Input
            id="species"
            placeholder="e.g., Dog, Cat, Bird"
            value={value.species || ''}
            onChange={(e) => handleChange('species', e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="color">Color</Label>
          <Input
            id="color"
            placeholder="e.g., Brown, Black & White"
            value={value.color || ''}
            onChange={(e) => handleChange('color', e.target.value)}
          />
        </div>

        <div className="space-y-2 col-span-2">
          <Label htmlFor="distinctiveTrait">Distinctive Trait</Label>
          <Input
            id="distinctiveTrait"
            placeholder="e.g., Long fur, Spotted coat"
            value={value.distinctiveTrait || ''}
            onChange={(e) => handleChange('distinctiveTrait', e.target.value)}
          />
        </div>
      </div>
    </div>
  );
}