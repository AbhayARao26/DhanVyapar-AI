import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import Layout from '../components/common/Layout';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ChatBot from '../components/common/ChatBot';
import { loanService, dashboardService } from '../services/api';
import { LoanApplication, DashboardStats } from '../types';
import { CheckCircle, XCircle, Clock, IndianRupee, Users, TrendingUp, Filter } from 'lucide-react';
import { toast } from 'sonner';

const LenderDashboard: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useSelector((state: RootState) => state.auth);
  const [loans, setLoans] = useState<LoanApplication[]>([]);
  const [filteredLoans, setFilteredLoans] = useState<LoanApplication[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [activeChatbot, setActiveChatbot] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [loansData, statsData] = await Promise.all([
          loanService.getLoanApplications('lender'),
          dashboardService.getDashboardStats('lender')
        ]);
        
        setLoans(loansData);
        setFilteredLoans(loansData);
        setStats(statsData);
      } catch (error) {
        toast.error('Failed to load dashboard data');
        console.error('Error loading dashboard:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    if (statusFilter === 'all') {
      setFilteredLoans(loans);
    } else {
      setFilteredLoans(loans.filter(loan => loan.status === statusFilter));
    }
  }, [statusFilter, loans]);

  const handleStatusUpdate = async (loanId: string, newStatus: LoanApplication['status']) => {
    try {
      await loanService.updateLoanStatus(loanId, newStatus);
      setLoans(prev => 
        prev.map(loan => 
          loan.id === loanId ? { ...loan, status: newStatus } : loan
        )
      );
      toast.success(`Loan ${newStatus} successfully`);
    } catch (error) {
      toast.error('Failed to update loan status');
      console.error('Error updating loan status:', error);
    }
  };

  const handleAIChatOpen = (aiType: string) => {
    setActiveChatbot(aiType);
  };

  const handleAIChatClose = () => {
    setActiveChatbot(null);
  };

  const getStatusColor = (status: LoanApplication['status']) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'disbursed':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCreditScoreColor = (score: number) => {
    if (score >= 750) return 'text-green-600';
    if (score >= 700) return 'text-blue-600';
    if (score >= 650) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <Layout>
        <LoadingSpinner />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            {t('dashboard.welcome')}, {user?.name}
          </h1>
          <p className="text-muted-foreground mt-1">{t('dashboard.lenderSubtitle')}</p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="glass rounded-xl p-4 md:p-6 min-h-[120px] flex flex-col justify-center"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-xs md:text-sm font-medium text-muted-foreground mb-1">{t('dashboard.totalAmount')}</p>
                  <p className="text-xl md:text-2xl font-bold text-foreground">₹{stats.totalAmount.toLocaleString()}</p>
                </div>
                <div className="ml-3">
                  <IndianRupee className="w-6 h-6 md:w-8 md:h-8 text-sapBlue-600" />
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass rounded-xl p-4 md:p-6 min-h-[120px] flex flex-col justify-center"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-xs md:text-sm font-medium text-muted-foreground mb-1">{t('dashboard.activeLoans')}</p>
                  <p className="text-xl md:text-2xl font-bold text-foreground">{stats.activeLoans}</p>
                </div>
                <div className="ml-3">
                  <Users className="w-6 h-6 md:w-8 md:h-8 text-green-600" />
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="glass rounded-xl p-4 md:p-6 min-h-[120px] flex flex-col justify-center"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-xs md:text-sm font-medium text-muted-foreground mb-1">{t('dashboard.pendingApplications')}</p>
                  <p className="text-xl md:text-2xl font-bold text-foreground">{stats.pendingApplications}</p>
                </div>
                <div className="ml-3">
                  <Clock className="w-6 h-6 md:w-8 md:h-8 text-yellow-600" />
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="glass rounded-xl p-4 md:p-6 min-h-[120px] flex flex-col justify-center"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-xs md:text-sm font-medium text-muted-foreground mb-1">{t('dashboard.defaultRate')}</p>
                  <p className="text-xl md:text-2xl font-bold text-foreground">{stats.defaultRate}%</p>
                </div>
                <div className="ml-3">
                  <TrendingUp className="w-6 h-6 md:w-8 md:h-8 text-red-600" />
                </div>
              </div>
            </motion.div>
          </div>
        )}

        {/* Loan Applications Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass rounded-lg"
        >
          <div className="p-6 border-b border-border/50">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-foreground">{t('loans.loanApplication')}</h2>
              <div className="flex items-center space-x-2">
                <Filter className="w-5 h-5 text-muted-foreground" />
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="glass-tab rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-sapBlue-500 text-foreground"
                  aria-label="Filter by loan status"
                >
                  <option value="all">{t('common.allStatus')}</option>
                  <option value="pending">{t('common.pending')}</option>
                  <option value="approved">{t('common.approved')}</option>
                  <option value="rejected">{t('common.rejected')}</option>
                  <option value="disbursed">{t('common.disbursed')}</option>
                </select>
              </div>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/20">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    {t('loans.borrower')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    {t('loans.amount')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    {t('loans.loanPurpose')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    {t('loans.creditScore')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    {t('common.status')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    {t('common.actions')}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {filteredLoans.map((loan) => (
                  <motion.tr
                    key={loan.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="hover:bg-gray-50"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{loan.borrowerName}</div>
                        <div className="text-sm text-gray-500">{loan.employmentType}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">₹{loan.amount.toLocaleString()}</div>
                      <div className="text-sm text-gray-500">{loan.term} months</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {loan.purpose}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${getCreditScoreColor(loan.creditScore)}`}>
                        {loan.creditScore}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(loan.status)}`}>
                        {t(`common.${loan.status}`)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {loan.status === 'pending' && (
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleStatusUpdate(loan.id, 'approved')}
                            className="text-green-600 hover:text-green-900 flex items-center space-x-1"
                          >
                            <CheckCircle className="w-4 h-4" />
                            <span>{t('common.approve')}</span>
                          </button>
                          <button
                            onClick={() => handleStatusUpdate(loan.id, 'rejected')}
                            className="text-red-600 hover:text-red-900 flex items-center space-x-1"
                          >
                            <XCircle className="w-4 h-4" />
                            <span>{t('common.reject')}</span>
                          </button>
                        </div>
                      )}
                      {loan.status === 'approved' && (
                        <button
                          onClick={() => handleStatusUpdate(loan.id, 'disbursed')}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          {t('common.disbursed')}
                        </button>
                      )}
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* AI Tools Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="mt-8 glass rounded-lg p-6"
        >
          <h2 className="text-xl font-semibold text-foreground mb-6">AI-Powered Tools</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button 
              onClick={() => handleAIChatOpen('risk-assessment')}
              className="p-4 bg-purple-500/10 hover:bg-purple-500/20 rounded-xl text-left transition-colors group"
            >
              <div className="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <span className="text-white font-bold text-sm">AI</span>
              </div>
              <h3 className="font-medium text-foreground mb-1">AI 1</h3>
              <p className="text-sm text-muted-foreground">Risk Assessment Tool</p>
            </button>
            
            <button 
              onClick={() => handleAIChatOpen('portfolio-optimizer')}
              className="p-4 bg-blue-500/10 hover:bg-blue-500/20 rounded-xl text-left transition-colors group"
            >
              <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <span className="text-white font-bold text-sm">AI</span>
              </div>
              <h3 className="font-medium text-foreground mb-1">AI 2</h3>
              <p className="text-sm text-muted-foreground">Portfolio Optimizer</p>
            </button>
            
            <button 
              onClick={() => handleAIChatOpen('market-analytics')}
              className="p-4 bg-green-500/10 hover:bg-green-500/20 rounded-xl text-left transition-colors group"
            >
              <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <span className="text-white font-bold text-sm">AI</span>
              </div>
              <h3 className="font-medium text-foreground mb-1">AI 3</h3>
              <p className="text-sm text-muted-foreground">Market Analytics</p>
            </button>
            
            <button 
              onClick={() => handleAIChatOpen('fraud-detection')}
              className="p-4 bg-orange-500/10 hover:bg-orange-500/20 rounded-xl text-left transition-colors group"
            >
              <div className="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                <span className="text-white font-bold text-sm">AI</span>
              </div>
              <h3 className="font-medium text-foreground mb-1">AI 4</h3>
              <p className="text-sm text-muted-foreground">Fraud Detection</p>
            </button>
          </div>
        </motion.div>
      </div>

      {/* AI Chatbot Windows */}
      {activeChatbot && (
        <ChatBot 
          open={true} 
          onClose={handleAIChatClose}
          aiType={activeChatbot}
        />
      )}
    </Layout>
  );
};

export default LenderDashboard;
