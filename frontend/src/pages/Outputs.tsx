import { useState, useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { motion, AnimatePresence } from 'motion/react'
import {
  Image as ImageIcon,
  FileText,
  Download,
  ExternalLink,
  Share2,
  Camera,
  Layers,
  Loader2
} from 'lucide-react'
import { apiRequest } from '@/lib/api'

interface Output {
  id: string
  type: 'collage' | 'story' | 'case_study' | 'linkedin_post'
  title: string
  session_id: string
  created_at: string
  url?: string
  thumbnail?: string
  ratio: string
}

export default function Outputs() {
  const [outputs, setOutputs] = useState<Output[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiRequest('/api/v1/sessions')
      .then((data) => {
        const sessions = data.sessions || []
        const outputPromises = sessions.map((session: any) =>
          apiRequest(`/api/v1/sessions/${session.session_id}/outputs`)
            .then((outputData) => {
              const sessionOutputs = outputData.outputs || []
              return sessionOutputs.map((o: any) => ({
                ...o,
                ratio: o.type === 'story' ? 'aspect-[9/16]' : 'aspect-video'
              }))
            })
            .catch(() => [])
        )

        return Promise.all(outputPromises).then((results) =>
          results.flat()
        )
      })
      .then((allOutputs) => setOutputs(allOutputs))
      .catch(() => { })
      .finally(() => setLoading(false))
  }, [])

  const getOutputConfig = (type: Output['type']) => {
    switch (type) {
      case 'collage':
        return { icon: ImageIcon, label: 'Collage' }
      case 'story':
        return { icon: Camera, label: 'Story' }
      case 'case_study':
        return { icon: FileText, label: 'Case Study' }
      case 'linkedin_post':
        return { icon: Share2, label: 'LinkedIn' }
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8 py-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-light text-white">Assets</h1>
          <p className="text-shade-50 text-sm">All generated content in one place</p>
        </div>
        <button className="h-10 px-5 rounded-full bg-white text-black text-xs font-semibold hover:bg-white/90 transition">
          Export All
        </button>
      </div>

      <Tabs defaultValue="all" className="space-y-6">
        <div className="sticky top-16 z-20 bg-void/80 backdrop-blur-md py-3 border-b border-white/5">
          <TabsList className="bg-dark-forest border border-white/5 p-1 rounded-full h-11">
            <TabsTrigger
              value="all"
              className="
rounded-full px-6 text-xs font-semibold
text-shade-50

data-[state=active]:bg-white
data-[state=active]:text-black
data-[state=active]:hover:bg-white
data-[state=active]:hover:text-black

data-[state=inactive]:hover:bg-white/10
data-[state=inactive]:hover:text-white

transition
"
            >
              All
            </TabsTrigger>

            <TabsTrigger
              value="collages"
              className="
rounded-full px-6 text-xs font-semibold
text-shade-50

data-[state=active]:bg-white
data-[state=active]:text-black
data-[state=active]:hover:bg-white
data-[state=active]:hover:text-black

data-[state=inactive]:hover:bg-white/10
data-[state=inactive]:hover:text-white

transition
"
            >
              Collages
            </TabsTrigger>

            <TabsTrigger
              value="stories"
              className="
rounded-full px-6 text-xs font-semibold
text-shade-50

data-[state=active]:bg-white
data-[state=active]:text-black
data-[state=active]:hover:bg-white
data-[state=active]:hover:text-black

data-[state=inactive]:hover:bg-white/10
data-[state=inactive]:hover:text-white

transition
"
            >
              Stories
            </TabsTrigger>

            <TabsTrigger
              value="documents"
              className="
rounded-full px-6 text-xs font-semibold
text-shade-50

data-[state=active]:bg-white
data-[state=active]:text-black
data-[state=active]:hover:bg-white
data-[state=active]:hover:text-black

data-[state=inactive]:hover:bg-white/10
data-[state=inactive]:hover:text-white

transition
"
            >
              Docs
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="all" className="mt-0">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-24 gap-4">
              <Loader2 className="h-10 w-10 animate-spin text-white" />
              <p className="text-shade-50 text-sm">Loading assets...</p>
            </div>
          ) : outputs.length === 0 ? (
            <div className="text-center py-24 space-y-4">
              <Layers className="h-10 w-10 mx-auto text-shade-70" />
              <p className="text-white">No assets yet</p>
            </div>
          ) : (
            <div className="columns-1 md:columns-2 lg:columns-3 gap-6 space-y-6">
              <AnimatePresence>
                {outputs.map((output, i) => {
                  const config = getOutputConfig(output.type)
                  const Icon = config.icon

                  return (
                    <motion.div
                      key={output.id}
                      initial={{ opacity: 0, y: 16 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.04 }}
                      className="break-inside-avoid"
                    >
                      <div className="bg-dark-forest border border-white/5 rounded-2xl overflow-hidden group hover:border-white/10 transition">
                        <div className={`relative ${output.ratio} bg-black/40 overflow-hidden`}>
                          {output.url && (
                            <img
                              src={`http://localhost:8000${output.url}`}
                              alt={output.title}
                              className="w-full h-full object-cover transition duration-500 group-hover:scale-105"
                            />
                          )}

                          <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition flex items-end p-4">
                            <div className="flex gap-2 w-full">
                              <button
                                className="flex-1 h-10 rounded-lg bg-white text-black text-xs font-medium flex items-center justify-center gap-2 hover:bg-white/90"
                                onClick={() => output.url && window.open(`http://localhost:8000${output.url}`, '_blank')}
                              >
                                <Download className="h-3.5 w-3.5" />
                                Download
                              </button>

                              <button
                                className="h-10 w-10 rounded-lg bg-white/10 text-white flex items-center justify-center hover:bg-white/20"
                                onClick={() => output.url && window.open(`http://localhost:8000${output.url}`, '_blank')}
                              >
                                <ExternalLink className="h-4 w-4" />
                              </button>
                            </div>
                          </div>
                        </div>

                        <div className="p-4">
                          <h3 className="text-sm text-white font-medium">
                            {output.title}
                          </h3>
                          <p className="text-[10px] text-shade-70 mt-1">
                            {output.session_id.slice(-6)}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  )
                })}
              </AnimatePresence>
            </div>
          )}
        </TabsContent>

        <TabsContent value="collages" className="mt-0" />
        <TabsContent value="stories" className="mt-0" />
        <TabsContent value="documents" className="mt-0" />
      </Tabs>
    </div>
  )
}