import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import StoryGame from '../components/StoryGame'

const mockStory = {
  id: 1,
  title: "Test Adventure",
  root_node: {
    id: 1,
    content: "You find yourself in a mysterious forest.",
    is_ending: false,
    is_winning_ending: false,
    options: [
      { text: "Go left", node_id: 2 },
      { text: "Go right", node_id: 3 }
    ]
  },
  all_nodes: {
    1: {
      id: 1,
      content: "You find yourself in a mysterious forest.",
      is_ending: false,
      is_winning_ending: false,
      options: [
        { text: "Go left", node_id: 2 },
        { text: "Go right", node_id: 3 }
      ]
    },
    2: {
      id: 2,
      content: "You found treasure!",
      is_ending: true,
      is_winning_ending: true,
      options: []
    },
    3: {
      id: 3,
      content: "You fell into a trap.",
      is_ending: true,
      is_winning_ending: false,
      options: []
    }
  }
}

describe('StoryGame', () => {
  it('renders story title and initial content', () => {
    render(<StoryGame story={mockStory} />)
    
    expect(screen.getByText('Test Adventure')).toBeInTheDocument()
    expect(screen.getByText('You find yourself in a mysterious forest.')).toBeInTheDocument()
  })

  it('renders story options when not at ending', () => {
    render(<StoryGame story={mockStory} />)
    
    expect(screen.getByText('What will you do?')).toBeInTheDocument()
    expect(screen.getByText('Go left')).toBeInTheDocument()
    expect(screen.getByText('Go right')).toBeInTheDocument()
  })

  it('navigates to next node when option is clicked', () => {
    render(<StoryGame story={mockStory} />)
    
    const leftOption = screen.getByText('Go left')
    fireEvent.click(leftOption)
    
    expect(screen.getByText('You found treasure!')).toBeInTheDocument()
    expect(screen.getByText('Congratulations')).toBeInTheDocument()
    expect(screen.getByText('You reached a winning ending')).toBeInTheDocument()
  })

  it('shows losing ending correctly', () => {
    render(<StoryGame story={mockStory} />)
    
    const rightOption = screen.getByText('Go right')
    fireEvent.click(rightOption)
    
    expect(screen.getByText('You fell into a trap.')).toBeInTheDocument()
    expect(screen.getByText('The End')).toBeInTheDocument()
    expect(screen.getByText('Your adventure has ended.')).toBeInTheDocument()
  })

  it('hides options at story ending', () => {
    render(<StoryGame story={mockStory} />)
    
    fireEvent.click(screen.getByText('Go left'))
    
    expect(screen.queryByText('What will you do?')).not.toBeInTheDocument()
    expect(screen.queryByText('Go left')).not.toBeInTheDocument()
    expect(screen.queryByText('Go right')).not.toBeInTheDocument()
  })

  it('restarts story when restart button is clicked', () => {
    render(<StoryGame story={mockStory} />)
    
    // Navigate to ending
    fireEvent.click(screen.getByText('Go left'))
    expect(screen.getByText('You found treasure!')).toBeInTheDocument()
    
    // Restart story
    fireEvent.click(screen.getByText('Restart Story'))
    expect(screen.getByText('You find yourself in a mysterious forest.')).toBeInTheDocument()
    expect(screen.getByText('What will you do?')).toBeInTheDocument()
  })

  it('calls onNewStory when new story button is clicked', () => {
    const mockOnNewStory = vi.fn()
    render(<StoryGame story={mockStory} onNewStory={mockOnNewStory} />)
    
    fireEvent.click(screen.getByText('New Story'))
    expect(mockOnNewStory).toHaveBeenCalledTimes(1)
  })

  it('does not render new story button when onNewStory not provided', () => {
    render(<StoryGame story={mockStory} />)
    
    expect(screen.queryByText('New Story')).not.toBeInTheDocument()
  })
})