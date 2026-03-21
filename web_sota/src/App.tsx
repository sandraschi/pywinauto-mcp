import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/app-layout';
import { Dashboard } from '@/pages/dashboard';
import { Windows } from '@/pages/windows';
import { Elements } from '@/pages/elements';
import { Biometrics } from '@/pages/biometrics';
import { Settings } from '@/pages/settings';
import { Tools } from '@/pages/tools';
import { Control } from '@/pages/control'; // Fallback
import { Visualizer } from '@/pages/visualizer'; // Fallback
import { Chat } from '@/pages/chat'; // Fallback

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/windows" element={<Windows />} />
          <Route path="/elements" element={<Elements />} />
          <Route path="/biometrics" element={<Biometrics />} />
          <Route path="/control" element={<Control />} />
          <Route path="/visualizer" element={<Visualizer />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/tools" element={<Tools />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
