'use client';

import { useState } from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Eye, EyeOff, ChevronDown, ChevronUp, HelpCircle } from 'lucide-react';
import { TrainingSettings as Settings, OptimizerType } from '@/types';
import { Card } from '@/components/ui/card';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface TrainingSettingsProps {
  onSettingsChange: (settings: Partial<Settings>) => void;
}

const defaultSettings: Settings = {
  replicateUsername: '',
  replicateApiKey: '',
  xaiApiKey: '',
  autoCaptioning: false,
  steps: 1000,
  loraRank: 16,
  hfRepoId: '',
  hfToken: '',
  learningRate: 0.0004,
  batchSize: 1,
  resolution: '512,768,1024',
  captionDropoutRate: 0.05,
  optimizer: 'adamw8bit',
};

export function TrainingSettings({ onSettingsChange }: TrainingSettingsProps) {
  const [settings, setSettings] = useState<Settings>(defaultSettings);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showReplicateKey, setShowReplicateKey] = useState(false);
  const [showXaiKey, setShowXaiKey] = useState(false);

  const handleChange = <K extends keyof Settings>(key: K, value: Settings[K]) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    onSettingsChange(newSettings);
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="replicateUsername">Replicate Username</Label>
          <Input
            id="replicateUsername"
            value={settings.replicateUsername}
            onChange={(e) => handleChange('replicateUsername', e.target.value)}
            placeholder="Enter your Replicate username"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="replicateApiKey">Replicate API Key</Label>
          <div className="relative">
            <Input
              id="replicateApiKey"
              type={showReplicateKey ? 'text' : 'password'}
              value={settings.replicateApiKey}
              onChange={(e) => handleChange('replicateApiKey', e.target.value)}
              placeholder="Enter your Replicate API key"
            />
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-2 top-1/2 -translate-y-1/2"
              onClick={() => setShowReplicateKey(!showReplicateKey)}
            >
              {showReplicateKey ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <Label htmlFor="xaiApiKey">xAI API Key</Label>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" className="h-4 w-4 p-0">
                  <HelpCircle className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                If you want to skip detailed description using xAI API, then leave the field empty and enable the Auto Captioning below
              </TooltipContent>
            </Tooltip>
          </div>
          <div className="relative">
            <Input
              id="xaiApiKey"
              type={showXaiKey ? 'text' : 'password'}
              value={settings.xaiApiKey}
              onChange={(e) => handleChange('xaiApiKey', e.target.value)}
              placeholder="Enter your xAI API key"
            />
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-2 top-1/2 -translate-y-1/2"
              onClick={() => setShowXaiKey(!showXaiKey)}
            >
              {showXaiKey ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <Label htmlFor="autoCaptioning">Auto Captioning</Label>
          <Switch
            id="autoCaptioning"
            checked={settings.autoCaptioning}
            onCheckedChange={(checked) => handleChange('autoCaptioning', checked)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="steps">Steps</Label>
          <Input
            id="steps"
            type="number"
            min={1}
            value={settings.steps}
            onChange={(e) => handleChange('steps', parseInt(e.target.value))}
          />
        </div>

        <Button
          variant="outline"
          className="w-full"
          onClick={() => setShowAdvanced(!showAdvanced)}
        >
          {showAdvanced ? (
            <>
              <ChevronUp className="mr-2 h-4 w-4" />
              Hide Advanced Options
            </>
          ) : (
            <>
              <ChevronDown className="mr-2 h-4 w-4" />
              Show Advanced Options
            </>
          )}
        </Button>

        {showAdvanced && (
          <Card className="p-4 space-y-4">
            <div className="space-y-2">
              <Label htmlFor="loraRank">LoRA Rank</Label>
              <Input
                id="loraRank"
                type="number"
                min={1}
                value={settings.loraRank}
                onChange={(e) => handleChange('loraRank', parseInt(e.target.value))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="hfRepoId">Hugging Face Repository ID</Label>
              <Input
                id="hfRepoId"
                value={settings.hfRepoId}
                onChange={(e) => handleChange('hfRepoId', e.target.value)}
                placeholder="username/repository"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="hfToken">Hugging Face Token</Label>
              <Input
                id="hfToken"
                value={settings.hfToken}
                onChange={(e) => handleChange('hfToken', e.target.value)}
                placeholder="Enter your Hugging Face token"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="learningRate">Learning Rate</Label>
              <Input
                id="learningRate"
                type="number"
                step="0.0001"
                min="0"
                value={settings.learningRate}
                onChange={(e) => handleChange('learningRate', parseFloat(e.target.value))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="batchSize">Batch Size</Label>
              <Input
                id="batchSize"
                type="number"
                min={1}
                value={settings.batchSize}
                onChange={(e) => handleChange('batchSize', parseInt(e.target.value))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="resolution">Resolution</Label>
              <Input
                id="resolution"
                value={settings.resolution}
                onChange={(e) => handleChange('resolution', e.target.value)}
                placeholder="512,768,1024"
              />
              <p className="text-sm text-muted-foreground">
                Comma-separated list of resolutions (e.g., 512,768,1024)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="captionDropoutRate">Caption Dropout Rate</Label>
              <Input
                id="captionDropoutRate"
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={settings.captionDropoutRate}
                onChange={(e) => handleChange('captionDropoutRate', parseFloat(e.target.value))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="optimizer">Optimizer</Label>
              <Select
                value={settings.optimizer}
                onValueChange={(value) => handleChange('optimizer', value as OptimizerType)}
              >
                <SelectTrigger id="optimizer">
                  <SelectValue placeholder="Select optimizer" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="adamw8bit">AdamW 8-bit</SelectItem>
                  <SelectItem value="prodigy">Prodigy</SelectItem>
                  <SelectItem value="adam8bit">Adam 8-bit</SelectItem>
                  <SelectItem value="lion8bit">Lion 8-bit</SelectItem>
                  <SelectItem value="adam">Adam</SelectItem>
                  <SelectItem value="adamw">AdamW</SelectItem>
                  <SelectItem value="lion">Lion</SelectItem>
                  <SelectItem value="adagrad">Adagrad</SelectItem>
                  <SelectItem value="adafactor">Adafactor</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}