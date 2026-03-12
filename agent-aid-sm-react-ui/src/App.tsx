import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import ChatWindow from './components/ChatWindow';

function App() {
  console.log("App rendering");
  const [role, setRole] = useState('ProductOwner');
  const [initialQuery, setInitialQuery] = useState<string | undefined>(undefined);

  const handleQuickQuery = (query: string) => {
    setInitialQuery(query);
    // Reset it shortly so it doesn't re-trigger if role changes
    setTimeout(() => setInitialQuery(undefined), 100);
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar
        currentRole={role}
        setRole={setRole}
        onQueryClick={handleQuickQuery}
      />

      <main className="ml-64 pb-24">
        <Dashboard role={role} />
      </main>

      <ChatWindow role={role} externalQuery={initialQuery} />
    </div>
  );
}

export default App;
