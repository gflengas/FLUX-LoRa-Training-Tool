'use client';

import { UploadCloud, Image as ImageIcon } from 'lucide-react';
import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card } from '@/components/ui/card';

interface ImageUploadProps {
  onImagesSelected: (files: File[]) => void;
}

export function ImageUpload({ onImagesSelected }: ImageUploadProps) {
  const [files, setFiles] = useState<File[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(prev => [...prev, ...acceptedFiles]);
    onImagesSelected(acceptedFiles);
  }, [onImagesSelected]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg']
    },
    multiple: true
  });

  return (
    <div className="space-y-4">
      <Card
        {...getRootProps()}
        className="border-2 border-dashed p-8 text-center cursor-pointer hover:border-primary transition-colors"
      >
        <input {...getInputProps()} />
        <UploadCloud className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
        {isDragActive ? (
          <p className="text-sm text-muted-foreground">Drop the images here...</p>
        ) : (
          <p className="text-sm text-muted-foreground">
            Drag & drop images here, or click to select files
          </p>
        )}
      </Card>
      
      {files.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          {files.map((file, index) => (
            <Card key={index} className="p-3 flex items-center space-x-2">
              <ImageIcon className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm truncate">{file.name}</span>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}