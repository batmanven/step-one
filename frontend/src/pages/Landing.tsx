import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { motion } from 'motion/react';
import {
  BarChart3,
  FileText,
  LayoutTemplate,
  Smartphone,
  FileCheck,
  ShieldCheck,
  ArrowRight,
  Sparkles,
  Zap,
  Globe
} from 'lucide-react';

export default function Landing() {
  const navigate = useNavigate();

  const features = [
    {
      icon: BarChart3,
      title: 'Asset Selection',
      description: 'Automatically selects optimal images using dual-axis scoring — aesthetic quality + semantic relevance.',
      color: 'text-blue-400'
    },
    {
      icon: FileText,
      title: 'Copy Generation',
      description: 'Platform-native LinkedIn & Instagram copy, distinct in tone and structure.',
      color: 'text-purple-400'
    },
    {
      icon: LayoutTemplate,
      title: 'Collage Builder',
      description: '4–6 image LinkedIn collages with dynamic grid layouts (2×2, 2×3, 3×2).',
      color: 'text-emerald-400'
    },
    {
      icon: Smartphone,
      title: 'Story Creator',
      description: '3–4 vertical Instagram Story frames with sequential narrative flow.',
      color: 'text-orange-400'
    },
    {
      icon: FileCheck,
      title: 'Case Study',
      description: 'Structured post-event documents with executive summary, engagement metrics & brand visibility.',
      color: 'text-pink-400'
    },
    {
      icon: ShieldCheck,
      title: 'QA Flagging',
      description: 'Low-confidence outputs are flagged — never forced — with full rationale.',
      color: 'text-cyan-400'
    }
  ];

  return (
    <div className="min-h-screen bg-background overflow-hidden">
      {/* Background Orbs */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-500/10 rounded-full blur-[120px] animate-pulse" style={{ animationDelay: '2s' }} />
      </div>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4">
        <div className="container mx-auto max-w-5xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-6">
              <Sparkles className="w-4 h-4" />
              <span>Next-Gen Content Engine</span>
            </div>
            <h1 className="text-6xl md:text-8xl font-bold tracking-tight mb-8 leading-[1.1]">
              Automate Your <br />
              <span className="text-gradient">Content Engine</span>
            </h1>
            <p className="text-xl text-muted-foreground mb-10 max-w-2xl mx-auto leading-relaxed">
              Transform raw event media into platform-ready marketing assets.
              High-fidelity outputs, zero manual effort.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button size="lg" className="h-14 px-8 text-lg rounded-full shadow-lg shadow-primary/25 group" onClick={() => navigate('/dashboard')}>
                Launch Dashboard
                <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Button>
              <Button size="lg" variant="outline" className="h-14 px-8 text-lg rounded-full glass hover:bg-white/5" onClick={() => navigate('/docs')}>
                Read Documentation
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 px-4 relative">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Powerful Features</h2>
            <p className="text-muted-foreground">Built for speed, accuracy, and aesthetic excellence.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="glass-card h-full hover:border-primary/50 transition-all group overflow-hidden border-white/5">
                  <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                    <feature.icon className="w-20 h-20" />
                  </div>
                  <CardHeader>
                    <div className={`w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform ${feature.color}`}>
                      <feature.icon className="h-6 w-6" />
                    </div>
                    <CardTitle className="text-xl group-hover:text-primary transition-colors">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats/Social Proof */}
      <section className="py-20 border-y border-white/5 bg-white/2">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { label: 'Processing Speed', value: '10x Faster', icon: Zap },
              { label: 'Media Assets', value: '500k+', icon: Globe },
              { label: 'Success Rate', value: '99.9%', icon: ShieldCheck },
              { label: 'User Rating', value: '4.9/5', icon: Sparkles },
            ].map((stat, i) => (
              <div key={i} className="space-y-2">
                <div className="flex justify-center mb-2">
                  <stat.icon className="w-5 h-5 text-primary/60" />
                </div>
                <div className="text-3xl font-bold">{stat.value}</div>
                <div className="text-sm text-muted-foreground uppercase tracking-wider font-medium">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-32 px-4 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto rounded-3xl bg-linear-to-br from-primary/20 to-blue-600/10 p-12 border border-white/10 relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(var(--primary-rgb),0.1),transparent)]" />
          <h2 className="text-4xl md:text-5xl font-bold mb-6 relative">Ready to amplify your presence?</h2>
          <p className="text-xl text-muted-foreground mb-10 max-w-2xl mx-auto relative">
            Join the elite teams automating their content pipeline with precision.
          </p>
          <Button size="lg" className="h-14 px-10 text-lg rounded-full relative" onClick={() => navigate('/dashboard')}>
            Get Started Now
          </Button>
        </motion.div>
      </section>

      <footer className="py-12 px-4 border-t border-white/5 text-center text-muted-foreground text-sm">
        <p>&copy; 2026 Content & Design Engine. All rights reserved.</p>
      </footer>
    </div>
  );
}
