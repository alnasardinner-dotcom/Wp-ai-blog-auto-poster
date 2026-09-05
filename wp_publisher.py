import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse

class WordPressPublisher:
    def __init__(self, site_url: str, username: str, app_password: str):
        # Clean site URL
        cleaned_url = site_url.strip().rstrip('/')
        if not cleaned_url.startswith('http://') and not cleaned_url.startswith('https://'):
            cleaned_url = 'https://' + cleaned_url
        self.site_url = cleaned_url
        self.username = username.strip()
        # Application password may contain spaces from WP UI, keep clean
        self.app_password = app_password.strip()
        self.api_endpoint = f"{self.site_url}/wp-json/wp/v2/posts"

    def test_connection(self) -> dict:
        """
        Tests connection to WordPress REST API using user credentials.
        """
        user_endpoint = f"{self.site_url}/wp-json/wp/v2/users/me"
        try:
            response = requests.get(
                user_endpoint,
                auth=HTTPBasicAuth(self.username, self.app_password),
                timeout=10
            )
            if response.status_code == 200:
                user_data = response.json()
                return {"success": True, "message": f"Connected successfully as '{user_data.get('name', self.username)}'!"}
            else:
                return {"success": False, "message": f"Authentication failed ({response.status_code}): {response.text}"}
        except Exception as e:
            return {"success": False, "message": f"Could not connect to WordPress site: {str(e)}"}

    def publish_post(
        self,
        title: str,
        content_html: str,
        meta_description: str,
        focus_keyword: str,
        status: str = "draft",
        category_ids: list = None
    ) -> dict:
        """
        Publishes or creates a draft post in WordPress with Rank Math SEO meta data.
        """
        headers = {
            "Content-Type": "application/json"
        }

        # Rank Math SEO meta fields
        meta_data = {
            "rank_math_title": title,
            "rank_math_description": meta_description,
            "rank_math_focus_keyword": focus_keyword
        }

        payload = {
            "title": title,
            "content": content_html,
            "excerpt": meta_description,
            "status": status,  # "publish" or "draft"
            "meta": meta_data
        }

        if category_ids:
            payload["categories"] = category_ids

        try:
            response = requests.post(
                self.api_endpoint,
                json=payload,
                auth=HTTPBasicAuth(self.username, self.app_password),
                headers=headers,
                timeout=20
            )

            if response.status_code in [200, 201]:
                post_data = response.json()
                post_id = post_data.get("id")
                post_link = post_data.get("link")
                edit_link = f"{self.site_url}/wp-admin/post.php?post={post_id}&action=edit"
                
                return {
                    "success": True,
                    "post_id": post_id,
                    "post_link": post_link,
                    "edit_link": edit_link,
                    "status": post_data.get("status"),
                    "message": f"Post successfully created as '{post_data.get('status')}'!"
                }
            else:
                return {
                    "success": False,
                    "message": f"WordPress API Error ({response.status_code}): {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Network or Publishing Error: {str(e)}"
            }
