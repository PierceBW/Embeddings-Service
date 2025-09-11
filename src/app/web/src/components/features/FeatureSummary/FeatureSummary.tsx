import React from 'react';
import { FEATURE_GROUPS } from '../../../constants/featureGroups';
import FeatureRow from '../../ui/FeatureRow';

interface Props {
  features: Record<string, unknown>;
}

export default function FeatureSummary({ features }: Props) {
  return (
    <div className="space-y-6">
      {FEATURE_GROUPS.map((group) => {
        const items = group.items.filter((it) => features.hasOwnProperty(it.id));
        if (items.length === 0) return null;
        return (
          <div key={group.title} className="mb-4">
            <h4 className="text-base md:text-lg font-semibold text-slate-800 mb-0">{group.title}</h4>
            <div className="grid grid-cols-2 md:grid-cols-2 gap-x-12 gap-y-0">
              {items.map((it) => (
                <FeatureRow key={it.id} label={it.label ?? it.id} value={String(features[it.id] as any)} />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}


