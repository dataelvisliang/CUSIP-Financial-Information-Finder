"""Data schemas for CUSIP processing"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class FinancialAttribute(str, Enum):
    """Supported financial attributes"""
    WAM = "weighted_average_maturity"
    MATURITY = "maturity_date"
    COUPON_RATE = "coupon_rate"
    YIELD = "yield"
    CREDIT_RATING = "credit_rating"
    ISSUER = "issuer"
    ISSUE_DATE = "issue_date"
    PAR_VALUE = "par_value"
    SECURITY_TYPE = "security_type"


@dataclass
class FinancialAttributeData:
    """Generic financial attribute data"""
    attribute_name: str
    value: Any
    confidence: Optional[str] = None
    source: Optional[str] = None
    raw_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attribute": self.attribute_name,
            "value": self.value,
            "confidence": self.confidence,
            "source": self.source
        }


@dataclass
class MaturityData:
    """Individual maturity data point"""
    cusip: str
    maturity_date: Optional[str] = None
    years_to_maturity: Optional[float] = None
    principal_amount: Optional[float] = None
    source: Optional[str] = None

    def __post_init__(self):
        """Validate data"""
        if not self.cusip:
            raise ValueError("CUSIP is required")


@dataclass
class CUSIPData:
    """Complete CUSIP data with all financial attributes"""
    cusip: str
    attributes: Dict[str, FinancialAttributeData] = field(default_factory=dict)
    maturities: List[MaturityData] = field(default_factory=list)
    raw_response: Optional[str] = None
    sources: List[str] = field(default_factory=list)

    def add_attribute(self, attr: FinancialAttributeData):
        """Add a financial attribute"""
        self.attributes[attr.attribute_name] = attr

    def get_attribute(self, name: str) -> Optional[FinancialAttributeData]:
        """Get a specific attribute"""
        return self.attributes.get(name)


@dataclass
class CUSIPAnalysisResult:
    """Complete analysis result for a CUSIP"""
    cusip: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    wam_years: Optional[float] = None
    wam_months: Optional[float] = None
    total_principal: Optional[float] = None
    maturity_count: int = 0
    maturities: List[MaturityData] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    raw_llm_response: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.wam_months is None and self.wam_years is not None:
            self.wam_months = self.wam_years * 12

    @property
    def is_success(self) -> bool:
        """Check if the result is successful"""
        return len(self.attributes) > 0 and self.error is None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display"""
        result = {
            "cusip": self.cusip,
            "attributes": self.attributes,
            "sources": self.sources,
            "error": self.error
        }

        if self.wam_years is not None:
            result["wam_years"] = round(self.wam_years, 2)
            result["wam_months"] = round(self.wam_months, 2)
            result["total_principal"] = self.total_principal
            result["maturity_count"] = self.maturity_count

        return result


@dataclass
class WAMResult:
    """Weighted Average Maturity calculation result (backward compatibility)"""
    cusip: str
    wam_years: Optional[float] = None
    wam_months: Optional[float] = None
    total_principal: Optional[float] = None
    maturity_count: int = 0
    maturities: List[MaturityData] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    raw_llm_response: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.wam_months is None and self.wam_years is not None:
            self.wam_months = self.wam_years * 12

    @property
    def is_success(self) -> bool:
        """Check if the result is successful"""
        return self.wam_years is not None and self.error is None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display"""
        return {
            "cusip": self.cusip,
            "wam_years": round(self.wam_years, 2) if self.wam_years else None,
            "wam_months": round(self.wam_months, 2) if self.wam_months else None,
            "total_principal": self.total_principal,
            "maturity_count": self.maturity_count,
            "sources": self.sources,
            "error": self.error
        }
