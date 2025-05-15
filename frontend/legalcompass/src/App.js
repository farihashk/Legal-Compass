import React, { useState } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [processing, setProcessing] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setProcessing(true);
  
    try {
      const response = await fetch('http://127.0.0.1:5000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input })
      });
      
      const data = await response.json();
      const botMessage = { 
        sender: 'bot', 
        text: data.response || "No answer available",
        source: data.source || 'unknown',
        sources: data.sources || [],
        lawyerRecommendation: data.lawyer_recommendation || [] // Including lawyer info
      };
      
      setMessages(prev => [...prev, botMessage]);
  
      if (data.lawyer_recommendation) {
        // Display lawyer recommendations if available
        setMessages(prev => [
          ...prev,
          {
            sender: 'bot',
            text: "Lawyer Recommendations:",
            sources: data.lawyer_recommendation.map(lawyer => `${lawyer.name}, ${lawyer.specialization}, located at ${lawyer.address}`).join("\n"),
            source: 'lawyer_info'
          }
        ]);
      }
  
    } catch (error) {
      console.error("Error calling backend:", error);
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: "Error getting response",
        source: 'error'
      }]);
    }
  
    setInput("");
    setProcessing(false);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('pdf', file);

    try {
      const response = await fetch('http://127.0.0.1:5000/process-pdf', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        setMessages(prev => [...prev, {
          sender: 'system',
          text: `PDF processed successfully (${data.chunks_processed} chunks)`,
          source: 'system'
        }]);
      } else {
        throw new Error(data.error || "Processing failed");
      }
    } catch (error) {
      console.error("Error processing PDF:", error);
      setMessages(prev => [...prev, {
        sender: 'system',
        text: `PDF processing error: ${error.message}`,
        source: 'error'
      }]);
    }
    
    setUploading(false);
    e.target.value = ''; // Reset file input
  };


  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="App">
      <div className="chat-wrapper">
        <div className="chat-header">LegalCompass</div>
        <div className="chat-content">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender === 'user' ? 'user-message' : 'bot-message'}`}>
              {msg.text}
            </div>
          ))}
          {processing && <div className="processing-indicator">Processing...</div>}
        </div>
        <div className="chat-input-area">
          <label className="file-upload">
            Upload PDF
            <input type="file" accept="application/pdf" multiple onChange={handleFileUpload} />
          </label>
          {uploading && <div className="uploading-indicator">Uploading...</div>}
          <textarea
            className="chat-input"
            placeholder="Type your question..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <button className="send-button" onClick={handleSend} disabled={processing || uploading}>
            {processing ? "Processing..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
