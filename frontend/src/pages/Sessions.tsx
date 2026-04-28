import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
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
  ChevronRight
} from 'lucide-react';
import { sessionsApi } from '../lib/api';
import { Button } from '@/components/ui/button';

interface Session {
  session_id: string;
  dataset: string;
  status: 'processing' | 'completed' | 'failed' | 'pending';
  progress?: number;
  created_at: string;
  assets_count?: number;
}

export default function Sessions() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
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
  }, []);

  const getStatusConfig = (status: Session['status']) => {
    switch (status) {
      case 'processing':
        return { icon: Loader2, color: 'text-blue-400', bg: 'bg-blue-500/10', label: 'Processing' };
      case 'completed':
        return { icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/10', label: 'Success' };
      case 'failed':
        return { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/10', label: 'Failed' };
      default:
        return { icon: Clock, color: 'text-yellow-400', bg: 'bg-yellow-500/10', label: 'Pending' };
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-4xl font-bold tracking-tight">Processing Queue</h2>
          <p className="text-muted-foreground mt-1">
            Historical and active content generation sessions
          </p>
        </div>
        <Button className="rounded-xl shadow-lg shadow-primary/20">
          <Layers className="mr-2 h-4 w-4" />
          Refresh Queue
        </Button>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-24 gap-4">
          <Loader2 className="h-10 w-10 animate-spin text-primary/50" />
          <p className="text-muted-foreground animate-pulse">Syncing with server...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {sessions.map((session, i) => {
            const config = getStatusConfig(session.status);
            const StatusIcon = config.icon;
            
            return (
              <motion.div
                key={session.session_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <Card className="glass-card border-white/5 hover:border-white/20 transition-all overflow-hidden group">
                  <CardContent className="p-0">
                    <div className="flex flex-col md:flex-row items-stretch md:items-center p-5 gap-6">
                      {/* Status & ID */}
                      <div className="flex items-center gap-4 min-w-[200px]">
                        <div className={`p-3 rounded-2xl ${config.bg} ${config.color}`}>
                          <StatusIcon className={`h-6 w-6 ${session.status === 'processing' ? 'animate-spin' : ''}`} />
                        </div>
                        <div>
                          <div className="text-sm font-mono text-muted-foreground">{session.session_id}</div>
                          <Badge variant="outline" className={`mt-1 border-none px-0 font-semibold ${config.color}`}>
                            {config.label}
                          </Badge>
                        </div>
                      </div>

                      {/* Dataset Info */}
                      <div className="flex-1 min-w-[200px]">
                        <div className="text-sm text-muted-foreground mb-1 flex items-center gap-2">
                          <Layers className="h-3 w-3" /> Dataset
                        </div>
                        <div className="font-semibold text-lg">{session.dataset}</div>
                      </div>

                      {/* Meta Info */}
                      <div className="flex gap-8">
                        <div className="min-w-[100px]">
                          <div className="text-sm text-muted-foreground mb-1 flex items-center gap-2">
                            <Calendar className="h-3 w-3" /> Date
                          </div>
                          <div className="font-medium">{new Date(session.created_at).toLocaleDateString()}</div>
                        </div>
                        <div className="min-w-[80px]">
                          <div className="text-sm text-muted-foreground mb-1 flex items-center gap-2">
                            <Layers className="h-3 w-3" /> Assets
                          </div>
                          <div className="font-medium">{session.assets_count}</div>
                        </div>
                      </div>

                      {/* Progress (if processing) */}
                      {session.status === 'processing' && (
                        <div className="flex-1 min-w-[150px] space-y-2">
                          <div className="flex justify-between text-xs font-medium">
                            <span>Processing Pipeline</span>
                            <span>{session.progress}%</span>
                          </div>
                          <Progress value={session.progress} className="h-2 bg-white/5" />
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex items-center gap-2 ml-auto">
                        <Button variant="ghost" size="icon" className="rounded-xl hover:bg-white/5 text-muted-foreground hover:text-primary">
                          <Eye className="h-5 w-5" />
                        </Button>
                        <Button variant="ghost" size="icon" className="rounded-xl hover:bg-white/5 text-muted-foreground hover:text-emerald-400">
                          <Download className="h-5 w-5" />
                        </Button>
                        <Button variant="ghost" size="icon" className="rounded-xl hover:bg-white/5 text-muted-foreground">
                          <ChevronRight className="h-5 w-5" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
