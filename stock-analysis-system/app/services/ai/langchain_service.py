"""
LangChain Agent Service
使用 LangGraph 的 create_react_agent 进行智能路由（官方推荐的新架构 LangChain 1.0+）
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

logger = logging.getLogger(__name__)


class LangChainChatService:
    """LangChain 聊天服务 - 使用官方 LangGraph"""
    
    def __init__(self):
        """初始化 LangChain Agent"""
        
        # 从 settings 获取 OpenAI API Key (会自动从 .env 加载)
        self.api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ OPENAI_API_KEY not set in .env file. AI chat will not work without a valid API key.")
            self.api_key = "dummy_key"  # 使用假 key 避免初始化错误
        
        # 初始化 LLM
        try:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",  # 使用 gpt-4o-mini 更快更便宜
                temperature=0.7,
                streaming=True,
                api_key=self.api_key
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChatOpenAI: {str(e)}")
            # 仍然创建一个基本的对象，避免完全崩溃
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
- You can only ANALYZE data, NOT execute trades or modify alerts/portfolio
- If users ask to buy/sell stocks or create/delete alerts, politely explain this interface is for analysis only
- Always cite the specific data sources when presenting numbers
- **USER IDENTITY**: The user is already authenticated. You DON'T need to ask for user ID or login info.
  All tools automatically access the logged-in user's data. Just call the tools directly.

**DATA COLLECTION**:
- If you find that data is missing or insufficient (e.g., no news, no price data), you can PROACTIVELY use the `collect_stock_data` tool to fetch fresh data
- The data collection is limited to the last 3 days (max 7 days) to keep it fast and relevant
- After collecting data, you can immediately use other analysis tools to provide insights
- Example workflow: User asks about MSFT sentiment → No news found → Call collect_stock_data(MSFT) → Then call analyze_stock_news(MSFT)

Remember: Be helpful, accurate, and insightful! Don't hesitate to collect fresh data when needed."""
        
        # 会话历史存储 (session_id -> List[BaseMessage])
        self.sessions: Dict[str, List[BaseMessage]] = {}
        
        logger.info("✅ LangChain Chat Service initialized (using LangGraph)")
    
    def _create_tools(self, user_id: int):
        """创建工具列表（绑定用户 ID）"""
        
        # 使用 partial 预填充 user_id
        tools = [
            StructuredTool.from_function(
                func=partial(analyze_portfolio_risk, user_id=user_id),
                name="analyze_portfolio_risk",
                description="分析用户投资组合的风险状况，包括集中度、波动性、行业分散度等。当用户询问'我的投资风险大吗'、'持仓风险如何'等问题时使用。",
                args_schema=PortfolioRiskInput
            ),
            StructuredTool.from_function(
                func=partial(analyze_market_sentiment, user_id=user_id),
                name="analyze_market_sentiment",
                description="分析市场或特定股票的情绪状况，包括看涨/看跌趋势、价格变化等。当用户询问'市场情绪怎么样'、'XX股票情绪如何'时使用。",
                args_schema=MarketSentimentInput
            ),
            StructuredTool.from_function(
                func=partial(analyze_stock_performance, user_id=user_id),
                name="analyze_stock_performance",
                description="分析个股的表现和技术指标，包括价格趋势、波动率、成交量等。当用户询问'AAPL表现如何'、'分析一下TSLA'时使用。",
                args_schema=StockPerformanceInput
            ),
            StructuredTool.from_function(
                func=partial(analyze_alert_status, user_id=user_id),
                name="analyze_alert_status",
                description="分析当前预警状态和触发风险，显示临近触发的预警。当用户询问'我的预警状态'、'哪些预警快触发了'时使用。",
                args_schema=AlertStatusInput
            ),
            StructuredTool.from_function(
                func=partial(analyze_portfolio_performance, user_id=user_id),
                name="analyze_portfolio_performance",
                description="分析投资组合的收益表现，包括总收益、个股排名、盈亏情况等。当用户询问'我的收益如何'、'哪个股票赚得最多'时使用。",
                args_schema=PortfolioPerformanceInput
            ),
            StructuredTool.from_function(
                func=partial(analyze_market_trend, user_id=user_id),
                name="analyze_market_trend",
                description="分析市场趋势和热点，基于用户追踪的股票。当用户询问'市场趋势'、'热门板块'时使用。",
                args_schema=MarketTrendInput
            ),
            StructuredTool.from_function(
                func=partial(analyze_stock_news, user_id=user_id),
                name="analyze_stock_news",
                description="获取并分析股票的最近新闻，包括新闻标题、来源、情绪评分等。当用户询问'XX股票有什么新闻'、'最近关于XX的消息'、'市场情绪'时使用。这对分析市场情绪非常有帮助。",
                args_schema=StockNewsInput
            ),
            StructuredTool.from_function(
                func=partial(collect_stock_data, user_id=user_id),
                name="collect_stock_data",
                description="主动收集股票的最新数据（价格、新闻等）。当数据库中没有数据或数据过时时使用。限制收集最近3天的数据（最多7天）。这个工具会调用真实的API获取最新信息。",
                args_schema=CollectStockDataInput
            ),
            StructuredTool.from_function(
                func=partial(analyze_stock_risk, user_id=user_id),
                name="analyze_stock_risk",
                description="分析单只股票的风险状况，包括波动率、最大回撤、Beta、风险等级等。当用户询问'XX股票风险如何'、'分析XX的风险'、'XX风险大吗'时使用。注意：这是针对单只股票的风险分析，不是投资组合风险。",
                args_schema=StockRiskInput
            )
        ]
        
        return tools
    
    def get_session_history(self, session_id: str) -> List[BaseMessage]:
        """获取会话历史"""
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
        处理用户输入（非流式）
        
        Args:
            user_input: 用户输入的消息
            session_id: 会话 ID
            user_id: 用户 ID
        
        Returns:
            包含 AI 响应的字典
        """
        try:
            # 创建绑定用户的工具
            tools = self._create_tools(user_id)
            
            # 使用官方的 create_react_agent (LangGraph)
            agent_executor = create_react_agent(
                model=self.llm,
                tools=tools
            )
            
            # 获取会话历史
            history = self.get_session_history(session_id)
            
            # 构建输入（包含 system message 和历史）
            messages = [SystemMessage(content=self.system_message)]
            messages.extend(history)
            messages.append(HumanMessage(content=user_input))
            
            # 执行
            result = await agent_executor.ainvoke({"messages": messages})
            
            # 提取响应
            response_messages = result.get("messages", [])
            ai_response = ""
            for msg in response_messages:
                if isinstance(msg, AIMessage) and msg.content:
                    ai_response = msg.content
            
            # 更新会话历史
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
                "response": f"抱歉，处理您的请求时出现错误: {str(e)}",
                "error": str(e)
            }
    
    async def chat_stream(
        self,
        user_input: str,
        session_id: str,
        user_id: int
    ) -> AsyncIterator[str]:
        """
        处理用户输入（流式响应）
        
        Args:
            user_input: 用户输入的消息
            session_id: 会话 ID
            user_id: 用户 ID
        
        Yields:
            响应内容的文本块
        """
        # 检查 LLM 是否初始化成功
        if self.llm is None:
            yield "❌ AI 服务未正确初始化。请检查 OPENAI_API_KEY 环境变量是否设置。"
            return
        
        if self.api_key == "dummy_key":
            yield "❌ OPENAI_API_KEY 未设置。\n\n"
            yield "请设置有效的 OpenAI API Key:\n"
            yield "```bash\n"
            yield "export OPENAI_API_KEY='sk-your-key-here'\n"
            yield "```\n"
            yield "然后重启后端服务。"
            return
        
        try:
            # 创建绑定用户的工具
            tools = self._create_tools(user_id)
            
            # 使用官方的 create_react_agent
            agent_executor = create_react_agent(
                model=self.llm,
                tools=tools
            )
            
            # 获取会话历史
            history = self.get_session_history(session_id)
            
            # 构建输入
            messages = [SystemMessage(content=self.system_message)]
            messages.extend(history)
            messages.append(HumanMessage(content=user_input))
            
            # 流式执行
            full_response = ""
            async for event in agent_executor.astream_events(
                {"messages": messages},
                version="v2"
            ):
                kind = event["event"]
                
                # 只输出 LLM 生成的内容
                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        full_response += content
                        yield content
            
            # 更新会话历史
            history.append(HumanMessage(content=user_input))
            history.append(AIMessage(content=full_response))
            
            logger.info(f"Stream completed for session {session_id}")
            
        except Exception as e:
            error_msg = f"Stream error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            # 发送错误信息给前端
            yield f"\n\n❌ 抱歉，处理您的请求时出现错误。\n\n"
            yield f"错误详情: {str(e)}\n\n"
            if "api_key" in str(e).lower():
                yield "💡 提示：请确保设置了有效的 OPENAI_API_KEY 环境变量"
    
    def clear_session(self, session_id: str):
        """清除会话历史"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session: {session_id}")
    
    def get_all_sessions(self) -> list:
        """获取所有会话 ID"""
        return list(self.sessions.keys())


# 全局实例
_chat_service: Optional[LangChainChatService] = None


def get_chat_service() -> LangChainChatService:
    """获取聊天服务实例（单例）"""
    global _chat_service
    if _chat_service is None:
        _chat_service = LangChainChatService()
    return _chat_service
