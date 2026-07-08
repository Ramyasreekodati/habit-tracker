import { useState, useEffect } from 'react';

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const [activeTab, setActiveTab] = useState('home');
  const [nextTask, setNextTask] = useState<any>(null);
  const [learningDebt, setLearningDebt] = useState<any[]>([]);
  const [healthLogs, setHealthLogs] = useState<any[]>([]);
  const [careerLogs, setCareerLogs] = useState<any[]>([]);

  // Form State
  const [sleep, setSleep] = useState(7);
  const [water, setWater] = useState(8);
  const [walk, setWalk] = useState(45);
  const [newTopic, setNewTopic] = useState("");
  const [category, setCategory] = useState("Git Commit");
  const [description, setDescription] = useState("");
  const [resumeImpact, setResumeImpact] = useState("");

  const handleLogin = async (e: any) => {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const res = await fetch('http://localhost:8000/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
      } else {
        alert("Invalid credentials");
      }
    } catch (err) {
      console.error(err);
      alert("Failed to connect to backend");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  const authFetch = async (url: string, options: any = {}) => {
    if (!token) return null;
    options.headers = { ...options.headers, 'Authorization': `Bearer ${token}` };
    const res = await fetch(url, options);
    if (res.status === 401) handleLogout();
    return res;
  };

  const fetchData = async () => {
    if (!token) return;
    try {
      let r1 = await authFetch('http://localhost:8000/next-task/');
      if (r1?.ok) setNextTask(await r1.json());
      let r2 = await authFetch('http://localhost:8000/learning_debt/');
      if (r2?.ok) setLearningDebt(await r2.json());
      let r3 = await authFetch('http://localhost:8000/health/');
      if (r3?.ok) setHealthLogs(await r3.json());
      let r4 = await authFetch('http://localhost:8000/career/');
      if (r4?.ok) setCareerLogs(await r4.json());
    } catch (err) { console.error(err); }
  };

  useEffect(() => {
    fetchData();
  }, [token]);

  const handleHealthSubmit = async (e: any) => {
    e.preventDefault();
    await authFetch('http://localhost:8000/health/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date: new Date().toISOString().split('T')[0], sleep, water, walk, exercise: 0, meditation: 0 })
    });
    fetchData();
    alert("Health logged!");
  };

  const handleDebtSubmit = async (e: any) => {
    e.preventDefault();
    await authFetch('http://localhost:8000/learning_debt/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic: newTopic, status: '❌ Not Mastered' })
    });
    setNewTopic("");
    fetchData();
  };

  const handleCareerSubmit = async (e: any) => {
    e.preventDefault();
    await authFetch('http://localhost:8000/career/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date: new Date().toISOString().split('T')[0], category, description, resume_impact: resumeImpact })
    });
    setDescription("");
    setResumeImpact("");
    fetchData();
    alert("Output mapped to Resume!");
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center font-sans">
        <form onSubmit={handleLogin} className="bg-slate-800 p-8 rounded-xl shadow-2xl border border-slate-700 max-w-sm w-full">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <svg className="w-6 h-6 text-indigo-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
            GrowthOS Login
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-1">Username</label>
              <input type="text" value={username} onChange={e => setUsername(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded p-3 text-white" required />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Password</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded p-3 text-white" required />
            </div>
            <button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 rounded transition-all">Secure Login</button>
          </div>
        </form>
      </div>
    );
  }

  const avgSleep = healthLogs.length > 0 ? healthLogs.reduce((acc, curr) => acc + curr.sleep, 0) / healthLogs.length : 0;

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 font-sans selection:bg-indigo-500/30">
      <div className="max-w-3xl mx-auto p-6 pt-12 relative">
        <button onClick={handleLogout} className="absolute top-4 right-4 text-sm text-slate-500 hover:text-white">Logout</button>
        {/* Navigation */}
        <div className="flex space-x-2 mb-12 bg-slate-800/50 p-1.5 rounded-xl border border-slate-700/50 mt-4">
          {['home', 'health', 'learning', 'career'].map((tab) => (
            <button key={tab} onClick={() => setActiveTab(tab)}
              className={`flex-1 py-2 px-4 rounded-lg font-semibold text-sm transition-all duration-200 ${
                activeTab === tab ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 shadow-sm' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/30'
              }`}
            >
              {tab === 'home' ? '⚡ What\'s Next?' : tab === 'health' ? '🧘 Health' : tab === 'learning' ? '🧠 Learning' : '🚀 Career'}
            </button>
          ))}
        </div>

        {/* Home Tab */}
        {activeTab === 'home' && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            {nextTask ? (
              <div className="bg-indigo-500/5 border border-indigo-500/20 border-l-4 border-l-indigo-500 rounded-xl p-8 mb-8">
                <p className="text-indigo-400 font-bold uppercase tracking-wider text-xs mb-2">Current Task</p>
                <h2 className="text-3xl font-extrabold text-white mb-6 tracking-tight">{nextTask.current_task}</h2>
                <div className="grid grid-cols-2 gap-4 mb-8 text-sm">
                  <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800"><span className="text-slate-400 block mb-1">Expected Duration</span><span className="font-semibold">{nextTask.expected_duration}</span></div>
                  <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800"><span className="text-slate-400 block mb-1">Difficulty</span><span className="font-semibold text-rose-300">{nextTask.difficulty}</span></div>
                  <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800 col-span-2"><span className="text-slate-400 block mb-1">Reason (Learning Debt)</span><span className="font-semibold">{nextTask.reason}</span></div>
                </div>
                <button className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-4 px-6 rounded-lg transition-all flex items-center justify-center gap-2">
                  ✅ Mark Complete & Get Next Task
                </button>
              </div>
            ) : (<div className="text-center py-20 text-slate-500"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto mb-4"></div>Loading Secure Engine...</div>)}
            
            <div className="bg-slate-800/30 border border-slate-700/50 rounded-xl p-5 flex items-start gap-4">
              <div className="bg-amber-500/20 p-2 rounded-lg text-amber-400">💡</div>
              <div>
                <h4 className="text-amber-400 font-bold mb-1">Opportunity Cost Indicator</h4>
                <p className="text-sm text-slate-400">If you spend 2 hours on YouTube right now, you will lose the opportunity to complete 1 Project Feature or solve 8 SQL problems.</p>
              </div>
            </div>
          </div>
        )}

        {/* Health Tab */}
        {activeTab === 'health' && (
          <div className="animate-in fade-in space-y-6">
            {avgSleep > 0 && avgSleep < 6.5 && (
              <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 p-4 rounded-xl">
                🚨 <b>Recovery Warning:</b> Sleep average is {avgSleep.toFixed(1)}h. Recommendation: Reduce workload temporarily.
              </div>
            )}
            <form onSubmit={handleHealthSubmit} className="bg-slate-800/50 border border-slate-700/50 p-6 rounded-xl grid grid-cols-3 gap-4">
              <div><label className="block text-sm mb-1 text-slate-400">Sleep (hrs)</label><input type="number" step="0.5" value={sleep} onChange={e => setSleep(Number(e.target.value))} className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white" /></div>
              <div><label className="block text-sm mb-1 text-slate-400">Water (glasses)</label><input type="number" value={water} onChange={e => setWater(Number(e.target.value))} className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white" /></div>
              <div><label className="block text-sm mb-1 text-slate-400">Walk (mins)</label><input type="number" value={walk} onChange={e => setWalk(Number(e.target.value))} className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white" /></div>
              <button type="submit" className="col-span-3 bg-indigo-600 hover:bg-indigo-500 p-3 rounded font-bold mt-2">Log Fixed Habits</button>
            </form>
          </div>
        )}

        {/* Learning Tab */}
        {activeTab === 'learning' && (
          <div className="animate-in fade-in space-y-6">
            <div className="bg-slate-800/50 border border-slate-700/50 p-6 rounded-xl">
              <h3 className="text-lg font-bold mb-4">Learning Debt Status</h3>
              <div className="space-y-3">
                {learningDebt.map(debt => (
                  <div key={debt.id} className="flex items-center gap-3 bg-slate-900/50 p-3 rounded border border-slate-800">
                    <span className="text-xl">{debt.status.includes('✅') ? '✅' : '❌'}</span>
                    <span className="font-semibold">{debt.topic}</span>
                  </div>
                ))}
              </div>
              <form onSubmit={handleDebtSubmit} className="mt-6 flex gap-2">
                <input type="text" placeholder="New Topic to Master..." value={newTopic} onChange={e => setNewTopic(e.target.value)} className="flex-1 bg-slate-900 border border-slate-700 rounded p-3 text-white" required />
                <button type="submit" className="bg-indigo-600 hover:bg-indigo-500 px-6 rounded font-bold">Add Debt</button>
              </form>
            </div>
          </div>
        )}

        {/* Career Tab */}
        {activeTab === 'career' && (
          <div className="animate-in fade-in space-y-6">
            <form onSubmit={handleCareerSubmit} className="bg-slate-800/50 border border-slate-700/50 p-6 rounded-xl space-y-4">
              <h3 className="text-lg font-bold">Map Output to Resume</h3>
              <div><label className="block text-sm mb-1 text-slate-400">Category</label>
                <select value={category} onChange={e => setCategory(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded p-3 text-white">
                  <option>Git Commit</option><option>Project Feature</option><option>SQL Problem</option><option>Application</option>
                </select>
              </div>
              <div><label className="block text-sm mb-1 text-slate-400">Description</label>
                <input type="text" value={description} onChange={e => setDescription(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded p-3 text-white" required />
              </div>
              <div><label className="block text-sm mb-1 text-slate-400">Resume Impact (Translation)</label>
                <textarea value={resumeImpact} onChange={e => setResumeImpact(e.target.value)} rows={3} className="w-full bg-slate-900 border border-slate-700 rounded p-3 text-white" required placeholder="e.g. Built vector retrieval pipeline..."></textarea>
              </div>
              <button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-500 p-3 rounded font-bold">Log Output</button>
            </form>
          </div>
        )}

      </div>
    </div>
  );
}

export default App;
