import sys
import logging

import pandas as pd
from neo4j import GraphDatabase


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout
)


class DBDriver:
    def __init__(self, url, user, password) -> None:
        self.__driver = GraphDatabase.driver(
            url,
            auth=(user, password)
        )
        try:
            self.__driver.verify_connectivity()
            logger.info('connected to neoj4 instance')
        except Exception as e:
            logger.error("cannot connect to neo4j instance")
            logger.error(e)

    def select_as_df(self, query: str) -> pd.DataFrame:
        res = pd.DataFrame()
        try:
            with self.__driver.session() as session:
                res = session.run(query).to_df()
                logger.info("query executed successfully")
                logger.info(f"got {res.shape[0]} items")
        except Exception as e:
            logger.error("Error executing the query")
            logger.error(e)
        finally:
            return res

    def execute(self, query: str) -> None:
        try:
            with self.__driver.session() as session:
                res = session.run(query).to_df()
                logger.info("query executed successfully")
                logger.info(f"got {res.shape[0]} items")
        except Exception as e:
            logger.error("Error executing the query")
            logger.error(e)


__all__ = ["DBDriver"]
