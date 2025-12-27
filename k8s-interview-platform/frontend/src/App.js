import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import AdminPanel from './components/AdminPanel';
import InterviewSession from './components/InterviewSession';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<AdminPanel />} />
          <Route path="/interview/:sessionId" element={<InterviewSession />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
