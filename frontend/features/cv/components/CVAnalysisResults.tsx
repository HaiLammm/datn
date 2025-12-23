'use client';

import { useState, useEffect } from 'react';
import { CVAnalysis } from '@datn/shared-types';
import { getCVAnalysis, getCVAnalysisStatus } from '../actions';
import { ScoreGauge } from './ScoreGauge';
import { AnalysisSummary } from './AnalysisSummary';
import { SkillCloud } from './SkillCloud';
import { SkillBreakdownCard } from './SkillBreakdownCard';
import { SkillCategoriesDisplay } from './SkillCategoriesDisplay';
import { SkillRecommendations } from './SkillRecommendations';
import { FeedbackSection } from './FeedbackSection';
import { LoadingState } from './LoadingState';

interface CVAnalysisResultsProps {
  cvId: string;
  initialAnalysis: CVAnalysis;
  skillSuggestions: string[]; // New prop for skill suggestions
}

export function CVAnalysisResults({ cvId, initialAnalysis, skillSuggestions }: CVAnalysisResultsProps) {
  const [analysis, setAnalysis] = useState<CVAnalysis>(initialAnalysis);
  const [isPolling, setIsPolling] = useState(analysis.status === 'PROCESSING' || analysis.status === 'PENDING');

  useEffect(() => {
    if (!isPolling) return;

    const pollStatus = async () => {
      try {
        const statusResponse = await getCVAnalysisStatus(cvId);
        if (statusResponse.status === 'COMPLETED') {
          // Fetch full analysis
          const fullAnalysis = await getCVAnalysis(cvId);
          setAnalysis(fullAnalysis);
          setIsPolling(false);
        } else if (statusResponse.status === 'FAILED') {
          setAnalysis(prev => ({ ...prev, status: 'FAILED' }));
          setIsPolling(false);
        }
        // Continue polling if still PROCESSING or PENDING
      } catch (error) {
        console.error('Polling error:', error);
        setIsPolling(false);
      }
    };

    const interval = setInterval(pollStatus, 3000); // Poll every 3 seconds

    return () => clearInterval(interval);
  }, [cvId, isPolling]);

  if (analysis.status === 'PENDING' || analysis.status === 'PROCESSING') {
    return <LoadingState />;
  }

  if (analysis.status === 'FAILED') {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-red-800 mb-2">
          Analysis Failed
        </h3>
        <p className="text-red-700">
          We encountered an error while analyzing your CV. Please try uploading again.
        </p>
      </div>
    );
  }

  // Extract feedback data from ai_feedback or use computed fields
  const feedbackData = {
    formatting_feedback: analysis.formatting_feedback || analysis.ai_feedback?.formatting_feedback || [],
    ats_hints: analysis.ats_hints || analysis.ai_feedback?.ats_hints || [],
    strengths: analysis.strengths || analysis.ai_feedback?.strengths || [],
    improvements: analysis.improvements || analysis.ai_feedback?.improvements || [],
    skill_suggestions: skillSuggestions, // Pass skill suggestions here
  };


  const experienceBreakdown = analysis.experience_breakdown || analysis.ai_feedback?.experience_breakdown;
  const criteriaExplanation = analysis.criteria_explanation || analysis.ai_feedback?.criteria;

  return (
    <div className="space-y-6">
      {/* Score Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          CV Quality Score
        </h2>
        <ScoreGauge score={analysis.ai_score || 0} />

        {/* Score Criteria Breakdown */}
        {criteriaExplanation && (
          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{criteriaExplanation.completeness}</div>
              <div className="text-xs text-gray-500">Completeness</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{criteriaExplanation.experience}</div>
              <div className="text-xs text-gray-500">Experience</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{criteriaExplanation.skills}</div>
              <div className="text-xs text-gray-500">Skills</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{criteriaExplanation.professionalism}</div>
              <div className="text-xs text-gray-500">Professionalism</div>
            </div>
          </div>
        )}
      </div>

      {/* Summary Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Professional Summary
        </h2>
        <AnalysisSummary summary={analysis.ai_summary || 'No summary available'} />
      </div>

      {/* Experience Breakdown Section */}
      {experienceBreakdown && (experienceBreakdown.total_years > 0 || experienceBreakdown.key_roles?.length > 0) && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Experience Overview
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <div className="text-3xl font-bold text-blue-600">
                {experienceBreakdown.total_years}+
              </div>
              <div className="text-sm text-gray-500">Years of Experience</div>
            </div>
            {experienceBreakdown.key_roles && experienceBreakdown.key_roles.length > 0 && (
              <div>
                <div className="text-sm font-medium text-gray-700 mb-2">Key Roles</div>
                <div className="flex flex-wrap gap-1">
                  {experienceBreakdown.key_roles.map((role, index) => (
                    <span key={index} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700">
                      {role}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {experienceBreakdown.industries && experienceBreakdown.industries.length > 0 && (
              <div>
                <div className="text-sm font-medium text-gray-700 mb-2">Industries</div>
                <div className="flex flex-wrap gap-1">
                  {experienceBreakdown.industries.map((industry, index) => (
                    <span key={index} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">
                      {industry}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Skill Analysis Section - Show breakdown if available (Story 5.6) */}
      {analysis.skill_breakdown && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Skill Analysis
          </h2>
          <SkillBreakdownCard breakdown={analysis.skill_breakdown} />
        </div>
      )}

      {/* Skills Section - Use categorized display if available, fallback to cloud */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          {analysis.skill_categories ? 'Skills Breakdown' : 'Extracted Skills'}
        </h2>
        {analysis.skill_categories ? (
          <SkillCategoriesDisplay categories={analysis.skill_categories} />
        ) : (
          <SkillCloud skills={analysis.extracted_skills || []} />
        )}
      </div>

      {/* Skill Recommendations Section - Show only if recommendations exist */}
      {analysis.skill_recommendations && analysis.skill_recommendations.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Skill Development Recommendations
          </h2>
          <SkillRecommendations recommendations={analysis.skill_recommendations} />
        </div>
      )}

      {/* Feedback Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Detailed Feedback
        </h2>
        <FeedbackSection feedback={feedbackData} />
      </div>
    </div>
  );
}