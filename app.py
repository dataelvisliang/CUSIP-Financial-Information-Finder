"""Streamlit frontend for CUSIP WAM Pipeline"""
import streamlit as st
import logging
from typing import Optional

from src.services.gemini_client import GeminiClient
from src.services.pipeline import CUSIPPipeline
from src.utils.validators import validate_cusip, format_cusip


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_session_state():
    """Initialize session state variables"""
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'pipeline' not in st.session_state:
        st.session_state.pipeline = None
    if 'results_history' not in st.session_state:
        st.session_state.results_history = []
    if 'use_custom_search' not in st.session_state:
        st.session_state.use_custom_search = False
    if 'custom_search_engine_id' not in st.session_state:
        st.session_state.custom_search_engine_id = ""
    if 'custom_search_api_key' not in st.session_state:
        st.session_state.custom_search_api_key = ""


def create_pipeline(
    api_key: str,
    use_custom_search: bool = False,
    custom_search_engine_id: Optional[str] = None,
    custom_search_api_key: Optional[str] = None
) -> Optional[CUSIPPipeline]:
    """
    Create pipeline instance

    Args:
        api_key: Google AI Studio API key
        use_custom_search: Whether to use Custom Search API
        custom_search_engine_id: Custom Search Engine ID (cx parameter)
        custom_search_api_key: API key for Custom Search API

    Returns:
        CUSIPPipeline instance or None
    """
    try:
        gemini_client = GeminiClient(
            api_key=api_key,
            use_custom_search=use_custom_search,
            custom_search_engine_id=custom_search_engine_id,
            custom_search_api_key=custom_search_api_key
        )
        pipeline = CUSIPPipeline(gemini_client=gemini_client)
        return pipeline
    except Exception as e:
        st.error(f"Failed to initialize pipeline: {str(e)}")
        logger.error(f"Pipeline initialization error: {str(e)}")
        return None


def display_result(result):
    """Display analysis result"""
    if result.error:
        st.error(f"Error: {result.error}")
        return

    st.success(f"Successfully analyzed CUSIP: {result.cusip}")

    st.subheader("Extracted Information")
    if result.attributes:
        for attr_name, attr_data in result.attributes.items():
            value = attr_data.get('value', 'N/A') if isinstance(attr_data, dict) else attr_data
            st.markdown(f"**{attr_name.replace('_', ' ').title()}:** {value}")
            if isinstance(attr_data, dict):
                if conf := attr_data.get('confidence'):
                    st.caption(f"Confidence: {conf}")
                if src := attr_data.get('source'):
                    if src != 'N/A':
                        st.caption(f"Source: {src}")
        st.divider()
    else:
        st.info("No attributes extracted")

    if result.sources:
        st.subheader("Sources")
        with st.expander(f"View {len(result.sources)} source(s)"):
            for i, source in enumerate(result.sources, 1):
                st.markdown(f"{i}. [{source}]({source})")

    if result.raw_llm_response:
        with st.expander("View Raw LLM Response"):
            st.text(result.raw_llm_response)


