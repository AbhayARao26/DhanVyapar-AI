
export type UserRole = 'lender' | 'borrower';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string;
}

export interface LoanApplication {
  id: string;
  borrowerId: string;
  borrowerName: string;
  amount: number;
  purpose: string;
  term: number; // in months
  interestRate: number;
  status: 'pending' | 'approved' | 'rejected' | 'disbursed';
  creditScore: number;
  monthlyIncome: number;
  employmentType: string;
  appliedDate: string;
  documents: string[];
}

export interface CreditScore {
  score: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'E';
  factors: {
    paymentHistory: number;
    creditUtilization: number;
    creditHistory: number;
    creditMix: number;
    newCredit: number;
  };
}

export interface RepaymentSchedule {
  id: string;
  loanId: string;
  installmentNumber: number;
  dueDate: string;
  amount: number;
  principal: number;
  interest: number;
  status: 'paid' | 'pending' | 'overdue';
}

export interface DashboardStats {
  totalAmount: number;
  activeLoans: number;
  pendingApplications: number;
  defaultRate: number;
}

export interface Lender {
  id: string;
  name: string;
  type: 'bank' | 'nbfc' | 'cooperative' | 'microfinance';
  logo?: string;
  interestRate: number;
  minAmount: number;
  maxAmount: number;
  maxTerm: number; // in months
  processingFee: number;
  eligibilityCriteria: {
    minCreditScore: number;
    minMonthlyIncome: number;
    maxAge: number;
    employmentTypes: string[];
  };
  features: string[];
  rating: number;
  reviewCount: number;
  processingTime: string; // e.g., "2-3 days"
}

export interface LoanRecommendation {
  lender: Lender;
  matchScore: number;
  eligibilityStatus: 'eligible' | 'partially_eligible' | 'not_eligible';
  reasons: string[];
  estimatedEMI: number;
  totalInterest: number;
}
