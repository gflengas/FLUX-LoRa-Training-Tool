'use client';

import { TrainingStatus as Status } from '@/types';
import { Card } from '@/components/ui/card';
import { AlertCircle, ExternalLink } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

interface TrainingStatusProps {
  status: Status;
}

export function TrainingStatusPanel({ status }: TrainingStatusProps) {
  if (status.status === 'idle') return null;

  return (
    <Card className="p-4 space-y-4">
      {status.replicateUrl && (
        <div className="space-y-2">
          <div className="text-sm font-medium">Training Progress</div>
          <Button
            variant="outline"
            className="w-full"
            onClick={() => window.open(status.replicateUrl, '_blank')}
          >
            <ExternalLink className="mr-2 h-4 w-4" />
            View on Replicate
          </Button>
        </div>
      )}

      {status.modelDestination && (
        <div className="space-y-2">
          <div className="text-sm font-medium">Model Destination</div>
          <div className="text-sm p-2 bg-muted rounded-md font-mono break-all">
            {status.modelDestination}
          </div>
        </div>
      )}

      {status.error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{status.error}</AlertDescription>
        </Alert>
      )}
    </Card>
  );
}