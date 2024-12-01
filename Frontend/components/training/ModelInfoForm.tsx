'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { ImageUpload } from './ImageUpload';
import { ImageGuidelines } from './ImageGuidelines';
import { ModelInfo, ModelType, TrainingStatus, ModelCharacteristics } from '@/types';
import { HelpCircle, ImageIcon, Play } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { HumanCharacteristicsForm } from './characteristics/HumanCharacteristics';
import { PetCharacteristicsForm } from './characteristics/PetCharacteristics';
import { ItemCharacteristicsForm } from './characteristics/ItemCharacteristics';
import { TrainingStatusPanel } from './TrainingStatus';

interface ModelInfoFormProps {
  onInfoChange: (info: Partial<ModelInfo>) => void;
}

export function ModelInfoForm({ onInfoChange }: ModelInfoFormProps) {
  const [modelType, setModelType] = useState<ModelType>('human');
  const [isUploadEnabled, setIsUploadEnabled] = useState(false);
  const [showGuidelines, setShowGuidelines] = useState(false);
  const [characteristics, setCharacteristics] = useState<Partial<ModelCharacteristics>>({});
  const [trainingStatus, setTrainingStatus] = useState<TrainingStatus>({
    status: 'idle',
  });

  const handleStartTraining = () => {
    // Simulate training start with Replicate URL and model destination
    setTrainingStatus({
      status: 'training',
      replicateUrl: 'https://replicate.com/training/abc123',
      modelDestination: '/models/custom-lora-v1',
    });
  };

  const handleTypeChange = (type: ModelType) => {
    setModelType(type);
    setCharacteristics({});
    onInfoChange({ type, characteristics: {} as ModelCharacteristics });
  };

  const handleCharacteristicsChange = (newCharacteristics: ModelCharacteristics) => {
    setCharacteristics(newCharacteristics);
    onInfoChange({ characteristics: newCharacteristics });
  };

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="name">Model Name</Label>
        <Input
          id="name"
          placeholder="Enter model name"
          onChange={(e) => onInfoChange({ name: e.target.value })}
        />
      </div>

      <div className="space-y-2">
        <Label>Model Type</Label>
        <RadioGroup
          defaultValue="human"
          onValueChange={(value) => handleTypeChange(value as ModelType)}
        >
          <div className="flex space-x-4">
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="human" id="human" />
              <Label htmlFor="human">Human</Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="item" id="item" />
              <Label htmlFor="item">Item</Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="pet" id="pet" />
              <Label htmlFor="pet">Pet</Label>
            </div>
          </div>
        </RadioGroup>
      </div>

      <div className="space-y-4">
        <Label>Characteristics</Label>
        {modelType === 'human' && (
          <HumanCharacteristicsForm
            onChange={handleCharacteristicsChange}
            value={characteristics}
          />
        )}
        {modelType === 'pet' && (
          <PetCharacteristicsForm
            onChange={handleCharacteristicsChange}
            value={characteristics}
          />
        )}
        {modelType === 'item' && (
          <ItemCharacteristicsForm
            onChange={handleCharacteristicsChange}
            value={characteristics}
          />
        )}
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Label>Training Images</Label>
          {isUploadEnabled && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowGuidelines(true)}
                >
                  <HelpCircle className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>View image guidelines</TooltipContent>
            </Tooltip>
          )}
        </div>
        
        {!isUploadEnabled ? (
          <>
            <Button
              variant="outline"
              className="w-full"
              onClick={() => setShowGuidelines(true)}
            >
              <ImageIcon className="mr-2 h-4 w-4" />
              View Image Guidelines
            </Button>
            <ImageGuidelines 
              open={showGuidelines}
              onOpenChange={setShowGuidelines}
              onAccept={() => {
                setIsUploadEnabled(true);
                setShowGuidelines(false);
              }}
            />
          </>
        ) : (
          <>
            <ImageGuidelines 
              open={showGuidelines}
              onOpenChange={setShowGuidelines}
              onAccept={() => setShowGuidelines(false)}
            />
            <ImageUpload
              onImagesSelected={(files) => onInfoChange({ images: files })}
            />
          </>
        )}
      </div>

      {isUploadEnabled && (
        <div className="space-y-4">
          <Button
            className="w-full"
            onClick={handleStartTraining}
            disabled={trainingStatus.status === 'training'}
          >
            <Play className="mr-2 h-4 w-4" />
            Start Training
          </Button>

          <TrainingStatusPanel status={trainingStatus} />
        </div>
      )}
    </div>
  );
}