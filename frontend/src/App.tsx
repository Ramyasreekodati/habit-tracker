import { useState, useEffect, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import CalendarHeatmap from 'react-calendar-heatmap';
import 'react-calendar-heatmap/dist/styles.css';

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const [activeTab, setActiveTab] = useState('mission');
  const [dailyMissions, setDailyMissions] = useState<any[]>([]);
  const [weeklyTargets, setWeeklyTargets] = useState<any[]>([]);
  const [monthlyGoals, setMonthlyGoals] = useState<any[]>([]);
  const [staleTasks, setStaleTasks] = useState<string[]>([]);
  const [learningDebt, setLearningDebt] = useState<any[]>([]);
  const [sessions, setSessions] = useState<any[]>([]);

  // Auth fetch wrapper
  const authFetch = async (url: string, options: any = {}) => {
    if (!token) return null;
    options.headers = { ...options.headers, 'Authorization': `Bearer ${token}` };
    const res = await fetch(url, options);
    if (res.status === 401) {
      localStorage.removeItem('token');
      setToken(null);
    }
    return res;
  };

  const handleLogin = async (e: any) => {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    try {
      const res = await fetch('http://localhost:8000/token', { method: 'POST', body: formData });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
      } else alert("Invalid credentials");
    } catch (err) { alert("Failed to connect to backend"); }
  };

  const fetchData = async () => {
    if (!token) return;
    authFetch('http://localhost:8000/mission/daily').then(r => r?.json()).then(setDailyMissions);
    authFetch('http://localhost:8000/mission/weekly').then(r => r?.json()).then(setWeeklyTargets);
    authFetch('http://localhost:8000/mission/monthly').then(r => r?.json()).then(setMonthlyGoals);
    authFetch('http://localhost:8000/engine/stale-tasks').then(r => r?.json()).then(d => setStaleTasks(d?.stale_tasks || []));
    authFetch('http://localhost:8000/learning_state/').then(r => r?.json()).then(setLearningDebt);
    authFetch('http://localhost:8000/sessions/').then(r => r?.json()).then(setSessions);
  };

  useEffect(() => { fetchData(); }, [token]);

  const generateSchedule = async () => {
    await authFetch('http://localhost:8000/engine/generate-schedule', { method: 'POST' });
    fetchData();
  };

  if (!token) return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center font-sans text-white">
      <form onSubmit={handleLogin} className="bg-slate-800 p-8 rounded-xl border border-slate-700 w-96 space-y-4">
        <h2 className="text-xl font-bold">GrowthOS V10</h2>
        <input type="text" placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} className="w-full p-2 bg-slate-900 rounded border border-slate-700" />
        <input type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} className="w-full p-2 bg-slate-900 rounded border border-slate-700" />
        <button type="submit" className="w-full p-2 bg-indigo-600 rounded font-bold hover:bg-indigo-500">Login</button>
      </form>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 font-sans pb-20">
      <div className="max-w-4xl mx-auto p-4 pt-10">
        
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-black tracking-tight text-white">GrowthOS <span className="text-indigo-500 text-sm align-top">V10</span></h1>
          <button onClick={()=>{localStorage.removeItem('token'); setToken(null);}} className="text-slate-500 text-sm">Logout</button>
        </div>

        {/* Navigation */}
        <div className="flex overflow-x-auto gap-2 mb-8 bg-slate-800/30 p-2 rounded-xl border border-slate-700/50">
          {[
            {id: 'mission', label: '🎯 Mission'},
            {id: 'analytics', label: '📈 Analytics'},
            {id: 'learning', label: 'L2 Learning'},
            {id: 'sessions', label: 'L3 Sessions'}
          ].map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={`whitespace-nowrap px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
                activeTab === t.id ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' : 'text-slate-400 hover:bg-slate-700/30'
              }`}>
              {t.label}
            </button>
          ))}
        </div>

        {/* 🎯 MISSION PLANNER */}
        {activeTab === 'mission' && (
          <div className="animate-in fade-in space-y-8">
            
            <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
              <div className="flex justify-between items-center mb-6">
                <h2 className="font-bold text-xl">Today's Mission</h2>
                <button onClick={generateSchedule} className="bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded text-sm font-bold">Auto-Generate Schedule</button>
              </div>
              <div className="space-y-3">
                {dailyMissions.length === 0 ? <p className="text-slate-400 text-sm">No schedule for today. Click generate.</p> : null}
                {dailyMissions.map((m, i) => (
                  <div key={i} className="flex gap-4 items-center bg-slate-900 p-3 rounded border border-slate-700">
                    <div className="font-mono text-indigo-400 text-sm w-16">{m.start_time}</div>
                    <div className="flex-1 font-semibold">{m.task}</div>
                    <div className="text-xs bg-slate-800 px-2 py-1 rounded text-slate-400">{m.category}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-8">
              <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
                <h2 className="font-bold text-xl mb-6">This Week</h2>
                <div className="space-y-4">
                  {weeklyTargets.map((w, i) => (
                    <div key={i}>
                      <div className="flex justify-between text-sm mb-1">
                        <span>{w.category}</span>
                        <span className="text-slate-400">{w.completed} / {w.target}</span>
                      </div>
                      <div className="w-full bg-slate-900 rounded-full h-2 border border-slate-700">
                        <div className="bg-indigo-500 h-2 rounded-full" style={{width: `${Math.min((w.completed/w.target)*100, 100)}%`}}></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
                <h2 className="font-bold text-xl mb-6">This Month</h2>
                <div className="space-y-4">
                  {monthlyGoals.map((m, i) => (
                    <div key={i} className="bg-slate-900 p-3 rounded border border-slate-700">
                      <div className="font-semibold">{m.goal}</div>
                      <div className="text-sm text-slate-400 flex justify-between mt-1">
                        <span>Metric: {m.target_value}</span>
                        <span className="text-indigo-400">{m.current_value}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

          </div>
        )}

        {/* Learning Debt */}
        {activeTab === 'learning' && (
          <div className="animate-in fade-in space-y-6">
            {staleTasks.length > 0 && (
              <div className="bg-rose-500/10 border border-rose-500/30 p-4 rounded-xl text-rose-400">
                <span className="font-bold">🚨 Aging Tasks Detected:</span> The following tasks have been sitting for >30 days with no recent review: {staleTasks.join(', ')}
              </div>
            )}
            
            <div className="space-y-2">
              {learningDebt.map(t => (
                <div key={t.id} className="bg-slate-800 p-4 rounded-xl flex justify-between items-center border border-slate-700">
                  <div>
                    <h3 className="font-bold">{t.topic}</h3>
                    <p className="text-xs text-slate-400">Target: {t.target_completion_date || 'None'} | Stage: {t.pipeline_stage}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analytics Dashboard */}
        {activeTab === 'analytics' && (
          <div className="animate-in fade-in space-y-6">
            <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
              <h2 className="font-bold text-xl mb-4">Deep Work Consistency Heatmap</h2>
              <div className="text-sm">
                <CalendarHeatmap
                  startDate={new Date(new Date().setMonth(new Date().getMonth() - 3))}
                  endDate={new Date()}
                  values={sessions.map(s => ({ date: s.session_date, count: s.output_quantity }))}
                  classForValue={(value) => {
                    if (!value || value.count === 0) return 'color-empty';
                    return `color-github-${Math.min(value.count, 4)}`;
                  }}
                />
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default App;
