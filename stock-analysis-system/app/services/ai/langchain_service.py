"""
LangChain Agent Service
Using LangGraph's create_react_agent for intelligent routing (officially recommended new architecture for LangChain 1.0+)
"""
from typing import Dict, Any, AsyncIterator, Optional, List
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
import logging
import os
from functools import partial
from app.config import settings

from app.services.ai.agents.analysis_tools import (
    analyze_portfolio_risk,
    analyze_market_sentiment,
    analyze_stock_performance,
    analyze_alert_status,
    analyze_portfolio_performance,
    analyze_market_trend,
    analyze_stock_news,
    collect_stock_data,
    analyze_stock_risk,
    PortfolioRiskInput,
    MarketSentimentInput,
    StockPerformanceInput,
    AlertStatusInput,
    PortfolioPerformanceInput,
    MarketTrendInput,
    StockNewsInput,
    CollectStockDataInput,
    StockRiskInput
)

from app.services.ai.agents.portfolio_management_agent import (
    view_portfolio,
    list_tracked_stocks,
    ViewPortfolioInput,
    ListTrackedStocksInput,
    add_holding,
    update_holding,
    delete_holding,
    track_stock,
    untrack_stock,
    AddHoldingInput,
    UpdateHoldingInput,
    DeleteHoldingInput,
    TrackStockInput,
    UntrackStockInput,
    reduce_holding,
    ReduceHoldingInput
)

logger = logging.getLogger(__name__)


# Global model configuration (Admin can modify)
_current_model = "gpt-4o-mini"  # Default model

def get_current_model() -> str:
    """Get current global AI model"""
    global _current_model
    return _current_model

def set_current_model(model: str) -> bool:
    """Set current global AI model (Admin only)"""
    global _current_model
    valid_models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "gpt-4-turbo", "gpt-4"]
    if model in valid_models:
        _current_model = model
        logger.info(f"Global AI model changed to: {model}")
        return True
    return False


