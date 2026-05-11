import os
import logging
from typing import Optional
from supabase import create_client, Client
from core.config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET

logger = logging.getLogger(__name__)

class CloudStorage:
    def __init__(self):
        self.enabled = False
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
                self.bucket = SUPABASE_BUCKET or "recon-artifacts"
                self.enabled = True
                logger.info("Cloud storage (Supabase) initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")

    async def upload_file(self, local_path: str, remote_path: str) -> Optional[str]:
        if not self.enabled:
            return None
        
        try:
            with open(local_path, 'rb') as f:
                self.client.storage.from_(self.bucket).upload(
                    path=remote_path,
                    file=f,
                    file_options={"upsert": "true"}
                )
            
            # Get public URL
            response = self.client.storage.from_(self.bucket).get_public_url(remote_path)
            return response
        except Exception as e:
            logger.error(f"Failed to upload file to cloud storage: {e}")
            return None

storage = CloudStorage()
