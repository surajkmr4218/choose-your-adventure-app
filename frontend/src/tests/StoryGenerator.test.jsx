import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import axios from 'axios'
import StoryGenerator from '../components/StoryGenerator'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

// Mock react-router-dom
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate
  }
})

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('StoryGenerator', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.clearAllTimers()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders theme input initially', () => {
    renderWithRouter(<StoryGenerator />)
    
    expect(screen.getByText('Enter a theme for your interactive story')).toBeInTheDocument()
  })

  it('shows loading status after story creation', async () => {
    mockedAxios.post.mockResolvedValueOnce({
      data: { job_id: 'test-job-id', status: 'pending' }
    })

    renderWithRouter(<StoryGenerator />)
    
    const input = screen.getByPlaceholderText('Enter a theme (e.g. prirates, space, medieval...)')
    const button = screen.getByText('Generate Story')
    
    fireEvent.change(input, { target: { value: 'fantasy' } })
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText('Creating your fantasy adventure...')).toBeInTheDocument()
    })
  })

  it('polls job status after story creation', async () => {
    mockedAxios.post.mockResolvedValueOnce({
      data: { job_id: 'test-job-id', status: 'processing' }
    })
    mockedAxios.get.mockResolvedValueOnce({
      data: { status: 'processing' }
    })

    renderWithRouter(<StoryGenerator />)
    
    const input = screen.getByPlaceholderText('Enter a theme (e.g. prirates, space, medieval...)')
    const button = screen.getByText('Generate Story')
    
    fireEvent.change(input, { target: { value: 'fantasy' } })
    fireEvent.click(button)

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'http://localhost:8000/api/stories/create',
        { theme: 'fantasy' }
      )
    })

    // Fast-forward time to trigger polling
    vi.advanceTimersByTime(5000)

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith(
        'http://localhost:8000/api/jobs/test-job-id'
      )
    })
  })

  it('navigates to story page when job completes', async () => {
    mockedAxios.post.mockResolvedValueOnce({
      data: { job_id: 'test-job-id', status: 'processing' }
    })
    mockedAxios.get.mockResolvedValueOnce({
      data: { status: 'completed', story_id: 123 }
    })

    renderWithRouter(<StoryGenerator />)
    
    const input = screen.getByPlaceholderText('Enter a theme (e.g. prirates, space, medieval...)')
    const button = screen.getByText('Generate Story')
    
    fireEvent.change(input, { target: { value: 'fantasy' } })
    fireEvent.click(button)

    // Fast-forward time to trigger polling
    vi.advanceTimersByTime(5000)

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/story/123')
    })
  })

  it('shows error message when story generation fails', async () => {
    mockedAxios.post.mockRejectedValueOnce(new Error('Network error'))

    renderWithRouter(<StoryGenerator />)
    
    const input = screen.getByPlaceholderText('Enter a theme (e.g. prirates, space, medieval...)')
    const button = screen.getByText('Generate Story')
    
    fireEvent.change(input, { target: { value: 'fantasy' } })
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText('Failed to generate story: Network error')).toBeInTheDocument()
    })
  })

  it('shows error message when job fails', async () => {
    mockedAxios.post.mockResolvedValueOnce({
      data: { job_id: 'test-job-id', status: 'processing' }
    })
    mockedAxios.get.mockResolvedValueOnce({
      data: { status: 'failed', error: 'LLM error' }
    })

    renderWithRouter(<StoryGenerator />)
    
    const input = screen.getByPlaceholderText('Enter a theme (e.g. prirates, space, medieval...)')
    const button = screen.getByText('Generate Story')
    
    fireEvent.change(input, { target: { value: 'fantasy' } })
    fireEvent.click(button)

    // Fast-forward time to trigger polling
    vi.advanceTimersByTime(5000)

    await waitFor(() => {
      expect(screen.getByText('LLM error')).toBeInTheDocument()
    })
  })

  it('resets state when try again button is clicked', async () => {
    mockedAxios.post.mockRejectedValueOnce(new Error('Network error'))

    renderWithRouter(<StoryGenerator />)
    
    const input = screen.getByPlaceholderText('Enter a theme (e.g. prirates, space, medieval...)')
    const button = screen.getByText('Generate Story')
    
    fireEvent.change(input, { target: { value: 'fantasy' } })
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText('Failed to generate story: Network error')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Try Again'))

    expect(screen.getByText('Enter a theme for your interactive story')).toBeInTheDocument()
    expect(screen.queryByText('Failed to generate story: Network error')).not.toBeInTheDocument()
  })
})