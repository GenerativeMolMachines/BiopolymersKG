import os
import sys
import shutil
import logging

import dotenv
from yadisk import YaDisk

dotenv.load_dotenv()

LOCAL_BACKUPS_LOCATION = os.environ["LOCAL_BACKUPS_LOCATION"]
REMOTE_BACKUPS_LOCATION = "/backups"

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Backuper:
    def __init__(self) -> None:
        self.client = self.connect_yadisk()

    @staticmethod
    def connect_yadisk() -> YaDisk:
        yadisk_client = YaDisk(token=os.environ["YADISK_TOKEN"])
        yadisk_client.check_token()

        return yadisk_client

    def check_existing_backups(self) -> list[str | None]:
        if not self.client.exists(REMOTE_BACKUPS_LOCATION):
            self.client.mkdir(REMOTE_BACKUPS_LOCATION)
            return []
        files = [i.name for i in self.client.listdir(REMOTE_BACKUPS_LOCATION)]
        return files
    
    def create_backup(self) -> None:
        command = """
        docker exec neo4j-neo4j-1 backup.sh && docker cp neo4j-neoj4-1:/var/lib/neo4j/backups/* ./backups
        """
        status = os.system(command)
        if not status:
            raise Exception("Error creating backup")

    def upload_backups(self) -> None:
        if not os.path.exists(LOCAL_BACKUPS_LOCATION):
            raise Exception(f"Local backups directory {LOCAL_BACKUPS_LOCATION} does not exist.")

        existing_backups = self.check_existing_backups()
        not_loaded_backups = [i for i in os.listdir(LOCAL_BACKUPS_LOCATION) if i not in existing_backups]

        for f in not_loaded_backups:
            self.client.upload(
                os.path.join(LOCAL_BACKUPS_LOCATION, f),
                os.path.join(REMOTE_BACKUPS_LOCATION, f),
                overwrite=True,
                timeout=100
            )

if __name__ == "__main__":
    backuper = Backuper()
    backuper.upload_backups()
