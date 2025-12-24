import uuid
import os
import logging
from django.conf import settings
from supabase import create_client, Client

logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    """Initialize and return Supabase client"""
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    bucket = os.environ.get('SUPABASE_BUCKET')
    
    logger.info(f"Supabase config - URL: {url}, Bucket: {bucket}")
    
    if not url or not key:
        error_msg = "SUPABASE_URL and SUPABASE_KEY must be set in environment"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if not bucket:
        logger.warning("SUPABASE_BUCKET not set, using default 'ultramine'")
        bucket = 'ultramine'
    
    return create_client(url, key)


def upload_image_to_supabase(file, folder: str = "deposits") -> str:
    """
    Upload image file to Supabase Storage
    
    Args:
        file: Django UploadedFile object
        folder: Subfolder in bucket (default: "deposits")
    
    Returns:
        Public URL of uploaded image
    """
    try:
        if not file:
            raise ValueError("No file provided")
        
        logger.info(f"Starting image upload: {file.name}")
        
        supabase = get_supabase_client()
        bucket_name = os.environ.get('SUPABASE_BUCKET', 'ultramine')
        
        file_extension = file.name.split('.')[-1].lower()
        if not file_extension:
            raise ValueError(f"Invalid file name: {file.name}")
        
        file_name = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"{folder}/{file_name}"
        
        logger.info(f"File path: {file_path}, Content-Type: {file.content_type}")
        
        file.seek(0)
        file_content = file.read()
        file.seek(0)
        
        if not file_content:
            raise ValueError("File is empty")
        
        logger.info(f"Uploading {len(file_content)} bytes to {bucket_name}/{file_path}")
        
        response = supabase.storage.from_(bucket_name).upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": file.content_type or "image/jpeg"}
        )
        
        logger.info(f"Upload response: {response}")
        
        supabase_url = os.environ.get('SUPABASE_URL')
        public_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{file_path}"
        
        logger.info(f"Upload successful! URL: {public_url}")
        return public_url
        
    except Exception as e:
        logger.error(f"Failed to upload image to Supabase: {str(e)}", exc_info=True)
        raise Exception(f"Failed to upload image to Supabase: {str(e)}")


def delete_image_from_supabase(image_url: str) -> bool:
    """
    Delete image from Supabase Storage
    
    Args:
        image_url: Public URL of the image
    
    Returns:
        True if deleted, False otherwise
    """
    try:
        supabase = get_supabase_client()
        bucket_name = os.environ.get('SUPABASE_BUCKET', 'ultramine')
        
        file_path = image_url.split(f'/{bucket_name}/')[-1]
        
        supabase.storage.from_(bucket_name).remove([file_path])
        
        return True
    except Exception as e:
        logger.error(f"Failed to delete image from Supabase: {str(e)}", exc_info=True)
        return False
