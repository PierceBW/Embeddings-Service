export interface FeatureDiff { key: string; from: unknown; to: unknown; pctDiff?: number }

const IMPORTANT_KEYS = ['loan_amnt', 'int_rate', 'sub_grade', 'dti', 'mort_acc'];

export const diffFeatures = (
  anchor: Record<string, unknown>,
  neighbour: Record<string, unknown>
): FeatureDiff[] => {
  const arr: FeatureDiff[] = [];
  IMPORTANT_KEYS.forEach((k) => {
    const av = anchor[k];
    const nv = neighbour[k];
    if (av === undefined || nv === undefined) return;

    let pct: number | undefined = undefined;
    if (!isNaN(Number(av)) && !isNaN(Number(nv))) {
      const aNum = Number(av);
      const nNum = Number(nv);
      pct = aNum === 0 ? undefined : Math.abs((nNum - aNum) / aNum);
    }
    arr.push({ key: k, from: av, to: nv, pctDiff: pct });
  });
  return arr;
};
