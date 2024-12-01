'use client';

import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { HumanCharacteristics } from '@/types';

interface HumanCharacteristicsFormProps {
  onChange: (characteristics: HumanCharacteristics) => void;
  value: Partial<HumanCharacteristics>;
}

export function HumanCharacteristicsForm({ onChange, value }: HumanCharacteristicsFormProps) {
  const handleChange = (field: keyof HumanCharacteristics, fieldValue: string | number) => {
    onChange({
      ...value as HumanCharacteristics,
      [field]: fieldValue,
    });
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="age">Age</Label>
          <Input
            id="age"
            type="number"
            min={0}
            max={100}
            value={value.age || ''}
            onChange={(e) => handleChange('age', parseInt(e.target.value))}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="gender">Gender</Label>
          <Select
            value={value.gender}
            onValueChange={(v) => handleChange('gender', v)}
          >
            <SelectTrigger id="gender">
              <SelectValue placeholder="Select gender" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="male">Male</SelectItem>
              <SelectItem value="female">Female</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="eyeColor">Eye Color</Label>
          <Select
            value={value.eyeColor}
            onValueChange={(v) => handleChange('eyeColor', v)}
          >
            <SelectTrigger id="eyeColor">
              <SelectValue placeholder="Select eye color" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="brown">Brown</SelectItem>
              <SelectItem value="blue">Blue</SelectItem>
              <SelectItem value="green">Green</SelectItem>
              <SelectItem value="hazel">Hazel</SelectItem>
              <SelectItem value="gray">Gray</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="bodyType">Body Type</Label>
          <Select
            value={value.bodyType}
            onValueChange={(v) => handleChange('bodyType', v)}
          >
            <SelectTrigger id="bodyType">
              <SelectValue placeholder="Select body type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="slim">Slim</SelectItem>
              <SelectItem value="athletic">Athletic</SelectItem>
              <SelectItem value="average">Average</SelectItem>
              <SelectItem value="curvy">Curvy</SelectItem>
              <SelectItem value="muscular">Muscular</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="ethnicity">Ethnicity</Label>
          <Select
            value={value.ethnicity}
            onValueChange={(v) => handleChange('ethnicity', v)}
          >
            <SelectTrigger id="ethnicity">
              <SelectValue placeholder="Select ethnicity" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="asian">Asian</SelectItem>
              <SelectItem value="black">Black</SelectItem>
              <SelectItem value="hispanic">Hispanic</SelectItem>
              <SelectItem value="white">White</SelectItem>
              <SelectItem value="middleEastern">Middle Eastern</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
}