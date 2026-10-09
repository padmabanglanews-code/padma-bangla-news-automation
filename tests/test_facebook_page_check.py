import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import facebook_page_check
import pipeline


class FacebookPageCheckTests(unittest.TestCase):
    def test_verifier_requests_page_identity_without_putting_token_in_url(self):
        token = "test-token-not-for-output"
        with (
            patch.dict(
                "os.environ",
                {"FACEBOOK_PAGE_ID": "123", "FACEBOOK_PAGE_ACCESS_TOKEN": token},
                clear=True,
            ),
            patch.object(
                pipeline,
                "_request_json",
                return_value={"id": "123", "name": "Padma Bangla News"},
            ) as request,
        ):
            result = pipeline.verify_facebook_page()

        self.assertEqual(result["status"], "success")
        args, kwargs = request.call_args
        self.assertEqual(args[0], "https://graph.facebook.com/v23.0/123?fields=id%2Cname")
        self.assertNotIn(token, args[0])
        self.assertEqual(kwargs["headers"]["Authorization"], f"Bearer {token}")
        self.assertNotIn("method", kwargs)

    def test_verifier_rejects_a_different_page_id(self):
        with (
            patch.dict(
                "os.environ",
                {"FACEBOOK_PAGE_ID": "123", "FACEBOOK_PAGE_ACCESS_TOKEN": "test-token"},
                clear=True,
            ),
            patch.object(pipeline, "_request_json", return_value={"id": "456", "name": "Other"}),
        ):
            with self.assertRaises(pipeline.PipelineError):
                pipeline.verify_facebook_page()

    def test_request_uses_get_and_a_bounded_timeout(self):
        response = unittest.mock.MagicMock()
        response.__enter__.return_value.read.return_value = b'{"id":"123","name":"Page"}'
        with patch.object(pipeline, "urlopen", return_value=response) as urlopen:
            result = pipeline._request_json(
                "https://graph.facebook.com/v23.0/123?fields=id%2Cname",
                headers={"Authorization": "Bearer test-token"},
            )

        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 30)
        self.assertEqual(result, {"id": "123", "name": "Page"})

    def test_entry_point_reports_pipeline_error_message(self):
        output = io.StringIO()
        with (
            patch.object(
                facebook_page_check,
                "verify_facebook_page",
                side_effect=pipeline.PipelineError("Missing GitHub settings: FACEBOOK_PAGE_ID"),
            ),
            redirect_stdout(output),
        ):
            result = facebook_page_check.main()

        self.assertEqual(result, 1)
        self.assertEqual(
            output.getvalue(),
            "Facebook Page verification failed: Missing GitHub settings: FACEBOOK_PAGE_ID\n",
        )

    def test_entry_point_reports_only_unexpected_exception_class(self):
        secret_text = "secret-token-and-response"
        output = io.StringIO()
        with (
            patch.object(
                facebook_page_check,
                "verify_facebook_page",
                side_effect=RuntimeError(secret_text),
            ),
            redirect_stdout(output),
        ):
            result = facebook_page_check.main()

        self.assertEqual(result, 1)
        self.assertEqual(
            output.getvalue(),
            "Facebook Page verification failed (RuntimeError). "
            "Check secure configuration and try again.\n",
        )
        self.assertNotIn(secret_text, output.getvalue())

    def test_facebook_http_error_reports_sanitized_graph_details(self):
        token = "fb-secret-token"
        secret = "client-secret-value"
        sensitive_url = "https://graph.facebook.com/v23.0/123?access_token=fb-secret-token"
        body = (
            '{"error":{"message":"Invalid token fb-secret-token; '
            'client secret client-secret-value; see https://example.test/path?token=x",'
            '"type":"OAuthException","code":190}}'
        ).encode()
        http_error = HTTPError(
            sensitive_url,
            401,
            "Unauthorized",
            {},
            io.BytesIO(body),
        )
        with (
            patch.dict(
                "os.environ",
                {
                    "FACEBOOK_PAGE_ACCESS_TOKEN": token,
                    "SERVICE_CLIENT_SECRET": secret,
                },
                clear=True,
            ),
            patch.object(pipeline, "urlopen", side_effect=http_error),
        ):
            with self.assertRaises(pipeline.PipelineError) as raised:
                pipeline._request_json(
                    "https://graph.facebook.com/v23.0/123?fields=id%2Cname",
                    headers={"Authorization": f"Bearer {token}"},
                    retries=1,
                )

        message = str(raised.exception)
        self.assertIn("code 190", message)
        self.assertIn("OAuthException", message)
        self.assertIn("Invalid token", message)
        self.assertNotIn(token, message)
        self.assertNotIn(secret, message)
        self.assertNotIn("https://", message)
        self.assertNotIn("access_token", message)

    def test_entry_point_reports_success_without_page_details(self):
        output = io.StringIO()
        with patch.object(
            facebook_page_check,
            "verify_facebook_page",
            return_value={"status": "success", "page_id": "123", "page_name": "Private Page"},
        ), redirect_stdout(output):
            result = facebook_page_check.main()

        self.assertEqual(result, 0)
        self.assertEqual(output.getvalue(), "Facebook Page verification passed.\n")
        self.assertNotIn("Private Page", output.getvalue())


if __name__ == "__main__":
    unittest.main()
