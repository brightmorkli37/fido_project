import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    full_name = Column(String, index=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<User(user_id={self.user_id}, full_name='{self.full_name}', date_created={self.date_created})>"