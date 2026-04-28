import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'motion/react';
import {
  Activity,
  Server,
  FolderOpen,
  Image as ImageIcon,
  BookOpen,
  Play,
  CheckCircle2,
  XCircle,
  Clock,
  Layers,
  ArrowUpRight
} from 'lucide-react';
import { healthApi, sessionsApi, apiRequest } from '../lib/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const [health, setHealth] = useState<'healthy' | 'offline' | 'checking'>('checking');
  const [datasetName, setDatasetName] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [statsData, setStatsData] = useState({
    activeSessions: '0',
    assetsProcessed: '0',
    apiVersion: 'v0.0.0',
    systemStatus: 'CHECKING'
  });

  useEffect(() => {
    healthApi.check()
      .then(() => {
        setHealth('healthy');
        setStatsData(prev => ({ ...prev, systemStatus: 'HEALTHY' }));
      })
      .catch(() => {
        setHealth('offline');
        setStatsData(prev => ({ ...prev, systemStatus: 'OFFLINE' }));
      });

    sessionsApi.getAll()
      .then(data => {
        const sessions = Array.isArray(data) ? data : (data.sessions || []);
        const totalAssets = sessions.reduce((sum: number, s: any) => sum + (s.total_assets || 0), 0);
        const activeCount = sessions.filter((s: any) => s.status === 'processing').length;

        setStatsData(prev => ({
          ...prev,
          activeSessions: sessions.length.toString(),
          assetsProcessed: totalAssets.toLocaleString()
        }));
      })
      .catch(err => console.error('Failed to fetch sessions stats:', err));

    // 3. Fetch API Version
    apiRequest('/')
      .then(data => {
        if (data && data.version) {
          setStatsData(prev => ({ ...prev, apiVersion: `v${data.version}` }));
        } else {
          setStatsData(prev => ({ ...prev, apiVersion: 'v1.0.0' }));
        }
      })
      .catch(() => {
        setStatsData(prev => ({ ...prev, apiVersion: 'v1.0.0' }));
      });
  }, []);

  const handleProcess = async () => {
    if (!datasetName) {
      setError('Please enter a dataset name');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await apiRequest(`/api/v1/process/${datasetName}`, {
        method: 'POST',
      });
      setResult({ message: response.message || 'Dataset processing started successfully' });
      setTimeout(() => navigate('/sessions'), 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to process dataset');
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    {
      title: 'System Health',
      value: statsData.systemStatus,
      subValue: health === 'healthy' ? 'All systems operational' : 'System connection lost',
      icon: Activity,
      color: health === 'healthy' ? 'text-emerald-400' : 'text-red-400',
      bg: health === 'healthy' ? 'bg-emerald-500/10' : 'bg-red-500/10'
    },
    {
      title: 'Total Sessions',
      value: statsData.activeSessions,
      subValue: 'Across all datasets',
      icon: Clock,
      color: 'text-blue-400',
      bg: 'bg-blue-500/10'
    },
    {
      title: 'Assets Processed',
      value: statsData.assetsProcessed,
      subValue: 'High-fidelity outputs',
      icon: Layers,
      color: 'text-purple-400',
      bg: 'bg-purple-500/10'
    },
    {
      title: 'API Version',
      value: statsData.apiVersion,
      subValue: 'Production build',
      icon: Server,
      color: 'text-orange-400',
      bg: 'bg-orange-500/10'
    }
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-10 py-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-5xl font-light tracking-tight text-white mb-2">Mission Control</h1>
          <p className="text-shade-50 text-lg">Real-time system overview and dataset orchestration</p>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/5 ${health === 'healthy' ? 'bg-dark-forest' : 'bg-red-500/10'}`}>
          <span className="relative flex h-2 w-2">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${health === 'healthy' ? 'bg-emerald-400' : 'bg-red-400'}`}></span>
            <span className={`relative inline-flex rounded-full h-2 w-2 ${health === 'healthy' ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
          </span>
          <span className={`text-[11px] font-bold uppercase tracking-wider ${health === 'healthy' ? 'text-emerald-500' : 'text-red-500'}`}>
            System {health}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="shopify-card p-6 group"
          >
            <div className="flex justify-between items-start mb-6">
              <span className="text-[11px] font-bold uppercase tracking-widest text-shade-70">{stat.title}</span>
              <div className={`p-2 rounded-full ${stat.bg} ${stat.color} group-hover:scale-110 transition-transform`}>
                <stat.icon className="h-4 w-4" />
              </div>
            </div>
            <div className="space-y-1">
              <h3 className="text-3xl font-light text-white">{stat.value}</h3>
              <p className="text-xs text-shade-50 font-medium">{stat.subValue}</p>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 shopify-card overflow-hidden">
          <div className="p-8 border-b border-white/5 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-600/10 text-blue-500">
              <Play className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-xl font-light text-white">Dataset Orchestrator</h2>
              <p className="text-xs text-shade-50">Deploy the content engine on a new media collection</p>
            </div>
          </div>

          <div className="p-8">
            <div className="bg-void/50 border border-white/5 rounded-xl p-8 space-y-6">
              <div className="space-y-3">
                <label className="text-[11px] font-bold uppercase tracking-widest text-shade-70 ml-1">Dataset Identifier</label>
                <div className="flex flex-col sm:flex-row gap-4">
                  <input
                    value={datasetName}
                    onChange={e => setDatasetName(e.target.value)}
                    placeholder="e.g. event_dataset_1"
                    className="flex-1 h-12 bg-dark-forest border border-white/5 rounded-lg px-6 text-sm text-white focus:ring-1 focus:ring-blue-500 outline-none transition-all placeholder:text-shade-70"
                  />
                  <button
                    onClick={handleProcess}
                    disabled={loading}
                    className="btn-pill h-12 bg-blue-600 hover:bg-blue-500 text-white flex items-center justify-center gap-3 shadow-lg shadow-blue-900/40 disabled:opacity-50 disabled:cursor-not-allowed group min-w-[180px]"
                  >
                    {loading ? (
                      <>
                        <Activity className="h-4 w-4 animate-spin" />
                        Deploying...
                      </>
                    ) : (
                      <>
                        <Play className="h-4 w-4 fill-white" />
                        <span className="text-xs font-bold uppercase tracking-widest">Run Pipeline</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              <AnimatePresence>
                {error && (
                  <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center gap-3">
                    <XCircle className="h-4 w-4 shrink-0" />
                    <span>{error}</span>
                  </motion.div>
                )}
                {result && (
                  <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-3">
                    <CheckCircle2 className="h-4 w-4 shrink-0" />
                    <span><strong>Success!</strong> {result.message}</span>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>

        {/* Quick Access Sidebar */}
        <div className="flex flex-col gap-4">
          {[
            { title: 'Processing Queue', desc: 'Monitor active sessions', icon: FolderOpen, path: '/sessions' },
            { title: 'Asset Repository', desc: 'Browse generated media', icon: ImageIcon, path: '/outputs' },
            { title: 'Technical Docs', desc: 'API and system architecture', icon: BookOpen, path: '/docs' },
          ].map((action, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + (i * 0.1) }}
              onClick={() => navigate(action.path)}
              className="shopify-card p-6 flex items-center justify-between group cursor-pointer hover:bg-white/5 active:scale-[0.98]"
            >
              <div className="flex items-center gap-5">
                <div className="p-3 rounded-xl bg-dark-forest text-shade-50 group-hover:text-white transition-colors">
                  <action.icon className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-base font-medium text-white">{action.title}</h3>
                  <p className="text-[11px] text-shade-50 font-medium">{action.desc}</p>
                </div>
              </div>
              <ArrowUpRight className="h-4 w-4 text-shade-70 group-hover:text-white group-hover:translate-x-1 group-hover:-translate-y-1 transition-all" />
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
