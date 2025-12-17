import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SkillBreakdownCard } from './SkillBreakdownCard';
import { SkillBreakdown } from '@datn/shared-types';

describe('SkillBreakdownCard', () => {
  const mockBreakdown: SkillBreakdown = {
    completeness_score: 5,
    categorization_score: 4,
    evidence_score: 3,
    market_relevance_score: 4,
    total_score: 16
  };

  it('renders total score with correct value', () => {
    render(<SkillBreakdownCard breakdown={mockBreakdown} />);
    
    expect(screen.getByText('16')).toBeInTheDocument();
    expect(screen.getByText('/25')).toBeInTheDocument();
  });

  it('renders all 4 sub-scores with correct labels', () => {
    render(<SkillBreakdownCard breakdown={mockBreakdown} />);
    
    expect(screen.getByText('Completeness')).toBeInTheDocument();
    expect(screen.getByText('Categorization')).toBeInTheDocument();
    expect(screen.getByText('Evidence')).toBeInTheDocument();
    expect(screen.getByText('Market Relevance')).toBeInTheDocument();
  });

  it('renders sub-scores with correct values in X/Y format', () => {
    render(<SkillBreakdownCard breakdown={mockBreakdown} />);
    
    expect(screen.getByText('5/7')).toBeInTheDocument(); // completeness
    // Note: categorization_score=4 and market_relevance_score=4 both show "4/6"
    expect(screen.getAllByText('4/6')).toHaveLength(2); // categorization + market_relevance
    expect(screen.getByText('3/6')).toBeInTheDocument(); // evidence
  });

  it('renders progress bars with correct aria attributes', () => {
    render(<SkillBreakdownCard breakdown={mockBreakdown} />);
    
    const progressBars = screen.getAllByRole('progressbar');
    expect(progressBars).toHaveLength(4);
    
    // Check first progress bar (Completeness)
    expect(progressBars[0]).toHaveAttribute('aria-valuenow', '5');
    expect(progressBars[0]).toHaveAttribute('aria-valuemax', '7');
  });

  it('applies green color for excellent score (20-25)', () => {
    const excellentBreakdown: SkillBreakdown = {
      completeness_score: 7,
      categorization_score: 6,
      evidence_score: 5,
      market_relevance_score: 5,
      total_score: 23
    };
    
    render(<SkillBreakdownCard breakdown={excellentBreakdown} />);
    
    expect(screen.getByText('Excellent')).toBeInTheDocument();
    expect(screen.getByText('23')).toBeInTheDocument();
  });

  it('applies blue color for good score (15-19)', () => {
    const goodBreakdown: SkillBreakdown = {
      completeness_score: 5,
      categorization_score: 4,
      evidence_score: 4,
      market_relevance_score: 4,
      total_score: 17
    };
    
    render(<SkillBreakdownCard breakdown={goodBreakdown} />);
    
    expect(screen.getByText('Good')).toBeInTheDocument();
  });

  it('applies yellow color for fair score (10-14)', () => {
    const fairBreakdown: SkillBreakdown = {
      completeness_score: 3,
      categorization_score: 3,
      evidence_score: 3,
      market_relevance_score: 3,
      total_score: 12
    };
    
    render(<SkillBreakdownCard breakdown={fairBreakdown} />);
    
    expect(screen.getByText('Fair')).toBeInTheDocument();
  });

  it('applies orange color for needs improvement score (0-9)', () => {
    const lowBreakdown: SkillBreakdown = {
      completeness_score: 2,
      categorization_score: 2,
      evidence_score: 2,
      market_relevance_score: 2,
      total_score: 8
    };
    
    render(<SkillBreakdownCard breakdown={lowBreakdown} />);
    
    expect(screen.getByText('Needs Improvement')).toBeInTheDocument();
  });

  it('handles edge case with zero scores', () => {
    const zeroBreakdown: SkillBreakdown = {
      completeness_score: 0,
      categorization_score: 0,
      evidence_score: 0,
      market_relevance_score: 0,
      total_score: 0
    };
    
    render(<SkillBreakdownCard breakdown={zeroBreakdown} />);
    
    expect(screen.getByText('0')).toBeInTheDocument();
    expect(screen.getByText('0/7')).toBeInTheDocument();
  });

  it('handles edge case with max scores', () => {
    const maxBreakdown: SkillBreakdown = {
      completeness_score: 7,
      categorization_score: 6,
      evidence_score: 6,
      market_relevance_score: 6,
      total_score: 25
    };
    
    render(<SkillBreakdownCard breakdown={maxBreakdown} />);
    
    expect(screen.getByText('25')).toBeInTheDocument();
    expect(screen.getByText('7/7')).toBeInTheDocument();
    expect(screen.getAllByText('6/6')).toHaveLength(3);
  });

  it('renders score descriptions for each sub-score', () => {
    render(<SkillBreakdownCard breakdown={mockBreakdown} />);
    
    expect(screen.getByText('Quantity and diversity of skills')).toBeInTheDocument();
    expect(screen.getByText('Coverage across skill categories')).toBeInTheDocument();
    expect(screen.getByText('Skill usage demonstrated in experience')).toBeInTheDocument();
    expect(screen.getByText('In-demand skills for current market')).toBeInTheDocument();
  });
});
