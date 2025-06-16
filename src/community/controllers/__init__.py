from abc import abstractmethod

from sqlalchemy.orm import Session


class BaseController:
    def __init__(self, db_session: Session, model_class):
        self.db_session = db_session
        self.model_class = model_class

    @abstractmethod
    def create(self, data: dict):
        """Create a new instance of the model."""
        pass

    @abstractmethod
    def get_by_id(self, item_id: int):
        """Retrieve an instance of the model by its ID."""
        pass

    @abstractmethod
    def update(self, item_id: int, data: dict):
        """Update an existing instance of the model."""
        pass

    @abstractmethod
    def delete(self, item_id: int):
        """Delete an instance of the model."""
        pass
