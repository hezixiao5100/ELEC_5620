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
    add_holding,
    update_holding,
    delete_holding,
    track_stock,
    untrack_stock,
    reduce_holding,
    ViewPortfolioInput,
    ListTrackedStocksInput,
    AddHoldingInput,
    UpdateHoldingInput,
    DeleteHoldingInput,
    TrackStockInput,
    UntrackStockInput,
    ReduceHoldingInput
)

logger = logging.getLogger(__name__)


class LangChainChatService:
    """LangChain Chat Service - using official LangGraph"""
    
    def __init__(self):
        """Initialize LangChain Agent"""
        
        # Get OpenAI API Key from settings (automatically loaded from .env)
        self.api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ OPENAI_API_KEY not set in .env file. AI chat will not work without a valid API key.")
            self.api_key = "dummy_key"  # Use dummy key to avoid initialization errors
        
        # Initialize LLM
        try:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",  # Using gpt-4o-mini for faster and cheaper operation
                temperature=0.7,
                streaming=True,
                api_key=self.api_key
            )
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
- You CAN manage portfolio holdings (add, update, delete, reduce) through confirmation workflow
- Portfolio operations use two-step confirmation: 
  **STEP 1 (Draft)**: When user requests an operation, call the tool with confirm=false
  **STEP 2 (Execute)**: When user confirms, call the same tool with confirm=true AND the exact token from step 1
  
- **CRITICAL: When returning draft results, you MUST:**
  1. Extract and display the actual token value from the tool response (e.g., "token": "abc123xyz")
  2. Clearly tell the user: "Here is the draft. The confirmation token is: [ACTUAL_TOKEN]"
  3. Instruct them: "Reply 'confirm' or 'yes' to proceed with this operation"
  4. Format the draft as a readable JSON code block
  
- **When user confirms:**
  1. Use the EXACT token from the draft response
  2. Call the same tool again with confirm=true and token=[THE_TOKEN]
  3. Do NOT generate new tokens or make up tokens - use the one from draft
  
- Always cite the specific data sources when presenting numbers
- **USER IDENTITY**: The user is already authenticated. You DON'T need to ask for user ID or login info.
  All tools automatically access the logged-in user's data. Just call the tools directly.

**DATA COLLECTION**:
- If you find that data is missing or insufficient (e.g., no news, no price data), you can PROACTIVELY use the `collect_stock_data` tool to fetch fresh data
- The data collection is limited to the last 3 days (max 7 days) to keep it fast and relevant
- After collecting data, you can immediately use other analysis tools to provide insights
- Example workflow: User asks about MSFT sentiment → No news found → Call collect_stock_data(MSFT) → Then call analyze_stock_news(MSFT)

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
                description="Analyze market or specific stock sentiment including bullish/bearish trends and price changes. Use when users ask 'How's the market sentiment?' or 'What's the sentiment for a stock?'.",
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
            # Portfolio Management Tools (增删改查)
            StructuredTool.from_function(
                func=partial(view_portfolio, user_id=user_id),
                name="view_portfolio",
                description="View the user's portfolio holdings and summary. Use when users ask to see their portfolio, holdings, or current positions.",
                args_schema=ViewPortfolioInput
            ),
            StructuredTool.from_function(
                func=partial(list_tracked_stocks, user_id=user_id),
                name="list_tracked_stocks",
                description="List all stocks the user is tracking with their baseline prices. Use when users ask about tracked stocks or monitoring list.",
                args_schema=ListTrackedStocksInput
            ),
            StructuredTool.from_function(
                func=partial(add_holding, user_id=user_id),
                name="add_holding",
                description="Add a new stock holding to the portfolio. Use when users say 'add', 'buy', 'purchase' stocks. Returns draft first, needs confirmation.",
                args_schema=AddHoldingInput
            ),
            StructuredTool.from_function(
                func=partial(update_holding, user_id=user_id),
                name="update_holding",
                description="Update an existing holding's quantity, price, or notes. Use when users want to modify existing positions. Returns draft first, needs confirmation.",
                args_schema=UpdateHoldingInput
            ),
            StructuredTool.from_function(
                func=partial(delete_holding, user_id=user_id),
                name="delete_holding",
                description="Delete a holding from the portfolio. Use when users say 'remove', 'delete', 'sell all' of a stock. Returns draft first, needs confirmation.",
                args_schema=DeleteHoldingInput
            ),
            StructuredTool.from_function(
                func=partial(reduce_holding, user_id=user_id),
                name="reduce_holding",
                description="Reduce quantity of an existing holding. Use when users say 'reduce', 'sell', 'partially sell' stocks. Returns draft first, needs confirmation.",
                args_schema=ReduceHoldingInput
            ),
            StructuredTool.from_function(
                func=partial(track_stock, user_id=user_id),
                name="track_stock",
                description="Start tracking a stock with optional baseline price for alerts. Use when users want to monitor a stock. Returns draft first, needs confirmation.",
                args_schema=TrackStockInput
            ),
            StructuredTool.from_function(
                func=partial(untrack_stock, user_id=user_id),
                name="untrack_stock",
                description="Stop tracking a stock. Use when users want to remove a stock from monitoring. Returns draft first, needs confirmation.",
                args_schema=UntrackStockInput
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
