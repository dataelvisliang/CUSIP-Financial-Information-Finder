"""Google Gemini client with search grounding capabilities"""
import json
import logging
import requests
from typing import List, Optional, Dict, Any
from google import genai
from google.genai import types


logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Google Gemini with search grounding"""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.0-flash",
        use_custom_search: bool = False,
        custom_search_engine_id: Optional[str] = None,
        custom_search_api_key: Optional[str] = None
    ):
        """
        Initialize Gemini client with search grounding

        Args:
            api_key: Google AI Studio API key
            model_name: Gemini model to use (default: gemini-2.0-flash)
            use_custom_search: Whether to use Custom Search API instead of Gemini Search Grounding
            custom_search_engine_id: Custom Search Engine ID (cx parameter)
            custom_search_api_key: API key for Custom Search API
        """
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.model_name = model_name
        self.use_custom_search = use_custom_search
        self.custom_search_engine_id = custom_search_engine_id
        self.custom_search_api_key = custom_search_api_key

        # Initialize the new GenAI client
        self.client = genai.Client(api_key=api_key)

        # Configure search grounding
        # Note: For Gemini 2.0+, GoogleSearch() doesn't support dynamic_retrieval_config
        # Both modes use the same GoogleSearch tool - the difference is in how we might
        # want to configure prompts or post-process results in the future
        logger.info(f"Using {'Custom Search API' if use_custom_search else 'Gemini Search Grounding'} for grounding")
        self.grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        # Generation configuration
        self.config = types.GenerateContentConfig(
            tools=[self.grounding_tool],
            temperature=0.1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="BLOCK_NONE"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="BLOCK_NONE"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="BLOCK_NONE"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_NONE"
                ),
            ]
        )

        search_mode = "Custom Search API" if use_custom_search else "Gemini Search Grounding"
        logger.info(f"Gemini client initialized with model: {model_name}, Search mode: {search_mode}")

    def _perform_custom_search(self, query: str, num_results: int = 10, trace_callback=None) -> List[Dict[str, Any]]:
        """Perform Google Custom Search API query"""
        def trace(msg):
            logger.info(msg)
            if trace_callback:
                trace_callback(msg)

        if not self.custom_search_engine_id or not self.custom_search_api_key:
            trace("  • Missing credentials, cannot perform custom search")
            return []

        trace(f"  • Query: '{query}'")
        trace(f"  • Search Engine ID: {self.custom_search_engine_id[:10]}...")
        trace("")

        try:
            response = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": self.custom_search_api_key,
                    "cx": self.custom_search_engine_id,
                    "q": query,
                    "num": min(num_results, 10)
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            search_info = data.get("searchInformation", {})
            trace(f"  • Search completed: {search_info.get('totalResults', '0')} results in {search_info.get('searchTime', 0):.2f}s")
            trace("")

            items = data.get("items", [])
            trace(f"  • Retrieved {len(items)} search result(s):")

            results = []
            for i, item in enumerate(items, 1):
                result = {k: item.get(k, "") for k in ["title", "link", "snippet", "displayLink"]}
                results.append(result)
                trace(f"    {i}. {result['title']}")
                trace(f"       URL: {result['link']}")

            return results

        except Exception as e:
            trace(f"  • Error: {str(e)}")
            logger.error(f"Custom search error: {str(e)}")
            return []

    def query_cusip_attributes(
        self,
        cusip: str,
        attributes: Optional[List[str]] = None,
        trace_callback=None
    ) -> Dict[str, Any]:
        """
        Query financial attributes for a CUSIP using search grounding

        Args:
            cusip: CUSIP identifier
            attributes: List of attributes to retrieve (if None, retrieves common attributes)
            trace_callback: Optional callback for tracing

        Returns:
            Dictionary containing the response text, sources, and metadata
        """
        def trace(message):
            logger.info(message)
            if trace_callback:
                trace_callback(message)

        if not cusip or len(cusip.strip()) == 0:
            raise ValueError("Valid CUSIP is required")

        cusip = cusip.strip().upper()

        if attributes is None or len(attributes) == 0:
            attributes = [
                "maturity date",
                "weighted average maturity (WAM)",
                "coupon rate",
                "yield",
                "credit rating",
                "issuer name",
                "security type",
                "par value"
            ]

        # Perform custom search if enabled
        custom_search_results = []
        custom_search_sources = []
        if self.use_custom_search:
            trace(f"═══════════════════════════════════════════════════════")
            trace(f"STEP 2: CUSTOM SEARCH API")
            trace(f"═══════════════════════════════════════════════════════")
            search_query = f"CUSIP {cusip} {' '.join(attributes)}"
            custom_search_results = self._perform_custom_search(
                query=search_query,
                num_results=10,
                trace_callback=trace
            )
            custom_search_sources = [r["link"] for r in custom_search_results]
            trace(f"  • Will incorporate {len(custom_search_results)} search results into prompt")
            trace(f"")
        else:
            trace(f"═══════════════════════════════════════════════════════")
            trace(f"STEP 2: SEARCH PREPARATION")
            trace(f"═══════════════════════════════════════════════════════")
            trace(f"  • Using Gemini Search Grounding (AI-driven)")
            trace(f"  • Gemini will perform web search automatically")
            trace(f"")

        trace(f"═══════════════════════════════════════════════════════")
        trace(f"STEP 3: PROMPT CONSTRUCTION")
        trace(f"═══════════════════════════════════════════════════════")
        prompt = self._build_cusip_query_prompt(cusip, attributes, custom_search_results)
        trace(f"  • Prompt length: {len(prompt)} characters")
        trace(f"  • Requested attributes: {', '.join(attributes)}")
        trace(f"")
        trace(f"--- PROMPT START ---")
        trace(prompt)
        trace(f"--- PROMPT END ---")
        trace(f"")

        try:
            trace(f"═══════════════════════════════════════════════════════")
            trace(f"STEP 4: GEMINI AI PROCESSING")
            trace(f"═══════════════════════════════════════════════════════")
            trace(f"  • Model: {self.model_name}")
            trace(f"  • Temperature: {self.config.temperature}, Top-P: {self.config.top_p}, Top-K: {self.config.top_k}")
            if self.use_custom_search:
                trace(f"  • Mode: Custom Search (results pre-fetched and included in prompt)")
            else:
                trace(f"  • Mode: Gemini Search Grounding (AI performs search)")
            trace(f"  • Sending request to Gemini API...")
            logger.info(f"Querying Gemini for CUSIP: {cusip}")

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.config
            )

            trace(f"  • ✓ Response received successfully")
            trace(f"  • Response length: {len(response.text)} characters")
            trace(f"")

            trace(f"═══════════════════════════════════════════════════════")
            trace(f"STEP 5: SOURCE EXTRACTION")
            trace(f"═══════════════════════════════════════════════════════")

            sources = self._extract_sources(response)
            trace(f"  • Gemini grounding sources: {len(sources)}")

            if sources:
                for i, source in enumerate(sources[:5], 1):
                    trace(f"    {i}. {source}")
                if len(sources) > 5:
                    trace(f"    ... and {len(sources) - 5} more")

            # Merge custom search sources with Gemini grounding sources
            all_sources = list(set(sources + custom_search_sources))

            if custom_search_sources:
                trace(f"  • Custom search sources: {len(custom_search_sources)}")
                trace(f"  • Total unique sources: {len(all_sources)}")

            result = {
                "cusip": cusip,
                "response_text": response.text,
                "sources": all_sources,
                "raw_response": response,
                "prompt_used": prompt
            }

            logger.info(f"Successfully retrieved data for CUSIP: {cusip}")
            return result

        except Exception as e:
            trace(f"[API] ❌ Error: {str(e)}")
            logger.error(f"Error querying Gemini for CUSIP {cusip}: {str(e)}")
            raise

    def _build_cusip_query_prompt(
        self,
        cusip: str,
        attributes: List[str],
        custom_search_results: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Build the prompt for querying CUSIP attributes

        Args:
            cusip: CUSIP identifier
            attributes: List of attributes to retrieve
            custom_search_results: Optional list of custom search results to include

        Returns:
            Formatted prompt string
        """
        # Build dynamic JSON structure based on requested attributes
        attributes_json_fields = []
        for attr in attributes:
            attr_key = attr.lower().replace(' ', '_')
            attributes_json_fields.append(f'    "{attr_key}": {{"value": "...", "source": "...", "confidence": "high/medium/low"}}')

        json_structure = "{\n" + ",\n".join(attributes_json_fields) + "\n  }"

        attributes_str = ", ".join(attributes)

        # Build custom search context if available
        search_context = ""
        if custom_search_results:
            search_context = "\n\n## Search Results Provided:\n\nHere are relevant search results to help you extract the information:\n\n"
            for i, result in enumerate(custom_search_results, 1):
                search_context += f"{i}. **{result['title']}**\n"
                search_context += f"   URL: {result['link']}\n"
                search_context += f"   Snippet: {result['snippet']}\n\n"
            search_context += "Use these search results to extract the requested information. Cite the specific URLs in your response.\n"

        if custom_search_results:
            prompt = f"""You are a financial data expert. Extract comprehensive information about the following CUSIP security from the search results provided below.

CUSIP: {cusip}

Please extract the following information for this CUSIP:
{attributes_str}
{search_context}
Instructions:
1. Analyze the search results provided above
2. Extract each requested attribute with its specific value from the search results
3. For maturity-related attributes:
   - If multiple maturities exist, extract ALL of them
   - Include maturity dates and corresponding principal amounts
   - Calculate WAM if requested: WAM = Σ(Maturity_i × Principal_i) / Σ(Principal_i)
4. Provide specific values with units (e.g., "5.25%", "$1,000,000", "2030-12-15")
5. Cite the exact source URL from the search results for each piece of information

Format your response as a JSON object with the requested attributes:
{{
  "cusip": "{cusip}",
  "attributes": {json_structure},
  "sources": ["list of all source URLs used"]
}}

Important:
- Only include the attributes that were requested
- If you cannot find information for an attribute in the search results, set value to "Not Available" and explain why in the source field
- Always cite specific URLs from the search results provided"""
        else:
            prompt = f"""You are a financial data expert. Search the web for comprehensive information about the following CUSIP security.

CUSIP: {cusip}

Please search for and extract the following information for this CUSIP:
{attributes_str}

Instructions:
1. Search reliable financial data sources (FINRA, SEC, Bloomberg, Reuters, bond marketplaces, etc.)
2. Look for PDF documents, official filings, prospectuses, and fact sheets that may contain this information
3. Extract each requested attribute with its specific value
4. For maturity-related attributes:
   - If multiple maturities exist, extract ALL of them
   - Include maturity dates and corresponding principal amounts
   - Calculate WAM if requested: WAM = Σ(Maturity_i × Principal_i) / Σ(Principal_i)
5. Provide specific values with units (e.g., "5.25%", "$1,000,000", "2030-12-15")
6. Cite the exact source URL or document name for each piece of information

Format your response as a JSON object with the requested attributes:
{{
  "cusip": "{cusip}",
  "attributes": {json_structure},
  "sources": ["list of all source URLs and documents"]
}}

Important:
- Only include the attributes that were requested
- If you cannot find information for an attribute, set value to "Not Available" and explain why in the source field
- If you find information in PDF documents, include the PDF URL in sources"""

        return prompt

    def _extract_sources(self, response) -> List[str]:
        """Extract grounding sources from Gemini response"""
        sources = []
        try:
            if hasattr(response, 'candidates') and response.candidates:
                metadata = response.candidates[0].grounding_metadata
                if metadata and hasattr(metadata, 'grounding_chunks'):
                    sources = [
                        chunk.web.uri for chunk in metadata.grounding_chunks
                        if hasattr(chunk, 'web') and hasattr(chunk.web, 'uri')
                    ]
            return list(set(sources))
        except Exception as e:
            logger.warning(f"Error extracting sources: {str(e)}")
            return []

    def query_with_custom_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Query Gemini with a custom prompt

        Args:
            prompt: Custom prompt text

        Returns:
            Dictionary containing response and sources
        """
        try:
            logger.info("Querying Gemini with custom prompt")

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.config
            )

            result = {
                "response_text": response.text,
                "sources": self._extract_sources(response),
                "raw_response": response
            }

            return result

        except Exception as e:
            logger.error(f"Error querying Gemini: {str(e)}")
            raise
