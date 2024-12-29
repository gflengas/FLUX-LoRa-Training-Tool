'use client';

import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { ImageUpload } from './ImageUpload';
import { ImageGuidelines } from './ImageGuidelines';
import { ModelInfo, ModelType, TrainingStatus, ModelCharacteristics, TrainingSettings } from '@/types';
import { HelpCircle, ImageIcon, Play } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { HumanCharacteristicsForm } from './characteristics/HumanCharacteristics';
import { PetCharacteristicsForm } from './characteristics/PetCharacteristics';
import { ItemCharacteristicsForm } from './characteristics/ItemCharacteristics';
import { TrainingStatusPanel } from './TrainingStatus';
import { startTraining } from '@/lib/api/training';
import { uploadImages } from '@/lib/api/upload';
import { useToast } from '@/hooks/use-toast';

interface ModelInfoFormProps {
  onInfoChange: (info: Partial<ModelInfo>) => void;
  trainingSettings: Partial<TrainingSettings>;
}

export function ModelInfoForm({ onInfoChange, trainingSettings }: ModelInfoFormProps) {
  const { toast } = useToast();
  const [modelInfo, setModelInfo] = useState<Partial<ModelInfo>>({});
  const [modelType, setModelType] = useState<ModelType>('human');
  const [isUploadEnabled, setIsUploadEnabled] = useState(false);
  const [showGuidelines, setShowGuidelines] = useState(false);
  const [characteristics, setCharacteristics] = useState<Partial<ModelCharacteristics>>({});
  const [trainingStatus, setTrainingStatus] = useState<TrainingStatus>({
    status: 'idle',
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleStartTraining = async () => {
    if (!modelInfo.images || modelInfo.images.length === 0) {
      toast({
        title: 'Error',
        description: 'Please upload at least one image',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    setTrainingStatus({ status: 'training' });

    try {
      // Upload images first
      const imageLocations = await uploadImages(modelInfo.images);

      // Start training process
      const response = await startTraining({
        modelInfo,
        settings: trainingSettings,
        imageLocations,
      });

      setTrainingStatus({
        status: 'training',
        replicateUrl: response.replicateUrl,
        modelDestination: response.modelDestination,
      });

      toast({
        title: 'Training Started',
        description: 'Your model training has begun successfully',
      });
    } catch (error) {
      console.error('Training error:', error);
      setTrainingStatus({
        status: 'failed',
        error: error instanceof Error ? error.message : 'Failed to start training',
      });

      toast({
        title: 'Error',
        description: 'Failed to start training. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
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
            disabled={isLoading || trainingStatus.status === 'training'}
          >
            <Play className="mr-2 h-4 w-4" />
            {isLoading ? 'Starting Training...' : 'Start Training'}
          </Button>

          <TrainingStatusPanel status={trainingStatus} />
        </div>
      )}
    </div>
  );
}