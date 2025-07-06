import React, { useState, useEffect } from 'react';
import CVForm from './components/CVForm';
import JobRanking from './components/JobRanking';
import CvImprovements from './components/CvImprovements';
import { ReactComponent as Logo } from './logo.svg';

function App() {
  const [result, setResult] = useState(false);
  const [error, setError] = useState(null);
  const [jobs, setJobs] = useState(null);
  const [cvImprovements, setCvImprovements] = useState(null);
  const [loading, setLoading] = useState(false);
  const [polling, setPolling] = useState(false);

  const fetchResults = async () => {
    setLoading(true);
    setError(null);
    try {
      const [improvementsRes, jobsRes] = await Promise.all([
        fetch('http://localhost:5002/api/improvements'),
        fetch('http://localhost:5002/api/jobrankings'),
      ]);
      if (!improvementsRes.ok || !jobsRes.ok) throw new Error('Failed to fetch results');
      const improvements = await improvementsRes.json();
      const jobs = await jobsRes.json();
      
      if (improvements && Object.keys(improvements).length > 0 && JSON.stringify(improvements) !== '{}') {
        setCvImprovements(improvements);
      }
      if (Array.isArray(jobs) && jobs.length > 0) {
        setJobs(jobs);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const startPolling = () => {
    setPolling(true);
    const pollInterval = setInterval(async () => {
      try {
        const [improvementsRes, jobsRes] = await Promise.all([
          fetch('http://localhost:5002/api/improvements'),
          fetch('http://localhost:5002/api/jobrankings'),
        ]);
        
        if (improvementsRes.ok && jobsRes.ok) {
          const improvements = await improvementsRes.json();
          const jobs = await jobsRes.json();
          
          if (improvements && Object.keys(improvements).length > 0 && JSON.stringify(improvements) !== '{}' && 
              Array.isArray(jobs) && jobs.length > 0) {
            setCvImprovements(improvements);
            setJobs(jobs);
            setPolling(false);
            clearInterval(pollInterval);
          }
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 2000);

    return () => clearInterval(pollInterval);
  };

  const handleFormResult = () => {
    setResult(true);
    fetchResults();
    startPolling();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-teal-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute top-40 left-40 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative z-10 min-h-screen flex flex-col items-center justify-start py-8 px-4">
        <div className="w-full max-w-4xl mx-auto">
          {/* Header Section */}
          <div className="text-center mb-12">
            <div className="flex justify-center mb-6">
              <div className="relative">
                <Logo className="w-20 h-20 text-white drop-shadow-2xl" />
                <div className="absolute inset-0 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full blur-xl opacity-30"></div>
              </div>
            </div>
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              CV Agent
            </h1>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              AI-powered CV analysis and job matching
            </p>
          </div>

          {/* Form Section */}
          <div className="w-full max-w-2xl mx-auto mb-12">
            <div className="backdrop-blur-xl bg-white/10 rounded-3xl border border-white/20 shadow-2xl p-8">
              <CVForm onResult={handleFormResult} onError={setError} />
              {error && (
                <div className="mt-4 p-4 bg-red-500/20 border border-red-500/30 rounded-xl text-red-200">
                  {error}
                </div>
              )}
            </div>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="text-center mb-8">
              <div className="inline-flex items-center px-6 py-3 bg-white/10 backdrop-blur-xl rounded-full border border-white/20">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-400 mr-3"></div>
                <span className="text-white font-medium">Processing your CV...</span>
              </div>
            </div>
          )}

          {/* Results Section */}
          {result && !loading && (
            <div className="space-y-8">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-white mb-2">Analysis Results</h2>
                <p className="text-gray-300">Your personalized insights and recommendations</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
                {/* Job Rankings */}
                <div className="min-w-[340px] w-full backdrop-blur-xl bg-white/10 rounded-3xl border border-white/20 shadow-2xl p-8 hover:bg-white/15 transition-all duration-300">
                  {jobs ? (
                    <JobRanking jobs={jobs} />
                  ) : (
                    <div className="text-center py-12">
                      <div className="relative mb-6">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto"></div>
                        <div className="absolute inset-0 rounded-full border-2 border-purple-400/20"></div>
                      </div>
                      <h3 className="text-xl font-semibold text-white mb-2">Waiting for Job Rankings</h3>
                      <p className="text-gray-300">Analyzing job matches...</p>
                    </div>
                  )}
                </div>

                {/* CV Improvements */}
                <div className="min-w-[340px] w-full backdrop-blur-xl bg-white/10 rounded-3xl border border-white/20 shadow-2xl p-8 hover:bg-white/15 transition-all duration-300">
                  {cvImprovements ? (
                    <CvImprovements improvements={cvImprovements} />
                  ) : (
                    <div className="text-center py-12">
                      <div className="relative mb-6">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto"></div>
                        <div className="absolute inset-0 rounded-full border-2 border-purple-400/20"></div>
                      </div>
                      <h3 className="text-xl font-semibold text-white mb-2">Waiting for CV Improvements</h3>
                      <p className="text-gray-300">Analyzing your CV...</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Polling Status */}
          {polling && (
            <div className="text-center mt-8">
              <div className="inline-flex items-center px-4 py-2 bg-purple-500/20 backdrop-blur-xl rounded-full border border-purple-500/30">
                <div className="animate-pulse w-2 h-2 bg-purple-400 rounded-full mr-2"></div>
                <span className="text-purple-200 text-sm">Polling for updates...</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
