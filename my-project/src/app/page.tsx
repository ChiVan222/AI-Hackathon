'use client';

import { useState } from 'react';

interface IdeaResponse {
  problems: string[];
  existing_solutions: string[];
  idea_concepts: string[];
  workflow_plan: string[];
}

export default function Home() {
  const [theme, setTheme] = useState('');
  const [constraints, setConstraints] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<IdeaResponse | null>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const constraintsList = constraints
        .split(',')
        .map(c => c.trim())
        .filter(c => c.length > 0);

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          theme: theme,
          constraints: constraintsList,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate ideas');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-4">
            🚀 AI Hackathon Idea Generator
          </h1>
          <p className="text-gray-600 text-lg">
            Powered by Gemini AI & Computational Thinking
          </p>
        </div>

        {/* Input Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border border-gray-100">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="theme" className="block text-sm font-semibold text-gray-700 mb-2">
                Hackathon Theme *
              </label>
              <input
                id="theme"
                type="text"
                value={theme}
                onChange={(e) => setTheme(e.target.value)}
                placeholder="e.g., Climate Change, Healthcare, Education..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition"
                required
              />
            </div>

            <div>
              <label htmlFor="constraints" className="block text-sm font-semibold text-gray-700 mb-2">
                Constraints (optional)
              </label>
              <input
                id="constraints"
                type="text"
                value={constraints}
                onChange={(e) => setConstraints(e.target.value)}
                placeholder="e.g., Mobile-first, Low-cost, 48 hours (comma-separated)"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition"
              />
              <p className="text-xs text-gray-500 mt-1">
                Separate multiple constraints with commas
              </p>
            </div>

            <button
              type="submit"
              disabled={loading || !theme}
              className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generating Ideas...
                </span>
              ) : (
                '✨ Generate Ideas'
              )}
            </button>
          </form>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm">❌ {error}</p>
            </div>
          )}
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* Problems Section */}
            <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
                <span className="text-3xl mr-3">🎯</span>
                Identified Problems
              </h2>
              <ul className="space-y-3">
                {result.problems.map((problem, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-purple-600 font-bold mr-3">{index + 1}.</span>
                    <span className="text-gray-700">{problem}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Existing Solutions Section */}
            <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
                <span className="text-3xl mr-3">💡</span>
                Existing Solutions
              </h2>
              <ul className="space-y-3">
                {result.existing_solutions.map((solution, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-blue-600 font-bold mr-3">{index + 1}.</span>
                    <span className="text-gray-700">{solution}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Idea Concepts Section */}
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl shadow-xl p-8 border-2 border-purple-200">
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
                <span className="text-3xl mr-3">🌟</span>
                Innovative Ideas
              </h2>
              <div className="grid gap-4 md:grid-cols-1">
                {result.idea_concepts.map((idea, index) => (
                  <div key={index} className="bg-white p-6 rounded-xl shadow-md">
                    <div className="flex items-start">
                      <span className="text-2xl font-bold text-purple-600 mr-4">#{index + 1}</span>
                      <p className="text-gray-700 flex-1">{idea}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Workflow Plan Section */}
            <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
                <span className="text-3xl mr-3">📋</span>
                Workflow Plan
              </h2>
              <div className="space-y-4">
                {result.workflow_plan.map((step, index) => (
                  <div key={index} className="flex items-start">
                    <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center text-white font-bold mr-4">
                      {index + 1}
                    </div>
                    <p className="text-gray-700 pt-1">{step}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500 text-sm">
          <p>Made with ❤️ using Next.js, Tailwind CSS & FastAPI</p>
        </div>
      </div>
    </div>
  );
}
