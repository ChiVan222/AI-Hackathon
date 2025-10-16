'use client';

import { useState } from 'react';

interface IdeaConcept {
  name: string;
  description: string;
  target_audience?: string;
}

interface InitialIdeaResponse {
  problems: string[];
  existing_solutions: string[];
  idea_concepts: IdeaConcept[];
}

interface WorkflowStep {
  phase: string;
  tasks: string[];
}

interface DetailedPlanResponse {
  idea_name: string;
  work_process: string;
  timeline_summary: string;
  suggested_tech_stack: string[];
  plan_steps: WorkflowStep[];
}

export default function Home() {
  const [theme, setTheme] = useState('');
  const [constraints, setConstraints] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<InitialIdeaResponse | null>(null);
  const [error, setError] = useState('');
  
  // New states for detailed plan
  const [selectedIdea, setSelectedIdea] = useState<IdeaConcept | null>(null);
  const [detailedPlan, setDetailedPlan] = useState<DetailedPlanResponse | null>(null);
  const [planLoading, setPlanLoading] = useState(false);
  const [teamMembers, setTeamMembers] = useState(4);
  const [durationHours, setDurationHours] = useState(48);

  // Helper function to get tech stack logo and URL
  const getTechInfo = (techName: string): { logoUrl: string; url: string; displayName: string; iconName: string } => {
    const tech = techName.toLowerCase().trim();
    
    // Common tech stack mappings with Simple Icons slugs
    const techMap: Record<string, { iconName: string; url: string; displayName?: string; color?: string }> = {
      // Frontend
      'react': { iconName: 'react', url: 'https://react.dev', color: '61DAFB' },
      'react native': { iconName: 'react', url: 'https://reactnative.dev', color: '61DAFB' },
      'next.js': { iconName: 'nextdotjs', url: 'https://nextjs.org', color: '000000' },
      'nextjs': { iconName: 'nextdotjs', url: 'https://nextjs.org', displayName: 'Next.js', color: '000000' },
      'vue': { iconName: 'vuedotjs', url: 'https://vuejs.org', color: '4FC08D' },
      'vue.js': { iconName: 'vuedotjs', url: 'https://vuejs.org', color: '4FC08D' },
      'angular': { iconName: 'angular', url: 'https://angular.io', color: 'DD0031' },
      'svelte': { iconName: 'svelte', url: 'https://svelte.dev', color: 'FF3E00' },
      'tailwind': { iconName: 'tailwindcss', url: 'https://tailwindcss.com', color: '06B6D4' },
      'tailwind css': { iconName: 'tailwindcss', url: 'https://tailwindcss.com', color: '06B6D4' },
      
      // Backend
      'node.js': { iconName: 'nodedotjs', url: 'https://nodejs.org', color: '339933' },
      'nodejs': { iconName: 'nodedotjs', url: 'https://nodejs.org', displayName: 'Node.js', color: '339933' },
      'express': { iconName: 'express', url: 'https://expressjs.com', color: '000000' },
      'express.js': { iconName: 'express', url: 'https://expressjs.com', color: '000000' },
      'fastapi': { iconName: 'fastapi', url: 'https://fastapi.tiangolo.com', color: '009688' },
      'django': { iconName: 'django', url: 'https://www.djangoproject.com', color: '092E20' },
      'flask': { iconName: 'flask', url: 'https://flask.palletsprojects.com', color: '000000' },
      'nest.js': { iconName: 'nestjs', url: 'https://nestjs.com', color: 'E0234E' },
      'nestjs': { iconName: 'nestjs', url: 'https://nestjs.com', displayName: 'NestJS', color: 'E0234E' },
      
      // Languages
      'python': { iconName: 'python', url: 'https://www.python.org', color: '3776AB' },
      'javascript': { iconName: 'javascript', url: 'https://developer.mozilla.org/en-US/docs/Web/JavaScript', color: 'F7DF1E' },
      'typescript': { iconName: 'typescript', url: 'https://www.typescriptlang.org', color: '3178C6' },
      'java': { iconName: 'openjdk', url: 'https://www.java.com', color: '437291' },
      'go': { iconName: 'go', url: 'https://go.dev', color: '00ADD8' },
      'golang': { iconName: 'go', url: 'https://go.dev', displayName: 'Go', color: '00ADD8' },
      'rust': { iconName: 'rust', url: 'https://www.rust-lang.org', color: '000000' },
      'php': { iconName: 'php', url: 'https://www.php.net', color: '777BB4' },
      
      // Databases
      'mongodb': { iconName: 'mongodb', url: 'https://www.mongodb.com', color: '47A248' },
      'postgresql': { iconName: 'postgresql', url: 'https://www.postgresql.org', color: '4169E1' },
      'postgres': { iconName: 'postgresql', url: 'https://www.postgresql.org', displayName: 'PostgreSQL', color: '4169E1' },
      'mysql': { iconName: 'mysql', url: 'https://www.mysql.com', color: '4479A1' },
      'redis': { iconName: 'redis', url: 'https://redis.io', color: 'DC382D' },
      'firebase': { iconName: 'firebase', url: 'https://firebase.google.com', color: 'FFCA28' },
      'supabase': { iconName: 'supabase', url: 'https://supabase.com', color: '3ECF8E' },
      'sqlite': { iconName: 'sqlite', url: 'https://www.sqlite.org', color: '003B57' },
      
      // Cloud & DevOps
      'aws': { iconName: 'amazonaws', url: 'https://aws.amazon.com', color: 'FF9900', displayName: 'AWS' },
      'azure': { iconName: 'microsoftazure', url: 'https://azure.microsoft.com', color: '0078D4' },
      'gcp': { iconName: 'googlecloud', url: 'https://cloud.google.com', displayName: 'Google Cloud', color: '4285F4' },
      'docker': { iconName: 'docker', url: 'https://www.docker.com', color: '2496ED' },
      'kubernetes': { iconName: 'kubernetes', url: 'https://kubernetes.io', color: '326CE5' },
      'vercel': { iconName: 'vercel', url: 'https://vercel.com', color: '000000' },
      'netlify': { iconName: 'netlify', url: 'https://www.netlify.com', color: '00C7B7' },
      
      // AI/ML
      'tensorflow': { iconName: 'tensorflow', url: 'https://www.tensorflow.org', color: 'FF6F00' },
      'pytorch': { iconName: 'pytorch', url: 'https://pytorch.org', color: 'EE4C2C' },
      'openai': { iconName: 'openai', url: 'https://openai.com', color: '412991' },
      'hugging face': { iconName: 'huggingface', url: 'https://huggingface.co', color: 'FFD21E' },
      'langchain': { iconName: 'chainlink', url: 'https://www.langchain.com', color: '375BD2' },
      
      // Mobile
      'flutter': { iconName: 'flutter', url: 'https://flutter.dev', color: '02569B' },
      'swift': { iconName: 'swift', url: 'https://swift.org', color: 'F05138' },
      'kotlin': { iconName: 'kotlin', url: 'https://kotlinlang.org', color: '7F52FF' },
      
      // Tools
      'git': { iconName: 'git', url: 'https://git-scm.com', color: 'F05032' },
      'github': { iconName: 'github', url: 'https://github.com', color: '181717' },
      'vscode': { iconName: 'visualstudiocode', url: 'https://code.visualstudio.com', displayName: 'VS Code', color: '007ACC' },
      'figma': { iconName: 'figma', url: 'https://www.figma.com', color: 'F24E1E' },
    };
    
    // Try to find exact match
    let result = techMap[tech];
    
    // If no exact match, try partial matching
    if (!result) {
      for (const [key, value] of Object.entries(techMap)) {
        if (tech.includes(key) || key.includes(tech)) {
          result = value;
          break;
        }
      }
    }
    
    // Default fallback
    if (!result) {
      return { 
        logoUrl: 'https://cdn.simpleicons.org/gnubash/4EAA25',
        iconName: 'gnubash',
        url: `https://www.google.com/search?q=${encodeURIComponent(techName)}`,
        displayName: techName 
      };
    }
    
    return { 
      logoUrl: `https://cdn.simpleicons.org/${result.iconName}/${result.color || '000000'}`,
      iconName: result.iconName,
      url: result.url,
      displayName: result.displayName || techName
    };
  };

  // Helper function to format text with line breaks
  const formatTextWithBreaks = (text: string) => {
    // Split by common sentence endings followed by space or newline
    const sentences = text.split(/(?<=[.!?])\s+/);
    
    return sentences.map((sentence, index) => (
      <span key={index}>
        {sentence.trim()}
        {index < sentences.length - 1 && <><br /><br /></>}
      </span>
    ));
  };

  // Helper function to format timeline with phase breaks and bold labels
  const formatTimelineWithPhases = (text: string) => {
    // Split by common line breaks or periods
    const lines = text.split(/(?:\r?\n|\. )/);
    
    return lines.map((line, index) => {
      if (!line.trim()) return null;
      
      let formattedLine: React.ReactNode = line.trim();
      
      // Check for "Total time:" or "Total Time:" to make bold
      if (/total\s+time/i.test(line)) {
        const match = line.match(/(.*?)(total\s+time:?)(.*)/i);
        if (match) {
          formattedLine = (
            <>
              {match[1]}
              <strong className="font-bold text-gray-900">{match[2]}</strong>
              {match[3]}
            </>
          );
        }
      }
      
      // Check for Phase pattern: "Phase X:"
      if (/Phase\s+\d+:/i.test(line)) {
        const match = line.match(/(Phase\s+\d+:)/i);
        if (match) {
          const parts = line.split(match[1]);
          formattedLine = (
            <>
              <strong className="font-semibold text-purple-700">{match[1]}</strong>
              {parts[1] || ''}
            </>
          );
        }
      }
      
      // Also bold other important labels
      const boldLabels = ['Total Duration:', 'Member Distribution:', 'Team Size:', 'Duration:'];
      boldLabels.forEach(label => {
        if (typeof formattedLine === 'string' && formattedLine.includes(label)) {
          const parts = formattedLine.split(label);
          formattedLine = (
            <>
              {parts[0]}
              <strong className="font-semibold text-gray-900">{label}</strong>
              {parts[1]}
            </>
          );
        }
      });
      
      return (
        <div key={index} className="leading-relaxed">
          {formattedLine}
        </div>
      );
    }).filter(Boolean);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    setSelectedIdea(null);
    setDetailedPlan(null);

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

  const handleGetDetailedPlan = async (idea: IdeaConcept) => {
    setPlanLoading(true);
    setError('');
    setSelectedIdea(idea);
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/plan/detailed`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          idea_concept: idea,
          team_members: teamMembers,
          duration_hours: durationHours,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate detailed plan');
      }

      const data = await response.json();
      setDetailedPlan(data);
      
      // Scroll to detailed plan section
      setTimeout(() => {
        document.getElementById('detailed-plan')?.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        });
      }, 100);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setPlanLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-4">
             HI.GPA
          </h1>
          <h2 className='text-lg font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-4'>
            Hackathon Idea Generator and Planning Assistant
          </h2>
          <h3 className="text-gray-600 mb-10">
            Powered by Gemini AI & Computational Thinking
          </h3>
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

            {/* Team Settings - Collapsible */}
            <div className="border-t pt-4">
              <details className="group">
                <summary className="cursor-pointer text-sm font-semibold text-gray-700 mb-2 flex items-center justify-between">
                  <span>⚙️ Plan Settings (Optional)</span>
                  <span className="text-purple-600 group-open:rotate-180 transition-transform">▼</span>
                </summary>
                <div className="mt-4 space-y-4 bg-gray-50 p-4 rounded-lg">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="teamMembers" className="block text-sm font-medium text-gray-700 mb-2">
                        Team Members
                      </label>
                      <input
                        id="teamMembers"
                        type="number"
                        min="1"
                        max="20"
                        value={teamMembers}
                        onChange={(e) => setTeamMembers(parseInt(e.target.value) || 4)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                      />
                    </div>
                    <div>
                      <label htmlFor="durationHours" className="block text-sm font-medium text-gray-700 mb-2">
                        Duration (hours)
                      </label>
                      <input
                        id="durationHours"
                        type="number"
                        min="1"
                        max="168"
                        value={durationHours}
                        onChange={(e) => setDurationHours(parseInt(e.target.value) || 48)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                      />
                    </div>
                  </div>
                  <p className="text-xs text-gray-500">
                    These settings will be used when generating detailed implementation plans
                  </p>
                </div>
              </details>
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
              <div className="grid gap-6 md:grid-cols-1">
                {result.idea_concepts.map((idea, index) => (
                  <div key={index} className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow">
                    <div className="space-y-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center mb-2">
                            <span className="text-2xl font-bold text-purple-600 mr-3">#{index + 1}</span>
                            <h3 className="text-xl font-semibold text-gray-800">{idea.name}</h3>
                          </div>
                          <p className="text-gray-600 ml-11">{idea.description}</p>
                          {idea.target_audience && (
                            <div className="ml-11 mt-2">
                              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                                🎯 {idea.target_audience}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="ml-11">
                        <button
                          onClick={() => handleGetDetailedPlan(idea)}
                          disabled={planLoading && selectedIdea?.name === idea.name}
                          className="mt-3 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-medium rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow hover:shadow-md text-sm"
                        >
                          {planLoading && selectedIdea?.name === idea.name ? (
                            <span className="flex items-center">
                              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              Generating Plan...
                            </span>
                          ) : (
                            '📋 Get Detailed Plan'
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Detailed Plan Section */}
        {detailedPlan && (
          <div id="detailed-plan" className="space-y-6 mt-8 animate-fadeIn">
            <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-2xl shadow-xl p-8 border-2 border-green-200">
              <h2 className="text-3xl font-bold text-gray-800 mb-6 flex items-center">
                <span className="text-4xl mr-3"></span>
                Detailed Implementation Plan: {detailedPlan.idea_name}
              </h2>

              {/* Work Process */}
              <div className="mb-6 bg-white p-6 rounded-xl shadow-md">
                <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                  <span className="text-2xl mr-2">⚙️</span>
                  Recommended Work Process
                </h3>
                <p className="text-gray-700 leading-relaxed">
                  {formatTextWithBreaks(detailedPlan.work_process)}
                </p>
              </div>

              {/* Timeline Summary */}
              <div className="mb-6 bg-white p-6 rounded-xl shadow-md">
                <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                  <span className="text-2xl mr-2">⏱️</span>
                  Timeline Overview
                </h3>
                <div className="text-gray-700 leading-relaxed space-y-2">
                  {formatTimelineWithPhases(detailedPlan.timeline_summary)}
                </div>
              </div>

              {/* Tech Stack */}
              <div className="mb-6 bg-white p-6 rounded-xl shadow-md">
                <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center">
                  <span className="text-2xl mr-2">💻</span>
                  Suggested Tech Stack
                </h3>
                <div className="flex flex-wrap gap-3">
                  {detailedPlan.suggested_tech_stack.map((tech, index) => {
                    const techInfo = getTechInfo(tech);
                    return (
                      <a
                        key={index}
                        href={techInfo.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2.5 bg-gradient-to-r from-blue-100 to-purple-100 text-gray-800 rounded-lg font-medium text-sm border border-blue-200 shadow-sm flex items-center gap-2 hover:from-blue-200 hover:to-purple-200 transition-colors cursor-pointer"
                      >
                        <img 
                          src={techInfo.logoUrl} 
                          alt={`${techInfo.displayName} logo`}
                          className="w-5 h-5"
                        />
                        <span>
                          {techInfo.displayName}
                        </span>
                      </a>
                    );
                  })}
                </div>
              </div>

              {/* Workflow Steps */}
              <div className="bg-white p-6 rounded-xl shadow-md">
                <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                  <span className="text-2xl mr-2">📋</span>
                  Implementation Phases
                </h3>
                <div className="space-y-6">
                  {detailedPlan.plan_steps.map((step, index) => (
                    <div key={index} className="border-l-4 border-purple-500 pl-6 py-2">
                      <h4 className="text-lg font-semibold text-purple-700 mb-2">
                        {step.phase}
                      </h4>
                      <ul className="space-y-2">
                        {step.tasks.map((task, taskIndex) => (
                          <li key={taskIndex} className="flex items-start">
                            <span className="text-green-600 mr-2 mt-1">✓</span>
                            <span className="text-gray-700">{task}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>

              {/* Plan Settings Info */}
              <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-gray-600">
                  📊 This plan is optimized for <strong>{teamMembers} team members</strong> over <strong>{durationHours} hours</strong>
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500 text-sm">
          <p>Scientia Naturalis - Est. 2025</p>
        </div>
      </div>
    </div>
  );
}
