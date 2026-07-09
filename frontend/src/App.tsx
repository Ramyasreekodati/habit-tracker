import { useState, useEffect } from 'react';
import { Target, CheckCircle2, Circle, Clock, ArrowRight, BarChart3, LayoutDashboard, BrainCircuit, Save, Sparkles, AlertTriangle, Lightbulb } from 'lucide-react';
import { BarChart, Bar, PieChart, Pie, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import CalendarHeatmap from 'react-calendar-heatmap';
import 'react-calendar-heatmap/dist/styles.css';

function App() {
  const [habits, setHabits] = useState<any[]>([]);
  const [habitLogs, setHabitLogs] = useState<Record<number, any>>({});
  const [allLogs, setAllLogs] = useState<any[]>([]);
  const [hanseiData, setHanseiData] = useState<any[]>([]);
  const [aiInsights, setAiInsights] = useState<any>(null);
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Hansei Form State
  const [hanseiForm, setHanseiForm] = useState({
    finished: '',
    distracted: '',
    mistake: '',
    change_tomorrow: ''
  });
  
  const today = new Date().toISOString().split('T')[0];

  const fetchData = async () => {
    fetch('http://localhost:8000/habits/').then(r => r.json()).then(setHabits);
    
    fetch(`http://localhost:8000/habit_logs/`).then(r => r.json()).then(data => {
      setAllLogs(data);
      const todayLogs = data.filter((l: any) => l.date === today);
      const logsMap: Record<number, any> = {};
      todayLogs.forEach((log: any) => {
        logsMap[log.habit_id] = { completed: log.completed, duration: log.duration };
      });
      setHabitLogs(logsMap);
    });

    fetch(`http://localhost:8000/hansei/`).then(r => r.json()).then(data => {
      setHanseiData(data);
      const todayHansei = data.find((d: any) => d.date === today);
      if (todayHansei) {
        setHanseiForm({
          finished: todayHansei.finished,
          distracted: todayHansei.distracted,
          mistake: todayHansei.mistake,
          change_tomorrow: todayHansei.change_tomorrow
        });
      }
    });
  };

  useEffect(() => {
    fetchData();
  }, [today]);

  const toggleHabit = async (habitId: number, currentStatus: boolean, duration: number = 0) => {
    const newStatus = !currentStatus;
    setHabitLogs({ ...habitLogs, [habitId]: { completed: newStatus, duration } });
    
    await fetch('http://localhost:8000/habit_logs/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ habit_id: habitId, date: today, completed: newStatus, duration })
    });
    fetch(`http://localhost:8000/habit_logs/`).then(r => r.json()).then(setAllLogs);
  };

  const updateDuration = async (habitId: number, completed: boolean, duration: number) => {
    setHabitLogs({ ...habitLogs, [habitId]: { completed, duration } });
    await fetch('http://localhost:8000/habit_logs/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ habit_id: habitId, date: today, completed, duration })
    });
    fetch(`http://localhost:8000/habit_logs/`).then(r => r.json()).then(setAllLogs);
  };

  const saveHansei = async () => {
    await fetch('http://localhost:8000/hansei/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        date: today,
        ...hanseiForm
      })
    });
    fetchData();
  };

  const fetchAiInsights = async () => {
    setIsAiLoading(true);
    try {
      const res = await fetch('http://localhost:8000/ai/analyze');
      const data = await res.json();
      setAiInsights(data);
    } catch (e) {
      console.error(e);
    }
    setIsAiLoading(false);
  };

  useEffect(() => {
    if (activeTab === 'ai' && !aiInsights) {
      fetchAiInsights();
    }
  }, [activeTab]);

  const categories = ['Career', 'MBA', 'Discipline', 'Bad Habits'];
  const COLORS = ['#3b82f6', '#10b981', '#a855f7', '#ef4444', '#f59e0b', '#ec4899'];

  // Analytics Computation
  const studyHoursMap: Record<string, number> = {};
  allLogs.forEach(log => {
    const habit = habits.find(h => h.id === log.habit_id);
    if (habit && (habit.category === 'Career' || habit.category === 'MBA') && log.duration > 0) {
      studyHoursMap[habit.name] = (studyHoursMap[habit.name] || 0) + (log.duration / 60);
    }
  });
  const studyData = Object.keys(studyHoursMap).map(k => ({ name: k, value: parseFloat(studyHoursMap[k].toFixed(2)) }));

  const completionData = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const dateStr = d.toISOString().split('T')[0];
    const dayLogs = allLogs.filter(l => l.date === dateStr && l.completed);
    const positiveLogs = dayLogs.filter(l => {
      const h = habits.find(x => x.id === l.habit_id);
      return h && h.category !== 'Bad Habits';
    });
    const totalPositive = habits.filter(h => h.category !== 'Bad Habits').length || 1;
    completionData.push({
      date: d.toLocaleDateString('en-US', { weekday: 'short' }),
      score: Math.round((positiveLogs.length / totalPositive) * 100)
    });
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-gray-300 font-sans pb-20 selection:bg-gray-700">
      {/* Navigation & Ikigai */}
      <div className="bg-[#111111] border-b border-gray-800/60 shadow-md sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-8 pt-6 pb-0 flex flex-col gap-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-8">
            <div>
              <h1 className="text-3xl font-black text-white tracking-tight flex items-baseline gap-3">
                Ikigai <span className="text-red-600/80 font-medium text-lg tracking-widest">生き甲斐</span>
              </h1>
              <div className="text-sm text-gray-400 mt-2">Mission: Become an AI Engineer.</div>
            </div>
            <div className="flex gap-1 overflow-x-auto scrollbar-hide">
              <button 
                onClick={() => setActiveTab('dashboard')}
                className={`px-4 py-2.5 rounded-t-lg font-semibold tracking-wide flex items-center gap-2 transition-colors whitespace-nowrap ${
                  activeTab === 'dashboard' ? 'bg-gray-800 text-white border-b-2 border-indigo-500' : 'text-gray-500 hover:text-gray-300 hover:bg-gray-900'
                }`}
              >
                <LayoutDashboard className="w-4 h-4" /> Dashboard
              </button>
              <button 
                onClick={() => setActiveTab('analytics')}
                className={`px-4 py-2.5 rounded-t-lg font-semibold tracking-wide flex items-center gap-2 transition-colors whitespace-nowrap ${
                  activeTab === 'analytics' ? 'bg-gray-800 text-white border-b-2 border-emerald-500' : 'text-gray-500 hover:text-gray-300 hover:bg-gray-900'
                }`}
              >
                <BarChart3 className="w-4 h-4" /> Analytics
              </button>
              <button 
                onClick={() => setActiveTab('hansei')}
                className={`px-4 py-2.5 rounded-t-lg font-semibold tracking-wide flex items-center gap-2 transition-colors whitespace-nowrap ${
                  activeTab === 'hansei' ? 'bg-gray-800 text-white border-b-2 border-amber-500' : 'text-gray-500 hover:text-gray-300 hover:bg-gray-900'
                }`}
              >
                <BrainCircuit className="w-4 h-4" /> Hansei
              </button>
              <button 
                onClick={() => setActiveTab('ai')}
                className={`px-4 py-2.5 rounded-t-lg font-semibold tracking-wide flex items-center gap-2 transition-colors whitespace-nowrap ${
                  activeTab === 'ai' ? 'bg-gray-800 text-white border-b-2 border-blue-500' : 'text-gray-500 hover:text-gray-300 hover:bg-gray-900'
                }`}
              >
                <Sparkles className="w-4 h-4" /> AI Coach
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto p-8 pt-10">
        
        {/* SURVIVAL DASHBOARD */}
        {activeTab === 'dashboard' && (
          <div className="animate-in fade-in zoom-in-95 duration-300">
            <div className="mb-8 border-b border-gray-800/60 pb-4 flex justify-between items-end">
              <div>
                <h2 className="text-2xl font-bold text-white tracking-tight">Today's Kaizen</h2>
                <p className="text-gray-500 text-sm mt-1">Focus on the 1% improvement.</p>
              </div>
              <div className="text-sm font-semibold text-indigo-400">
                {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {categories.map(category => {
                const categoryHabits = habits.filter(h => h.category === category);
                if (categoryHabits.length === 0) return null;
                const needsTimeTrack = category === 'Career' || category === 'MBA';
                
                return (
                  <div key={category} className="bg-[#111111] p-6 rounded-2xl border border-gray-800/40 shadow-xl">
                    <h3 className="text-lg font-semibold text-gray-200 mb-5 flex items-center gap-3">
                      {category === 'Career' && <Target className="w-5 h-5 text-blue-400/80" />}
                      {category === 'MBA' && <CheckCircle2 className="w-5 h-5 text-emerald-400/80" />}
                      {category === 'Discipline' && <Clock className="w-5 h-5 text-purple-400/80" />}
                      {category === 'Bad Habits' && <ArrowRight className="w-5 h-5 text-red-400/80" />}
                      {category}
                    </h3>
                    <div className="space-y-3">
                      {categoryHabits.map(habit => {
                        const logData = habitLogs[habit.id] || { completed: false, duration: 0 };
                        const isCompleted = logData.completed;
                        const duration = logData.duration;

                        return (
                          <div key={habit.id} className={`flex items-center gap-3 p-3 rounded-xl border transition-all duration-300 ${
                              isCompleted 
                                ? (category === 'Bad Habits' ? 'bg-red-950/20 border-red-900/30' : 'bg-emerald-950/20 border-emerald-900/30')
                                : 'bg-[#1a1a1a] border-gray-800'
                            }`}>
                            
                            <button 
                              onClick={() => toggleHabit(habit.id, isCompleted, duration)}
                              className="flex-1 flex items-center justify-between text-left group"
                            >
                              <span className={`font-medium tracking-wide ${isCompleted && category !== 'Bad Habits' ? 'line-through opacity-50 text-emerald-400' : 'text-gray-300'} ${isCompleted && category === 'Bad Habits' ? 'text-red-400' : ''}`}>
                                {habit.name}
                              </span>
                              {isCompleted ? (
                                <CheckCircle2 className={`w-5 h-5 transition-transform scale-110 ${category === 'Bad Habits' ? 'text-red-500' : 'text-emerald-500'}`} />
                              ) : (
                                <Circle className="w-5 h-5 text-gray-600 group-hover:text-gray-400 transition-colors" />
                              )}
                            </button>

                            {needsTimeTrack && (
                              <div className="flex items-center gap-2 border-l border-gray-700/50 pl-3">
                                <input 
                                  type="number" 
                                  placeholder="0"
                                  min="0"
                                  value={duration || ''}
                                  onChange={(e) => updateDuration(habit.id, isCompleted, parseInt(e.target.value) || 0)}
                                  className="w-16 bg-[#222] border border-gray-700 rounded px-2 py-1 text-sm text-center text-gray-300 focus:outline-none focus:border-indigo-500"
                                />
                                <span className="text-xs text-gray-500">min</span>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ANALYTICS DASHBOARD */}
        {activeTab === 'analytics' && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="bg-[#111111] p-6 rounded-2xl border border-gray-800/40 shadow-xl">
                <h3 className="font-bold text-gray-200 mb-6 tracking-tight flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-indigo-400" /> Daily Completion Rate (%)
                </h3>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={completionData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                      <XAxis dataKey="date" stroke="#666" tick={{fill: '#888', fontSize: 12}} />
                      <YAxis stroke="#666" domain={[0, 100]} tick={{fill: '#888', fontSize: 12}} />
                      <Tooltip contentStyle={{backgroundColor: '#1a1a1a', border: '1px solid #333', borderRadius: '8px'}} />
                      <Bar dataKey="score" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="bg-[#111111] p-6 rounded-2xl border border-gray-800/40 shadow-xl">
                <h3 className="font-bold text-gray-200 mb-6 tracking-tight flex items-center gap-2">
                  <PieChart className="w-5 h-5 text-emerald-400" /> Study Hours Distribution
                </h3>
                <div className="h-64 flex justify-center items-center">
                  {studyData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie data={studyData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                          {studyData.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                        </Pie>
                        <Tooltip contentStyle={{backgroundColor: '#1a1a1a', border: '1px solid #333', borderRadius: '8px'}} />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="text-gray-500 text-sm">No study time logged yet.</div>
                  )}
                </div>
              </div>
            </div>

            <div className="bg-[#111111] p-6 rounded-2xl border border-gray-800/40 shadow-xl">
              <h3 className="font-bold text-gray-200 mb-6 tracking-tight">Consistency Heatmap (Deep Work)</h3>
              <div className="text-sm px-4">
                <CalendarHeatmap
                  startDate={new Date(new Date().setMonth(new Date().getMonth() - 3))}
                  endDate={new Date()}
                  values={allLogs.filter(l => l.completed).map(l => ({ date: l.date, count: 1 }))}
                  classForValue={(value) => {
                    if (!value || value.count === 0) return 'color-empty';
                    return `color-github-3`;
                  }}
                />
              </div>
            </div>
          </div>
        )}

        {/* HANSEI REFLECTION */}
        {activeTab === 'hansei' && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="mb-8 border-b border-gray-800/60 pb-4">
              <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                Hansei Reflection <span className="text-amber-500/80 font-medium text-lg tracking-widest ml-2">反省</span>
              </h2>
              <p className="text-gray-500 text-sm mt-1">Honest self-reflection and learning from mistakes. (Takes 5 mins)</p>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              
              <div className="bg-[#111111] p-6 rounded-2xl border border-gray-800/40 shadow-xl">
                <h3 className="text-lg font-semibold text-gray-200 mb-6 flex items-center gap-2">
                  <BrainCircuit className="w-5 h-5 text-amber-500" /> Evening Checkout
                </h3>
                
                <div className="space-y-5">
                  <div>
                    <label className="block text-sm font-medium text-emerald-400 mb-2">1. What did I finish today?</label>
                    <textarea 
                      className="w-full bg-[#1a1a1a] border border-gray-700 rounded-lg p-3 text-sm text-gray-300 focus:outline-none focus:border-amber-500 h-24"
                      placeholder="e.g. Completed 2 SQL problems and watched MBA lecture."
                      value={hanseiForm.finished}
                      onChange={e => setHanseiForm({...hanseiForm, finished: e.target.value})}
                    ></textarea>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-red-400 mb-2">2. What distracted me today?</label>
                    <textarea 
                      className="w-full bg-[#1a1a1a] border border-gray-700 rounded-lg p-3 text-sm text-gray-300 focus:outline-none focus:border-amber-500 h-24"
                      placeholder="e.g. Mindless scrolling on Twitter for an hour."
                      value={hanseiForm.distracted}
                      onChange={e => setHanseiForm({...hanseiForm, distracted: e.target.value})}
                    ></textarea>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-purple-400 mb-2">3. What mistake did I repeat?</label>
                    <textarea 
                      className="w-full bg-[#1a1a1a] border border-gray-700 rounded-lg p-3 text-sm text-gray-300 focus:outline-none focus:border-amber-500 h-24"
                      placeholder="e.g. Trying to study on the couch instead of at my desk."
                      value={hanseiForm.mistake}
                      onChange={e => setHanseiForm({...hanseiForm, mistake: e.target.value})}
                    ></textarea>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-blue-400 mb-2">4. What will I change tomorrow?</label>
                    <textarea 
                      className="w-full bg-[#1a1a1a] border border-gray-700 rounded-lg p-3 text-sm text-gray-300 focus:outline-none focus:border-amber-500 h-24"
                      placeholder="e.g. Leave my phone in the kitchen while studying."
                      value={hanseiForm.change_tomorrow}
                      onChange={e => setHanseiForm({...hanseiForm, change_tomorrow: e.target.value})}
                    ></textarea>
                  </div>

                  <button 
                    onClick={saveHansei}
                    className="w-full bg-amber-600 hover:bg-amber-500 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition-colors mt-4"
                  >
                    <Save className="w-5 h-5" /> Save Reflection
                  </button>
                </div>
              </div>

              <div className="bg-[#111111] p-6 rounded-2xl border border-gray-800/40 shadow-xl overflow-hidden flex flex-col h-[800px]">
                <h3 className="text-lg font-semibold text-gray-200 mb-6 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-gray-400" /> Reflection History
                </h3>
                <div className="flex-1 overflow-y-auto pr-2 space-y-4">
                  {hanseiData.length === 0 ? (
                    <div className="text-center text-gray-500 mt-10">No reflections logged yet.</div>
                  ) : (
                    hanseiData.map(log => (
                      <div key={log.id} className="bg-[#1a1a1a] border border-gray-800 rounded-xl p-4">
                        <div className="font-bold text-amber-500 border-b border-gray-700 pb-2 mb-3">
                          {new Date(log.date).toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
                        </div>
                        <div className="space-y-3 text-sm">
                          {log.finished && <div><span className="text-emerald-400 font-medium">Finished:</span> <span className="text-gray-400">{log.finished}</span></div>}
                          {log.distracted && <div><span className="text-red-400 font-medium">Distracted:</span> <span className="text-gray-400">{log.distracted}</span></div>}
                          {log.mistake && <div><span className="text-purple-400 font-medium">Mistake:</span> <span className="text-gray-400">{log.mistake}</span></div>}
                          {log.change_tomorrow && <div><span className="text-blue-400 font-medium">Change:</span> <span className="text-gray-400">{log.change_tomorrow}</span></div>}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* AI COACH */}
        {activeTab === 'ai' && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="mb-8 border-b border-gray-800/60 pb-4">
              <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                AI Coach <span className="text-blue-500/80 font-medium text-lg tracking-widest ml-2">知能</span>
              </h2>
              <p className="text-gray-500 text-sm mt-1">Autonomous pattern and risk detection engine.</p>
            </div>

            {isAiLoading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
              </div>
            ) : aiInsights ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                
                <div className="bg-[#111111] p-6 rounded-2xl border border-blue-900/40 shadow-xl">
                  <h3 className="text-lg font-semibold text-blue-400 mb-6 flex items-center gap-2">
                    <BrainCircuit className="w-5 h-5" /> Detected Patterns
                  </h3>
                  <ul className="space-y-4">
                    {aiInsights.patterns.map((p: string, i: number) => (
                      <li key={i} className="flex items-start gap-3 text-sm text-gray-300">
                        <span className="text-blue-500 font-bold mt-0.5">•</span>
                        {p}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-[#111111] p-6 rounded-2xl border border-red-900/40 shadow-xl">
                  <h3 className="text-lg font-semibold text-red-400 mb-6 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5" /> Burnout & Risks
                  </h3>
                  <ul className="space-y-4">
                    {aiInsights.risks.map((p: string, i: number) => (
                      <li key={i} className="flex items-start gap-3 text-sm text-gray-300">
                        <span className="text-red-500 font-bold mt-0.5">•</span>
                        {p}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-[#111111] p-6 rounded-2xl border border-emerald-900/40 shadow-xl">
                  <h3 className="text-lg font-semibold text-emerald-400 mb-6 flex items-center gap-2">
                    <Lightbulb className="w-5 h-5" /> Recommendations
                  </h3>
                  <ul className="space-y-4">
                    {aiInsights.recommendations.map((p: string, i: number) => (
                      <li key={i} className="flex items-start gap-3 text-sm text-gray-300">
                        <span className="text-emerald-500 font-bold mt-0.5">→</span>
                        {p}
                      </li>
                    ))}
                  </ul>
                </div>

              </div>
            ) : (
              <div className="flex justify-center items-center h-64 text-gray-500">
                Failed to load insights.
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}

export default App;
