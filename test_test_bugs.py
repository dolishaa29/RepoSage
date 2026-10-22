from unittest.mock import patch, MagicMock
import unittest
import test_bugs

class TestGetUser(unittest.TestCase):
    @patch("sqlite3.connect")
    def test_get_user_uses_parameterized_query(self, mock_connect):
        mock_db = MagicMock()
        mock_connect.return_value = mock_db
        
        test_bugs.get_user("alice' OR '1'='1")
        
        mock_db.execute.assert_called_once_with(
            "SELECT * FROM users WHERE name = ?",
            ("alice' OR '1'='1",)
        )

if __name__ == "__main__":
    unittest.main()
