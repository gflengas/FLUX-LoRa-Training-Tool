'use client';

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ModelInfoForm } from '@/components/training/ModelInfoForm';
import { TrainingSettings } from '@/components/training/TrainingSettings';
import { ModelInfo, TrainingSettings as Settings } from '@/types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Brain, Settings2 } from 'lucide-react';

export default function Home() {
  const [modelInfo, setModelInfo] = useState<Partial<ModelInfo>>({});
  const [trainingSettings, setTrainingSettings] = useState<Partial<Settings>>({});

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8 text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">LoRA Model Training</h1>
          <p className="text-muted-foreground">
            Create custom LoRA models with your own dataset
          </p>
        </div>
        
        <Tabs defaultValue="info" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="info" className="space-x-2">
              <Brain className="h-4 w-4" />
              <span>Model Information</span>
            </TabsTrigger>
            <TabsTrigger value="settings" className="space-x-2">
              <Settings2 className="h-4 w-4" />
              <span>Training Settings</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="info">
            <Card>
              <CardHeader>
                <CardTitle>Model Information</CardTitle>
                <CardDescription>
                  Define your model details and upload training images
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ModelInfoForm
                  onInfoChange={(info) => setModelInfo({ ...modelInfo, ...info })}
                  trainingSettings={trainingSettings}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle>Training Settings</CardTitle>
                <CardDescription>
                  Configure the parameters for your training process
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TrainingSettings
                  onSettingsChange={(settings) =>
                    setTrainingSettings({ ...trainingSettings, ...settings })
                  }
                />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}