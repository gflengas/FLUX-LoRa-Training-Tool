'use client';

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ImageIcon, CheckCircle2 } from 'lucide-react';

interface ImageGuidelinesProps {
  onAccept: () => void;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ImageGuidelines({ onAccept, open, onOpenChange }: ImageGuidelinesProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Image Guidelines for Best Results</DialogTitle>
          <DialogDescription>
            Please read these guidelines carefully to ensure optimal training results
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="h-[400px] pr-4">
          <div className="space-y-6">
            <section className="space-y-3">
              <h3 className="font-semibold">Image Quality Requirements</h3>
              <ul className="list-disc pl-6 space-y-2 text-sm">
                <li>High-resolution images (minimum 512x512 pixels)</li>
                <li>Clear, well-lit subjects with minimal blur</li>
                <li>Consistent lighting conditions across images</li>
                <li>Sharp focus on the main subject</li>
              </ul>
            </section>

            <section className="space-y-3">
              <h3 className="font-semibold">Subject Guidelines</h3>
              <ul className="list-disc pl-6 space-y-2 text-sm">
                <li>Include various angles and poses</li>
                <li>Maintain consistent subject distance</li>
                <li>Avoid busy or distracting backgrounds</li>
                <li>Include 20-30 images for optimal results</li>
              </ul>
            </section>

            <section className="space-y-3">
              <h3 className="font-semibold">Technical Specifications</h3>
              <ul className="list-disc pl-6 space-y-2 text-sm">
                <li>Supported formats: JPG, PNG</li>
                <li>Maximum file size: 10MB per image</li>
                <li>Recommended aspect ratio: 1:1 (square)</li>
                <li>Color space: RGB</li>
              </ul>
            </section>

            <section className="space-y-3">
              <h3 className="font-semibold">Best Practices</h3>
              <ul className="list-disc pl-6 space-y-2 text-sm">
                <li>Remove any watermarks or text overlays</li>
                <li>Ensure consistent image style</li>
                <li>Avoid heavily edited or filtered images</li>
                <li>Include natural variations in lighting and background</li>
              </ul>
            </section>
          </div>
        </ScrollArea>

        <DialogFooter>
          <Button onClick={onAccept} className="w-full">
            <CheckCircle2 className="mr-2 h-4 w-4" />
            I have read the guidelines and want to proceed
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}