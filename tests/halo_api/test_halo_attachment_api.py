import base64
import json
from unittest import mock
from unittest.mock import MagicMock

from halo.halo_manager import HaloManager


class TestHaloAttachmentAPI:
    @mock.patch("halo.halo_api_client.requests.post")
    def test_manager_correctly_encodes_attachment_for_api(
        self, mock_post: MagicMock, access_token, attachment_filename: str, attachment_data: bytes
    ):
        halo_manager: HaloManager
        # Set up the mock to pretend to authenticate us
        mock_post.return_value.json.return_value = access_token
        mock_post.return_value.status_code = 200
        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        # Now set up the mock to pretend to handle the upload
        mock_response = {"foo": "bar"}
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.status_code = 201

        halo_manager.upload_file(attachment_filename, attachment_data)

        actual_payload = json.loads(mock_post.call_args[1]["data"])[0]
        base64_payload = base64.b64encode(attachment_data).decode("ascii")  # /PS-IGNORE
        expected_payload = f"data:text/plain;base64,{base64_payload}"
        assert "filename" in actual_payload
        assert actual_payload["filename"] == attachment_filename
        assert "data_base64" in actual_payload
        assert actual_payload["data_base64"] == expected_payload
