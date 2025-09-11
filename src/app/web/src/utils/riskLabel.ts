import { MetadataResponse } from '../hooks/useMetadata';

export const riskLabel = (level: number | undefined, meta?: MetadataResponse): string => {
  if (level === undefined) return '';
  if (!meta) return String(level);
  const found = meta.risk_categories.find((item) => item.code === level);
  return found ? found.default_name : String(level);
}; 