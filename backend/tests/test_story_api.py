from unittest.mock import patch
from models.story import Story, StoryNode
from models.job import StoryJob


class TestStoryAPI:
    
    def test_create_story_endpoint(self, client, db_session):
        """Test story creation endpoint returns job"""
        response = client.post("/api/stories/create", json={"theme": "fantasy"})
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"
        assert "created_at" in data
        
        # Verify job was created in database
        job = db_session.query(StoryJob).filter(StoryJob.job_id == data["job_id"]).first()
        assert job is not None
        assert job.theme == "fantasy"
    
    def test_get_complete_story_success(self, client, db_session):
        """Test retrieving a complete story"""
        # Create test story with nodes
        story = Story(title="Test Story", session_id="test-session")
        db_session.add(story)
        db_session.flush()
        
        root_node = StoryNode(
            story_id=story.id,
            content="Root content",
            is_root=True,
            is_ending=False,
            is_winning_ending=False,
            options=[{"text": "Option 1", "node_id": 2}]
        )
        ending_node = StoryNode(
            story_id=story.id,
            content="Ending content", 
            is_root=False,
            is_ending=True,
            is_winning_ending=True,
            options=[]
        )
        db_session.add_all([root_node, ending_node])
        db_session.commit()
        
        response = client.get(f"/api/stories/{story.id}/complete")
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Story"
        assert data["session_id"] == "test-session"
        assert "root_node" in data
        assert "all_nodes" in data
    
    def test_get_complete_story_not_found(self, client):
        """Test retrieving non-existent story returns 404"""
        response = client.get("/api/stories/999/complete")
        assert response.status_code == 404
        assert response.json()["detail"] == "Story not found"
    
    @patch('core.story_generator.StoryGenerator.generate_story')
    @patch('routers.story.SessionLocal')
    def test_generate_story_task_success(self, mock_session_local, mock_generate, db_session, mock_openai_response):
        """Test successful story generation task"""
        from routers.story import generate_story_task
        
        # Mock the session to use our test session
        mock_session_local.return_value = db_session
        
        # Create a test job
        job = StoryJob(
            job_id="test-job-id",
            session_id="test-session",
            theme="fantasy",
            status="pending"
        )
        db_session.add(job)
        db_session.commit()
        
        # Mock story generation
        mock_story = Story(id=1, title="Generated Story", session_id="test-session")
        mock_generate.return_value = mock_story
        
        # Run the task
        generate_story_task("test-job-id", "fantasy", "test-session")
        
        # Verify job was updated
        updated_job = db_session.query(StoryJob).filter(StoryJob.job_id == "test-job-id").first()
        assert updated_job.status == "completed"
        assert updated_job.story_id == 1
        assert updated_job.completed_at is not None
    
    def test_session_id_cookie_handling(self, client):
        """Test that session ID is properly handled in cookies"""
        response = client.post("/api/stories/create", json={"theme": "sci-fi"})
        
        assert response.status_code == 200
        # Check that session cookie was set
        assert "session_id" in response.cookies