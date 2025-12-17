import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SkillRecommendations } from './SkillRecommendations';

describe('SkillRecommendations', () => {
  const mockRecommendations = [
    'Consider adding more technical skills to your CV',
    'Learn in-demand skills like Kubernetes and AWS',
    'Add skills in databases to show broader expertise'
  ];

  it('renders all recommendations as list items', () => {
    render(<SkillRecommendations recommendations={mockRecommendations} />);
    
    expect(screen.getByText(/Consider adding more technical skills/)).toBeInTheDocument();
    expect(screen.getByText(/Learn in-demand skills like Kubernetes/)).toBeInTheDocument();
    expect(screen.getByText(/Add skills in databases/)).toBeInTheDocument();
  });

  it('shows empty state message when no recommendations', () => {
    render(<SkillRecommendations recommendations={[]} />);
    
    expect(screen.getByText(/No recommendations at this time/)).toBeInTheDocument();
  });

  it('renders with numbered indicators for each recommendation', () => {
    render(<SkillRecommendations recommendations={mockRecommendations} />);
    
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('renders section title with icon', () => {
    render(<SkillRecommendations recommendations={mockRecommendations} />);
    
    expect(screen.getByText(/Skill Development Suggestions/)).toBeInTheDocument();
  });

  it('renders with accessible list structure', () => {
    render(<SkillRecommendations recommendations={mockRecommendations} />);
    
    const list = screen.getByRole('list', { name: /Skill recommendations/ });
    expect(list).toBeInTheDocument();
    
    const items = screen.getAllByRole('listitem');
    expect(items).toHaveLength(3);
  });

  it('handles single recommendation', () => {
    render(<SkillRecommendations recommendations={['Single recommendation']} />);
    
    expect(screen.getByText('Single recommendation')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.queryByText('2')).not.toBeInTheDocument();
  });

  it('handles long recommendations text', () => {
    const longRecommendation = 'This is a very long recommendation that contains a lot of text to test how the component handles lengthy content and whether it wraps correctly without breaking the layout or causing any visual issues.';
    
    render(<SkillRecommendations recommendations={[longRecommendation]} />);
    
    expect(screen.getByText(longRecommendation)).toBeInTheDocument();
  });

  it('handles special characters in recommendations', () => {
    const specialCharsRecommendation = 'Learn C++, C#, and .NET for enterprise development';
    
    render(<SkillRecommendations recommendations={[specialCharsRecommendation]} />);
    
    expect(screen.getByText(specialCharsRecommendation)).toBeInTheDocument();
  });
});
