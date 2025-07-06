import React, { useState } from 'react';

function CVForm({ onResult, onError }) {
  const [inputMode, setInputMode] = useState('url');
  const [url, setUrl] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const webhook = 'https://jxrgenn.app.n8n.cloud/webhook-test/558f7c16-8db5-4fe4-a396-d8faf1987be6';

  const handleInputChange = (mode) => setInputMode(mode);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      let res;
      if (inputMode === 'url') {
        res = await fetch(webhook, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url }),
        });
      } else if (inputMode === 'file' && file) {
        const formData = new FormData();
        formData.append('file', file);
        res = await fetch(webhook, {
          method: 'POST',
          body: formData,
        });
      }
      if (res && res.ok) {
        if (onResult) onResult(await res.json());
      } else {
        throw new Error('Submission failed');
      }
    } catch (err) {
      if (onError) onError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-white mb-2">Upload Your CV</h2>
        <p className="text-gray-300">Choose how you'd like to submit your CV for analysis</p>
      </div>

      {/* Input Mode Toggle */}
      <div className="flex justify-center mb-8">
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-1 border border-white/20">
          <button
            type="button"
            className={`px-6 py-3 rounded-xl font-medium transition-all duration-200 ${
              inputMode === 'url' 
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg' 
                : 'text-gray-300 hover:text-white'
            }`}
            onClick={() => handleInputChange('url')}
          >
            LinkedIn URL
          </button>
          <button
            type="button"
            className={`px-6 py-3 rounded-xl font-medium transition-all duration-200 ${
              inputMode === 'file' 
                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg' 
                : 'text-gray-300 hover:text-white'
            }`}
            onClick={() => handleInputChange('file')}
          >
            Upload File
          </button>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {inputMode === 'url' && (
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              LinkedIn Profile URL
            </label>
            <input
              type="url"
              className="w-full px-4 py-3 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
              placeholder="https://www.linkedin.com/in/your-profile"
              value={url}
              onChange={e => setUrl(e.target.value)}
              required
            />
          </div>
        )}

        {inputMode === 'file' && (
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              CV File (PDF, DOC, DOCX, TXT)
            </label>
            <div className="relative">
              <input
                type="file"
                className="w-full px-4 py-3 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-purple-500 file:text-white hover:file:bg-purple-600 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
                accept=".pdf,.doc,.docx,.txt"
                onChange={e => setFile(e.target.files[0])}
                required
              />
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-3 px-6 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Analyzing CV...
            </div>
          ) : (
            'Analyze CV'
          )}
        </button>
      </form>
    </div>
  );
}

export default CVForm; 