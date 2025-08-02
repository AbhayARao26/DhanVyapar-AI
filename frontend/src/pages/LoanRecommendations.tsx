import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useNavigate, useLocation } from 'react-router-dom';
import Layout from '../components/common/Layout';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { LoanRecommendation, LoanApplication } from '../types';
import { 
  Building2, 
  Star, 
  Clock, 
  IndianRupee, 
  TrendingUp, 
  CheckCircle, 
  AlertCircle, 
  XCircle,
  ArrowLeft,
  Calculator,
  FileText
} from 'lucide-react';
import { toast } from 'sonner';

const LoanRecommendations: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [recommendations, setRecommendations] = useState<LoanRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'eligible' | 'top_rated'>('all');

  // Get loan application data from navigation state
  const loanApplication = location.state?.loanApplication as LoanApplication;

  useEffect(() => {
    if (!loanApplication) {
      navigate('/borrowers/dashboard');
      return;
    }

    // Simulate API call to get loan recommendations
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Mock loan recommendations data
        const mockRecommendations: LoanRecommendation[] = [
          {
            lender: {
              id: '1',
              name: 'State Bank of India',
              type: 'bank',
              logo: '🏦',
              interestRate: 8.5,
              minAmount: 50000,
              maxAmount: 1000000,
              maxTerm: 60,
              processingFee: 1.5,
              eligibilityCriteria: {
                minCreditScore: 650,
                minMonthlyIncome: 25000,
                maxAge: 65,
                employmentTypes: ['salaried', 'self-employed']
              },
              features: ['Flexible EMI', 'Quick Approval', 'No Prepayment Charges'],
              rating: 4.2,
              reviewCount: 1250,
              processingTime: '3-5 days'
            },
            matchScore: 92,
            eligibilityStatus: 'eligible',
            reasons: ['Credit score matches requirement', 'Income sufficient', 'Loan amount within limit'],
            estimatedEMI: 12458,
            totalInterest: 148960
          },
          {
            lender: {
              id: '2',
              name: 'HDFC Bank',
              type: 'bank',
              logo: '🏛️',
              interestRate: 9.2,
              minAmount: 100000,
              maxAmount: 2000000,
              maxTerm: 72,
              processingFee: 2.0,
              eligibilityCriteria: {
                minCreditScore: 700,
                minMonthlyIncome: 30000,
                maxAge: 60,
                employmentTypes: ['salaried']
              },
              features: ['Digital Process', 'Instant Approval', 'Doorstep Service'],
              rating: 4.5,
              reviewCount: 2100,
              processingTime: '1-2 days'
            },
            matchScore: 85,
            eligibilityStatus: 'eligible',
            reasons: ['High credit score advantage', 'Premium banking customer', 'Quick processing'],
            estimatedEMI: 13250,
            totalInterest: 165000
          },
          {
            lender: {
              id: '3',
              name: 'Bajaj Finserv',
              type: 'nbfc',
              logo: '💰',
              interestRate: 11.5,
              minAmount: 25000,
              maxAmount: 500000,
              maxTerm: 48,
              processingFee: 2.5,
              eligibilityCriteria: {
                minCreditScore: 600,
                minMonthlyIncome: 20000,
                maxAge: 70,
                employmentTypes: ['salaried', 'self-employed', 'business']
              },
              features: ['Instant Approval', 'Minimal Documentation', 'Flexible Tenure'],
              rating: 4.0,
              reviewCount: 890,
              processingTime: '2-4 hours'
            },
            matchScore: 78,
            eligibilityStatus: 'eligible',
            reasons: ['Fast processing', 'Low documentation', 'Flexible criteria'],
            estimatedEMI: 15123,
            totalInterest: 225840
          },
          {
            lender: {
              id: '4',
              name: 'Mahindra Finance',
              type: 'nbfc',
              logo: '🚜',
              interestRate: 12.8,
              minAmount: 20000,
              maxAmount: 300000,
              maxTerm: 36,
              processingFee: 3.0,
              eligibilityCriteria: {
                minCreditScore: 550,
                minMonthlyIncome: 15000,
                maxAge: 65,
                employmentTypes: ['salaried', 'self-employed', 'agriculture']
              },
              features: ['Rural Focus', 'Agriculture Loans', 'Easy Approval'],
              rating: 3.8,
              reviewCount: 450,
              processingTime: '1-3 days'
            },
            matchScore: 65,
            eligibilityStatus: 'partially_eligible',
            reasons: ['Higher interest rate', 'Suitable for rural areas', 'Lower amount limit'],
            estimatedEMI: 16890,
            totalInterest: 208040
          }
        ];

        setRecommendations(mockRecommendations);
      } catch (error) {
        toast.error('Failed to load loan recommendations');
        console.error('Error loading recommendations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [loanApplication, navigate]);

  const getEligibilityIcon = (status: string) => {
    switch (status) {
      case 'eligible':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'partially_eligible':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'not_eligible':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getEligibilityColor = (status: string) => {
    switch (status) {
      case 'eligible':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'partially_eligible':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'not_eligible':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const filteredRecommendations = recommendations.filter(rec => {
    switch (selectedFilter) {
      case 'eligible':
        return rec.eligibilityStatus === 'eligible';
      case 'top_rated':
        return rec.lender.rating >= 4.0;
      default:
        return true;
    }
  });

  const handleApplyToLender = (lenderId: string) => {
    toast.success('Redirecting to lender application...');
    // Here you would implement the actual application logic
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center min-h-[60vh]">
          <LoadingSpinner />
          <p className="mt-4 text-muted-foreground">{t('recommendations.analyzing')}</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/borrowers/dashboard')}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              title="Back to Dashboard"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
                {t('recommendations.title')}
              </h1>
              <p className="text-muted-foreground mt-1">
                {t('recommendations.subtitle')} ₹{loanApplication?.amount.toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        {/* Loan Application Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-lg p-6"
        >
          <h2 className="text-lg font-semibold text-foreground mb-4">{t('recommendations.applicationSummary')}</h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="flex items-center space-x-3">
              <IndianRupee className="w-5 h-5 text-sapBlue-600" />
              <div>
                <p className="text-sm text-muted-foreground">{t('loans.amount')}</p>
                <p className="font-semibold">₹{loanApplication?.amount.toLocaleString()}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <FileText className="w-5 h-5 text-sapBlue-600" />
              <div>
                <p className="text-sm text-muted-foreground">{t('loans.loanPurpose')}</p>
                <p className="font-semibold">{loanApplication?.purpose}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Clock className="w-5 h-5 text-sapBlue-600" />
              <div>
                <p className="text-sm text-muted-foreground">{t('loans.loanTerm')}</p>
                <p className="font-semibold">{loanApplication?.term} {t('common.months')}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <TrendingUp className="w-5 h-5 text-sapBlue-600" />
              <div>
                <p className="text-sm text-muted-foreground">{t('loans.creditScore')}</p>
                <p className="font-semibold">{loanApplication?.creditScore}</p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2">
          {['all', 'eligible', 'top_rated'].map((filter) => (
            <button
              key={filter}
              onClick={() => setSelectedFilter(filter as any)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedFilter === filter
                  ? 'bg-sapBlue-600 text-white'
                  : 'bg-white/10 text-muted-foreground hover:bg-white/20'
              }`}
            >
              {t(`recommendations.filter.${filter}`)}
            </button>
          ))}
        </div>

        {/* Recommendations List */}
        <div className="space-y-4">
          {filteredRecommendations.map((recommendation, index) => (
            <motion.div
              key={recommendation.lender.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass rounded-lg p-6 hover:shadow-lg transition-all duration-300"
            >
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
                {/* Lender Info */}
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="text-3xl">{recommendation.lender.logo}</div>
                      <div>
                        <h3 className="text-xl font-semibold text-foreground">{recommendation.lender.name}</h3>
                        <div className="flex items-center space-x-4 mt-1">
                          <span className="text-sm text-muted-foreground capitalize">
                            {recommendation.lender.type}
                          </span>
                          <div className="flex items-center space-x-1">
                            <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                            <span className="text-sm font-medium">{recommendation.lender.rating}</span>
                            <span className="text-sm text-muted-foreground">
                              ({recommendation.lender.reviewCount})
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getEligibilityIcon(recommendation.eligibilityStatus)}
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getEligibilityColor(recommendation.eligibilityStatus)}`}>
                        {t(`recommendations.eligibility.${recommendation.eligibilityStatus}`)}
                      </span>
                    </div>
                  </div>

                  {/* Key Details */}
                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-muted-foreground">{t('recommendations.interestRate')}</p>
                      <p className="font-semibold text-sapBlue-600">{recommendation.lender.interestRate}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">{t('recommendations.processingTime')}</p>
                      <p className="font-semibold">{recommendation.lender.processingTime}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">{t('recommendations.estimatedEMI')}</p>
                      <p className="font-semibold">₹{recommendation.estimatedEMI.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">{t('recommendations.matchScore')}</p>
                      <p className="font-semibold text-green-600">{recommendation.matchScore}%</p>
                    </div>
                  </div>

                  {/* Features */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {recommendation.lender.features.map((feature) => (
                      <span
                        key={feature}
                        className="px-3 py-1 bg-sapBlue-100 text-sapBlue-800 text-xs rounded-full"
                      >
                        {feature}
                      </span>
                    ))}
                  </div>

                  {/* Reasons */}
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-2">{t('recommendations.reasons')}</p>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      {recommendation.reasons.map((reason) => (
                        <li key={reason} className="flex items-center space-x-2">
                          <CheckCircle className="w-3 h-3 text-green-500" />
                          <span>{reason}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-col space-y-3 lg:w-48">
                  <button
                    onClick={() => handleApplyToLender(recommendation.lender.id)}
                    disabled={recommendation.eligibilityStatus === 'not_eligible'}
                    className="bg-sapBlue-600 text-white px-6 py-3 rounded-lg hover:bg-sapBlue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    <FileText className="w-4 h-4" />
                    <span>{t('recommendations.applyNow')}</span>
                  </button>
                  <button className="border border-border px-6 py-2 rounded-lg hover:bg-white/5 transition-colors flex items-center justify-center space-x-2">
                    <Calculator className="w-4 h-4" />
                    <span>{t('recommendations.calculateEMI')}</span>
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {filteredRecommendations.length === 0 && (
          <div className="text-center py-12">
            <Building2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">{t('recommendations.noResults')}</p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default LoanRecommendations;
