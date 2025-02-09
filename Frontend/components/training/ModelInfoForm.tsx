'use client';

import { useState, useCallback, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { ImageGuidelines } from './ImageGuidelines';
import { ModelInfo, ModelType, TrainingStatus, ModelCharacteristics, TrainingSettings, HumanCharacteristics, PetCharacteristics, ItemCharacteristics } from '@/types';
import { HelpCircle, ImageIcon, Play, Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { HumanCharacteristicsForm } from './characteristics/HumanCharacteristics';
import { PetCharacteristicsForm } from './characteristics/PetCharacteristics';
import { ItemCharacteristicsForm } from './characteristics/ItemCharacteristics';
import { TrainingStatusPanel } from './TrainingStatus';
import { startTraining } from '@/lib/api/training';
import { useToast } from '@/hooks/use-toast';
import { useDropzone } from 'react-dropzone';
import { Card } from '@/components/ui/card';

interface ModelInfoFormProps {
  onInfoChange: (info: Partial<ModelInfo>) => void;
  trainingSettings: Partial<TrainingSettings>;
  modelInfo: Partial<ModelInfo>;
}

export function ModelInfoForm({ onInfoChange, trainingSettings, modelInfo }: ModelInfoFormProps) {
  const { toast } = useToast();
  const [modelType, setModelType] = useState<ModelType>(modelInfo.type || 'human');
  const [imageLocation, setImageLocation] = useState<string>('');
  const [zipFile, setZipFile] = useState<File | null>(null);
  const [showGuidelines, setShowGuidelines] = useState(false);
  const [hasAcceptedGuidelines, setHasAcceptedGuidelines] = useState(false);
  const [characteristics, setCharacteristics] = useState<Partial<ModelCharacteristics>>(modelInfo.characteristics || {});
  const [trainingStatus, setTrainingStatus] = useState<TrainingStatus>({
    status: 'idle',
  });
  const [isLoading, setIsLoading] = useState(false);

  // Set initial model type in parent state
  useEffect(() => {
    if (!modelInfo.type) {
      onInfoChange({ ...modelInfo, type: modelType });
    }
  }, []);

  useEffect(() => {
    setModelType(modelInfo.type || 'human');
    setCharacteristics(modelInfo.characteristics || {});
  }, [modelInfo]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setZipFile(file);
      setImageLocation(file.name);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/zip': ['.zip'],
    },
    multiple: false
  });

  const handleStartTraining = async () => {
    console.log('Button clicked - handleStartTraining called');
    console.log('Current state:', {
      modelInfo,
      trainingSettings,
      imageLocation,
      zipFile,
      characteristics
    });
    
    // Validate model info
    if (!modelInfo.name) {
      console.log('Validation failed: No model name');
      toast({
        title: 'Error',
        description: 'Please enter a model name',
        variant: 'destructive',
      });
      return;
    }

    if (!modelInfo.type) {
      console.log('Validation failed: No model type');
      toast({
        title: 'Error',
        description: 'Please select a model type',
        variant: 'destructive',
      });
      return;
    }

    if (!modelInfo.characteristics || Object.keys(modelInfo.characteristics).length === 0) {
      console.log('Validation failed: No characteristics', modelInfo.characteristics);
      toast({
        title: 'Error',
        description: 'Please fill in the characteristics',
        variant: 'destructive',
      });
      return;
    }

    if (!zipFile) {
      console.log('Validation failed: No ZIP file');
      toast({
        title: 'Error',
        description: 'Please select a ZIP file',
        variant: 'destructive',
      });
      return;
    }

    // Create FormData to send the file
    const formData = new FormData();
    formData.append('file', zipFile);

    // First upload the file
    try {
      const uploadResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
        throw new Error('Failed to upload file');
      }

      const { filePath } = await uploadResponse.json();

      // Now start the training with the server-side file path
      const characteristicsString = Object.entries(modelInfo.characteristics)
        .map(([key, value]) => `${key}: ${value}`)
        .join(', ');

      const response = await startTraining({
        modelInfo: {
          ...(modelInfo as ModelInfo),
          characteristics: characteristicsString as unknown as ModelCharacteristics,
        },
        settings: trainingSettings as TrainingSettings,
        imageLocation: filePath, // Use the server-side file path
      });

      console.log('Training response:', response);

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
        description: error instanceof Error ? error.message : 'Failed to start training. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleTypeChange = (type: ModelType) => {
    setModelType(type);
    setCharacteristics({});
    // Update parent state with new type and reset characteristics
    onInfoChange({
      ...modelInfo,
      type,
      characteristics: {} as ModelCharacteristics
    });
  };

  const handleCharacteristicsChange = (newCharacteristics: ModelCharacteristics) => {
    setCharacteristics(newCharacteristics);
    // Update parent state with new characteristics while preserving type
    onInfoChange({
      ...modelInfo,
      characteristics: newCharacteristics
    });
  };

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="name">Model Name</Label>
        <Input
          id="name"
          placeholder="Enter model name"
          value={modelInfo.name || ''}
          onChange={(e) => onInfoChange({ ...modelInfo, name: e.target.value })}
        />
      </div>

      <div className="space-y-2">
        <Label>Model Type</Label>
        <RadioGroup
          value={modelType}
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
            value={characteristics as Partial<HumanCharacteristics>}
          />
        )}
        {modelType === 'pet' && (
          <PetCharacteristicsForm
            onChange={handleCharacteristicsChange}
            value={characteristics as Partial<PetCharacteristics>}
          />
        )}
        {modelType === 'item' && (
          <ItemCharacteristicsForm
            onChange={handleCharacteristicsChange}
            value={characteristics as Partial<ItemCharacteristics>}
          />
        )}
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Label>Training Images</Label>
          {hasAcceptedGuidelines && (
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

        {!hasAcceptedGuidelines ? (
          <Button
            variant="outline"
            className="w-full"
            onClick={() => setShowGuidelines(true)}
          >
            <ImageIcon className="mr-2 h-4 w-4" />
            View Image Guidelines
          </Button>
        ) : (
          <>
            <Card
              {...getRootProps()}
              className="border-2 border-dashed p-8 text-center cursor-pointer hover:border-primary transition-colors"
            >
              <input {...getInputProps()} />
              <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              {isDragActive ? (
                <p className="text-sm text-muted-foreground">Drop the ZIP file here...</p>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Drag & drop your ZIP file here, or click to select
                </p>
              )}
            </Card>

            {zipFile && (
              <Card className="p-3 flex items-center space-x-2">
                <ImageIcon className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm truncate">{zipFile.name}</span>
              </Card>
            )}
          </>
        )}

        <ImageGuidelines 
          open={showGuidelines}
          onOpenChange={setShowGuidelines}
          onAccept={() => {
            setShowGuidelines(false);
            setHasAcceptedGuidelines(true);
          }}
        />
      </div>

      <div className="space-y-4">
        {hasAcceptedGuidelines && (
          <>
            <Button
              className="w-full"
              onClick={handleStartTraining}
              disabled={isLoading || trainingStatus.status === 'training' || !zipFile}
            >
              <Play className="mr-2 h-4 w-4" />
              {isLoading ? 'Starting Training...' : 'Start Training'}
            </Button>

            <TrainingStatusPanel status={trainingStatus} />
          </>
        )}
      </div>
    </div>
  );
}