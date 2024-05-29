from enum import Enum as ENUM
from sqlalchemy import Column, Date, ForeignKey, Integer, String, Boolean, Enum, Float
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, index=True)
    hashed_password = Column(String, index=True)
    is_admin = Column(Boolean, index=True)

    khachkars = relationship("Khachkar", back_populates="owner")

class KhachkarState(ENUM):
    processing_video = "processing_video"
    not_meshed = "not_meshed"
    creating_mesh = "creating_mesh"
    meshed = "meshed"
    ready = "ready"

class AccessibilityLevel(str, ENUM):
    very_easy = "Very easy"
    easy = "Easy"
    normal = "Normal"
    hard = "Hard"
    very_hard = "Very hard"

class ConditionOfPreservation(str, ENUM):
    very_good = "Very good"
    good = "Good"
    normal = "Normal"
    bad = "Bad"
    very_bad = "Very bad"

class Landscape(str, ENUM):
    mountain = "Mountain"
    flat_land = "Flat land"
    other = "Other"

class Location(str, ENUM):
    unk = "Unknown"
    ejmiatsin = "Ejmiatsin/Vagharshapat, Armavir Province, Armenia"
    amaghu_valley = "Noravank/Amaghu Valley, Vayodz Dzor Province, Armenia"
    noratus = "Noratus historical village, Gegharkunik Province, Armenia"
    other = "Other"

class Khachkar(Base):
    __tablename__ = "khachkar"

    id = Column(Integer, primary_key=True)

    location = Column(Enum(Location))
    latitude = Column(Float)
    longitude = Column(Float)
    landscape = Column(Enum(Landscape))
    accessibility = Column(Enum(AccessibilityLevel))
    production_period = Column(String)
    condition_of_preservation = Column(Enum(ConditionOfPreservation))
    inscription = Column(String)
    important_features = Column(String)
    references = Column(String)
    date = Column(Date, primary_key=False)
    image = Column(String, primary_key=False)
    video = Column(String, primary_key=False)
    state = Column(Enum(KhachkarState), nullable=False, default=KhachkarState.processing_video)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="khachkars")
    mesh_transformations = relationship("MeshTransformations", back_populates="khachkar")

    def as_dict(self) -> dict:
        info_dict = {
            "id": self.id,
            "location": self.location,
            "latLong": f"{self.latitude}, {self.longitude}",
            "landscape": self.landscape,
            "accessibility": self.accessibility,
            "productionPeriod": self.production_period,
            "conditionOfPreservation": self.condition_of_preservation,
            "inscription": self.inscription,
            "importantFeatures": self.important_features,
            "references": self.references
        }
        for key in info_dict:
            if info_dict[key] is None:
                info_dict[key] = ""
        return info_dict
    
class MeshTransformations(Base):
    __tablename__ = "mesh_transformations"

    scale = Column(Float, default=1.0)
    rotation_x = Column(Float, default=0.0)
    rotation_y = Column(Float, default=0.0)
    rotation_z = Column(Float, default=0.0)
    offset_x = Column(Float, default=0.0)
    offset_y = Column(Float, default=0.0)
    offset_z = Column(Float, default=0.0)

    khachkar_id = Column(Integer, ForeignKey("khachkar.id"), primary_key=True)
    khachkar = relationship("Khachkar", back_populates="mesh_transformations")
    
    def as_dict(self) -> dict:
        return {
            "scale": self.scale,
            "rotationX": self.rotation_x,
            "rotationY": self.rotation_y,
            "rotationZ": self.rotation_z,
            "offsetX": self.offset_x,
            "offsetY": self.offset_y,
            "offsetZ": self.offset_z
        }