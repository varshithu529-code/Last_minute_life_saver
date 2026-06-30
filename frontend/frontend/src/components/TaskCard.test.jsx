import { render, screen } from '@testing-library/react';
import TaskCard from '../components/TaskCard';

describe('TaskCard', () => {
  it('renders task title and score', () => {
    const task = {
      id: 1,
      title: 'Test task',
      description: 'Description',
      status: 'todo',
      priority: 'urgent_important',
      ml_score: 0.85,
      due_date: '2026-06-30T12:00:00',
    };
    render(<TaskCard task={task} />);
    expect(screen.getByText('Test task')).toBeInTheDocument();
    expect(screen.getByText(/85%/)).toBeInTheDocument();
  });
});
