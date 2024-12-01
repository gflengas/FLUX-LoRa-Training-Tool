'use client';

import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { ItemCharacteristics } from '@/types';

interface ItemCharacteristicsFormProps {
  onChange: (characteristics: ItemCharacteristics) => void;
  value: Partial<ItemCharacteristics>;
}

export function ItemCharacteristicsForm({ onChange, value }: ItemCharacteristicsFormProps) {
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="purpose">Purpose</Label>
        <Input
          id="purpose"
          placeholder="e.g., Furniture, Tool, Decoration"
          value={value.purpose || ''}
          onChange={(e) => onChange({ purpose: e.target.value })}
        />
      </div>
    </div>
  );
}