'use client';

import { TrainingStatus as Status } from '@/types';
import { Card } from '@/components/ui/card';
import { AlertCircle, ExternalLink, Activity, Hash, Link2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

interface TrainingStatusProps {
  status: Status;
}

function truncateUrl(url: string) {
  return url.replace(/^https?:\/\//, '').replace(/\/$/, '');
}

export function TrainingStatusPanel({ status }: TrainingStatusProps) {
  if (status.status === 'idle') return null;

  return (
    <Card className="p-4">
      <div className="space-y-3 text-sm">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-muted-foreground" />
          <span className="font-medium">Status:</span>
          <span className="capitalize">{status.status}</span>
        </div>

        {status.trainingId && (
          <div className="flex items-center gap-2">
            <Hash className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium">Training ID:</span>
            <code className="px-2 py-1 bg-muted rounded font-mono text-xs">
              {status.trainingId}
            </code>
          </div>
        )}

        {status.modelUrl && (
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <Link2 className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">Model:</span>
              <Button 
                variant="link" 
                className="h-auto p-0 text-xs font-normal"
                onClick={() => window.open(status.modelUrl, '_blank')}
              >
                View Model Page
                <ExternalLink className="ml-1 h-3 w-3" />
              </Button>
            </div>
            <div className="pl-6 text-xs text-muted-foreground font-mono">
              {truncateUrl(status.modelUrl)}
            </div>
          </div>
        )}

        {status.replicateUrl && (
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">Training:</span>
              <Button 
                variant="link" 
                className="h-auto p-0 text-xs font-normal"
                onClick={() => window.open(status.replicateUrl, '_blank')}
              >
                View Progress
                <ExternalLink className="ml-1 h-3 w-3" />
              </Button>
            </div>
            <div className="pl-6 text-xs text-muted-foreground font-mono">
              {truncateUrl(status.replicateUrl)}
            </div>
          </div>
        )}
      </div>

      {status.error && (
        <Alert variant="destructive" className="mt-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{status.error}</AlertDescription>
        </Alert>
      )}
    </Card>
  );
}