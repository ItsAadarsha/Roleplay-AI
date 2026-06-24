# Tests for database.py functions
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from bson import ObjectId
from bson.errors import InvalidId
from database import save_session, get_sessions, pick_session


class TestSaveSession:
    """Test suite for save_session() function."""

    @patch('database.sessions_col')
    @patch('database.success')
    def test_save_session_new_session(self, mock_success, mock_col):
        """Test saving a new session without session_id."""
        # Arrange
        persona_name = "Lyra"
        messages = [
            {"role": "system", "content": "You are Lyra..."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        mock_col.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        # Act
        save_session(persona_name, messages)
        
        # Assert
        mock_col.insert_one.assert_called_once()
        call_args = mock_col.insert_one.call_args[0][0]
        assert call_args["persona"] == persona_name
        assert call_args["messages"] == messages
        assert "created_at" in call_args
        assert "updated_at" in call_args
        assert isinstance(call_args["created_at"], datetime)
        assert isinstance(call_args["updated_at"], datetime)

    @patch('database.sessions_col')
    @patch('database.info')
    def test_save_session_empty_messages_returns_early(self, mock_info, mock_col):
        """Test that empty messages list triggers early return without DB call."""
        # Arrange
        persona_name = "Lyra"
        messages = []
        
        # Act
        save_session(persona_name, messages)
        
        # Assert
        mock_col.insert_one.assert_not_called()
        mock_col.update_one.assert_not_called()
        mock_info.assert_called_once_with("No messages to save.")

    @patch('database.sessions_col')
    def test_save_session_update_existing_session_with_objectid(self, mock_col):
        """Test updating an existing session with ObjectId string."""
        # Arrange
        persona_name = "Lyra"
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi!"}
        ]
        session_id = str(ObjectId())  # Valid ObjectId string
        mock_col.update_one.return_value = Mock(matched_count=1)
        
        # Act
        save_session(persona_name, messages, session_id)
        
        # Assert
        mock_col.update_one.assert_called_once()
        assert not mock_col.insert_one.called

    @patch('database.sessions_col')
    def test_save_session_update_with_invalid_objectid_string(self, mock_col):
        """Test updating session with invalid ObjectId string falls back to insert."""
        # Arrange
        persona_name = "Lyra"
        messages = [{"role": "user", "content": "Test"}]
        session_id = "invalid-id"
        mock_col.update_one.return_value = Mock(matched_count=0)
        mock_col.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        # Act
        save_session(persona_name, messages, session_id)
        
        # Assert
        # Should try update first, then insert when no match found
        mock_col.update_one.assert_called_once()
        mock_col.insert_one.assert_called_once()

    @patch('database.sessions_col')
    def test_save_session_update_no_match_inserts_new(self, mock_col):
        """Test that update without match inserts a new session."""
        # Arrange
        persona_name = "Lyra"
        messages = [{"role": "user", "content": "Test"}]
        session_id = str(ObjectId())
        mock_col.update_one.return_value = Mock(matched_count=0)  # No match
        mock_col.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        # Act
        save_session(persona_name, messages, session_id)
        
        # Assert
        mock_col.update_one.assert_called_once()
        mock_col.insert_one.assert_called_once()

    @patch('database.sessions_col')
    def test_save_session_long_messages_list(self, mock_col):
        """Test saving session with many messages."""
        # Arrange
        persona_name = "Lyra"
        messages = [{"role": "user" if i % 2 == 0 else "assistant", "content": f"Message {i}"} 
                   for i in range(100)]
        mock_col.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        # Act
        save_session(persona_name, messages)
        
        # Assert
        call_args = mock_col.insert_one.call_args[0][0]
        assert len(call_args["messages"]) == 100

    @patch('database.sessions_col')
    def test_save_session_special_characters_in_messages(self, mock_col):
        """Test saving session with special characters in message content."""
        # Arrange
        persona_name = "Lyra"
        messages = [
            {"role": "user", "content": "Hello! @#$%^&*()"},
            {"role": "assistant", "content": "Response with 'quotes' and \"double quotes\""}
        ]
        mock_col.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        # Act
        save_session(persona_name, messages)
        
        # Assert
        call_args = mock_col.insert_one.call_args[0][0]
        assert call_args["messages"] == messages

    @patch('database.sessions_col')
    @patch('database.success')
    def test_save_session_prints_success_message_new(self, mock_success, mock_col):
        """Test that success message is printed for new session."""
        # Arrange
        messages = [{"role": "user", "content": "Test"}]
        mock_col.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        # Act
        save_session("Lyra", messages)
        
        # Assert
        mock_success.assert_called_once_with("Session saved.")

    @patch('database.sessions_col')
    @patch('database.success')
    def test_save_session_prints_success_message_update(self, mock_success, mock_col):
        """Test that success message is printed for session update."""
        # Arrange
        session_id = str(ObjectId())
        messages = [{"role": "user", "content": "Test"}]
        mock_col.update_one.return_value = Mock(matched_count=1)
        
        # Act
        save_session("Lyra", messages, session_id)
        
        # Assert
        mock_success.assert_called_once_with("Session updated.")

    @patch('database.sessions_col')
    def test_save_session_update_operation_structure(self, mock_col):
        """Test that update operation has correct structure."""
        # Arrange
        persona_name = "TestPersona"
        messages = [{"role": "user", "content": "Test"}]
        session_id = str(ObjectId())
        mock_col.update_one.return_value = Mock(matched_count=1)
        
        # Act
        save_session(persona_name, messages, session_id)
        
        # Assert
        call_args = mock_col.update_one.call_args
        query_filter = call_args[0][0]
        update_doc = call_args[0][1]
        
        assert "_id" in query_filter
        assert "$set" in update_doc
        assert update_doc["$set"]["persona"] == persona_name
        assert update_doc["$set"]["messages"] == messages
        assert "updated_at" in update_doc["$set"]

    @patch('database.sessions_col')
    def test_save_session_objectid_conversion_valid(self, mock_col):
        """Test that valid ObjectId string is converted correctly."""
        # Arrange
        valid_objectid = ObjectId()
        session_id = str(valid_objectid)
        messages = [{"role": "user", "content": "Test"}]
        mock_col.update_one.return_value = Mock(matched_count=1)
        
        # Act
        save_session("Lyra", messages, session_id)
        
        # Assert
        call_args = mock_col.update_one.call_args[0][0]
        assert call_args["_id"] == valid_objectid

    @patch('database.sessions_col')
    def test_save_session_invalid_objectid_uses_string_directly(self, mock_col):
        """Test that invalid ObjectId string is used as-is (not converted)."""
        # Arrange
        invalid_id = "not-a-valid-objectid"
        messages = [{"role": "user", "content": "Test"}]
        mock_col.update_one.return_value = Mock(matched_count=0)
        mock_col.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        # Act
        save_session("Lyra", messages, invalid_id)
        
        # Assert
        # The update should be attempted with the string as-is
        call_args = mock_col.update_one.call_args[0][0]
        assert call_args["_id"] == invalid_id

    @patch('database.sessions_col')
    @patch('database.info')
    def test_save_session_none_session_id_creates_new(self, mock_info, mock_col):
        """Test that None session_id creates a new session."""
        # Arrange
        persona_name = "Lyra"
        messages = [{"role": "user", "content": "Test"}]
        mock_col.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        # Act
        save_session(persona_name, messages, None)
        
        # Assert
        mock_col.insert_one.assert_called_once()
        mock_col.update_one.assert_not_called()


class TestGetSessions:
    """Test suite for get_sessions() function."""

    @patch('database.sessions_col')
    def test_get_sessions_returns_sessions(self, mock_col):
        """Test that get_sessions returns list of sessions."""
        # Arrange
        persona_name = "Lyra"
        mock_sessions = [
            {"_id": ObjectId(), "created_at": datetime.now(), "messages": [{"role": "user", "content": "Test"}]},
            {"_id": ObjectId(), "created_at": datetime.now(), "messages": [{"role": "user", "content": "Test2"}]}
        ]
        mock_cursor = Mock()
        mock_cursor.sort.return_value.limit.return_value = mock_sessions
        mock_col.find.return_value = mock_cursor
        
        # Act
        result = get_sessions(persona_name)
        
        # Assert
        assert result == mock_sessions
        mock_col.find.assert_called_once_with(
            {"persona": persona_name},
            {"_id": 1, "created_at": 1, "messages": 1}
        )

    @patch('database.sessions_col')
    def test_get_sessions_returns_empty_list(self, mock_col):
        """Test that get_sessions returns empty list when no sessions exist."""
        # Arrange
        persona_name = "UnknownPersona"
        mock_cursor = Mock()
        mock_cursor.sort.return_value.limit.return_value = []
        mock_col.find.return_value = mock_cursor
        
        # Act
        result = get_sessions(persona_name)
        
        # Assert
        assert result == []

    @patch('database.sessions_col')
    def test_get_sessions_limits_to_five(self, mock_col):
        """Test that get_sessions limits results to 5 sessions."""
        # Arrange
        persona_name = "Lyra"
        mock_cursor = Mock()
        mock_cursor.sort.return_value.limit.return_value = []
        mock_col.find.return_value = mock_cursor
        
        # Act
        get_sessions(persona_name)
        
        # Assert
        mock_cursor.sort.assert_called_once_with("created_at", -1)
        mock_cursor.sort.return_value.limit.assert_called_once_with(5)

    @patch('database.sessions_col')
    def test_get_sessions_sorts_by_created_at_descending(self, mock_col):
        """Test that get_sessions sorts by created_at in descending order."""
        # Arrange
        persona_name = "Lyra"
        mock_cursor = Mock()
        mock_cursor.sort.return_value.limit.return_value = []
        mock_col.find.return_value = mock_cursor
        
        # Act
        get_sessions(persona_name)
        
        # Assert
        mock_cursor.sort.assert_called_once_with("created_at", -1)

    @patch('database.sessions_col')
    def test_get_sessions_projection_fields(self, mock_col):
        """Test that get_sessions uses correct projection."""
        # Arrange
        persona_name = "Lyra"
        mock_cursor = Mock()
        mock_cursor.sort.return_value.limit.return_value = []
        mock_col.find.return_value = mock_cursor
        
        # Act
        get_sessions(persona_name)
        
        # Assert
        call_args = mock_col.find.call_args
        assert call_args[0][1] == {"_id": 1, "created_at": 1, "messages": 1}

    @patch('database.sessions_col')
    def test_get_sessions_projection_excludes_unexpected_fields(self, mock_col):
        """Test that returned documents only contain projected fields."""
        # Arrange
        persona_name = "Lyra"
        mock_sessions = [
            {"_id": ObjectId(), "created_at": datetime.now(), "messages": [{"role": "user", "content": "Test"}]}
        ]
        mock_cursor = Mock()
        mock_cursor.sort.return_value.limit.return_value = mock_sessions
        mock_col.find.return_value = mock_cursor
        
        # Act
        result = get_sessions(persona_name)
        
        # Assert
        assert len(result) == 1
        session = result[0]
        # Verify expected fields are present
        assert "_id" in session
        assert "created_at" in session
        assert "messages" in session
        # Verify unexpected fields are NOT present (projection working)
        assert "persona" not in session
        assert "updated_at" not in session


class TestPickSession:
    """Test suite for pick_session() function."""

    @patch('database.get_sessions')
    def test_pick_session_no_sessions_returns_none(self, mock_get_sessions):
        """Test that pick_session returns None if no sessions exist."""
        # Arrange
        mock_get_sessions.return_value = []
        
        # Act
        result = pick_session("Lyra")
        
        # Assert
        assert result is None
        mock_get_sessions.assert_called_once_with("Lyra")

    @patch('database.prompt_input')
    @patch('database.print_sessions')
    @patch('database.get_sessions')
    def test_pick_session_returns_none_on_n(self, mock_get_sessions, mock_print_sessions, mock_prompt_input):
        """Test that entering 'n' or 'N' returns None."""
        # Arrange
        mock_get_sessions.return_value = [{"_id": "1", "created_at": datetime.now(), "messages": []}]
        mock_prompt_input.return_value = " N "  # Test trimming and case-insensitivity
        
        # Act
        result = pick_session("Lyra")
        
        # Assert
        assert result is None
        mock_print_sessions.assert_called_once()

    @patch('database.prompt_input')
    @patch('database.print_sessions')
    @patch('database.get_sessions')
    def test_pick_session_returns_session_on_valid_index(self, mock_get_sessions, mock_print_sessions, mock_prompt_input):
        """Test that entering a valid index returns the correct session."""
        # Arrange
        sessions = [
            {"_id": "session1", "created_at": datetime.now(), "messages": []},
            {"_id": "session2", "created_at": datetime.now(), "messages": []}
        ]
        mock_get_sessions.return_value = sessions
        mock_prompt_input.return_value = "2"
        
        # Act
        result = pick_session("Lyra")
        
        # Assert
        assert result == sessions[1]

    @patch('builtins.print')
    @patch('database.prompt_input')
    @patch('database.print_sessions')
    @patch('database.get_sessions')
    def test_pick_session_exits_on_exit(self, mock_get_sessions, mock_print_sessions, mock_prompt_input, mock_print):
        """Test that entering 'exit' raises SystemExit(0)."""
        # Arrange
        mock_get_sessions.return_value = [{"_id": "1", "created_at": datetime.now(), "messages": []}]
        mock_prompt_input.return_value = " ExIt "
        
        # Act & Assert
        with pytest.raises(SystemExit) as exc_info:
            pick_session("Lyra")
        
        assert exc_info.value.code == 0
        mock_print.assert_any_call("Exiting program. Goodbye!")

    @patch('builtins.print')
    @patch('database.prompt_input')
    @patch('database.print_sessions')
    @patch('database.get_sessions')
    def test_pick_session_empty_input_then_valid(self, mock_get_sessions, mock_print_sessions, mock_prompt_input, mock_print):
        """Test that empty input is handled and loops until a valid input is given."""
        # Arrange
        sessions = [{"_id": "session1", "created_at": datetime.now(), "messages": []}]
        mock_get_sessions.return_value = sessions
        mock_prompt_input.side_effect = ["", "1"]
        
        # Act
        result = pick_session("Lyra")
        
        # Assert
        assert result == sessions[0]
        mock_print.assert_any_call("Input cannot be empty. Please try again.")

    @patch('builtins.print')
    @patch('database.prompt_input')
    @patch('database.print_sessions')
    @patch('database.get_sessions')
    def test_pick_session_out_of_bounds_then_valid(self, mock_get_sessions, mock_print_sessions, mock_prompt_input, mock_print):
        """Test that out of bounds index prints error and loops until valid."""
        # Arrange
        sessions = [{"_id": "session1", "created_at": datetime.now(), "messages": []}]
        mock_get_sessions.return_value = sessions
        mock_prompt_input.side_effect = ["0", "2", "1"]
        
        # Act
        result = pick_session("Lyra")
        
        # Assert
        assert result == sessions[0]
        mock_print.assert_any_call("Please enter a number between 1 and 1.")

    @patch('builtins.print')
    @patch('database.prompt_input')
    @patch('database.print_sessions')
    @patch('database.get_sessions')
    def test_pick_session_invalid_format_then_valid(self, mock_get_sessions, mock_print_sessions, mock_prompt_input, mock_print):
        """Test that non-numeric invalid input prints error and loops until valid."""
        # Arrange
        sessions = [{"_id": "session1", "created_at": datetime.now(), "messages": []}]
        mock_get_sessions.return_value = sessions
        mock_prompt_input.side_effect = ["not-a-number", "1"]
        
        # Act
        result = pick_session("Lyra")
        
        # Assert
        assert result == sessions[0]
        mock_print.assert_any_call("Invalid input. Enter a number, N, or Exit.")

    @patch('builtins.print')
    @patch('database.prompt_input')
    @patch('database.print_sessions')
    @patch('database.get_sessions')
    def test_pick_session_keyboard_interrupt(self, mock_get_sessions, mock_print_sessions, mock_prompt_input, mock_print):
        """Test that KeyboardInterrupt returns None and prints cancellation message."""
        # Arrange
        mock_get_sessions.return_value = [{"_id": "1", "created_at": datetime.now(), "messages": []}]
        mock_prompt_input.side_effect = KeyboardInterrupt
        
        # Act
        result = pick_session("Lyra")
        
        # Assert
        assert result is None
        mock_print.assert_any_call("\nInput cancelled.")

    @patch('builtins.print')
    @patch('database.prompt_input')
    @patch('database.print_sessions')
    @patch('database.get_sessions')
    def test_pick_session_eof_error(self, mock_get_sessions, mock_print_sessions, mock_prompt_input, mock_print):
        """Test that EOFError returns None and prints cancellation message."""
        # Arrange
        mock_get_sessions.return_value = [{"_id": "1", "created_at": datetime.now(), "messages": []}]
        mock_prompt_input.side_effect = EOFError
        
        # Act
        result = pick_session("Lyra")
        
        # Assert
        assert result is None
        mock_print.assert_any_call("\nInput cancelled.")



