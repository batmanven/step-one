import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { 
  Clock, 
  CheckCircle2, 
  XCircle, 
  Loader2,
  Eye,
  Download,
  Calendar,
  Layers,
  ChevronRight,
  RefreshCw
} from 'lucide-react';
import { sessionsApi } from '../lib/api';

interface Session {
  session_id: string;
  dataset: string;
  status: 'processing' | 'completed' | 'failed' | 'pending';
  progress?: number;
  created_at: string;
  assets_count?: number;
}

export default function Sessions() {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSessions = () => {
    setLoading(true);
    sessionsApi.getAll()
      .then(data => {
        const sessionsData = Array.isArray(data) ? data : (data.sessions || []);
        setSessions(sessionsData.map((s: any) => ({
          session_id: s._id || s.session_id,
          dataset: s.event_name || s.dataset || 'Unknown',
          status: s.status || 'pending',
          progress: s.progress || 0,
          created_at: s.created_at || new Date().toISOString(),
          assets_count: s.total_assets || s.assets_count || 0
        })));
      })
      .catch((err) => {
        console.error('Failed to load sessions:', err);
        setSessions([]);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const getStatusConfig = (status: Session['status']) => {
    switch (status) {
      case 'processing':
        return { icon: Loader2, color: 'text-blue-500', bg: 'bg-blue-500/10', label: 'Processing' };
      case 'completed':
        return { icon: CheckCircle2, color: 'text-emerald-500', bg: 'bg-emerald-500/10', label: 'Success' };
      case 'failed':
        return { icon: XCircle, color: 'text-red-500', bg: 'bg-red-500/10', label: 'Failed' };
      default:
        return { icon: Clock, color: 'text-amber-500', bg: 'bg-amber-500/10', label: 'Pending' };
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-10 py-4">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-5xl font-light tracking-tight text-white mb-2">Processing Queue</h1>
          <p className="text-shade-50 text-lg">Historical and active content generation sessions</p>
        </div>
        <button 
          onClick={fetchSessions}
          className="btn-pill min-w-[160px] bg-dark-forest border border-white/5 text-white text-xs flex items-center justify-center gap-2 hover:bg-forest transition-colors"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Refresh Queue
        </button>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-32 gap-6 shopify-card">
          <div className="relative">
            <Loader2 className="h-12 w-12 animate-spin text-blue-500" />
            <div className="absolute inset-0 blur-xl bg-blue-500/20 rounded-full" />
          </div>
          <p className="text-shade-50 font-medium animate-pulse">Syncing with cluster...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {sessions.length === 0 ? (
            <div className="shopify-card p-20 text-center space-y-4">
              <div className="inline-flex p-4 rounded-full bg-dark-forest text-shade-70 mb-2">
                <Layers className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-light text-white">No sessions found</h3>
              <p className="text-shade-50 max-w-xs mx-auto">Start a new pipeline to see your sessions appear here.</p>
            </div>
          ) : (
            sessions.map((session, i) => {
              const config = getStatusConfig(session.status);
              const StatusIcon = config.icon;
              
              return (
                <motion.div
                  key={session.session_id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="shopify-card group hover:border-white/10"
                >
                  <div className="flex flex-col md:flex-row items-center p-6 gap-8">
                    {/* Status & ID */}
                    <div className="flex items-center gap-5 min-w-[240px]">
                      <div className={`p-3.5 rounded-xl ${config.bg} ${config.color} group-hover:scale-105 transition-transform`}>
                        <StatusIcon className={`h-6 w-6 ${session.status === 'processing' ? 'animate-spin' : ''}`} />
                      </div>
                      <div className="space-y-1">
                        <div className="text-[10px] font-bold text-shade-70 uppercase tracking-widest leading-none mb-1">Session ID</div>
                        <div className="text-sm font-mono text-white truncate max-w-[120px]">{session.session_id}</div>
                        <div className={`text-[11px] font-bold uppercase tracking-wider ${config.color}`}>
                          {config.label}
                        </div>
                      </div>
                    </div>

                    {/* Dataset Info */}
                    <div className="flex-1 min-w-[180px]">
                      <div className="text-[10px] font-bold text-shade-70 uppercase tracking-widest mb-1">Dataset</div>
                      <div className="text-lg font-light text-white">{session.dataset}</div>
                    </div>

                    {/* Meta Info */}
                    <div className="flex gap-12">
                      <div className="min-w-[100px]">
                        <div className="text-[10px] font-bold text-shade-70 uppercase tracking-widest mb-1">Date</div>
                        <div className="text-sm font-medium text-white">{new Date(session.created_at).toLocaleDateString()}</div>
                      </div>
                      <div className="min-w-[80px]">
                        <div className="text-[10px] font-bold text-shade-70 uppercase tracking-widest mb-1">Assets</div>
                        <div className="text-sm font-medium text-white">{session.assets_count || 0}</div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-3 ml-auto">
                      <button 
                        onClick={() => navigate(`/outputs?session=${session.session_id}`)}
                        className="p-2.5 rounded-lg bg-dark-forest text-shade-50 hover:text-white transition-colors"
                        title="View Assets"
                      >
                        <Eye className="h-4.5 w-4.5" />
                      </button>
                      <button 
                        onClick={() => window.open(`http://localhost:8000/api/v1/sessions/${session.session_id}/download-all`, '_blank')}
                        className="p-2.5 rounded-lg bg-dark-forest text-shade-50 hover:text-emerald-500 transition-colors"
                        title="Download Bundle (.zip)"
                      >
                        <Download className="h-4.5 w-4.5" />
                      </button>
                      <button 
                        onClick={() => navigate(`/outputs?session=${session.session_id}`)}
                        className="p-2.5 rounded-lg bg-blue-600/10 text-blue-500 hover:bg-blue-600/20 transition-all"
                      >
                        <ChevronRight className="h-4.5 w-4.5" />
                      </button>
                    </div>
                  </div>
                  
                  {/* Progress bar at bottom for processing */}
                  {session.status === 'processing' && (
                    <div className="h-1 w-full bg-void overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${session.progress || 0}%` }}
                        className="h-full bg-blue-500"
                        transition={{ duration: 1 }}
                      />
                    </div>
                  )}
                </motion.div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
