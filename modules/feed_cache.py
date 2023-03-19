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
        The AWS region of the DynamoDB, i.e., "us-west-2"
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
        region: str,
        table_name: str,
        p_key_name: str,
        s_key_name: str,
    ) -> None:
        """
        The initializer
        """
        global log
        log = Log()
        AttrDefs = [
            {"AttributeName": p_key_name, "AttributeType": "S"},
            {"AttributeName": s_key_name, "AttributeType": "S"},
        ]
        KeySchema = [
            {"AttributeName": p_key_name, "KeyType": "HASH"},
            {"AttributeName": s_key_name, "KeyType": "RANGE"},
        ]
        self._table = None
        self._p_key_name = p_key_name
        self._s_key_name = s_key_name
        try:
            session = boto3.session.Session(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=access_key,
                region_name=region,
            )
            ddb = session.resource("dynamodb")
            table_names = [table.name for table in ddb.tables.all()]
            if table_name in table_names:
                self._table = ddb.Table(table_name)
            else:
                log.inform(
                    f'The feed cache table "{table_name}" doesn\'t exist; attempting to create...'
                )
                ddb_table = ddb.create_table(
                    TableName=table_name,
                    BillingMode="PAY_PER_REQUEST",
                    KeySchema=KeySchema,
                    AttributeDefinitions=AttrDefs,
                )
                log.inform("Waiting on the table to be ready...")
                session.client("dynamodb").get_waiter("table_exists").wait(
                    TableName=table_name
                )
                self._table = ddb_table
        except:
            log.crit("Could not instantiate the FeedCache object.")
            raise Exception()

    def get_all(self) -> list[dict]:
        """
        Scan the entire DynamoDB cache and return all records.
        """
        items = None
        try:
            response = self._table.scan()
            items = response["Items"]
        except:
            log.crit("The get_all attempt encountered an exception")
            raise Exception()
        return items

    def get_item(self, p_key: str, s_key: str) -> dict:
        """
        Get a single item from the DynamoDC cache, if it exists
        """
        item = None
        try:
            response = self._table.get_item(
                Key={self._p_key_name: p_key, self._s_key_name: s_key}
            )
            item = response.get("Item")
        except:
            log.crit("The get_item attempt encountered an exception")
            raise Exception()
        return item

    def put_item(
        self, p_key: str, s_key: str, link: str, title: str, tooted: bool
    ) -> bool:
        """
        Put a single item into the DynamoDC cache, overwriting if already present
        """
        put_success = False
        try:
            response = self._table.put_item(
                Item={
                    self._p_key_name: p_key,
                    self._s_key_name: s_key,
                    "link": link,
                    "title": title,
                    "tooted": tooted,
                }
            )
        except:
            log.crit("The put_item attempt encountered an exception")
            raise Exception()
        return put_success
