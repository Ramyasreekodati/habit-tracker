import { useState, useEffect, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const [activeTab, setActiveTab] = useState('home');
  const [nextTask, setNextTask] = useState<any>(null);
  const [oppCost, setOppCost] = useState<string>("");
  const [learningDebt, setLearningDebt] = useState<any[]>([]);
  const [sessions, setSessions] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [careerLogs, setCareerLogs] = useState<any[]>([]);

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
    authFetch('http://localhost:8000/engine/next-task').then(r => r?.json()).then(setNextTask);
    authFetch('http://localhost:8000/engine/opportunity-cost').then(r => r?.json()).then(d => setOppCost(d?.message));
    authFetch('http://localhost:8000/learning_state/').then(r => r?.json()).then(setLearningDebt);
    authFetch('http://localhost:8000/sessions/').then(r => r?.json()).then(setSessions);
    authFetch('http://localhost:8000/projects/').then(r => r?.json()).then(setProjects);
    authFetch('http://localhost:8000/career/').then(r => r?.json()).then(setCareerLogs);
  };

  useEffect(() => { fetchData(); }, [token]);

  // Session Timer Logic
  const [timerActive, setTimerActive] = useState(false);
  const [sessionSeconds, setSessionSeconds] = useState(0);
  const [sessionTopic, setSessionTopic] = useState("");
  const intervalRef = useRef<any>(null);

  const toggleTimer = () => {
    if (timerActive) {
      clearInterval(intervalRef.current);
      setTimerActive(false);
      // Log session
      const mins = Math.floor(sessionSeconds / 60);
      const outQ = prompt("How many problems/features did you complete?");
      authFetch('http://localhost:8000/sessions/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ date: new Date().toISOString().split('T')[0], topic: sessionTopic, start_time: "Started", end_time: "Ended", duration_minutes: mins, output_quantity: Number(outQ) })
      }).then(() => { setSessionSeconds(0); fetchData(); });
    } else {
      setTimerActive(true);
      intervalRef.current = setInterval(() => setSessionSeconds(s => s + 1), 1000);
    }
  };

  // Learning State Form
  const [newTopic, setNewTopic] = useState("");
  const [diff, setDiff] = useState(5);
  const [imp, setImp] = useState(5);
  const [freq, setFreq] = useState(5);

  const addLearningTopic = (e: any) => {
    e.preventDefault();
    authFetch('http://localhost:8000/learning_state/', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ topic: newTopic, difficulty: diff, importance: imp, interview_frequency: freq, pipeline_stage: "Learn" })
    }).then(() => { setNewTopic(""); fetchData(); });
  };

  // Career Form
  const [careerCat, setCareerCat] = useState("Project Feature");
  const [careerDesc, setCareerDesc] = useState("");
  const [careerImpact, setCareerImpact] = useState("");

  const handleAIImpact = async () => {
    const res = await authFetch('http://localhost:8000/engine/generate-resume', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ text: careerDesc })
    });
    if (res?.ok) {
      const data = await res.json();
      setCareerImpact(data.resume_bullet);
    }
  };

  const addCareerOutput = (e: any) => {
    e.preventDefault();
    authFetch('http://localhost:8000/career/', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ date: new Date().toISOString().split('T')[0], category: careerCat, description: careerDesc, resume_impact: careerImpact })
    }).then(() => { setCareerDesc(""); setCareerImpact(""); fetchData(); });
  };

  if (!token) return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center font-sans text-white">
      <form onSubmit={handleLogin} className="bg-slate-800 p-8 rounded-xl border border-slate-700 w-96 space-y-4">
        <h2 className="text-xl font-bold">GrowthOS V9</h2>
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
          <h1 className="text-2xl font-black tracking-tight text-white">GrowthOS <span className="text-indigo-500 text-sm align-top">V9</span></h1>
          <button onClick={()=>{localStorage.removeItem('token'); setToken(null);}} className="text-slate-500 text-sm">Logout</button>
        </div>

        {/* 5 Layer Navigation */}
        <div className="flex overflow-x-auto gap-2 mb-8 bg-slate-800/30 p-2 rounded-xl border border-slate-700/50">
          {[
            {id: 'home', label: '⚡ Next'},
            {id: 'analytics', label: '📈 Analytics'},
            {id: 'health', label: 'L1 Health'},
            {id: 'learning', label: 'L2 Learning'},
            {id: 'sessions', label: 'L3 Sessions'},
            {id: 'projects', label: 'L4 Projects'},
            {id: 'career', label: 'L5 Career'}
          ].map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={`whitespace-nowrap px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
                activeTab === t.id ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' : 'text-slate-400 hover:bg-slate-700/30'
              }`}>
              {t.label}
            </button>
          ))}
        </div>

        {/* Next Task Engine */}
        {activeTab === 'home' && (
          <div className="animate-in fade-in space-y-6">
            {nextTask && (
              <div className="bg-indigo-500/10 border-l-4 border-indigo-500 rounded-r-xl p-6">
                <p className="text-indigo-400 text-xs font-bold uppercase mb-2">Priority Calculation: {nextTask.priority_score}</p>
                <h2 className="text-3xl font-extrabold mb-4">{nextTask.current_task}</h2>
                <div className="flex gap-4 text-sm text-slate-300 mb-6">
                  <div className="bg-slate-800 px-3 py-1 rounded">Stage: {nextTask.pipeline_stage}</div>
                  <div className="bg-slate-800 px-3 py-1 rounded">{nextTask.reason}</div>
                </div>
                
                <div className="bg-slate-900 border border-slate-700 p-4 rounded-xl flex items-center justify-between">
                  <div>
                    <input type="text" placeholder="Session Topic" value={sessionTopic} onChange={e=>setSessionTopic(e.target.value)} className="bg-slate-800 text-white p-2 rounded border border-slate-700 mr-4" />
                    <span className="font-mono text-xl text-indigo-400">{Math.floor(sessionSeconds/60)}:{('0'+(sessionSeconds%60)).slice(-2)}</span>
                  </div>
                  <button onClick={toggleTimer} className={`px-6 py-2 rounded font-bold ${timerActive ? 'bg-rose-600' : 'bg-emerald-600'}`}>
                    {timerActive ? 'Stop Session & Log' : 'Start Deep Work'}
                  </button>
                </div>
              </div>
            )}
            <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700 flex items-center gap-4">
              <div className="text-amber-500">💡</div>
              <div className="text-sm font-semibold text-slate-300">{oppCost}</div>
            </div>
          </div>
        )}

        {/* Layer 2: Learning */}
        {activeTab === 'learning' && (
          <div className="animate-in fade-in space-y-6">
            <form onSubmit={addLearningTopic} className="bg-slate-800/50 p-6 rounded-xl border border-slate-700 grid grid-cols-4 gap-4">
              <div className="col-span-4 font-bold">Add Learning Topic</div>
              <input type="text" placeholder="Topic (e.g. Window Functions)" value={newTopic} onChange={e=>setNewTopic(e.target.value)} className="col-span-4 p-2 bg-slate-900 rounded border border-slate-700" required />
              <div><label className="text-xs text-slate-400">Difficulty (1-10)</label><input type="number" value={diff} onChange={e=>setDiff(Number(e.target.value))} className="w-full p-2 bg-slate-900 rounded border border-slate-700"/></div>
              <div><label className="text-xs text-slate-400">Importance (1-10)</label><input type="number" value={imp} onChange={e=>setImp(Number(e.target.value))} className="w-full p-2 bg-slate-900 rounded border border-slate-700"/></div>
              <div><label className="text-xs text-slate-400">Freq in Interviews (1-10)</label><input type="number" value={freq} onChange={e=>setFreq(Number(e.target.value))} className="w-full p-2 bg-slate-900 rounded border border-slate-700"/></div>
              <div className="flex items-end"><button type="submit" className="w-full p-2 bg-indigo-600 rounded font-bold hover:bg-indigo-500">Add</button></div>
            </form>

            <div className="space-y-2">
              {learningDebt.map(t => (
                <div key={t.id} className="bg-slate-800 p-4 rounded-xl flex justify-between items-center border border-slate-700">
                  <div>
                    <h3 className="font-bold">{t.topic}</h3>
                    <p className="text-xs text-slate-400">Priority: {t.difficulty * t.importance * t.interview_frequency} | Stage: {t.pipeline_stage}</p>
                  </div>
                  <div className="flex gap-2">
                    {['Learn', 'Implement', 'Test', 'Review', 'Master'].map(stage => (
                      <button key={stage} onClick={() => authFetch(`http://localhost:8000/learning_state/${t.id}/pipeline?pipeline_stage=${stage}`, {method:'PUT'}).then(fetchData)} className={`px-2 py-1 text-xs rounded ${t.pipeline_stage === stage ? 'bg-indigo-500 text-white' : 'bg-slate-700 text-slate-400'}`}>{stage}</button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Layer 3: Sessions */}
        {activeTab === 'sessions' && (
          <div className="animate-in fade-in space-y-4">
            <h2 className="font-bold text-xl">Historical Deep Work</h2>
            {sessions.map(s => (
              <div key={s.id} className="bg-slate-800 p-4 rounded-xl flex justify-between items-center border border-slate-700">
                <div>
                  <h3 className="font-bold">{s.topic}</h3>
                  <p className="text-xs text-slate-400">{s.date} | {s.duration_minutes} mins</p>
                </div>
                <div className="bg-indigo-500/20 text-indigo-300 font-bold px-4 py-2 rounded-lg text-sm">
                  Output: {s.output_quantity}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Layer 5: Career */}
        {activeTab === 'career' && (
          <div className="animate-in fade-in space-y-6">
            <form onSubmit={addCareerOutput} className="bg-slate-800/50 p-6 rounded-xl border border-slate-700 space-y-4">
              <h2 className="font-bold text-xl">Log Output & GenAI Resume</h2>
              <input type="text" placeholder="What did you do? (e.g. Built RAG chatbot using Langchain)" value={careerDesc} onChange={e=>setCareerDesc(e.target.value)} className="w-full p-2 bg-slate-900 rounded border border-slate-700" required />
              
              <div className="flex gap-2">
                <button type="button" onClick={handleAIImpact} className="bg-emerald-600/20 text-emerald-400 border border-emerald-600/30 font-bold px-4 py-2 rounded flex-1">✨ Generate AI Resume Bullet</button>
              </div>

              <textarea value={careerImpact} onChange={e=>setCareerImpact(e.target.value)} placeholder="AI will generate professional impact here..." className="w-full p-2 bg-slate-900 rounded border border-slate-700 h-24"></textarea>
              <button type="submit" className="w-full p-3 bg-indigo-600 hover:bg-indigo-500 rounded font-bold">Commit to Career Timeline</button>
            </form>
          </div>
        )}

        {/* Analytics Dashboard */}
        {activeTab === 'analytics' && (
          <div className="animate-in fade-in space-y-6">
            <div className="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
              <h2 className="font-bold text-xl mb-4">Output Velocity Over Time</h2>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={sessions.slice().reverse()}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="date" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px' }} />
                    <Line type="monotone" dataKey="output_quantity" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default App;
