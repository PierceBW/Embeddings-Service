export type FeatureGroup = {
  title: string;
  // Array of feature IDs as they appear in features_json. If an ID is absent in the payload, it is skipped.
  // Labels can optionally include a description in parentheses; the row component will render it on a second line.
  items: Array<{ id: string; label?: string }>;
};

// Hard-coded groups for the Summary view
export const FEATURE_GROUPS: FeatureGroup[] = [
  {
    title: 'Loan Details:',
    items: [
      { id: 'loan_amnt', label: 'Loan Amount' },
      { id: 'title', label: 'Loan Title' },
      { id: 'int_rate', label: 'Interest Rate' },
      { id: 'sub_grade', label: 'Loan Sub-grade' },
    ],
  },
  {
    title: 'Borrower Profile:',
    items: [
      { id: 'emp_title', label: 'Employment Title' },
      { id: 'emp_length', label: 'Employment Length' },
      { id: 'addr_state', label: 'State of Primary Residence' },
      { id: 'zip_code', label: 'Zip Code of Primary Residence' },
    ],
  },
  {
    title: 'Credit History:',
    items: [
      { id: 'dti', label: 'Debt-to-income Ratio' },
      { id: 'avg_cur_bal', label: 'Average Current Balance' },
      { id: 'mort_acc', label: 'Mortgage Accounts' },
      { id: 'earliest_cr_line', label: 'Earliest Credit Line' },
      { id: 'fico_range_high', label: 'FICO Range High (Upper bound of FICO score)' },
      { id: 'num_op_rev_tl', label: 'Number of Open Revolving Accounts (Credit cards, lines of credit, etc.)' },
      { id: 'revol_util', label: 'Revolving Line Utilization Rate (Percent of credit borrower is using relative to all available revolving credit)' }

    ],
  },
];