def main():
    """Main application"""
    st.set_page_config(
        page_title="CUSIP Financial Analyzer",
        page_icon="📊",
        layout="wide"
    )

    init_session_state()

    st.title("📊 CUSIP Financial Information Finder")
    st.markdown("""
    Find any financial information about CUSIP securities using Google Gemini with Search Grounding.
    Searches the web including PDF documents, SEC filings, and prospectuses to extract the exact information you need.
    """)

    with st.sidebar:
        st.header("Configuration")

        api_key_input = st.text_input(
            "Google AI Studio API Key",
            type="password",
            value=st.session_state.api_key,
            help="Enter your Google AI Studio API key"
        )

        if api_key_input != st.session_state.api_key:
            st.session_state.api_key = api_key_input
            st.session_state.pipeline = None

        st.divider()

        st.subheader("Search Configuration")

        use_custom_search = st.checkbox(
            "Use Custom Search API",
            value=st.session_state.use_custom_search,
            help="Enable Custom Search API for more control over search results"
        )

        if use_custom_search != st.session_state.use_custom_search:
            st.session_state.use_custom_search = use_custom_search
            st.session_state.pipeline = None

        if st.session_state.use_custom_search:
            st.info("📌 Custom Search API mode: More control over search results")

            custom_search_engine_id = st.text_input(
                "Custom Search Engine ID (cx)",
                value=st.session_state.custom_search_engine_id,
                help="Enter your Custom Search Engine ID",
                placeholder="e.g., c59349299d4a041d3"
            )

            if custom_search_engine_id != st.session_state.custom_search_engine_id:
                st.session_state.custom_search_engine_id = custom_search_engine_id
                st.session_state.pipeline = None

            custom_search_api_key = st.text_input(
                "Custom Search API Key",
                type="password",
                value=st.session_state.custom_search_api_key,
                help="Enter your Custom Search API key"
            )

            if custom_search_api_key != st.session_state.custom_search_api_key:
                st.session_state.custom_search_api_key = custom_search_api_key
                st.session_state.pipeline = None
        else:
            st.info("🤖 Gemini Search Grounding mode: Automatic AI-processed results")

        if st.session_state.api_key:
            if st.session_state.pipeline is None:
                with st.spinner("Initializing pipeline..."):
                    st.session_state.pipeline = create_pipeline(
                        api_key=st.session_state.api_key,
                        use_custom_search=st.session_state.use_custom_search,
                        custom_search_engine_id=st.session_state.custom_search_engine_id if st.session_state.use_custom_search else None,
                        custom_search_api_key=st.session_state.custom_search_api_key if st.session_state.use_custom_search else None
                    )

            if st.session_state.pipeline:
                search_mode = "Custom Search API" if st.session_state.use_custom_search else "Gemini Search Grounding"
                st.success(f"✓ Pipeline ready ({search_mode})")
            else:
                st.error("Pipeline initialization failed")
        else:
            st.warning("Please enter your API key")

        st.divider()

        st.subheader("About")
        st.markdown("""
        This tool uses:
        - **Google Gemini 2.0** with Search Grounding
        - **Dual Search Modes**:
          - Gemini Search Grounding (Automatic AI-processed results)
          - Custom Search API (More control over search results)
        - **Web Search** for real-time data retrieval
        - **PDF Document Parsing** for prospectuses and filings
        - **Flexible attribute extraction** - request any information
        - **Source citations** for all extracted data
        - **Comprehensive tracing** - see every step of processing
        """)

        if st.session_state.results_history:
            st.divider()
            st.subheader("Query History")
            st.write(f"Total queries: {len(st.session_state.results_history)}")
            if st.button("Clear History"):
                st.session_state.results_history = []
                st.rerun()

    if not st.session_state.pipeline:
        st.info("👈 Please enter your Google AI Studio API key in the sidebar to get started")
        st.markdown("""
        ### How to get your API key:
        1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. Sign in with your Google account
        3. Click "Create API Key"
        4. Copy and paste it in the sidebar
        """)
        return

    st.header("Query CUSIP")

    cusip_input = st.text_input(
        "Enter CUSIP Number",
        placeholder="e.g., 912828Z29",
        help="9-character CUSIP identifier",
        max_chars=9
    )

    custom_attributes = st.text_area(
        "What information do you want to find? (one per line)",
        placeholder="maturity date\ncoupon rate\nyield\ncredit rating\nissuer name\npar value",
        help="Specify the attributes you want to retrieve for this CUSIP. You can request any financial information.",
        height=150
    )

    query_button = st.button("🔍 Analyze", type="primary", use_container_width=True)

    if query_button and cusip_input:
        cusip_formatted = format_cusip(cusip_input)
        is_valid, error_msg = validate_cusip(cusip_formatted)

        if not is_valid:
            st.error(f"Invalid CUSIP: {error_msg}")
            return

        st.divider()

        attributes_list = None
        if custom_attributes.strip():
            attributes_list = [attr.strip() for attr in custom_attributes.split('\n') if attr.strip()]

        if not attributes_list:
            st.warning("Please specify what information you want to find about this CUSIP.")
            return

        # Create trace container
        trace_container = st.expander("📋 Processing Trace", expanded=True)
        trace_placeholder = trace_container.empty()

        traces = []

        def add_trace(message):
            traces.append(f"⏱ {message}")
            trace_placeholder.code("\n".join(traces))

        try:
            search_mode = "Custom Search API" if st.session_state.use_custom_search else "Gemini Search Grounding"
            add_trace(f"═══════════════════════════════════════════════════════")
            add_trace(f"STEP 1: INITIALIZATION")
            add_trace(f"═══════════════════════════════════════════════════════")
            add_trace(f"  • CUSIP: {cusip_formatted}")
            add_trace(f"  • Search Mode: {search_mode}")
            add_trace(f"  • Requested Attributes: {', '.join(attributes_list)}")
            add_trace(f"")

            result = st.session_state.pipeline.process_cusip(
                cusip=cusip_formatted,
                attributes=attributes_list,
                trace_callback=add_trace
            )

            add_trace(f"")
            add_trace(f"═══════════════════════════════════════════════════════")
            add_trace(f"✅ ANALYSIS COMPLETE")
            add_trace(f"═══════════════════════════════════════════════════════")

            st.session_state.results_history.append({
                'cusip': cusip_formatted,
                'timestamp': st.session_state.get('timestamp', 'N/A'),
                'success': result.is_success
            })

            st.divider()
            display_result(result)

        except Exception as e:
            add_trace(f"")
            add_trace(f"❌ ERROR: {str(e)}")
            st.error(f"Error processing CUSIP: {str(e)}")
            logger.error(f"Processing error: {str(e)}", exc_info=True)

    if st.session_state.results_history:
        st.divider()
        st.subheader("Recent Queries")
        for i, query in enumerate(reversed(st.session_state.results_history[-5:]), 1):
            status = "✅" if query['success'] else "❌"
            st.caption(f"{status} {query['cusip']}")


if __name__ == "__main__":
    main()
