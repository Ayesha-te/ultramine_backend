import os
from django.core.files.storage import Storage
from django.conf import settings
from io import BytesIO


class SupabaseStorage(Storage):
    """Custom storage backend for Supabase"""

    def __init__(self):
        try:
            from supabase import create_client
        except ImportError:
            raise ImportError("supabase-py is not installed. Install it with: pip install supabase")

        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_KEY
        self.bucket_name = settings.SUPABASE_BUCKET
        self.client = create_client(self.supabase_url, self.supabase_key)

    def _open(self, name, mode='rb'):
        try:
            response = self.client.storage.from_(self.bucket_name).download(name)
            return BytesIO(response)
        except Exception as e:
            raise FileNotFoundError(f"File {name} not found in Supabase: {str(e)}")

    def _save(self, name, content):
        try:
            file_data = content.read() if hasattr(content, 'read') else content
            self.client.storage.from_(self.bucket_name).upload(
                path=name,
                file=file_data,
                file_options={"content-type": self._get_content_type(name)}
            )
            return name
        except Exception as e:
            raise IOError(f"Failed to save file {name} to Supabase: {str(e)}")

    def delete(self, name):
        try:
            self.client.storage.from_(self.bucket_name).remove([name])
        except Exception as e:
            raise IOError(f"Failed to delete file {name} from Supabase: {str(e)}")

    def exists(self, name):
        try:
            self.client.storage.from_(self.bucket_name).list(path=name)
            return True
        except:
            return False

    def listdir(self, path):
        try:
            files = self.client.storage.from_(self.bucket_name).list(path=path)
            dirs = []
            file_list = []
            for file in files:
                if file.get('metadata') and file['metadata'].get('mimetype') == 'application/octet-stream':
                    dirs.append(file['name'])
                else:
                    file_list.append(file['name'])
            return dirs, file_list
        except Exception:
            return [], []

    def size(self, name):
        try:
            file_obj = self.client.storage.from_(self.bucket_name).get_metadata(name)
            return file_obj.get('size', 0)
        except Exception:
            return 0

    def url(self, name):
        try:
            url = self.client.storage.from_(self.bucket_name).get_public_url(name)
            return url
        except Exception:
            return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{name}"

    def get_accessed_time(self, name):
        return None

    def get_created_time(self, name):
        return None

    def get_modified_time(self, name):
        return None

    @staticmethod
    def _get_content_type(filename):
        import mimetypes
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or 'application/octet-stream'
