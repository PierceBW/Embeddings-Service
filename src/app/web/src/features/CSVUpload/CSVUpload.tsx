import React, { useState } from 'react';
import Papa, { ParseResult } from 'papaparse';
import { Button } from '../../components/ui';
import { useBatchPredict } from '../../hooks/useBatchPredict';
import { MODEL_FIELD_MAPPINGS } from '../../constants/modelFieldMappings';
import { useMetadata } from '../../hooks/useMetadata';

export default function CSVUpload({ onComplete }: { onComplete?: () => void }) {
  const [rows, setRows] = useState<Record<string, string | number | boolean>[]>([]);
  const [error, setError] = useState<string | null>(null);
  const batchMutation = useBatchPredict();
  const { data: metadata } = useMetadata();

  const handleFile = (file: File) => {
    setError(null);
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (res: ParseResult<Record<string, string | number>>) => {
        if (res.errors.length) {
          setError('CSV parse error');
          return;
        }
        const cleaned = res.data.map((row: Record<string, string | number>) => {
          const obj: Record<string, string | number | boolean> = {};
          Object.entries(row).forEach(([k, v]) => {
            obj[k] = v as string | number | boolean;
          });
          return obj;
        });
        setRows(cleaned);
      },
    });
  };

  const missingColumns = () => {
    if (!metadata || !rows.length) return [];
    const cols = Object.keys(rows[0]);
    return metadata.feature_order.filter((f) => !cols.includes(f));
  };

  return (
    <div className="bg-white shadow rounded p-6 mt-6 max-w-3xl mx-auto">
      <input
        type="file"
        accept=".csv,text/csv"
        onChange={(e) => e.target.files && handleFile(e.target.files[0])}
      />

      {error && <p className="text-red-500 mt-2">{error}</p>}

      {rows.length > 0 && (
        <div className="mt-4">
          <p className="text-sm text-gray-700">Parsed {rows.length} rows.</p>
          {missingColumns().length > 0 ? (
            <p className="text-red-500 text-sm mt-1">
              Missing columns: {missingColumns().join(', ')}
            </p>
          ) : (
            <Button
              onClick={() => batchMutation.mutate(rows)}
              disabled={batchMutation.isPending}
            >
              {batchMutation.isPending ? 'Predicting…' : 'Submit Batch'}
            </Button>
          )}
        </div>
      )}

      {batchMutation.data && (
        <div className="mt-4">
          <h3 className="font-semibold mb-2">Batch Results</h3>
          <p className="text-sm text-gray-600">{batchMutation.data.length} predictions completed.</p>
          {onComplete && (
            <button className="mt-3 text-indigo-600 hover:underline text-sm" onClick={onComplete}>Close</button>
          )}
        </div>
      )}
    </div>
  );
} 