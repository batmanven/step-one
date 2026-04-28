import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
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
import { healthApi } from '../lib/api';
import { apiRequest } from '../lib/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const [health, setHealth] = useState<'healthy' | 'offline' | 'checking'>('checking');
  const [datasetName, setDatasetName] = useState('event_dataset_1_conference');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    healthApi.check()
      .then(() => setHealth('healthy'))
      .catch(() => setHealth('offline'));
  }, []);

  const handleProcess = async () => {
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
      value: health.toUpperCase(),
      subValue: 'All systems operational',
      icon: Activity,
      color: health === 'healthy' ? 'text-emerald-400' : health === 'offline' ? 'text-red-400' : 'text-yellow-400',
      bg: health === 'healthy' ? 'bg-emerald-500/10' : health === 'offline' ? 'bg-red-500/10' : 'bg-yellow-500/10'
    },
    {
      title: 'Active Sessions',
      value: '12',
      subValue: '+3 since last hour',
      icon: Clock,
      color: 'text-blue-400',
      bg: 'bg-blue-500/10'
    },
    {
      title: 'Assets Processed',
      value: '1,284',
      subValue: '98% success rate',
      icon: Layers,
      color: 'text-purple-400',
      bg: 'bg-purple-500/10'
    },
    {
      title: 'API Version',
      value: 'v1.0.0',
      subValue: 'Latest release',
      icon: Server,
      color: 'text-orange-400',
      bg: 'bg-orange-500/10'
    }
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-4xl font-bold tracking-tight">Mission Control</h2>
          <p className="text-muted-foreground mt-1">
            Real-time system overview and dataset orchestration
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="px-3 py-1 bg-white/5 border-white/10">
            <span className={`w-2 h-2 rounded-full mr-2 ${health === 'healthy' ? 'bg-emerald-500' : 'bg-red-500'} animate-pulse`} />
            System {health}
          </Badge>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <Card className="glass-card border-white/5 hover:border-white/20 transition-all group">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">{stat.title}</CardTitle>
                <div className={`p-2 rounded-lg ${stat.bg} ${stat.color} group-hover:scale-110 transition-transform`}>
                  <stat.icon className="h-4 w-4" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                  {stat.subValue}
                </p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Process Dataset Section */}
        <Card className="lg:col-span-2 glass-card border-white/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Play className="w-5 h-5 text-primary" />
              Dataset Orchestrator
            </CardTitle>
            <CardDescription>
              Deploy the content engine on a new media collection
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4 p-6 rounded-2xl bg-white/5 border border-white/5">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-muted-foreground ml-1">Dataset Identifier</label>
                <div className="flex gap-3">
                  <Input
                    value={datasetName}
                    onChange={e => setDatasetName(e.target.value)}
                    placeholder="e.g. event_dataset_1_conference"
                    className="h-12 bg-black/20 border-white/10 focus:border-primary/50 transition-all rounded-xl"
                  />
                  <Button 
                    onClick={handleProcess} 
                    disabled={loading}
                    className="h-12 px-8 rounded-xl shadow-lg shadow-primary/20 hover:scale-105 active:scale-95 transition-all"
                  >
                    {loading ? (
                      <>
                        <Activity className="mr-2 h-5 w-5 animate-spin" />
                        Deploying...
                      </>
                    ) : (
                      <>
                        <Play className="mr-2 h-5 w-5" />
                        Run Pipeline
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>

            <AnimatePresence>
              {error && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
                  <Alert variant="destructive" className="bg-red-500/10 border-red-500/20 text-red-400">
                    <XCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                </motion.div>
              )}
              {result && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
                  <Alert className="bg-emerald-500/10 border-emerald-500/20 text-emerald-400">
                    <CheckCircle2 className="h-4 w-4" />
                    <AlertDescription>
                      <strong>Success!</strong> {result.message}
                    </AlertDescription>
                  </Alert>
                </motion.div>
              )}
            </AnimatePresence>
          </CardContent>
        </Card>

        {/* Quick Access */}
        <div className="flex flex-col gap-6">
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
            >
              <Card 
                className="cursor-pointer glass-card border-white/5 hover:border-primary/30 hover:bg-white/5 transition-all group" 
                onClick={() => navigate(action.path)}
              >
                <CardHeader className="p-5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="p-3 rounded-xl bg-white/5 text-muted-foreground group-hover:text-primary transition-colors">
                        <action.icon className="w-5 h-5" />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{action.title}</CardTitle>
                        <CardDescription className="text-xs">{action.desc}</CardDescription>
                      </div>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-muted-foreground group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                  </div>
                </CardHeader>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
