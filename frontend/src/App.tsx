import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Layout from './components/layout/Layout';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import Sessions from './pages/Sessions';
import Outputs from './pages/Outputs';
import ApiDocs from './pages/ApiDocs';
import { AnimatePresence, motion } from 'motion/react';
import { Toaster } from 'sonner';
import './index.css';

function PageWrapper({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  );
}

function AnimatedRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Landing />} />
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<PageWrapper><Dashboard /></PageWrapper>} />
          <Route path="/sessions" element={<PageWrapper><Sessions /></PageWrapper>} />
          <Route path="/outputs" element={<PageWrapper><Outputs /></PageWrapper>} />
          <Route path="/docs" element={<PageWrapper><ApiDocs /></PageWrapper>} />
        </Route>
      </Routes>
    </AnimatePresence>
  );
}

function App() {
  return (
    <AppProvider>
      <Toaster theme="dark" position="bottom-right" richColors />
      <BrowserRouter>
        <AnimatedRoutes />
      </BrowserRouter>
    </AppProvider>
  );
}

export default App;
