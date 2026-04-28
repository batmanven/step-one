import { useState, useEffect, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'motion/react'
import {
  Image as ImageIcon,
  FileText,
  Download,
  ExternalLink,
  Share2,
  Camera,
  Layers,
  Loader2,
  Play,
  Calendar,
  Zap,
  Eye,
  XCircle
} from 'lucide-react'
import { apiRequest } from '@/lib/api'
import { toast } from 'sonner'

interface Output {
  id: string
  type: 'collage' | 'story' | 'case_study' | 'linkedin_post' | 'reel'
  title: string
  session_id: string
  created_at: string
  url?: string
  thumbnail?: string
  ratio: string
}

const TABS = ['all', 'collages', 'stories', 'reels', 'docs']

export default function Outputs() {
  const [searchParams] = useSearchParams()
  const sessionFilter = searchParams.get('session')
  
  const [outputs, setOutputs] = useState<Output[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('all')
  const [selectedDoc, setSelectedDoc] = useState<Output | null>(null)
  const [docContent, setDocContent] = useState('')
  const [fetchingDoc, setFetchingDoc] = useState(false)

  const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

  useEffect(() => {
    let mounted = true

    apiRequest('/api/v1/sessions')
      .then((data) => {
        const sessions = data.sessions || []

        const requests = sessions.map((session: any) =>
          apiRequest(`/api/v1/sessions/${session.session_id}/outputs`)
            .then((res) =>
              (res.outputs || []).map((o: any) => ({
                ...o,
                ratio: o.type === 'story' || o.type === 'reel'
                  ? 'aspect-[9/16]'
                  : 'aspect-video'
              }))
            )
            .catch(() => [])
        )

        return Promise.allSettled(requests).then((results) =>
          results.flatMap((r: any) => (r.status === 'fulfilled' ? r.value : []))
        )
      })
      .then((allOutputs) => {
        allOutputs.sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at))
        if (mounted) setOutputs(allOutputs)
      })
      .catch((err) => console.error(err))
      .finally(() => mounted && setLoading(false))

    return () => { mounted = false }
  }, [])

  const openDoc = async (o: Output) => {
    setSelectedDoc(o)
    setFetchingDoc(true)
    try {
      const res = await apiRequest(`/api/v1/sessions/text-content?path=${o.url}`)
      setDocContent(res.content || 'No content found.')
    } catch (e) {
      setDocContent('Failed to load document content.')
    } finally {
      setFetchingDoc(false)
    }
  }

  const filtered = useMemo(() => {
    let base = outputs
    if (sessionFilter) {
      base = base.filter(o => o.session_id === sessionFilter)
    }
    
    if (activeTab === 'all') return base
    if (activeTab === 'collages') return base.filter(o => o.type === 'collage')
    if (activeTab === 'stories') return base.filter(o => o.type === 'story')
    if (activeTab === 'reels') return base.filter(o => o.type === 'reel')
    if (activeTab === 'docs') return base.filter(o => o.type === 'case_study')
    return base
  }, [outputs, activeTab, sessionFilter])

  const getConfig = (type: Output['type']) => {
    switch (type) {
      case 'collage':
        return { icon: ImageIcon, label: 'Collage', color: 'text-blue-400' }
      case 'story':
        return { icon: Camera, label: 'Story', color: 'text-pink-400' }
      case 'reel':
        return { icon: Play, label: 'Reel', color: 'text-purple-400' }
      case 'case_study':
        return { icon: FileText, label: 'Doc', color: 'text-amber-400' }
      default:
        return { icon: Layers, label: 'Asset', color: 'text-white' }
    }
  }

  const renderAsset = (o: Output) => {
    const url = `${BASE_URL}${o.url}`

    if (o.type === 'case_study') {
      return (
        <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-amber-500/10 to-orange-500/5 border border-amber-500/10 p-8 text-center space-y-4">
          <div className="relative">
            <FileText className="h-16 w-16 text-amber-500" />
            <div className="absolute -top-2 -right-2 px-2 py-0.5 bg-amber-500 text-black text-[8px] font-black uppercase rounded">Draft</div>
          </div>
          <div>
            <p className="text-white font-bold tracking-tight">Technical Analysis</p>
            <p className="text-[10px] text-amber-500/60 uppercase font-bold tracking-widest mt-1">AI Generated Report</p>
          </div>
          <div className="flex gap-2">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-1 w-8 bg-amber-500/20 rounded-full" />
            ))}
          </div>
        </div>
      )
    }

    if (o.type === 'reel') {
      return (
        <video
          src={url}
          muted
          loop
          playsInline
          className="w-full h-full object-cover"
          onMouseEnter={(e) => e.currentTarget.play()}
          onMouseLeave={(e) => e.currentTarget.pause()}
        />
      )
    }

    return (
      <img
        src={url}
        alt={o.title}
        loading="lazy"
        className="w-full h-full object-cover"
      />
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-10 space-y-10">

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <p className="text-xs uppercase tracking-widest text-white/40 flex items-center gap-2">
            <Zap className="h-3 w-3" /> Outputs
          </p>
          <h1 className="text-4xl font-semibold text-white mt-1">Asset Gallery</h1>
        </div>

        <div className="flex items-center gap-4">
          <div className="px-4 py-2 bg-black/40 border border-white/5 rounded-xl">
            <p className="text-xs text-white/40">Total</p>
            <p className="text-white font-bold text-lg">{outputs.length}</p>
          </div>
          <button className="h-11 px-6 bg-white text-black rounded-full text-sm font-semibold">
            Export
          </button>
        </div>
      </div>

      <div className="flex justify-center">
        <div className="flex gap-2 bg-black/40 border border-white/5 p-1.5 rounded-full">
          {TABS.map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-5 h-10 rounded-full text-xs font-semibold capitalize transition ${activeTab === tab
                  ? 'bg-white text-black'
                  : 'text-white/50 hover:text-white'
                }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex flex-col items-center py-32 gap-4">
          <Loader2 className="h-10 w-10 animate-spin text-white/40" />
          <p className="text-white/40 text-sm">Loading assets...</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-32 border border-dashed border-white/10 rounded-2xl">
          <Layers className="mx-auto h-10 w-10 text-white/20 mb-3" />
          <p className="text-white text-lg">No {activeTab} found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence>
            {filtered.map((o, i) => {
              const cfg = getConfig(o.type)
              const Icon = cfg.icon
              const url = `${BASE_URL}${o.url}`

              return (
                <motion.div
                  key={o.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ delay: Math.min(i * 0.02, 0.15) }}
                >
                  <div className="group border border-white/5 rounded-2xl overflow-hidden bg-black/40 hover:border-white/20 transition">

                    <div className={`relative ${o.ratio}`}>
                      {renderAsset(o)}

                      <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition flex items-center justify-center gap-3">
                        <button
                          onClick={() => o.type === 'case_study' ? openDoc(o) : window.open(url, '_blank')}
                          className="h-10 px-4 bg-white text-black rounded-lg text-xs font-semibold flex items-center gap-2"
                        >
                          {o.type === 'case_study' ? <Eye className="h-3 w-3" /> : <Download className="h-3 w-3" />}
                          {o.type === 'case_study' ? 'View Report' : 'Download'}
                        </button>

                        <button
                          onClick={() => window.open(url, '_blank')}
                          className="h-10 px-4 bg-white/10 text-white rounded-lg text-xs flex items-center gap-2"
                        >
                          <ExternalLink className="h-3 w-3" />
                          File
                        </button>
                      </div>

                      <div className="absolute top-3 left-3 px-2 py-1 bg-black/70 rounded-full flex items-center gap-1 text-[10px]">
                        <Icon className={`h-3 w-3 ${cfg.color}`} />
                        <span>{cfg.label}</span>
                      </div>
                    </div>

                    <div className="p-4 space-y-2">
                      <p className="text-white text-sm font-medium truncate">{o.title}</p>

                      <div className="flex justify-between text-xs text-white/40">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(o.created_at).toLocaleDateString()}
                        </span>
                        <span>{o.session_id.split('_').pop()}</span>
                      </div>


                    </div>

                  </div>
                </motion.div>
              )
            })}
          </AnimatePresence>
        </div>
      )}

      {/* Doc Viewer Modal */}
      <AnimatePresence>
        {selectedDoc && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-10">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedDoc(null)}
              className="absolute inset-0 bg-void/90 backdrop-blur-xl"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-4xl max-h-full bg-dark-forest border border-white/10 rounded-3xl overflow-hidden shadow-2xl flex flex-col"
            >
              <div className="p-6 border-b border-white/5 flex items-center justify-between bg-black/20">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-amber-500/10 rounded-xl text-amber-500">
                    <FileText className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">{selectedDoc.title}</h3>
                    <p className="text-xs text-shade-70 uppercase tracking-widest font-bold mt-0.5">Post-Event Technical Analysis</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedDoc(null)}
                  className="p-2 hover:bg-white/10 rounded-full transition"
                >
                  <XCircle className="h-6 w-6 text-shade-70" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-8 md:p-12">
                {fetchingDoc ? (
                  <div className="flex flex-col items-center justify-center py-20 gap-4">
                    <Loader2 className="h-10 w-10 animate-spin text-amber-500" />
                    <p className="text-shade-50 animate-pulse">Decrypting analysis...</p>
                  </div>
                ) : (
                  <div className="prose prose-invert max-w-none">
                    <pre className="text-sm md:text-base text-shade-50 leading-relaxed whitespace-pre-wrap font-sans">
                      {docContent}
                    </pre>
                  </div>
                )}
              </div>

              <div className="p-6 border-t border-white/5 bg-black/20 flex items-center justify-between">
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(docContent)
                    toast.success('Report content copied to clipboard')
                  }}
                  className="h-12 px-8 bg-white text-black rounded-xl text-sm font-bold flex items-center gap-3 hover:bg-shade-50 transition active:scale-95"
                >
                  <Share2 className="h-4 w-4" />
                  Copy Analysis Content
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}