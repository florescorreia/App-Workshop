import React,{useEffect,useState,createContext,useContext} from 'react';
import {createRoot} from 'react-dom/client';
import {BrowserRouter,Routes,Route,NavLink,Link,useLocation} from 'react-router-dom';
import '@fontsource/inter/400.css';import '@fontsource/inter/500.css';import '@fontsource/inter/600.css';import '@fontsource/inter/700.css';
import './style.css';
import {api,send,setSession,RecordData} from './api';
import {ErrorBox,Field} from './components';
import {Overview,Ideas,Pipeline,MyWork,Value,Process,Settings} from './pages';
import {IdeaWorkspace,NewIdea} from './workspace';
import {Guide} from './guide';
import {RemovedIdeas} from './ideaRemoval';

export const AppContext=createContext<{user:RecordData;refs:RecordData;refreshRefs:()=>Promise<void>}>({user:{},refs:{},refreshRefs:async()=>{}});
export const useApp=()=>useContext(AppContext);
function App(){
 const [session,sessionSet]=useState<RecordData|null>(null),[loading,setLoading]=useState(true),[error,setError]=useState(''),[refs,setRefs]=useState<RecordData|null>(null);
 const [email,setEmail]=useState(''),[password,setPassword]=useState(''),[busy,setBusy]=useState(false),[nav,setNav]=useState(false);
 const refreshRefs=async()=>setRefs(await api('/references'));
 useEffect(()=>{api('/session/me').then(data=>{setSession(data);sessionSet(data);return refreshRefs();}).catch(()=>{}).finally(()=>setLoading(false));},[]);
 async function login(e:React.FormEvent){e.preventDefault();setBusy(true);setError('');try{const data=await send('/session/login',{email,password});setSession(data);await refreshRefs();sessionSet(data);setPassword('');}catch(e){setError(String((e as Error).message));}finally{setBusy(false);}}
 async function logout(){try{await send('/session/logout',{});sessionSet(null);setRefs(null);}catch(e){setError((e as Error).message);}}
 if(loading)return <div className="loading">Opening IdeaFlow…</div>;
 if(!session)return <div className="login-shell"><div className="login-story"><div className="brand"><span className="brand-mark">↗</span> IdeaFlow</div><h1>Good ideas.<br/>Clear ownership.<br/><em>Measured value.</em></h1><p>One shared workspace to turn improvement opportunities into lasting results.</p><div className="login-stages">Capture → Develop → Deliver → Verify</div></div><main className="login-card"><span className="eyebrow">YOUR IMPROVEMENT WORKSPACE</span><h2>Welcome back</h2><p>Sign in to your local IdeaFlow workspace.</p><form onSubmit={login}><Field label="Email"><input type="email" autoComplete="username" required value={email} onChange={e=>setEmail(e.target.value)}/></Field><Field label="Password"><input type="password" autoComplete="current-password" required value={password} onChange={e=>setPassword(e.target.value)}/></Field><ErrorBox error={error}/><button className="primary wide" disabled={busy}>{busy?'Signing in…':'Sign in →'}</button></form><small>Your work stays in this workspace.</small></main></div>;
 if(!refs)return <div className="loading">Loading reference lists…</div>;
 return <AppContext.Provider value={{user:session.user,refs,refreshRefs}}><div className={'app-shell '+(nav?'nav-open':'')}><aside className="sidebar"><Link className="brand" to="/"><span className="brand-mark">↗</span> IdeaFlow</Link><div className="sidebar-caption">IDEAS INTO VALUE</div><nav>{[['/','Overview','◫'],['/ideas','Ideas','◇'],['/my-work','My Work','✓'],['/pipeline','Pipeline','▥'],['/process','Process','⇄'],['/value','Value','$'],['/guide','Walkthrough','?'],['/settings','Settings','⚙']].map(([to,label,icon])=><NavLink key={to} to={to} end={to==='/'||to==='/ideas'} onClick={()=>setNav(false)}><span aria-hidden>{icon}</span>{label}</NavLink>)}</nav><div className="sidebar-footer"><div className="avatar">{session.user.name[0]}</div><div><strong>{session.user.name}</strong><small>{session.user.role}</small></div><button aria-label="Sign out" title="Sign out" onClick={logout}>↪</button></div></aside><div className="content-shell"><header className="topbar"><button className="nav-toggle" aria-label="Toggle navigation" onClick={()=>setNav(!nav)}>☰</button><span>Improvement portfolio <span className="topbar-muted">/ Local workspace</span></span><Link className="button primary" to="/ideas/new">＋ New idea</Link></header><main className="main"><ErrorBox error={error}/><Routes><Route path="/" element={<Overview/>}/><Route path="/ideas" element={<Ideas/>}/><Route path="/ideas/new" element={<NewIdea/>}/><Route path="/ideas/:id" element={<IdeaWorkspace/>}/><Route path="/my-work" element={<MyWork/>}/><Route path="/pipeline" element={<Pipeline/>}/><Route path="/process" element={<Process/>}/><Route path="/value" element={<Value/>}/><Route path="/guide" element={<Guide/>}/><Route path="/removed-ideas" element={<RemovedIdeas/>}/><Route path="/settings" element={<Settings/>}/><Route path="*" element={<div><h1>Page not found</h1><Link to="/">Return to Overview</Link></div>}/></Routes></main><footer className="footer">IdeaFlow · USD · {session.timezone} <span>From possibility to proof</span></footer></div></div></AppContext.Provider>;
}
createRoot(document.getElementById('root')!).render(<BrowserRouter><App/></BrowserRouter>);
