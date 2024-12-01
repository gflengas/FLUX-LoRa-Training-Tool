'use client';

import { Brain } from 'lucide-react';
import { ThemeToggle } from '@/components/theme/ThemeToggle';

export function Header() {
  return (
    <header className="border-b">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Brain className="h-6 w-6" />
          <span className="font-bold text-lg">LoRA Trainer</span>
        </div>
        <ThemeToggle />
      </div>
    </header>
  );
}