"""CUSIP processing pipeline"""
import json
import re
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.schemas import (
    CUSIPAnalysisResult,
    MaturityData,
    FinancialAttributeData
)
from .gemini_client import GeminiClient


logger = logging.getLogger(__name__)


class CUSIPPipeline:
    """Pipeline for processing CUSIP queries and extracting financial attributes"""

    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize the pipeline

        Args:
            gemini_client: Configured GeminiClient instance
        """
        self.gemini_client = gemini_client
        logger.info("CUSIP Pipeline initialized")

    def process_cusip(
        self,
        cusip: str,
        attributes: Optional[List[str]] = None,
        trace_callback=None
    ) -> CUSIPAnalysisResult:
        """
        Process a CUSIP and extract financial attributes

        Args:
            cusip: CUSIP identifier
            attributes: List of attributes to retrieve
            trace_callback: Optional callback function for tracing

        Returns:
            CUSIPAnalysisResult with extracted data
        """
        def trace(message):
            logger.info(message)
            if trace_callback:
                trace_callback(message)

        try:
            trace(f"[Pipeline] Starting CUSIP processing: {cusip}")
            trace(f"[Pipeline] Attributes requested: {len(attributes) if attributes else 0}")

            gemini_response = self.gemini_client.query_cusip_attributes(
                cusip=cusip,
                attributes=attributes,
                trace_callback=trace
            )

            trace(f"[Parser] Parsing Gemini response...")
            result = self._parse_gemini_response(
                cusip=cusip,
                response_data=gemini_response,
                trace_callback=trace
            )

            trace(f"[Pipeline] ✓ Processing complete")
            trace(f"[Pipeline] Attributes extracted: {len(result.attributes) if result.attributes else 0}")
            return result

        except Exception as e:
            error_msg = f"Pipeline error: {str(e)}"
            trace(f"[Pipeline] ❌ Error: {error_msg}")
            logger.error(error_msg)
            return CUSIPAnalysisResult(
                cusip=cusip,
                error=error_msg
            )

    def _parse_gemini_response(
        self,
        cusip: str,
        response_data: Dict[str, Any],
        trace_callback=None
    ) -> CUSIPAnalysisResult:
        """
        Parse Gemini response and extract structured data

        Args:
            cusip: CUSIP identifier
            response_data: Response from Gemini client
            trace_callback: Optional callback for tracing

        Returns:
            CUSIPAnalysisResult
        """
        def trace(message):
            logger.info(message)
            if trace_callback:
                trace_callback(message)

        response_text = response_data.get("response_text", "")
        sources = response_data.get("sources", [])

        trace(f"[Parser] Extracting JSON from response...")
        try:
            parsed_data = self._extract_json_from_response(response_text)

            if parsed_data:
                trace(f"[Parser] ✓ JSON extracted successfully")
                trace(f"[Parser] Building structured result from JSON...")
                return self._build_result_from_json(
                    cusip=cusip,
                    parsed_data=parsed_data,
                    sources=sources,
                    raw_response=response_text,
                    trace_callback=trace
                )
            else:
                trace(f"[Parser] ⚠ No JSON found, using text extraction fallback")
                return self._build_result_from_text(
                    cusip=cusip,
                    response_text=response_text,
                    sources=sources,
                    trace_callback=trace
                )

        except Exception as e:
            trace(f"[Parser] ⚠ Error parsing response: {str(e)}")
            trace(f"[Parser] Using text extraction fallback")
            logger.warning(f"Error parsing response, using fallback: {str(e)}")
            return self._build_result_from_text(
                cusip=cusip,
                response_text=response_text,
                sources=sources,
                trace_callback=trace
            )

    def _extract_json_from_response(self, response_text: str) -> Optional[Dict]:
        """
        Extract JSON object from response text

        Args:
            response_text: Raw response text

        Returns:
            Parsed JSON dictionary or None
        """
        try:
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group(0)
                json_str = re.sub(r'```json\s*|\s*```', '', json_str)
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.debug(f"JSON parsing failed: {str(e)}")

        return None

    def _build_result_from_json(
        self,
        cusip: str,
        parsed_data: Dict,
        sources: List[str],
        raw_response: str,
        trace_callback=None
    ) -> CUSIPAnalysisResult:
        """
        Build result from parsed JSON data

        Args:
            cusip: CUSIP identifier
            parsed_data: Parsed JSON dictionary
            sources: List of source URLs
            raw_response: Raw response text

        Returns:
            CUSIPAnalysisResult
        """
        attributes = {}
        maturities = []
        wam_years = None
        total_principal = None

        attr_data = parsed_data.get("attributes", {})
        for attr_name, attr_info in attr_data.items():
            if isinstance(attr_info, dict):
                attributes[attr_name] = {
                    "value": attr_info.get("value"),
                    "source": attr_info.get("source"),
                    "confidence": attr_info.get("confidence")
                }
            else:
                attributes[attr_name] = {"value": attr_info}

        maturity_list = parsed_data.get("maturities", [])
        for mat in maturity_list:
            try:
                maturity = MaturityData(
                    cusip=cusip,
                    maturity_date=mat.get("date"),
                    years_to_maturity=self._safe_float(mat.get("years_to_maturity")),
                    principal_amount=self._safe_float(mat.get("principal_amount")),
                    source=mat.get("source")
                )
                maturities.append(maturity)
            except Exception as e:
                logger.warning(f"Error parsing maturity data: {str(e)}")

        wam_years = self._safe_float(parsed_data.get("calculated_wam_years"))
        if not wam_years and maturities:
            wam_years = self._calculate_wam(maturities)

        if wam_years:
            total_principal = sum(m.principal_amount for m in maturities if m.principal_amount)

        all_sources = list(set(sources + parsed_data.get("sources", [])))

        return CUSIPAnalysisResult(
            cusip=cusip,
            attributes=attributes,
            wam_years=wam_years,
            total_principal=total_principal,
            maturity_count=len(maturities),
            maturities=maturities,
            sources=all_sources,
            raw_llm_response=raw_response
        )

    def _build_result_from_text(
        self,
        cusip: str,
        response_text: str,
        sources: List[str],
        trace_callback=None
    ) -> CUSIPAnalysisResult:
        """
        Build result from unstructured text response

        Args:
            cusip: CUSIP identifier
            response_text: Raw response text
            sources: List of source URLs

        Returns:
            CUSIPAnalysisResult
        """
        attributes = self._extract_attributes_from_text(response_text)

        return CUSIPAnalysisResult(
            cusip=cusip,
            attributes=attributes,
            sources=sources,
            raw_llm_response=response_text,
            metadata={"parsing_method": "text_extraction"}
        )

    def _extract_attributes_from_text(self, text: str) -> Dict[str, Any]:
        """Extract attributes from unstructured text using regex patterns"""
        patterns = {
            "maturity_date": r"(?:maturity date|matures on)[\s:]+(\d{4}-\d{2}-\d{2}|\w+ \d{1,2},? \d{4})",
            "coupon_rate": r"(?:coupon rate|coupon)[\s:]+(\d+\.?\d*%)",
            "yield": r"(?:yield|ytm)[\s:]+(\d+\.?\d*%)",
            "credit_rating": r"(?:credit rating|rating)[\s:]+([A-Z][A-Za-z0-9+\-]+)",
            "issuer": r"(?:issuer|issued by)[\s:]+([A-Z][A-Za-z0-9\s,\.]+?)(?:\.|,|\n|$)",
            "par_value": r"(?:par value|face value)[\s:]+\$?([\d,]+\.?\d*)",
        }

        attributes = {}
        for name, pattern in patterns.items():
            if match := re.search(pattern, text, re.IGNORECASE):
                attributes[name] = {"value": match.group(1).strip()}
        return attributes

    def _calculate_wam(self, maturities: List[MaturityData]) -> Optional[float]:
        """
        Calculate Weighted Average Maturity

        Args:
            maturities: List of MaturityData objects

        Returns:
            WAM in years or None
        """
        try:
            total_weighted = 0
            total_principal = 0

            for maturity in maturities:
                if maturity.years_to_maturity and maturity.principal_amount:
                    total_weighted += maturity.years_to_maturity * maturity.principal_amount
                    total_principal += maturity.principal_amount

            if total_principal > 0:
                wam = total_weighted / total_principal
                logger.info(f"Calculated WAM: {wam:.2f} years")
                return wam

        except Exception as e:
            logger.error(f"Error calculating WAM: {str(e)}")

        return None

    def _safe_float(self, value: Any) -> Optional[float]:
        """
        Safely convert value to float

        Args:
            value: Value to convert

        Returns:
            Float value or None
        """
        if value is None:
            return None
        try:
            if isinstance(value, str):
                value = value.replace(',', '').replace('$', '').replace('%', '')
            return float(value)
        except (ValueError, TypeError):
            return None

    def get_wam_only(self, cusip: str) -> CUSIPAnalysisResult:
        """
        Get only WAM calculation for a CUSIP

        Args:
            cusip: CUSIP identifier

        Returns:
            CUSIPAnalysisResult focused on WAM
        """
        return self.process_cusip(
            cusip=cusip,
            attributes=["weighted average maturity (WAM)", "maturity dates", "principal amounts"]
        )
