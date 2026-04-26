import React, { useState } from 'react';
import './index.css';

function App() {
  const [view, setView] = useState('landing');
  const [token, setToken] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [company, setCompany] = useState('');
  const [useCase, setUseCase] = useState('');
  const [selectedWorkflow, setSelectedWorkflow] = useState('inbox_autopilot');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      const res = await fetch('http://localhost:8000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        setToken(data.access_token);
        setView('dashboard');
      } else { alert("Invalid credentials"); }
    } catch (err) { alert("Backend not running"); }
  };

  const handleWaitlist = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/api/waitlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, company_name: company, use_case: useCase, selected_agent: selectedWorkflow, estimated_volume: 'starter' })
      });
      if (res.ok) { alert("You're on the list! We'll reach out shortly."); setView('landing'); }
    } catch (err) { alert("Backend not running"); }
  };

  const renderNav = () => (
    <nav className="nav">
      <div className="nav-brand" onClick={() => setView('landing')} style={{cursor:'pointer'}}>
        <span className="mushroom-icon">🍄</span> SPORLYWORKS
      </div>
      <div className="nav-links">
        <a href="#how" onClick={() => setView('landing')}>How It Works</a>
        <a href="#pricing" onClick={() => setView('landing')}>Pricing</a>
        {token
          ? <a href="#" onClick={() => setView('dashboard')}>Dashboard</a>
          : <a href="#" onClick={() => setView('login')}>Client Login</a>}
      </div>
    </nav>
  );

  if (view === 'login') return (
    <div className="container">
      {renderNav()}
      <section className="hero" style={{maxWidth:'400px',margin:'0 auto',textAlign:'left'}}>
        <h1>Client Access</h1>
        <form onSubmit={handleLogin} style={{display:'flex',flexDirection:'column',gap:'1rem',marginTop:'2rem'}}>
          <input type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required />
          <input type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} required />
          <button type="submit" className="btn-primary">Log In</button>
        </form>
      </section>
    </div>
  );

  if (view === 'waitlist') return (
    <div className="container">
      {renderNav()}
      <section className="hero" style={{maxWidth:'500px',margin:'0 auto',textAlign:'left'}}>
        <h1>Get Started</h1>
        <p>Pick a workflow. Connect your accounts. It starts working tomorrow.</p>
        <form onSubmit={handleWaitlist} style={{display:'flex',flexDirection:'column',gap:'1rem',marginTop:'2rem'}}>
          <input type="text" placeholder="Company or Name" value={company} onChange={e=>setCompany(e.target.value)} required />
          <input type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} required />
          <label style={{fontWeight:'bold',marginTop:'0.5rem'}}>Which workflow do you need?</label>
          <select value={selectedWorkflow} onChange={e=>setSelectedWorkflow(e.target.value)} style={{padding:'0.75rem',borderRadius:'4px',border:'1px solid #ccc'}}>
            <option value="inbox_autopilot">Inbox Autopilot</option>
            <option value="lead_qualifier">Lead Qualifier</option>
            <option value="ops_monitor">Ops Monitor</option>
          </select>
          <textarea placeholder="Anything else we should know?" value={useCase} onChange={e=>setUseCase(e.target.value)} rows={3} />
          <button type="submit" className="btn-primary">Join Waitlist</button>
        </form>
      </section>
    </div>
  );

  if (view === 'dashboard' && token) return (
    <div className="container">
      {renderNav()}
      <section className="hero" style={{textAlign:'left'}}>
        <h1>Welcome back.</h1>
        <p>Your workflows are running.</p>
        <div className="features-grid" style={{marginTop:'2rem'}}>
          <div className="feature-card"><h3>Inbox Autopilot</h3><p>Status: Active<br/>Emails triaged today: 47</p></div>
          <div className="feature-card"><h3>System Health</h3><p>Uptime: 99.9%<br/>Next digest: 6:00 AM</p></div>
        </div>
        <button onClick={()=>{setToken(null);setView('landing')}} className="btn-secondary" style={{marginTop:'2rem'}}>Log Out</button>
      </section>
    </div>
  );

  // LANDING PAGE
  return (
    <div className="container">
      {renderNav()}

      <section className="hero">
        <h1>Autonomous Workflows.<br/>Zero Setup.</h1>
        <p>
          Connect your business tools. SporlyWorks runs pre-built, AI-powered workflows
          that get smarter automatically as technology advances. No drag-and-drop builders. No coding. It just works.
        </p>
        <div className="hero-buttons">
          <button onClick={()=>setView('waitlist')} className="btn-primary">Get Started Free</button>
          <button onClick={()=>setView('login')} className="btn-secondary">Client Login</button>
        </div>
      </section>

      <section id="how" className="features">
        <h2 style={{textAlign:'center',marginBottom:'1rem'}}>Pick a Workflow. Connect. Done.</h2>
        <p style={{textAlign:'center',maxWidth:'600px',margin:'0 auto 3rem',color:'#666'}}>
          Unlike Zapier or Make, you don't build anything. We give you tested, autonomous workflows
          that run 24/7. As AI models improve, your workflows get smarter — automatically.
        </p>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📬</div>
            <h3>Inbox Autopilot</h3>
            <p>Connects to your email. Sorts urgent from noise. Drafts replies. Sends you one clean daily briefing instead of 100 interruptions.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3>Lead Qualifier</h3>
            <p>Watches your inbound inquiries. Researches each prospect. Scores and enriches the lead. Only pings you when someone is worth your time.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Ops Monitor</h3>
            <p>Sweeps your support tickets, invoices, and internal channels. Flags problems before they escalate. Drafts reports so you don't have to.</p>
          </div>
        </div>
      </section>

      <section id="pricing" className="features" style={{background:'#f1ebd9',padding:'4rem 2rem',borderRadius:'8px',marginTop:'4rem'}}>
        <h2 style={{textAlign:'center',marginBottom:'1rem'}}>Simple, Honest Pricing</h2>
        <p style={{textAlign:'center',maxWidth:'600px',margin:'0 auto 3rem'}}>Start free. Upgrade when it saves you real time.</p>
        <div className="features-grid" style={{gridTemplateColumns:'1fr 1fr 1fr',maxWidth:'900px',margin:'0 auto'}}>

          <div className="feature-card" style={{background:'white',border:'1px solid #e0e0e0'}}>
            <h3 style={{fontSize:'1.3rem',marginBottom:'0.5rem'}}>Starter</h3>
            <div style={{fontSize:'2.2rem',fontWeight:'bold',color:'#C5A059',marginBottom:'1rem'}}>Free</div>
            <p style={{fontWeight:'bold',color:'#666'}}>Try it out</p>
            <ul style={{textAlign:'left',marginTop:'1rem',lineHeight:'1.8',fontSize:'0.9rem'}}>
              <li>✓ 1 workflow</li>
              <li>✓ 1 connected account</li>
              <li>✓ 100 actions/month</li>
            </ul>
            <button onClick={()=>setView('waitlist')} className="btn-secondary" style={{marginTop:'2rem',width:'100%'}}>Start Free</button>
          </div>

          <div className="feature-card" style={{background:'white',border:'2px solid #C5A059'}}>
            <h3 style={{fontSize:'1.3rem',marginBottom:'0.5rem'}}>Pro</h3>
            <div style={{fontSize:'2.2rem',fontWeight:'bold',color:'#C5A059',marginBottom:'1rem'}}>$49<span style={{fontSize:'1rem',color:'#666'}}>/mo</span></div>
            <p style={{fontWeight:'bold',color:'#666'}}>For growing businesses</p>
            <ul style={{textAlign:'left',marginTop:'1rem',lineHeight:'1.8',fontSize:'0.9rem'}}>
              <li>✓ 3 workflows</li>
              <li>✓ 5 connected accounts</li>
              <li>✓ 2,000 actions/month</li>
              <li>✓ Priority support</li>
            </ul>
            <button onClick={()=>setView('waitlist')} className="btn-primary" style={{marginTop:'2rem',width:'100%'}}>Get Started</button>
          </div>

          <div className="feature-card" style={{background:'#2B2B2B',color:'white'}}>
            <h3 style={{fontSize:'1.3rem',marginBottom:'0.5rem',color:'white'}}>Business</h3>
            <div style={{fontSize:'2.2rem',fontWeight:'bold',color:'#C5A059',marginBottom:'1rem'}}>$149<span style={{fontSize:'1rem',color:'#aaa'}}>/mo</span></div>
            <p style={{fontWeight:'bold',color:'#ccc'}}>Unlimited & dedicated</p>
            <ul style={{textAlign:'left',marginTop:'1rem',lineHeight:'1.8',color:'#ddd',fontSize:'0.9rem'}}>
              <li>✓ Unlimited workflows</li>
              <li>✓ Unlimited accounts</li>
              <li>✓ Unlimited actions</li>
              <li>✓ Dedicated infrastructure</li>
            </ul>
            <button onClick={()=>setView('waitlist')} className="btn-primary" style={{marginTop:'2rem',width:'100%',border:'1px solid #C5A059'}}>Contact Us</button>
          </div>

        </div>
      </section>
    </div>
  );
}

export default App;
