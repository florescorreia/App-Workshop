import React,{useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';
type Session={email:string;role:string;csrf:string;title:string};
type Note={id:string;body:string;record_version:number};
function App(){
 const [session,setSession]=useState<Session|null>(null),[email,setEmail]=useState(''),[password,setPassword]=useState(''),[error,setError]=useState(''),[notes,setNotes]=useState<Note[]>([]),[body,setBody]=useState(''),[loading,setLoading]=useState(true),[busy,setBusy]=useState(false);
 async function api(path:string,data?:unknown){const response=await fetch('/api'+path,{method:data===undefined?'GET':'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':session?.csrf||''},body:data===undefined?undefined:JSON.stringify(data)});const result=await response.json();if(!response.ok)throw new Error(typeof result.detail==='string'?result.detail:'Check the form and retry');return result;}
 useEffect(()=>{api('/session/me').then(setSession).catch(()=>{}).finally(()=>setLoading(false));},[]);
 useEffect(()=>{if(session)api('/notes').then(setNotes).catch(e=>setError(e.message));},[session]);
 async function login(event:React.FormEvent){event.preventDefault();setBusy(true);setError('');try{setSession(await api('/session/login',{email,password}));setPassword('');}catch(e){setError((e as Error).message);}finally{setBusy(false);}}
 async function save(event:React.FormEvent){event.preventDefault();setBusy(true);setError('');try{const note=await api('/notes',{body});setNotes([...notes,note]);setBody('');}catch(e){setError((e as Error).message);}finally{setBusy(false);}}
 if(loading)return <main><p>Opening your workspace…</p></main>;
 return <main><header><h1>{session?.title||'{{APP_TITLE}}'}</h1>{session&&<button onClick={async()=>{try{await api('/session/logout',{});setSession(null);setNotes([]);}catch(e){setError((e as Error).message);}}}>Sign out</button>}</header>{error&&<p role="alert">{error}</p>}{!session?<form onSubmit={login}><h2>Sign in</h2><label>Email<input type="email" autoComplete="username" required value={email} onChange={e=>setEmail(e.target.value)}/></label><label>Password<input type="password" autoComplete="current-password" required value={password} onChange={e=>setPassword(e.target.value)}/></label><button disabled={busy}>Sign in</button></form>:<><p>Signed in as {session.email}</p><section><h2>Your notes</h2>{notes.length?<ul>{notes.map(note=><li key={note.id}>{note.body}</li>)}</ul>:<p>No notes yet. Add your first note when ready.</p>}<form onSubmit={save}><label>New note<textarea required maxLength={2000} value={body} onChange={e=>setBody(e.target.value)}/></label><button disabled={busy}>Save note</button></form></section></>}</main>;
}
createRoot(document.getElementById('root')!).render(<App/>);
