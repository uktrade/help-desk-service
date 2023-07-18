
from unittest.mock import patch
from unittest import mock
import pytest

from halo.clam_av import av_scan_file, check_av_service, \
                         skip_file_extension, CLAM_AV_HOST

from django.conf import settings

EICAR = settings.BASE_DIR / "tests/help_desk_api/eicar.txt"
CLEAN = settings.BASE_DIR / "tests/help_desk_api/clean_file.txt"

CLAM_AV_LINK = "host.docker.internal"
CLAM_AV_PATH = "/"
CLAM_AV_PATH_NOT_OK = "/v3"


class TestClamAVScan():

    # †est different file paths with the @pytest.mark.parametrize decorator
    @pytest.mark.parametrize("path", [
                (CLEAN),
    ])
    @patch("requests.post")
    def test_av_scan_malware_not_found(self, mock_post, path):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
                                        'malware': False, 
                                        'reason': None, 
                                        'time': 0.0049}
        av_passed = av_scan_file(path)
        assert av_passed is True


    @pytest.mark.parametrize("path", [
                (EICAR),
    ])
    @patch("requests.post")
    def test_av_scan_malware_found(self, mock_post, path):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
                                      'malware': True, 
                                      'reason': 'Win.Test.EICAR_HDB-1', 
                                      'time': 0.0057}
        av_passed = av_scan_file(path)
        assert av_passed is False

    
    @patch("requests.get")
    @pytest.mark.parametrize("url, av_path", [
                (CLAM_AV_HOST, CLAM_AV_PATH),
    ])
    def test_av_service_ok(self, mocker, url, av_path):
        mocker.return_value.status_code = 200
        service = check_av_service(url, av_path)
        assert service == "OK"


    @patch("requests.get")
    @pytest.mark.parametrize("url, av_path", [
                (CLAM_AV_HOST, CLAM_AV_PATH_NOT_OK),
    ])
    def test_av_service_not_ok(self, mocker, url, av_path):
        mocker.return_value.status_code = 404
        service = check_av_service(url, av_path)
        assert service == "NOT OK"

    
    @mock.patch("halo.clam_av.pathlib")
    def test_no_connection_if_ext_exempt(self, mocker ):
        assert skip_file_extension(EICAR) is False

    