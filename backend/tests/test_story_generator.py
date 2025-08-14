from unittest.mock import patch, MagicMock
from core.story_generator import StoryGenerator
from core.models import StoryNodeLLM
from models.story import Story, StoryNode


class TestStoryGenerator:
    
    @patch('core.story_generator.ChatOpenAI')
    def test_get_llm_with_env_api_key(self, mock_chat_openai):
        """Test LLM initialization with environment API key"""
        with patch('os.getenv', return_value="test-api-key"):
            StoryGenerator._get_llm()
            mock_chat_openai.assert_called_with(model="gpt-4o-mini", api_key="test-api-key")
    
    @patch('core.story_generator.ChatOpenAI')
    def test_get_llm_without_env_api_key(self, mock_chat_openai):
        """Test LLM initialization without environment API key"""
        with patch('os.getenv', return_value=None):
            StoryGenerator._get_llm()
            mock_chat_openai.assert_called_with(model="gpt-4o-mini")
    
    @patch('core.story_generator.StoryGenerator._get_llm')
    def test_generate_story_success(self, mock_get_llm, db_session, mock_openai_response):
        """Test successful story generation"""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '''
        {
            "title": "Test Adventure",
            "rootNode": {
                "content": "You find yourself in a mysterious forest.",
                "isEnding": false,
                "isWinningEnding": false,
                "options": [
                    {
                        "text": "Go left",
                        "nextNode": {
                            "content": "You found treasure!",
                            "isEnding": true,
                            "isWinningEnding": true,
                            "options": []
                        }
                    }
                ]
            }
        }
        '''
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        # Generate story
        story = StoryGenerator.generate_story(db_session, "test-session", "fantasy")
        
        # Verify story was created
        assert isinstance(story, Story)
        assert story.title == "Test Adventure"
        assert story.session_id == "test-session"
        
        # Verify nodes were created
        nodes = db_session.query(StoryNode).filter(StoryNode.story_id == story.id).all()
        assert len(nodes) == 2  # Root node + one ending node
        
        root_node = next((node for node in nodes if node.is_root), None)
        assert root_node is not None
        assert root_node.content == "You find yourself in a mysterious forest."
        assert not root_node.is_ending
        assert len(root_node.options) == 1
    
    def test_process_story_node_dict_conversion(self, db_session):
        """Test that dict node data is properly converted to StoryNodeLLM"""
        node_dict = {
            "content": "Test content",
            "isEnding": True,
            "isWinningEnding": False,
            "options": []
        }
        
        node = StoryGenerator._process_story_node(db_session, 1, node_dict, is_root=True)
        
        assert isinstance(node, StoryNode)
        assert node.content == "Test content"
        assert node.is_ending
        assert not node.is_winning_ending
        assert node.is_root
    
    def test_process_story_node_with_options(self, db_session):
        """Test processing node with multiple options"""
        from core.models import StoryOptionLLM
        
        node_data = StoryNodeLLM(
            content="Root content",
            isEnding=False,
            isWinningEnding=False,
            options=[
                StoryOptionLLM(
                    text='Option 1',
                    nextNode={
                        "content": "Ending 1",
                        "isEnding": True,
                        "isWinningEnding": True,
                        "options": []
                    }
                ),
                StoryOptionLLM(
                    text='Option 2',
                    nextNode={
                        "content": "Ending 2",
                        "isEnding": True,
                        "isWinningEnding": False,
                        "options": []
                    }
                )
            ]
        )
        
        root_node = StoryGenerator._process_story_node(db_session, 1, node_data, is_root=True)
        
        assert len(root_node.options) == 2
        assert root_node.options[0]["text"] == "Option 1"
        assert root_node.options[1]["text"] == "Option 2"
        
        # Verify child nodes were created
        all_nodes = db_session.query(StoryNode).filter(StoryNode.story_id == 1).all()
        assert len(all_nodes) == 3  # Root + 2 endings