class LangChainChatService:
    """LangChain Chat Service - using official LangGraph"""
    
    def __init__(self):
        """Initialize LangChain Agent"""
        
        # Get OpenAI API Key from settings (automatically loaded from .env)
        self.api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ OPENAI_API_KEY not set in .env file. AI chat will not work without a valid API key.")
            self.api_key = "dummy_key"  # Use dummy key to avoid initialization errors
        
        # Initialize LLM with global model configuration
        try:
            current_model = get_current_model()
            self.llm = ChatOpenAI(
                model=current_model,  # Use global model configuration
                temperature=0.7,
                streaming=True,
                api_key=self.api_key
            )
            logger.info(f"Initialized ChatOpenAI with model: {current_model}")
        except Exception as e:
            logger.error(f"Failed to initialize ChatOpenAI: {str(e)}")
            # Still create a basic object to avoid complete crash
            self.llm = None
        
        # System prompt
        self.system_message = """You are a professional stock market analysis assistant named "AI Analyst".

Your role is to help investors understand their portfolio risks, market trends, and investment performance through data-driven analysis.

Key responsibilities:
1. Analyze portfolio risks and provide actionable insights
2. Monitor market sentiment and alert users to important changes  
3. Evaluate stock performance using technical indicators
4. Track alert status and warn of upcoming triggers
5. Calculate portfolio returns and identify top/worst performers
6. Identify market trends and sector rotations

Communication style:
- Be friendly, professional, and conversational
- Use emojis sparingly to highlight key points (📊 📈 📉 ⚠️ ✅)
- Explain complex financial concepts in simple terms
- Always provide specific data and numbers to support your analysis
- When tools return errors or no data, explain clearly and suggest alternatives
- Format responses with clear sections and bullet points

Important notes:
- Portfolio management actions (add/update/delete holdings, track/untrack) are ALLOWED via tools and REQUIRE a two-step confirmation (draft → confirm). You MUST follow the confirmation workflow below.
- You cannot execute real trades; operations only modify the internal tracking portfolio.
- Always cite the specific data sources when presenting numbers
- **USER IDENTITY**: The user is already authenticated. You DON'T need to ask for user ID or login info.
  All tools automatically access the logged-in user's data. Just call the tools directly.

**DATA COLLECTION**:
- If you find that data is missing or insufficient (e.g., no news, no price data), you can PROACTIVELY use the `collect_stock_data` tool to fetch fresh data
- The data collection is limited to the last 3 days (max 7 days) to keep it fast and relevant
- After collecting data, you can immediately use other analysis tools to provide insights
- Example workflow: User asks about MSFT sentiment → No news found → Call collect_stock_data(MSFT) → Then call analyze_stock_news(MSFT)

CONFIRMATION WORKFLOW FOR WRITE OPERATIONS:
- Some portfolio tools return a DRAFT first with fields {status:"draft", token, diff_summary}.
- When the user replies with messages like "confirm <token>" or "cancel <token>", you MUST call the same tool again with confirm=true and token=<token> (or discard for cancel).
- Always echo a concise summary of the executed change after confirmation.

OUTPUT FORMAT FOR TOOL RESULTS:
- When a tool returns an object containing a field named "status" or "token", you MUST render the raw JSON payload inside a fenced code block using the json language tag, e.g.:
```
```json
{ "status": "draft", "token": "abc123", "diff_summary": "..." }
```
```
- Place any natural language explanation BEFORE or AFTER the code block, but DO NOT modify keys/values inside the JSON.

Remember: Be helpful, accurate, and insightful! Don't hesitate to collect fresh data when needed."""
        
        # Session history storage (session_id -> List[BaseMessage])
        self.sessions: Dict[str, List[BaseMessage]] = {}
        
        logger.info("✅ LangChain Chat Service initialized (using LangGraph)")
    
    def _create_tools(self, user_id: int):
        """Create tool list (bind user ID)"""
        
        # Use partial to pre-fill user_id
        tools = [
            StructuredTool.from_function(
                func=partial(analyze_portfolio_risk, user_id=user_id),
                name="analyze_portfolio_risk",
                description="Analyze user portfolio risk including concentration, volatility, sector diversification, etc. Use when users ask questions like 'How risky is my investment?' or 'What's my portfolio risk?'.",
                args_schema=PortfolioRiskInput
            ),
            StructuredTool.from_function(
                func=partial(analyze_market_sentiment, user_id=user_id),
                name="analyze_market_sentiment",
                description="Analyze market, portfolio, or specific stock sentiment. Use for: 'analyze this client's portfolio sentiment' (scope=portfolio) or 'what's sentiment for NVDA' (scope=stock, symbol=NVDA).",
                args_schema=MarketSentimentInput
            ),
            StructuredTool.from_function(
                func=partial(analyze_stock_performance, user_id=user_id),
                name="analyze_stock_performance",
                description="Analyze individual stock performance and technical indicators including price trends, volatility, and volume. Use when users ask 'How's AAPL performing?' or 'Analyze TSLA'.",
                args_schema=StockPerformanceInput
            ),
            StructuredTool.from_function(
                func=partial(analyze_alert_status, user_id=user_id),
                name="analyze_alert_status",
                description="Analyze current alert status and trigger risks, showing alerts that are close to triggering. Use when users ask 'What's my alert status?' or 'Which alerts may trigger soon?'.",
                args_schema=AlertStatusInput
            ),
            StructuredTool.from_function(
                func=partial(analyze_portfolio_performance, user_id=user_id),
                name="analyze_portfolio_performance",
                description="Analyze portfolio return performance including total returns, stock rankings, and P/L. Use when users ask 'How are my returns?' or 'Which stock gained the most?'.",
                args_schema=PortfolioPerformanceInput
            ),
            StructuredTool.from_function(
                func=partial(analyze_market_trend, user_id=user_id),
                name="analyze_market_trend",
                description="Analyze market trends and hotspots based on user-tracked stocks. Use when users ask about 'market trends' or 'hot sectors'.",
                args_schema=MarketTrendInput
            ),
            StructuredTool.from_function(
                func=partial(analyze_stock_news, user_id=user_id),
                name="analyze_stock_news",
                description="Retrieve and analyze recent stock news including headlines, sources, and sentiment scores. Use for queries like 'News about XX stock' or 'Recent sentiment'.",
                args_schema=StockNewsInput
            ),
            StructuredTool.from_function(
                func=partial(collect_stock_data, user_id=user_id),
                name="collect_stock_data",
                description="Proactively collect latest stock data (price, news, etc.). Use when DB has no data or it's outdated. Limited to last 3 days (max 7). Calls real APIs.",
                args_schema=CollectStockDataInput
            ),
            StructuredTool.from_function(
                func=partial(analyze_stock_risk, user_id=user_id),
                name="analyze_stock_risk",
                description="Analyze an individual stock's risk (volatility, max drawdown, Beta, risk level). Note: for single stock, not portfolio.",
                args_schema=StockRiskInput
            ),
            # Portfolio Management (P0 - read-only)
            StructuredTool.from_function(
                func=partial(view_portfolio, user_id=user_id),
                name="view_portfolio",
                description="View the user's or selected client's portfolio holdings with optional summary. Use for: 'show my/client portfolio'.",
                args_schema=ViewPortfolioInput
            ),
            StructuredTool.from_function(
                func=partial(list_tracked_stocks, user_id=user_id),
                name="list_tracked_stocks",
                description="List tracked stocks for the user/client, including baseline price if available. Use for: 'what stocks am I tracking?'.",
                args_schema=ListTrackedStocksInput
            ),
            # Write operations with two-step confirmation
            StructuredTool.from_function(
                func=partial(add_holding, user_id=user_id),
                name="add_holding",
                description="Create a new portfolio holding. This tool uses a two-step confirmation: first returns a draft and token, then execute with confirm=true and token.",
                args_schema=AddHoldingInput
            ),
            StructuredTool.from_function(
                func=partial(update_holding, user_id=user_id),
                name="update_holding",
                description="Update an existing holding (quantity/price/notes). Two-step confirmation required.",
                args_schema=UpdateHoldingInput
            ),
            StructuredTool.from_function(
                func=partial(delete_holding, user_id=user_id),
                name="delete_holding",
                description="Delete a holding by id. Two-step confirmation required.",
                args_schema=DeleteHoldingInput
            ),
            StructuredTool.from_function(
                func=partial(track_stock, user_id=user_id),
                name="track_stock",
                description="Start tracking a stock for the user/client with optional baseline price. Two-step confirmation required.",
                args_schema=TrackStockInput
            ),
            StructuredTool.from_function(
                func=partial(untrack_stock, user_id=user_id),
                name="untrack_stock",
                description="Stop tracking a stock. Two-step confirmation required.",
                args_schema=UntrackStockInput
            ),
            StructuredTool.from_function(
                func=partial(reduce_holding, user_id=user_id),
                name="reduce_holding",
                description="Reduce an existing holding by quantity (keeps average cost unchanged). Two-step confirmation required.",
                args_schema=ReduceHoldingInput
            )
        ]
        
        return tools
    
    def get_session_history(self, session_id: str) -> List[BaseMessage]:
        """Get session history"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            logger.info(f"Created new chat session: {session_id}")
        return self.sessions[session_id]
    
    async def chat(
        self,
        user_input: str,
        session_id: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Handle user input (non-streaming)
        
        Args:
            user_input: User input message
            session_id: Session ID
            user_id: User ID
        
        Returns:
            Dict containing AI response
        """
        try:
            # Create user-bound tools
            tools = self._create_tools(user_id)
            
            # Use official create_react_agent (LangGraph)
            agent_executor = create_react_agent(
                model=self.llm,
                tools=tools
            )
            
            # Get session history
            history = self.get_session_history(session_id)
            
            # Build input (include system message and history)
            messages = [SystemMessage(content=self.system_message)]
            messages.extend(history)
            messages.append(HumanMessage(content=user_input))
            
            # Execute
            result = await agent_executor.ainvoke({"messages": messages})
            
            # Extract response
            response_messages = result.get("messages", [])
            ai_response = ""
            for msg in response_messages:
                if isinstance(msg, AIMessage) and msg.content:
                    ai_response = msg.content
            
            # Update session history
            history.append(HumanMessage(content=user_input))
            history.append(AIMessage(content=ai_response))
            
            logger.info(f"Chat completed for session {session_id}")
            
            return {
                "status": "success",
                "response": ai_response,
                "intermediate_steps": []
            }
            
        except Exception as e:
            logger.error(f"Chat error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "response": f"Sorry, an error occurred while processing your request: {str(e)}",
                "error": str(e)
            }
    
    async def chat_stream(
        self,
        user_input: str,
        session_id: str,
        user_id: int
    ) -> AsyncIterator[str]:
        """
        Handle user input (streaming response)
        
        Args:
            user_input: User input message
            session_id: Session ID
            user_id: User ID
        
        Yields:
            Text chunks of response content
        """
        # Check if LLM initialized
        if self.llm is None:
            yield "❌ AI service not properly initialized. Please check if OPENAI_API_KEY is set."
            return
        
        if self.api_key == "dummy_key":
            yield "❌ OPENAI_API_KEY not set.\n\n"
            yield "Please set a valid OpenAI API Key:\n"
            yield "```bash\n"
            yield "export OPENAI_API_KEY='sk-your-key-here'\n"
            yield "```\n"
            yield "Then restart the backend service."
            return
        
        try:
            # Create user-bound tools
            tools = self._create_tools(user_id)
            
            # Use official create_react_agent
            agent_executor = create_react_agent(
                model=self.llm,
                tools=tools
            )
            
            # Get session history
            history = self.get_session_history(session_id)
            
            # Build input
            messages = [SystemMessage(content=self.system_message)]
            messages.extend(history)
            messages.append(HumanMessage(content=user_input))
            
            # Stream execution
            full_response = ""
            async for event in agent_executor.astream_events(
                {"messages": messages},
                version="v2"
            ):
                kind = event["event"]
                
                # Only output LLM-generated content
                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        full_response += content
                        yield content
            
            # Update session history
            history.append(HumanMessage(content=user_input))
            history.append(AIMessage(content=full_response))
            
            logger.info(f"Stream completed for session {session_id}")
            
        except Exception as e:
            error_msg = f"Stream error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            # Send error info to frontend
            yield f"\n\n❌ Sorry, an error occurred while processing your request.\n\n"
            yield f"Error details: {str(e)}\n\n"
            if "api_key" in str(e).lower():
                yield "💡 Tip: Please ensure a valid OPENAI_API_KEY environment variable is set"
    
    def clear_session(self, session_id: str):
        """Clear session history"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session: {session_id}")
    
    def get_all_sessions(self) -> list:
        """Get all session IDs"""
        return list(self.sessions.keys())


# Global instance
_chat_service: Optional[LangChainChatService] = None


def get_chat_service() -> LangChainChatService:
    """Get chat service instance (singleton)"""
    global _chat_service
    if _chat_service is None:
        _chat_service = LangChainChatService()
    return _chat_service
