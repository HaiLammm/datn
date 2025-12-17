import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SkillCategoriesDisplay } from './SkillCategoriesDisplay';
import { SkillCategories } from '@datn/shared-types';

describe('SkillCategoriesDisplay', () => {
  const mockCategories: SkillCategories = {
    programming_languages: ['Python', 'JavaScript', 'TypeScript'],
    frameworks: ['React', 'FastAPI', 'Next.js'],
    databases: ['PostgreSQL', 'Redis'],
    devops: ['Docker', 'Kubernetes', 'AWS'],
    soft_skills: ['Teamwork', 'Communication'],
    ai_ml: ['PyTorch', 'TensorFlow'],
    other: ['Git']
  };

  it('renders all populated categories', () => {
    render(<SkillCategoriesDisplay categories={mockCategories} />);
    
    expect(screen.getByText(/Programming Languages/)).toBeInTheDocument();
    expect(screen.getByText(/Frameworks/)).toBeInTheDocument();
    expect(screen.getByText(/Databases/)).toBeInTheDocument();
    expect(screen.getByText(/DevOps/)).toBeInTheDocument();
    expect(screen.getByText(/Soft Skills/)).toBeInTheDocument();
    expect(screen.getByText(/AI\/ML/)).toBeInTheDocument();
    expect(screen.getByText(/Other/)).toBeInTheDocument();
  });

  it('does not render empty categories', () => {
    const partialCategories: SkillCategories = {
      programming_languages: ['Python'],
      frameworks: [],
      databases: [],
      devops: [],
      soft_skills: [],
      other: []
    };
    
    render(<SkillCategoriesDisplay categories={partialCategories} />);
    
    expect(screen.getByText(/Programming Languages/)).toBeInTheDocument();
    expect(screen.queryByText(/Frameworks \(/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Databases \(/)).not.toBeInTheDocument();
  });

  it('renders skill badges with correct text', () => {
    render(<SkillCategoriesDisplay categories={mockCategories} />);
    
    expect(screen.getByText('Python')).toBeInTheDocument();
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('Docker')).toBeInTheDocument();
    expect(screen.getByText('PyTorch')).toBeInTheDocument();
  });

  it('shows skill count per category', () => {
    render(<SkillCategoriesDisplay categories={mockCategories} />);
    
    expect(screen.getByText(/Programming Languages \(3\)/)).toBeInTheDocument();
    expect(screen.getByText(/Frameworks \(3\)/)).toBeInTheDocument();
    expect(screen.getByText(/Databases \(2\)/)).toBeInTheDocument();
  });

  it('shows total skills count', () => {
    render(<SkillCategoriesDisplay categories={mockCategories} />);
    
    // Total: 3+3+2+3+2+2+1 = 16 skills
    expect(screen.getByText(/16 skills found/)).toBeInTheDocument();
  });

  it('handles empty categories object gracefully', () => {
    const emptyCategories: SkillCategories = {
      programming_languages: [],
      frameworks: [],
      databases: [],
      devops: [],
      soft_skills: [],
      other: []
    };
    
    render(<SkillCategoriesDisplay categories={emptyCategories} />);
    
    expect(screen.getByText(/No categorized skills available/)).toBeInTheDocument();
  });

  it('applies correct color classes for each category', () => {
    const singleSkillPerCategory: SkillCategories = {
      programming_languages: ['Python'],
      frameworks: ['React'],
      databases: ['PostgreSQL'],
      devops: ['Docker'],
      soft_skills: ['Teamwork'],
      ai_ml: ['PyTorch'],
      other: ['Git']
    };
    
    render(<SkillCategoriesDisplay categories={singleSkillPerCategory} />);
    
    // Check that badges are rendered (color classes are applied via Tailwind)
    const pythonBadge = screen.getByText('Python');
    expect(pythonBadge).toHaveClass('bg-blue-100', 'text-blue-800');
    
    const reactBadge = screen.getByText('React');
    expect(reactBadge).toHaveClass('bg-green-100', 'text-green-800');
    
    const postgresBadge = screen.getByText('PostgreSQL');
    expect(postgresBadge).toHaveClass('bg-purple-100', 'text-purple-800');
    
    const dockerBadge = screen.getByText('Docker');
    expect(dockerBadge).toHaveClass('bg-orange-100', 'text-orange-800');
    
    const teamworkBadge = screen.getByText('Teamwork');
    expect(teamworkBadge).toHaveClass('bg-pink-100', 'text-pink-800');
    
    const pytorchBadge = screen.getByText('PyTorch');
    expect(pytorchBadge).toHaveClass('bg-indigo-100', 'text-indigo-800');
    
    const gitBadge = screen.getByText('Git');
    expect(gitBadge).toHaveClass('bg-gray-100', 'text-gray-800');
  });

  it('renders with aria labels for accessibility', () => {
    render(<SkillCategoriesDisplay categories={mockCategories} />);
    
    const programmingList = screen.getByRole('list', { name: /Programming Languages skills/ });
    expect(programmingList).toBeInTheDocument();
  });

  it('handles categories with optional ai_ml field', () => {
    const withoutAiMl: SkillCategories = {
      programming_languages: ['Python'],
      frameworks: ['React'],
      databases: ['PostgreSQL'],
      devops: ['Docker'],
      soft_skills: ['Teamwork'],
      other: []
    };
    
    render(<SkillCategoriesDisplay categories={withoutAiMl} />);
    
    expect(screen.queryByText(/AI\/ML/)).not.toBeInTheDocument();
    expect(screen.getByText('Python')).toBeInTheDocument();
  });

  it('displays single category count correctly', () => {
    const singleCategory: SkillCategories = {
      programming_languages: ['Python'],
      frameworks: [],
      databases: [],
      devops: [],
      soft_skills: [],
      other: []
    };
    
    render(<SkillCategoriesDisplay categories={singleCategory} />);
    
    expect(screen.getByText(/1 skill found across 1 category/)).toBeInTheDocument();
  });
});
