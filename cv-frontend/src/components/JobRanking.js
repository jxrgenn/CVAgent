import React from 'react';

function JobRanking({ jobs }) {
  const sortedJobs = [...jobs].sort((a, b) => b.match_rate - a.match_rate);
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Ranked Job Matches</h2>
      <div className="flex flex-col gap-4">
        {sortedJobs.map((job, idx) => (
          <div key={idx} className={`rounded-xl border-l-4 p-4 bg-white/90 shadow ${job.match_rate > 80 ? 'border-green-500' : job.match_rate > 60 ? 'border-yellow-500' : 'border-red-500'}`}>
            <div className="flex items-center mb-2">
              <h3 className="font-semibold text-lg flex-1">{job.company_name} - {job.job_title}</h3>
              <span className={`px-2 py-1 rounded text-xs font-bold ${job.match_rate > 80 ? 'bg-green-100 text-green-700' : job.match_rate > 60 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>Match: {job.match_rate}%</span>
            </div>
            <div className="w-full h-2 bg-gray-200 rounded mb-2 overflow-hidden">
              <div className={`${job.match_rate > 80 ? 'bg-green-400' : job.match_rate > 60 ? 'bg-yellow-400' : 'bg-red-400'} h-2 rounded`} style={{ width: `${job.match_rate}%` }}></div>
            </div>
            <div className="mb-1">
              <span className="font-semibold text-sm">Match Breakdown:</span>
              <ul className="list-disc list-inside text-sm text-gray-700">
                {job.match_breakdown.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
            <div className="mb-1">
              <span className="font-semibold text-sm">Missing Requirements:</span>
              <ul className="list-disc list-inside text-sm text-gray-700">
                {job.missing_requirements.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
            <div className="mb-1">
              <span className="font-semibold text-sm">Recommendations:</span>
              <ul className="list-disc list-inside text-sm text-gray-700">
                {job.recommendations.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
            <div className="mt-2 text-xs italic text-gray-600">{job.summary}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default JobRanking; 