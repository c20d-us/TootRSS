"""
A wrapper class for the feed cache stored in DynamoDB
"""
import boto3.session
from modules.log import Log


class FeedCache:
    """
    A class to manage the RSS feed cache stored in AWS DynamoDB

    Parameters
    ----------
    access_key_id: str
        The AWS access key ID
    access_key: str
        The AWS secret access key
    region: str
        The AWS region of the DynamoDB
    table_name: str
        The name of the DynamoDB table to use
    p_key_name: str
        The name of the table's partition key
    s_key_name: str
        The name of the table's sort key
    """

    log = None

    def __init__(
        self,
        access_key_id: str,
        access_key: str,
        make_table: bool,
        region: str,
        table_name: str,
        p_key_name: str,
        s_key_name: str
    ) -> None:
        """
        The initializer
        """
        global log
        log = Log()
        self._table = None
        self._p_key_name = p_key_name
        self._s_key_name = s_key_name
        self._table_name = table_name
        try:
            session = boto3.session.Session(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=access_key,
                region_name=region
            )
            ddb = session.resource("dynamodb")
            if not table_name in [table.name for table in ddb.tables.all()]:
                if make_table:
                    self._make_table(ddb, session)
                else:
                    log.crit(f"The feed cache table \"{table_name}\" does not exist, and make_table is not True.")
                    raise Exception()
            else:
                self._table = ddb.Table(table_name)
        except:
            log.crit("Could not instantiate the FeedCache object.")
            raise Exception()

    def _make_table(self, ddb_resource: boto3.Session.resource, boto3_session: boto3.session.Session) -> None:
        try:
            log.inform(f"The feed cache table \"{self._table_name}\" doesn\'t exist; attempting to create...")
            ddb_table = ddb_resource.create_table(
                TableName=self._table_name,
                BillingMode="PAY_PER_REQUEST",
                KeySchema=[
                        {"AttributeName": self._p_key_name, "KeyType": "HASH"},
                        {"AttributeName": self._s_key_name, "KeyType": "RANGE"}
                ],
                AttributeDefinitions=[
                    {"AttributeName": self._p_key_name, "AttributeType": "S"},
                    {"AttributeName": self._s_key_name, "AttributeType": "S"}
                ],
            )
            log.inform("Waiting on the table to be ready...")
            boto3_session.client("dynamodb").get_waiter("table_exists").wait(TableName=self._table_name)
            self._table = ddb_table
        except:
            log.crit("Could not create the FeedCache table.")
            raise Exception()

    def get_item(self, p_key: str, s_key: str) -> dict:
        """
        Get a single item from the DynamoDC cache, if it exists
        """
        try:
            response = self._table.get_item(
                Key={self._p_key_name: p_key, self._s_key_name: s_key}
            )
            return response.get("Item")
        except Exception as ex:
            log.crit(f"The get_item attempt encountered an exception: \"{ex}\"")
            raise Exception()

    def put_item(self, p_key: str, s_key: str, link: str, title: str, tooted: bool) -> None:
        """
        Put a single item into the DynamoDC cache, overwriting if already present
        """
        try:
            _ = self._table.put_item(
                Item={
                    self._p_key_name: p_key,
                    self._s_key_name: s_key,
                    "link": link,
                    "title": title,
                    "tooted": tooted
                }
            )
        except Exception as ex:
            log.crit(f"The put_item attempt encountered an exception: \"{ex}\"")
            raise Exception()