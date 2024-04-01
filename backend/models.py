from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, index=True)
    hashed_password = Column(String, index=True)

    khachkars = relationship("Khachkar", back_populates="owner")

class Khachkar(Base):
    __tablename__ = "khachkar"

    id = Column(Integer, primary_key=True)

    location = Column(String)
    latLong = Column(String)
    scenario = Column(String)
    setting = Column(String)
    landscape = Column(String)
    accessibility = Column(String)
    masters_name = Column(String)
    category = Column(String)
    production_period = Column(String)
    motive = Column(String)
    condition_of_preservation = Column(String)
    inscription = Column(String)
    important_features = Column(String)
    backside = Column(String)
    history_ownership = Column(String)
    commemorative_activities = Column(String)
    references = Column(String)
    date = Column(Date, primary_key=False)
    image = Column(String, primary_key=False)
    video = Column(String, primary_key=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="khachkars")