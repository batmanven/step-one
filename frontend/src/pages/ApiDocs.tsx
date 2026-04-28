import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { motion } from 'motion/react';
import {
  ExternalLink,
  Code,
  Play,
  BookOpen,
  Terminal,
  Cpu,
  Hash,
  ShieldCheck
} from 'lucide-react';

export default function ApiDocs() {
  const endpoints = [
    { method: 'GET', path: '/health', desc: 'System pulse and connectivity check', color: 'bg-emerald-500' },
    { method: 'POST', path: '/sessions', desc: 'Initialize a new orchestration session', color: 'bg-blue-500' },
    { method: 'GET', path: '/sessions', desc: 'Retrieve historical execution logs', color: 'bg-emerald-500' },
    { method: 'GET', path: '/sessions/:id', desc: 'Deep-dive into specific session telemetry', color: 'bg-emerald-500' },
    { method: 'POST', path: '/upload/:session_id', desc: 'Stream raw media assets to cluster', color: 'bg-blue-500' },
    { method: 'POST', path: '/workflow/process', desc: 'Execute end-to-end inference pipeline', color: 'bg-purple-500' },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-12 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-8 border-b border-white/5">
        <div className="space-y-4">
          <Badge className="bg-primary/20 text-primary border-primary/20 rounded-full px-4 py-1">API Reference v1.0</Badge>
          <h2 className="text-5xl font-bold tracking-tight">Core Infrastructure</h2>
          <p className="text-xl text-muted-foreground max-w-2xl">
            Technical specifications for programmatically interacting with the Content & Design Engine.
          </p>
        </div>
        <div className="flex gap-3">
          <Button onClick={() => window.open('http://localhost:8000/docs', '_blank')} className="rounded-xl shadow-lg shadow-primary/20">
            <ExternalLink className="mr-2 h-4 w-4" />
            Swagger
          </Button>
          <Button variant="outline" onClick={() => window.open('http://localhost:8000/redoc', '_blank')} className="glass border-white/10 rounded-xl">
            <BookOpen className="mr-2 h-4 w-4" />
            ReDoc
          </Button>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-8">
          {/* Base URL Card */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card className="glass-card border-white/5 overflow-hidden">
              <div className="bg-white/5 p-4 flex items-center gap-3 border-b border-white/5">
                <Terminal className="w-5 h-5 text-primary" />
                <span className="font-semibold text-sm">Base Endpoint</span>
              </div>
              <CardContent className="p-6">
                <div className="bg-black/40 p-4 rounded-xl border border-white/5 flex items-center justify-between group">
                  <code className="text-primary font-mono text-lg">https://api.content-engine.ai/v1</code>
                  <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <Hash className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Endpoints */}
          <div className="space-y-4">
            <h3 className="text-2xl font-bold flex items-center gap-2">
              <Cpu className="w-6 h-6 text-primary" />
              Available Endpoints
            </h3>
            <div className="grid gap-3">
              {endpoints.map((ep, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="group flex items-center gap-4 p-4 rounded-2xl bg-white/2 border border-white/5 hover:border-primary/30 transition-all hover:bg-white/5"
                >
                  <Badge className={`${ep.color} text-white min-w-[60px] flex justify-center py-1 rounded-lg`}>{ep.method}</Badge>
                  <code className="font-mono text-sm flex-1">{ep.path}</code>
                  <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">{ep.desc}</span>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-8">
          {/* Auth/Security */}
          <Card className="glass-card border-white/5 bg-linear-to-br from-primary/10 to-transparent">
            <CardContent className="p-6 space-y-4">
              <div className="p-3 rounded-2xl bg-primary/20 w-fit">
                <ShieldCheck className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold">Authentication</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                All requests require a Bearer token in the Authorization header. Revoke keys via the developer portal.
              </p>
              <div className="bg-black/40 p-3 rounded-xl border border-white/5 font-mono text-xs text-primary/70">
                Authorization: Bearer {'<token>'}
              </div>
            </CardContent>
          </Card>

          {/* Code Example */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold flex items-center gap-2">
              <Code className="w-5 h-5 text-primary" />
              Inference Request
            </h3>
            <div className="bg-[#0d1117] p-5 rounded-2xl border border-white/5 font-mono text-[13px] leading-relaxed relative group shadow-2xl">
              <div className="flex gap-1.5 mb-4">
                <div className="w-2.5 h-2.5 rounded-full bg-red-500/50" />
                <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/50" />
                <div className="w-2.5 h-2.5 rounded-full bg-green-500/50" />
              </div>
              <pre className="text-blue-300">
                {`curl -X POST \\
  'https://api.content.ai/v1/process' \\
  -H 'Authorization: Bearer sk_live_...' \\
  -d '{
    "session_id": "SES-9421",
    "priority": "high",
    "notify": true
  }'`}
              </pre>
              <Button size="icon" variant="ghost" className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                <Play className="w-4 h-4 text-emerald-400" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
