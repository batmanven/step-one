import { useNavigate } from 'react-router-dom';
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
      color: 'text-blue-500'
    },
    {
      icon: FileText,
      title: 'Copy Generation',
      description: 'Platform-native LinkedIn & Instagram copy, distinct in tone and structure.',
      color: 'text-purple-500'
    },
    {
      icon: LayoutTemplate,
      title: 'Collage Builder',
      description: '4–6 image LinkedIn collages with dynamic grid layouts (2×2, 2×3, 3×2).',
      color: 'text-emerald-500'
    },
    {
      icon: Smartphone,
      title: 'Story Creator',
      description: '3–4 vertical Instagram Story frames with sequential narrative flow.',
      color: 'text-orange-500'
    },
    {
      icon: FileCheck,
      title: 'Case Study',
      description: 'Structured post-event documents with executive summary, engagement metrics & brand visibility.',
      color: 'text-pink-500'
    },
    {
      icon: ShieldCheck,
      title: 'QA Flagging',
      description: 'Low-confidence outputs are flagged — never forced — with full rationale.',
      color: 'text-cyan-500'
    }
  ];

  return (
    <div className="min-h-screen bg-void overflow-hidden selection:bg-neon-green selection:text-black">
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10">
        <div className="absolute top-[-10%] left-[-10%] w-[60%] h-[60%] bg-blue-600/5 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[60%] h-[60%] bg-neon-green/5 rounded-full blur-[120px]" />
      </div>

      <nav className="h-20 flex items-center justify-between px-10 border-b border-white/5 bg-void/50 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-3 group cursor-pointer" onClick={() => navigate('/')}>

          <span className="text-sm font-bold text-white uppercase tracking-widest">Content Engine</span>
        </div>
        <div className="flex items-center gap-8">
          <button onClick={() => navigate('/docs')} className="text-xs font-bold text-shade-50 hover:text-white uppercase tracking-widest transition-colors">Documentation</button>
          <button onClick={() => navigate('/dashboard')} className="btn-pill bg-white text-black text-xs font-bold uppercase tracking-widest hover:opacity-90">Enter System</button>
        </div>
      </nav>

      <section className="relative pt-40 pb-32 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          >


            <h1 className="text-7xl md:text-[110px] font-light tracking-tighter mb-10 leading-[0.95] text-white">
              Automate Your <br />
              <span className="text-blue-500">Content Machine.</span>
            </h1>

            <p className="text-xl md:text-2xl text-shade-50 mb-14 max-w-3xl mx-auto leading-relaxed font-light">
              Transform raw event media into platform-ready marketing assets. <br className="hidden md:block" />
              High-fidelity outputs, absolute precision, zero manual friction.
            </p>

            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
              <button
                onClick={() => navigate('/dashboard')}
                className="btn-pill h-16 px-16 bg-blue-600 text-white text-sm font-bold uppercase tracking-widest hover:bg-blue-500 shadow-2xl shadow-blue-900/40 flex items-center gap-4 group"
              >
                Launch Dashboard
                <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
              </button>
              <button
                onClick={() => navigate('/docs')}
                className="btn-pill h-16 px-16 border border-white/10 text-white text-sm font-bold uppercase tracking-widest hover:bg-white/5 transition-all"
              >
                Technical Docs
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="py-40 px-4 bg-dark-forest/30 border-y border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-24">
            <h2 className="text-[11px] font-bold text-blue-500 uppercase tracking-[0.4em] mb-4">Core Intelligence</h2>
            <h3 className="text-5xl font-light text-white tracking-tight">Built for aesthetic excellence.</h3>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="shopify-card p-10 group relative overflow-hidden"
              >
                <div className="absolute -right-8 -bottom-8 opacity-[0.02] group-hover:opacity-[0.05] transition-opacity">
                  <feature.icon className="w-40 h-40 text-white" />
                </div>

                <div className={`w-14 h-14 rounded-2xl bg-void border border-white/5 flex items-center justify-center mb-8 group-hover:scale-110 group-hover:border-blue-500/30 transition-all ${feature.color}`}>
                  <feature.icon className="h-6 w-6" />
                </div>

                <h4 className="text-xl font-medium text-white mb-4 group-hover:text-blue-400 transition-colors">{feature.title}</h4>
                <p className="text-shade-50 text-sm leading-relaxed font-medium">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-32 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-12 text-center">
            {[
              { label: 'Latency', value: '< 2.4s', icon: Zap },
              { label: 'Datasets', value: '1,200+', icon: Globe },
              { label: 'Precision', value: '99.9%', icon: ShieldCheck },
              { label: 'Confidence', value: 'High', icon: Sparkles },
            ].map((stat, i) => (
              <div key={i} className="space-y-3">
                <div className="flex justify-center mb-4">
                  <stat.icon className="w-5 h-5 text-blue-500" />
                </div>
                <div className="text-4xl font-light text-white">{stat.value}</div>
                <div className="text-[10px] text-shade-70 uppercase tracking-[0.2em] font-bold">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-40 px-4 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="max-w-5xl mx-auto shopify-card p-24 bg-linear-to-br from-blue-600/10 to-transparent border-white/10"
        >
          <h2 className="text-5xl md:text-6xl font-light text-white mb-8 tracking-tight">Ready to activate?</h2>
          <p className="text-xl text-shade-50 mb-12 max-w-2xl mx-auto font-light leading-relaxed">
            Join the elite teams automating their content pipeline with surgical precision and aesthetic excellence.
          </p>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-pill h-16 px-14 bg-white text-black text-sm font-bold uppercase tracking-widest hover:opacity-90 shadow-2xl shadow-white/10"
          >
            Access the Dashboard
          </button>
        </motion.div>
      </section>

      <footer className="py-16 px-10 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-6">
        <div className="flex items-center gap-3">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600/20">
            <Sparkles className="h-4 w-4 text-blue-500" />
          </div>
          <span className="text-[10px] font-bold text-white uppercase tracking-widest">Content & Design Engine</span>
        </div>
        <p className="text-[10px] text-shade-70 uppercase tracking-widest font-bold">&copy; 2026 StepOne AI. All rights reserved.</p>
      </footer>
    </div>
  );
}
