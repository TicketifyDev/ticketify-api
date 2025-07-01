from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Load environment variables from the .env file
load_dotenv()
mongo_uri = os.getenv('MONGO_URI')
mongo_db = os.getenv('MONGO_DB')

# Connect to MongoDB using Motor's AsyncIOMotorClient
client = AsyncIOMotorClient(mongo_uri)
db = client[mongo_db]

class MongoDB:
    def __init__(self, collection_name) :
        """
        Initialize MongoDB with a specific collection.
        """
        self.collection = db[collection_name]

    async def create(self, document : dict):
        """
        Method to insert a new document into the collection.
        """
        try :
            await self.collection.insert_one(document)
        except Exception as e:
            print(f"Error while inserting document : {e}")

    async def read(self, query : dict):
        """
        Method to retrieve a single document from the collection.

        Args:
            query : The query to filter the document.
        
        Returns:
            dict : The retrieved document or None if no document matches the query.
        """
        try :
            result = await self.collection.find_one(query)
            return result
        except Exception as e:
            print(f"Error while reading document : {e}")

    async def update(self, query : dict, update_data : dict):
        """
        Method to update a document in the collection.

        Args:
            query : The query to find the document.
            update_data : The data to update the document with.

        Returns:
            int: The number of documents modified.
        """
        try:
            result = await self.collection.update_one(query, {"$set": update_data})
            return result.modified_count
        except Exception as e:
            print(f"Error while updating document : {e}")
            return 0

    async def delete(self, query : dict):
        """
        Method to delete a  document from the collection

        Args:
            query : The query to find the document to delete.

        Returns:
            int: The number of documents deleted.
        """
        try :
            result = await self.collection.delete_one(query)
            return result.deleted_count
        except Exception as e:
            print(f"Error while deleting document : {e}")
            return 0
    
    async def read_all(self):
        """
        Method to retrieve all documents from the collection.

        Returns:
            List : A list of all documents.
        """
        try :
            cursor = self.collection.find({})
            results = []
            async for document in cursor:
                results.append(document)
            return results
        except Exception as e:
            print(f"Error while reading documents : {e}")

    async def is_collection_empty(self):
        """
        Method to check if the MongoDB collection is empty.

        Returns:
            bool: True if the collection is empty, False otherwise.
        """
        try:
            count = await self.collection.count_documents({})
            return count == 0
        except Exception as e:
            print(f"Error while checking if collection is empty: {e}")
            return False  # Return False in case of error to assume it's not empty
        
    async def count_documents(self, query: dict = {}) -> int:
        """
        Method to count the number of documents in the collection based on a query.

        Args:
            query (dict): The query to filter the documents. Defaults to empty {} if not provided.

        Returns:
            int: The number of documents that match the query.
        """
        try:
            count = await self.collection.count_documents(query)
            return count
        except Exception as e:
            print(f"Error while counting documents: {e}")
            return 0  # Return 0 if there's an error
        
    async def read_many(self, query: dict, projection: dict = None, skip: int = 0, limit: int = 10, sort_criteria: list = None):
        """
        Method to retrieve multiple documents with pagination support.

        Args:
            query (dict): The query to filter the documents.
            skip (int): The number of documents to skip for pagination.
            limit (int): The maximum number of documents to return.
            sort_criteria (list): A list of tuples specifying the fields and order for sorting. 
                              E.g., [("field_name", 1)] for ascending or [("field_name", -1)] for descending.

        Returns:
            List[dict]: A list of the retrieved documents.
        """
        try:
            cursor = self.collection.find(query, projection)

            # Apply sorting if sort_criteria is provided
            if sort_criteria:
                cursor = cursor.sort(sort_criteria)
            
            # Apply skip and limit for pagination
            cursor = cursor.skip(skip).limit(limit)
            
            results = []
            async for document in cursor:
                results.append(document)
            return results
        except Exception as e:
            print(f"Error while reading documents with pagination: {e}")
            return []
           
           
# Dependency Injection class
class MongoDBCollectionProvider:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    def __call__(self):
        # Returns the MongoDB collection for the given collection name
        return MongoDB(self.collection_name)
    
