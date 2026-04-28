import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { motion, AnimatePresence } from 'motion/react';
import {
  Image as ImageIcon,
  FileText,
  Download,
  ExternalLink,
  Share2,
  Camera,
  Layers,
  Sparkles,
  Zap,
  Loader2
} from 'lucide-react';
import { apiRequest } from '@/lib/api';

interface Output {
  id: string;
  type: 'collage' | 'story' | 'case_study' | 'linkedin_post';
  title: string;
  session_id: string;
  created_at: string;
  url?: string;
  thumbnail?: string;
  ratio: string;
}

export default function Outputs() {
  const [outputs, setOutputs] = useState<Output[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch all sessions first, then get their outputs
    apiRequest('/api/v1/sessions')
      .then((data) => {
        const sessions = data.sessions || [];
        const allOutputs: Output[] = [];
        
        // Fetch outputs for each session
        const outputPromises = sessions.map((session: any) =>
          apiRequest(`/api/v1/sessions/${session.session_id}/outputs`)
            .then((outputData) => {
              const sessionOutputs = outputData.outputs || [];
              return sessionOutputs.map((o: any) => ({
                ...o,
                ratio: o.type === 'story' ? 'aspect-[9/16]' : 'aspect-video'
              }));
            })
            .catch(() => [])
        );

        return Promise.all(outputPromises).then((results) => {
          results.forEach(sessionOutputs => allOutputs.push(...sessionOutputs));
          return allOutputs;
        });
      })
      .then((allOutputs) => {
        setOutputs(allOutputs);
      })
      .catch((err) => {
        console.error('Failed to load outputs:', err);
      })
      .finally(() => setLoading(false));
  }, []);

  const getOutputConfig = (type: Output['type']) => {
    switch (type) {
      case 'collage':
        return { icon: ImageIcon, color: 'text-blue-400', bg: 'bg-blue-500/10', label: 'Collage' };
      case 'story':
        return { icon: Camera, color: 'text-pink-400', bg: 'bg-pink-500/10', label: 'Story' };
      case 'case_study':
        return { icon: FileText, color: 'text-emerald-400', bg: 'bg-emerald-500/10', label: 'Case Study' };
      case 'linkedin_post':
        return { icon: Share2, color: 'text-blue-500', bg: 'bg-blue-500/10', label: 'LinkedIn' };
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-4xl font-bold tracking-tight">Asset Repository</h2>
          <p className="text-muted-foreground mt-1">
            Review and export generated marketing collateral
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" className="glass border-white/10 rounded-xl">
            <Zap className="mr-2 h-4 w-4" /> Export All
          </Button>
          <Button className="rounded-xl shadow-lg shadow-primary/20">
            <Sparkles className="mr-2 h-4 w-4" /> Bulk Optimization
          </Button>
        </div>
      </div>

      <Tabs defaultValue="all" className="space-y-8">
        <div className="flex items-center justify-between">
          <TabsList className="bg-white/5 border border-white/10 p-1 h-12 rounded-2xl">
            <TabsTrigger value="all" className="rounded-xl px-6 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">All Assets</TabsTrigger>
            <TabsTrigger value="collages" className="rounded-xl px-6">Collages</TabsTrigger>
            <TabsTrigger value="stories" className="rounded-xl px-6">Stories</TabsTrigger>
            <TabsTrigger value="documents" className="rounded-xl px-6">Docs</TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="all" className="mt-0">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-24 gap-4">
              <Loader2 className="h-10 w-10 animate-spin text-primary/50" />
              <p className="text-muted-foreground animate-pulse">Loading assets...</p>
            </div>
          ) : outputs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-24 gap-4">
              <Layers className="h-10 w-10 text-muted-foreground/50" />
              <p className="text-muted-foreground">No assets generated yet. Process a dataset first.</p>
            </div>
          ) : (
            <div className="columns-1 md:columns-2 lg:columns-3 gap-6 space-y-6">
            <AnimatePresence>
              {outputs.map((output, i) => {
                const config = getOutputConfig(output.type);
                const Icon = config.icon;

                return (
                  <motion.div
                    key={output.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.05 }}
                    className="break-inside-avoid"
                  >
                    <Card className="glass-card border-white/5 hover:border-white/20 transition-all group overflow-hidden">
                      <div className={`relative ${output.ratio} bg-white/2 overflow-hidden`}>
                        {/* Real Image or Placeholder */}
                        {output.url ? (
                          <img 
                            src={`http://localhost:8000${output.url}`} 
                            alt={output.title}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              e.currentTarget.style.display = 'none';
                              e.currentTarget.nextElementSibling?.classList.remove('hidden');
                            }}
                          />
                        ) : null}
                        <div className={`absolute inset-0 flex items-center justify-center opacity-20 group-hover:opacity-40 transition-opacity ${output.url ? 'hidden' : ''}`}>
                          <Icon className="w-20 h-20" />
                        </div>
                        <div className="absolute inset-0 bg-linear-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-4">
                          <div className="flex gap-2 w-full">
                            <Button 
                              variant="secondary" 
                              size="sm" 
                              className="flex-1 rounded-xl bg-white/10 hover:bg-white/20 backdrop-blur-md border-white/10 text-white"
                              onClick={() => output.url && window.open(`http://localhost:8000${output.url}`, '_blank')}
                            >
                              <Download className="mr-2 h-4 w-4" /> Download
                            </Button>
                            <Button 
                              variant="secondary" 
                              size="icon" 
                              className="rounded-xl bg-white/10 hover:bg-white/20 backdrop-blur-md border-white/10 text-white"
                              onClick={() => output.url && window.open(`http://localhost:8000${output.url}`, '_blank')}
                            >
                              <ExternalLink className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                        <Badge className="absolute top-3 left-3 bg-black/50 backdrop-blur-md border-white/10 text-[10px] uppercase tracking-widest font-bold">
                          {config.label}
                        </Badge>
                      </div>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="font-semibold text-lg leading-tight group-hover:text-primary transition-colors">{output.title}</h3>
                            <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                              <Layers className="h-3 w-3" /> {output.session_id}
                            </div>
                          </div>
                          <div className={`p-2 rounded-lg ${config.bg} ${config.color}`}>
                            <Icon className="h-4 w-4" />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
          )}
        </TabsContent>

        <TabsContent value="collages" className="mt-0">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* Filtered items would go here */}
            <p className="text-muted-foreground text-center py-20 col-span-full">Filtered view enabled. Showing only collages.</p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
