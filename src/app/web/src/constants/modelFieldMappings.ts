export interface FieldConfig {
  label: string;
  type?: 'text' | 'number' | 'select';
}

/**
 * Mapping of active_model identifier (as returned by /metadata) ->
 * mapping of raw feature key -> FieldConfig used by the UI.
 */
export const MODEL_FIELD_MAPPINGS: Record<string, Record<string, FieldConfig>> = {
  value_attrition_cnn: {
    satisfaction_level: { label: 'Satisfaction Level', type: 'number' },
    last_evaluation: { label: 'Last Evaluation Score', type: 'number' },
    number_project: { label: 'Projects Completed', type: 'number' },
    average_montly_hours: { label: 'Avg Monthly Hours', type: 'number' },
    time_spend_company: { label: 'Years at Company', type: 'number' },
    Work_accident: { label: 'Work Accident (0/1)', type: 'number' },
    promotion_last_5years: { label: 'Promoted in Last 5 Years', type: 'number' },
    sales: { label: 'Department', type: 'text' },
    salary: { label: 'Salary Tier', type: 'text' },
  },
  hybrid_risk_mlp: {
    addr_state: { label: 'State of Primary Residence', type: 'text' },
    earliest_cr_line: { label: "Date of Earliest Reported Credit", type: 'text' },
    emp_length: { label: 'Employment Length (where 0 means less than 1 year and 10 means 10 or more years)', type: 'text' },
    emp_title: { label: 'Employee Title', type: 'text' },
    sub_grade: { label: 'Loan Sub Grade', type: 'text' },
    title: { label: 'Loan Title (Purpose of loan)', type: 'text' },
    zip_code: { label: 'Zip Code of primary Residence', type: 'text' },
    avg_cur_bal: { label: 'Average Current Balance (of all Accounts)', type: 'number' },
    dti: { label: 'Debt-to-Income Ratio', type: 'number' },
    fico_range_high: { label: "Upper boundary of the borrower’s FICO at loan origination", type: 'number' },
    int_rate: { label: 'Interest Rate', type: 'number' },
    loan_amnt: { label: 'Loan Amount', type: 'number' },
    mort_acc: { label: 'Number of Mortgage Accounts', type: 'number' },
    num_op_rev_tl: { label: 'Number of Open Revolving Accounts', type: 'number' },
    revol_util: { label: 'Revolving Line Utilization Rate (the amount of credit the borrower is using relative to all available revolving credit)', type: 'number' },
  },
};