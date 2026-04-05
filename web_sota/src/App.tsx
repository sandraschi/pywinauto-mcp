import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/app-layout';
import { Dashboard } from '@/pages/dashboard';
import { Windows } from '@/pages/windows';
import { Elements } from '@/pages/elements';
import { Biometrics } from '@/pages/biometrics';
import { Settings } from '@/pages/settings';
import { Help } from '@/pages/help';
import { Tools } from '@/pages/tools';
import { Chat } from '@/pages/chat';

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/windows" element={<Windows />} />
          <Route path="/elements" element={<Elements />} />
          <Route path="/biometrics" element={<Biometrics />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/tools" element={<Tools />} />
          <Route path="/help" element={<Help />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
