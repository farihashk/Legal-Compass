import React, { useState, useEffect, useRef } from 'react';
import Papa from 'papaparse';
import axios from 'axios';
import LawyerMap from './components/LawyerMap';
import './App.css';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://127.0.0.1:5000';

function App() {
  const [allLawyers, setAllLawyers] = useState([]);
  const [lawyers, setLawyers] = useState([]);               // the 10 we display
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [processing, setProcessing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showOverlay, setShowOverlay] = useState(false);
  const chatEndRef = useRef(null);

  // 1) load and parse CSV once
  useEffect(() => {
    fetch('/wills_lawyers.csv')
      .then(r => r.text())
      .then(csv => {
        Papa.parse(csv, {
          header: true,
          skipEmptyLines: true,
          complete: results => {
            // convert strings to numbers where needed:
            const data = results.data.map(row => ({
              ...row,
              latitude: parseFloat(row.latitude),
              longitude: parseFloat(row.longitude),
              rating: parseFloat(row.rating),
            }));
            setAllLawyers(data);
          }
        });
      })
      .catch(console.error);
  }, []);

  // 2) auto‑scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 3) helper to pick 10 random lawyers
  const pickRandom10 = () => {
    const arr = [...allLawyers];
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr.slice(0, 10);
  };

  // 4) toggle overlay + randomize
  const handleToggle = () => {
    if (!showOverlay) {
      setLawyers(pickRandom10());
    }
    setShowOverlay(v => !v);
  };

  // 5) send question
  const sendQuestion = async () => {
    if (!input.trim()) return;
    setMessages(m => [...m, { sender: 'user', text: input }]);
    setInput('');
    setProcessing(true);
    try {
      const { data } = await axios.post(`${API_BASE}/ask`, { question: input });
      setMessages(m => [...m, { sender: 'bot', text: data.response }]);
      if (data.lawyer_recommendation?.length) {
        setMessages(m => [...m, {
          sender: 'bot',
          text: 'Lawyer Recommendations:',
          details: data.lawyer_recommendation
        }]);
      }
    } catch {
      setMessages(m => [...m, { sender: 'bot', text: 'Error fetching response' }]);
    }
    setProcessing(false);
  };

  // 6) upload PDF
  const uploadPdf = async e => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    const form = new FormData();
    form.append('pdf', file);
    try {
      const { data } = await axios.post(`${API_BASE}/process-pdf`, form);
      setMessages(m => [...m, {
        sender: 'system',
        text: `PDF processed (${data.chunks_processed} chunks)`
      }]);
    } catch {
      setMessages(m => [...m, { sender: 'system', text: 'PDF processing failed' }]);
    }
    setUploading(false);
    e.target.value = '';
  };

  const handleKey = e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendQuestion();
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <button className="toggle-btn" onClick={handleToggle}>
          {showOverlay ? 'Hide Lawyers & Map' : 'Show Lawyers & Map'}
        </button>
        <h1 className="app-title">LegalCompass Assistant</h1>
      </header>

      <main className="chat-wrapper">
        {showOverlay && (
          <div className="map-overlay">
            <aside className="lawyer-list-panel">
              <h3>Lawyers</h3>
              <ul>
                {lawyers.map(l => (
                  <li key={l.id}>
                    <a href={l.profile_url} target="_blank" rel="noreferrer">
                      <strong>{l.name}</strong>
                    </a><br/>
                    {l.category}
                  </li>
                ))}
              </ul>
            </aside>
            <div className="map-panel">
              <LawyerMap lawyers={lawyers} />
            </div>
          </div>
        )}

        <div className="chat-content">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.sender}`}>
              <p>{msg.text}</p>
              {msg.details && (
                <ul className="detail-list">
                  {msg.details.map((l, j) => (
                    <li key={j}>{l.name} — {l.specialization}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        <div className="controls">
          <input
            type="file"
            accept="application/pdf"
            onChange={uploadPdf}
            disabled={uploading}
          />
          <textarea
            placeholder="Type your question…"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
          />
          <button onClick={sendQuestion} disabled={processing || uploading}>
            {processing ? 'Thinking…' : 'Send'}
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;
