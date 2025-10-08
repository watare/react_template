"""
SCL File model for tracking uploaded IEC 61850 files
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class SCLFile(Base):
    """SCL File uploaded and converted to RDF"""
    __tablename__ = "scl_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # bytes

    # File storage paths
    scl_path = Column(String(512), nullable=False)  # Original SCL file
    rdf_path = Column(String(512), nullable=True)   # Converted RDF file
    validated_scl_path = Column(String(512), nullable=True)  # Round-trip validated SCL

    # Conversion status
    status = Column(String(50), nullable=False, default="uploaded")  # uploaded, converting, converted, failed, validated
    error_message = Column(Text, nullable=True)

    # Validation
    is_validated = Column(Boolean, default=False)
    validation_passed = Column(Boolean, nullable=True)
    validation_message = Column(Text, nullable=True)

    # RDF statistics
    triple_count = Column(Integer, nullable=True)
    fuseki_dataset = Column(String(255), nullable=True)  # Fuseki dataset name

    # Metadata
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    converted_at = Column(DateTime, nullable=True)

    # Relationships
    uploader = relationship("User", back_populates="scl_files")

    def __repr__(self):
        return f"<SCLFile {self.filename} ({self.status})>"
