import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { AlertTriangle, Check, X, ShieldAlert, BadgeCheck } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

interface FlaggedItem {
  _id: string
  output_type: string
  flag_reason: string
  confidence_score: number
}

export default function ReviewQueue() {
  const [flaggedItems, setFlaggedItems] = useState<FlaggedItem[]>([
    { _id: '1', output_type: 'case_study', flag_reason: 'Confidence score below threshold', confidence_score: 0.75 },
    { _id: '2', output_type: 'linkedin', flag_reason: 'Potential hallucination detected', confidence_score: 0.68 },
    { _id: '3', output_type: 'instagram_stories', flag_reason: 'Semantic accuracy concerns', confidence_score: 0.72 },
  ])

  const handleApprove = (id: string) => {
    setFlaggedItems(prev => prev.filter(item => item._id !== id))
  }

  const handleReject = (id: string) => {
    setFlaggedItems(prev => prev.filter(item => item._id !== id))
  }

  return (
    <div className="glass-card border-white/5 rounded-3xl overflow-hidden">
      <div className="p-8 border-b border-white/5 bg-white/2">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-yellow-500/10 text-yellow-500">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-xl font-bold tracking-tight">Human-in-the-Loop Queue</h3>
            <p className="text-sm text-muted-foreground mt-0.5">High-confidence flagging for manual intervention</p>
          </div>
        </div>
      </div>
      <div className="divide-y divide-white/5">
        <AnimatePresence mode="popLayout">
          {flaggedItems.length > 0 ? (
            flaggedItems.map((item, i) => (
              <motion.div
                key={item._id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ delay: i * 0.1 }}
                className="p-6 hover:bg-white/2 transition-colors group"
              >
                <div className="flex items-start justify-between gap-6">
                  <div className="flex-1 space-y-3">
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-lg capitalize">{item.output_type.replace('_', ' ')}</span>
                      <Badge variant="outline" className="bg-red-500/10 text-red-400 border-red-500/20 text-[10px] uppercase tracking-widest px-2 py-0">
                        Flagged
                      </Badge>
                    </div>
                    
                    <div className="flex items-center gap-2 text-sm text-muted-foreground bg-white/5 p-3 rounded-xl border border-white/5">
                      <AlertTriangle className="w-4 h-4 text-yellow-500 shrink-0" />
                      {item.flag_reason}
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-1.5 bg-white/5 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-red-500 rounded-full" 
                            style={{ width: `${item.confidence_score * 100}%` }} 
                          />
                        </div>
                        <span className="text-xs font-mono text-muted-foreground">
                          Confidence: <span className="text-red-400 font-bold">{(item.confidence_score * 100).toFixed(0)}%</span>
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col sm:flex-row gap-2 self-center">
                    <Button
                      onClick={() => handleApprove(item._id)}
                      variant="outline"
                      className="rounded-xl border-white/10 hover:bg-emerald-500/10 hover:text-emerald-400 hover:border-emerald-500/20 px-6 h-10"
                    >
                      <Check className="mr-2 h-4 w-4" />
                      Authorize
                    </Button>
                    <Button
                      onClick={() => handleReject(item._id)}
                      variant="outline"
                      className="rounded-xl border-white/10 hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/20 px-6 h-10"
                    >
                      <X className="mr-2 h-4 w-4" />
                      Discard
                    </Button>
                  </div>
                </div>
              </motion.div>
            ))
          ) : (
            <div className="py-20 text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto">
                <BadgeCheck className="w-8 h-8 text-emerald-500" />
              </div>
              <div>
                <p className="text-lg font-bold">Queue is clear</p>
                <p className="text-sm text-muted-foreground">All items have been verified and processed.</p>
              </div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
