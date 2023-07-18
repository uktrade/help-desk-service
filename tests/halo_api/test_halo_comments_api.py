from unittest.mock import patch

import pytest
from halo.halo_api_client import HaloClientNotFoundException
from halo.halo_manager import HaloManager

from help_desk_api.serializers import HaloToZendeskCommentSerializer


class TestCommentsViews:
    """
    Get Comments Tests
    """

    @patch("requests.get")
    @patch("requests.post")
    def test_get_comment_success(self, mock_post, mock_get):
        """
        GET Comment Success
        """
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "fake-access-token"}

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "actions": [{"outcome": "comment", "id": 1, "note": "note", "who": "Test"}]
        }

        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        comment = halo_manager.get_comments(123)
        assert isinstance(comment[0], HaloToZendeskCommentSerializer)
        assert isinstance(comment, list)
        assert comment[0].note == "note"

    @patch("requests.get")
    @patch("requests.post")
    def test_get_comment_failure(self, mock_post, mock_get):
        """
        GET Comment Failure
        """
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "fake-access-token"}

        mock_get.return_value.status_code = 400
        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        with pytest.raises(HaloClientNotFoundException) as excinfo:
            halo_manager.get_comments(123)
        assert excinfo.typename == "HaloClientNotFoundException"
