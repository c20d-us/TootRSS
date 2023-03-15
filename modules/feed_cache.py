"""
A wrapper class for the feed cache stored in DynamoDB
"""
import boto3


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

    def __init__(self, access_key_id: str, access_key: str, region: str, table_name: str, p_key_name: str, s_key_name: str) -> None:
        """
        The initializer
        """
        self._table = None
        self._p_key_name = p_key_name
        self._s_key_name = s_key_name
        try:
            ddb = boto3.resource(
                "dynamodb",
                aws_access_key_id=access_key_id,
                aws_secret_access_key=access_key,
                region_name=region,
            )
            self._table = ddb.Table(table_name)
        except Exception:
            raise Exception(
                f"Could not instantiate the FeedCache object."
            )

    def get_all(self) -> list[dict]:
        """
        Scan the entire DynamoDB cache and return all records.
        """
        items = None
        try:
            response = self._table.scan()
            items = response["Items"]
        except Exception as ex:
            raise Exception(f"get_all encountered exception {ex}")
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
        except Exception:
            raise Exception("Get_item encountered exception")
        return item

    def put_item(self, p_key: str, s_key: str, link: str, title: str, tooted: bool) -> bool:
        """
        Put a single item into the DynamoDC cache, overwriting if already present
        """
        put_success = False
        try:
            response = self._table.put_item(
                Item={
                    self._p_key_name: p_key,
                    self._s_key_name: s_key,
                    'link': link,
                    'title': title,
                    'tooted': tooted
                }
            )
        except:
            raise Exception("Problem!")
        return put_success