import React from 'react';
import { Loader2 } from 'lucide-react';

export default function LoadingState({ message = 'Executing analytical query against MySQL...' }) {
  return (
    <div className="py-20 flex flex-col items-center justify-center text-center">
      <Loader2 className="w-8 h-8 text-brand-500 animate-spin mb-3" />
      <p className="text-sm font-medium text-slate-300">{message}</p>
      <p className="text-xs text-slate-500 mt-1">Retrieving verified SQL dataset</p>
    </div>
  );
}
