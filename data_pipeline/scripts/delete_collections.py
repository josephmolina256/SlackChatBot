import weaviate

from ..constants import WEAVIATE_COLLECTION_NAME


try:
    client = weaviate.connect_to_local()
    assert client.is_live()

    client.collections.delete(WEAVIATE_COLLECTION_NAME)
    

    client.close()

except Exception as e:
    print(e)
    client.close()
