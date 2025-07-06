import React from 'react';

function CvImprovements({ improvements }) {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">CV Improvement Suggestions</h2>
      <div className="rounded-xl bg-white/90 shadow p-4">
        <div className="mb-2">
          <span className="font-semibold text-base">Missing Sections:</span>
          <ul className="list-disc list-inside text-sm text-gray-700">
            {improvements.missing_sections.map((section, i) => (
              <li key={i}>{section}</li>
            ))}
          </ul>
        </div>
        <div className="mb-2">
          <span className="font-semibold text-base">Weak Points:</span>
          <ul className="list-disc list-inside text-sm text-gray-700">
            {improvements.weak_points.map((point, i) => (
              <li key={i}>{point}</li>
            ))}
          </ul>
        </div>
        <div className="mb-2">
          <span className="font-semibold text-base">Recommendations:</span>
          <ul className="list-disc list-inside text-sm text-gray-700">
            {improvements.recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        </div>
        <div className="mt-2 text-xs italic text-gray-600">{improvements.summary}</div>
      </div>
    </div>
  );
}

export default CvImprovements; 