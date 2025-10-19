# 股票分析系统 - 架构说明文档

## 📚 目录
1. [系统概述](#系统概述)
2. [MVC架构原则](#mvc架构原则)
3. [项目结构详解](#项目结构详解)
4. [各层职责说明](#各层职责说明)
5. [数据流向](#数据流向)
6. [开发指南](#开发指南)
7. [常见问题](#常见问题)

---

## 系统概述

### 什么是股票分析系统？
这是一个智能股票分析和预警系统，帮助用户：
- 📊 追踪关注的股票价格变化
- 🤖 使用AI自动分析股票风险和趋势
- ⚠️ 在股票价格异常时自动发送预警
- 📈 生成专业的投资分析报告

### 系统的三种用户
1. **个人投资者** - 追踪自己的股票，接收预警
2. **理财顾问** - 管理多个客户的投资组合
3. **系统管理员** - 管理用户和系统运行

---

## MVC架构原则

### 什么是MVC？
MVC是一种软件设计模式，将应用程序分为三个核心部分：

```
┌─────────────────────────────────────────────────────────┐
│                      用户界面 (View)                      │
│                  前端 / API响应展示                       │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│                   控制器 (Controller)                     │
│                   API Routes (api/)                      │
│              处理HTTP请求，调用业务逻辑                    │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│                     模型 (Model)                         │
│          Services + Agents + Repositories               │
│              业务逻辑 + 数据处理 + 数据访问                │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│                    数据库 (Database)                      │
│                      MySQL数据库                         │
└─────────────────────────────────────────────────────────┘
```

### 我们的MVC实现

| MVC组件 | 对应目录 | 职责 |
|---------|---------|------|
| **View (视图)** | 前端应用 (未包含) | 展示数据给用户 |
| **Controller (控制器)** | `app/api/` | 接收请求，返回响应 |
| **Model (模型)** | `app/models/` + `app/services/` + `app/agents/` | 业务逻辑和数据处理 |
| **Data Access (数据访问)** | `app/repositories/` | 数据库操作 |

---

## 项目结构详解

### 完整目录树
```
stock-analysis-system/
│
├── app/                              # 应用主目录
│   ├── main.py                       # 🚀 应用入口（启动文件）
│   ├── config.py                     # ⚙️ 配置管理
│   ├── database.py                   # 🗄️ 数据库连接
│   │
│   ├── api/                          # 🎮 Controller层 - API路由
│   │   ├── deps.py                   # 依赖注入（认证、数据库会话）
│   │   ├── auth.py                   # 登录、注册接口
│   │   ├── stocks.py                 # 股票管理接口
│   │   ├── portfolio.py              # 投资组合接口
│   │   ├── reports.py                # 报告查询接口
│   │   ├── alerts.py                 # 预警管理接口
│   │   └── admin.py                  # 管理员接口
│   │
│   ├── models/                       # 📊 Model层 - 数据库模型
│   │   ├── user.py                   # 用户表
│   │   ├── stock.py                  # 股票表
│   │   ├── stock_data.py             # 股票价格历史表
│   │   ├── news.py                   # 新闻表
│   │   ├── alert.py                  # 预警表
│   │   ├── report.py                 # 报告表
│   │   └── tracked_stock.py          # 用户追踪股票关联表
│   │
│   ├── schemas/                      # 📝 数据验证模型
│   │   ├── user.py                   # 用户相关的请求/响应格式
│   │   ├── stock.py                  # 股票相关的请求/响应格式
│   │   ├── alert.py                  # 预警相关的请求/响应格式
│   │   ├── report.py                 # 报告相关的请求/响应格式
│   │   └── auth.py                   # 认证相关的请求/响应格式
│   │
│   ├── services/                     # 💼 业务逻辑层
│   │   ├── auth_service.py           # 用户认证业务逻辑
│   │   ├── stock_service.py          # 股票管理业务逻辑
│   │   ├── alert_service.py          # 预警管理业务逻辑
│   │   ├── report_service.py         # 报告生成业务逻辑
│   │   └── monitoring_service.py     # 后台监控业务逻辑
│   │
│   ├── agents/                       # 🤖 AI代理层
│   │   ├── base_agent.py             # 代理基类
│   │   ├── agent_manager.py          # 代理管理器（协调所有代理）
│   │   ├── data_collection_agent.py  # 数据收集代理
│   │   ├── risk_analysis_agent.py    # 风险分析代理
│   │   ├── analysis_agent.py         # 技术分析代理
│   │   ├── emotional_analysis_agent.py # 情绪分析代理
│   │   └── report_generate_agent.py  # 报告生成代理
│   │
│   ├── repositories/                 # 🗃️ 数据访问层
│   │   ├── user_repository.py        # 用户数据访问
│   │   ├── stock_repository.py       # 股票数据访问
│   │   ├── alert_repository.py       # 预警数据访问
│   │   └── report_repository.py      # 报告数据访问
│   │
│   ├── external/                     # 🌐 外部API客户端
│   │   ├── stock_api_client.py       # 股票数据API
│   │   └── news_api_client.py        # 新闻数据API
│   │
│   ├── core/                         # 🔐 核心功能
│   │   ├── security.py               # JWT认证、密码加密
│   │   └── exceptions.py             # 自定义异常
│   │
│   └── utils/                        # 🛠️ 工具函数
│       └── validators.py             # 数据验证工具
│
├── docs/                             # 📖 文档
├── requirements.txt                  # 📦 依赖包列表
├── .env                              # 🔑 环境变量（不提交到Git）
├── .gitignore                        # 🚫 Git忽略文件
└── README.md                         # 📄 项目说明
```

---

## 各层职责说明

### 1. API层 (Controller) - `app/api/`

**作用**：接收HTTP请求，返回HTTP响应

**职责**：
- ✅ 接收前端发来的HTTP请求
- ✅ 验证请求参数是否正确
- ✅ 调用Service层处理业务逻辑
- ✅ 将处理结果转换为HTTP响应返回

**示例**：
```python
# app/api/stocks.py
@router.post("/track")
async def track_stock(
    request: TrackStockRequest,      # 接收请求数据
    current_user = Depends(get_current_user),  # 验证用户登录
    db: Session = Depends(get_db)    # 获取数据库连接
):
    # 调用Service处理业务
    stock_service = StockService(db)
    result = stock_service.track_stock(current_user.id, request.symbol)
    
    # 返回响应
    return {"message": "Stock tracked successfully", "data": result}
```

**文件说明**：
- `deps.py` - 依赖注入，提供认证、数据库等公共功能
- `auth.py` - 处理登录、注册、登出
- `stocks.py` - 处理股票追踪、查询
- `portfolio.py` - 处理投资组合管理
- `reports.py` - 处理报告生成和查询
- `alerts.py` - 处理预警管理
- `admin.py` - 处理系统管理功能

---

### 2. Service层 (Business Logic) - `app/services/`

**作用**：实现业务逻辑，协调各个组件

**职责**：
- ✅ 实现具体的业务规则
- ✅ 协调Repository、Agent、External API
- ✅ 处理复杂的业务流程
- ✅ 事务管理

**示例**：
```python
# app/services/stock_service.py
class StockService:
    def track_stock(self, user_id: int, symbol: str):
        # 1. 验证股票代码
        if not self.validate_symbol(symbol):
            raise InvalidStockSymbolException()
        
        # 2. 从外部API获取股票信息
        stock_info = self.stock_api_client.get_stock_data(symbol)
        
        # 3. 保存到数据库
        stock = self.stock_repo.get_or_create(symbol, stock_info)
        
        # 4. 添加到用户追踪列表
        self.stock_repo.add_tracked_stock(user_id, stock.id)
        
        return stock
```

**文件说明**：
- `auth_service.py` - 用户注册、登录、token生成
- `stock_service.py` - 股票追踪、查询、搜索
- `alert_service.py` - 预警创建、查询、确认
- `report_service.py` - 报告生成、查询（调用Agent）
- `monitoring_service.py` - 后台定时监控任务

---

### 3. Agent层 (AI Processing) - `app/agents/`

**作用**：AI智能分析，处理复杂的分析任务

**职责**：
- ✅ 收集和处理数据
- ✅ 执行AI分析算法
- ✅ 生成分析结果
- ✅ 多个Agent协同工作

**Agent工作流程**：
```
用户请求分析
    ↓
AgentManager (协调器)
    ↓
并行执行多个Agent：
    ├─→ DataCollectionAgent (收集数据)
    ├─→ RiskAnalysisAgent (分析风险)
    ├─→ AnalysisAgent (技术分析)
    └─→ EmotionalAnalysisAgent (情绪分析)
    ↓
ReportGenerateAgent (生成报告)
    ↓
返回完整报告
```

**各Agent职责**：

#### 3.1 AgentManager - 代理管理器
```python
# app/agents/agent_manager.py
class AgentManager:
    """协调所有AI代理"""
    
    async def run_stock_analysis_pipeline(self, user_id, stock_symbol):
        # 1. 收集数据
        data = await self.data_collection_agent.execute_task(...)
        
        # 2. 并行分析
        risk = await self.risk_analysis_agent.execute_task(data)
        tech = await self.analysis_agent.execute_task(data)
        sentiment = await self.emotional_analysis_agent.execute_task(data)
        
        # 3. 生成报告
        report = await self.report_generate_agent.execute_task({
            "risk": risk,
            "technical": tech,
            "sentiment": sentiment
        })
        
        return report
```

#### 3.2 DataCollectionAgent - 数据收集代理
**职责**：
- 从外部API获取股票价格数据
- 收集相关新闻
- 获取市场整体数据
- 验证数据质量

#### 3.3 RiskAnalysisAgent - 风险分析代理
**职责**：
- 计算股票波动率
- 计算VaR（风险价值）
- 检查是否触发预警阈值
- 分析投资组合相关性

#### 3.4 AnalysisAgent - 技术分析代理
**职责**：
- 计算技术指标（RSI、MACD、移动平均线）
- 识别趋势（上涨、下跌、横盘）
- 生成买卖信号（买入、卖出、持有）
- 基本面分析（市盈率、市净率等）

#### 3.5 EmotionalAnalysisAgent - 情绪分析代理
**职责**：
- 分析新闻情感（正面、负面、中性）
- 计算市场情绪指数
- 分析社交媒体讨论热度
- 计算恐慌贪婪指数

#### 3.6 ReportGenerateAgent - 报告生成代理
**职责**：
- 综合所有分析结果
- 生成可读的分析报告
- 创建数据可视化
- 提供投资建议

---

### 4. Repository层 (Data Access) - `app/repositories/`

**作用**：封装所有数据库操作

**职责**：
- ✅ 执行数据库CRUD操作（增删改查）
- ✅ 封装复杂的SQL查询
- ✅ 提供统一的数据访问接口
- ✅ 不包含业务逻辑

**示例**：
```python
# app/repositories/stock_repository.py
class StockRepository:
    def get_by_symbol(self, symbol: str):
        """根据股票代码查询股票"""
        return self.db.query(Stock).filter(Stock.symbol == symbol).first()
    
    def add_tracked_stock(self, user_id: int, stock_id: int):
        """添加用户追踪的股票"""
        tracked = TrackedStock(user_id=user_id, stock_id=stock_id)
        self.db.add(tracked)
        self.db.commit()
        return tracked
    
    def get_tracked_stocks(self, user_id: int):
        """获取用户追踪的所有股票"""
        return self.db.query(Stock).join(TrackedStock).filter(
            TrackedStock.user_id == user_id
        ).all()
```

**文件说明**：
- `user_repository.py` - 用户表的增删改查
- `stock_repository.py` - 股票表的增删改查
- `alert_repository.py` - 预警表的增删改查
- `report_repository.py` - 报告表的增删改查

---

### 5. Model层 (Database Models) - `app/models/`

**作用**：定义数据库表结构

**职责**：
- ✅ 定义数据库表的字段
- ✅ 定义表之间的关系
- ✅ 提供ORM映射

**示例**：
```python
# app/models/user.py
class User(Base):
    __tablename__ = "users"
    
    # 字段定义
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.INVESTOR)
    alert_threshold = Column(Float, default=-5.0)
    
    # 关系定义
    tracked_stocks = relationship("TrackedStock", back_populates="user")
    alerts = relationship("Alert", back_populates="user")
    reports = relationship("Report", back_populates="user")
```

**数据库表关系图**：
```
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│    User     │───────│  TrackedStock    │───────│    Stock    │
│  (用户表)    │  1:N  │  (追踪关联表)     │  N:1  │  (股票表)    │
└─────────────┘       └──────────────────┘       └─────────────┘
      │                                                  │
      │ 1:N                                         1:N │
      ↓                                                  ↓
┌─────────────┐                                  ┌─────────────┐
│    Alert    │                                  │  StockData  │
│  (预警表)    │                                  │ (价格历史表) │
└─────────────┘                                  └─────────────┘
      │                                                  │
      │ 1:N                                         1:N │
      ↓                                                  ↓
┌─────────────┐                                  ┌─────────────┐
│   Report    │                                  │    News     │
│  (报告表)    │                                  │  (新闻表)    │
└─────────────┘                                  └─────────────┘
```

**表说明**：
- `user.py` - 用户信息（用户名、密码、角色）
- `stock.py` - 股票基本信息（代码、名称、行业）
- `stock_data.py` - 股票价格历史（开盘、收盘、最高、最低）
- `news.py` - 新闻文章（标题、内容、情感分数）
- `alert.py` - 预警记录（类型、阈值、状态）
- `report.py` - 分析报告（摘要、风险等级、建议）
- `tracked_stock.py` - 用户追踪股票的关联表

---

### 6. Schema层 (Data Validation) - `app/schemas/`

**作用**：定义API请求和响应的数据格式

**职责**：
- ✅ 验证请求数据格式
- ✅ 定义响应数据格式
- ✅ 自动生成API文档

**示例**：
```python
# app/schemas/stock.py

# 请求格式
class TrackStockRequest(BaseModel):
    symbol: str  # 必须是字符串
    
# 响应格式
class StockResponse(BaseModel):
    id: int
    symbol: str
    name: str
    sector: Optional[str]
    market_cap: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True  # 允许从ORM模型转换
```

---

### 7. External层 (External APIs) - `app/external/`

**作用**：封装外部API调用

**职责**：
- ✅ 调用股票数据API
- ✅ 调用新闻API
- ✅ 处理API限流
- ✅ 错误处理和重试

**示例**：
```python
# app/external/stock_api_client.py
class StockAPIClient:
    async def get_stock_data(self, symbol: str):
        """从外部API获取股票数据"""
        url = f"{self.base_url}/quote/{symbol}"
        response = await httpx.get(url, params={"apikey": self.api_key})
        return response.json()
```

---

### 8. Core层 (Core Functionality) - `app/core/`

**作用**：提供核心功能

**职责**：
- ✅ JWT token生成和验证
- ✅ 密码加密和验证
- ✅ 自定义异常定义

**示例**：
```python
# app/core/security.py
def create_access_token(data: dict):
    """创建JWT访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def verify_password(plain_password: str, hashed_password: str):
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)
```

---

## 数据流向

### 完整请求流程示例：用户追踪股票

```
1. 用户发起请求
   POST /api/v1/stocks/track
   Body: {"symbol": "AAPL"}
   Header: Authorization: Bearer <token>
   
   ↓

2. API层 (Controller)
   app/api/stocks.py: track_stock()
   - 验证JWT token
   - 验证请求数据格式
   - 获取当前用户信息
   
   ↓

3. Service层 (Business Logic)
   app/services/stock_service.py: track_stock()
   - 验证股票代码是否有效
   - 调用外部API获取股票信息
   - 检查用户是否已追踪该股票
   
   ↓

4. External API层
   app/external/stock_api_client.py: get_stock_data()
   - 调用外部股票数据API
   - 返回股票基本信息
   
   ↓

5. Repository层 (Data Access)
   app/repositories/stock_repository.py
   - get_or_create(): 查询或创建股票记录
   - add_tracked_stock(): 添加追踪关系
   
   ↓

6. Database层
   MySQL数据库
   - 插入/更新 stocks 表
   - 插入 tracked_stocks 表
   
   ↓

7. 返回响应
   Service → API → 用户
   Response: {
     "message": "Stock tracked successfully",
     "data": {
       "id": 1,
       "symbol": "AAPL",
       "name": "Apple Inc."
     }
   }
```

### AI分析流程示例：生成股票分析报告

```
1. 用户请求分析
   POST /api/v1/reports/generate
   Body: {"stock_id": 1}
   
   ↓

2. API层
   app/api/reports.py: generate_report()
   
   ↓

3. Service层
   app/services/report_service.py: generate_report()
   - 调用 AgentManager
   
   ↓

4. Agent层 - 并行执行
   app/agents/agent_manager.py: run_stock_analysis_pipeline()
   
   ┌────────────────────────────────────────┐
   │                                        │
   ├─→ DataCollectionAgent                 │
   │   - 收集股票价格数据                    │
   │   - 收集相关新闻                        │
   │                                        │
   ├─→ RiskAnalysisAgent                   │
   │   - 计算波动率                          │
   │   - 计算VaR                            │
   │   - 检查预警阈值                        │
   │                                        │
   ├─→ AnalysisAgent                       │
   │   - 计算RSI、MACD                      │
   │   - 识别趋势                           │
   │   - 生成交易信号                        │
   │                                        │
   └─→ EmotionalAnalysisAgent              │
       - 分析新闻情感                        │
       - 计算情绪分数                        │
   └────────────────────────────────────────┘
   
   ↓

5. 报告生成
   ReportGenerateAgent
   - 综合所有分析结果
   - 生成完整报告
   
   ↓

6. 保存报告
   Repository → Database
   - 保存到 reports 表
   
   ↓

7. 返回报告
   返回完整的分析报告给用户
```

---

## 开发指南

### 新手开发流程

#### 步骤1：理解需求
假设需求：**添加"收藏股票"功能**

#### 步骤2：确定涉及的层
- ✅ API层：需要新增接口
- ✅ Service层：需要业务逻辑
- ✅ Repository层：需要数据库操作
- ✅ Model层：可能需要新表（如果已有则不需要）

#### 步骤3：从下往上开发

**3.1 Model层（如果需要新表）**
```python
# app/models/favorite_stock.py
class FavoriteStock(Base):
    __tablename__ = "favorite_stocks"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
```

**3.2 Repository层**
```python
# app/repositories/stock_repository.py
def add_favorite_stock(self, user_id: int, stock_id: int):
    """添加收藏股票"""
    favorite = FavoriteStock(user_id=user_id, stock_id=stock_id)
    self.db.add(favorite)
    self.db.commit()
    return favorite

def get_favorite_stocks(self, user_id: int):
    """获取用户收藏的股票"""
    return self.db.query(Stock).join(FavoriteStock).filter(
        FavoriteStock.user_id == user_id
    ).all()
```

**3.3 Service层**
```python
# app/services/stock_service.py
def favorite_stock(self, user_id: int, stock_id: int):
    """收藏股票业务逻辑"""
    # 1. 检查股票是否存在
    stock = self.stock_repo.get_by_id(stock_id)
    if not stock:
        raise StockNotFoundException()
    
    # 2. 检查是否已收藏
    if self.stock_repo.is_favorited(user_id, stock_id):
        raise AlreadyFavoritedException()
    
    # 3. 添加收藏
    return self.stock_repo.add_favorite_stock(user_id, stock_id)
```

**3.4 API层**
```python
# app/api/stocks.py
@router.post("/favorite/{stock_id}")
async def favorite_stock(
    stock_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """收藏股票接口"""
    stock_service = StockService(db)
    result = stock_service.favorite_stock(current_user.id, stock_id)
    return {"message": "Stock favorited successfully", "data": result}
```

#### 步骤4：测试
1. 启动应用：`uvicorn app.main:app --reload`
2. 访问文档：http://localhost:8000/docs
3. 测试接口

---

### 开发规范

#### 1. 命名规范

**文件命名**：
- 使用小写字母和下划线：`stock_service.py`
- 一个文件一个主要类

**类命名**：
- 使用大驼峰命名：`StockService`
- 名称要有意义：`UserRepository` 而不是 `UR`

**函数命名**：
- 使用小写字母和下划线：`get_stock_data()`
- 动词开头：`create_user()`, `update_alert()`, `delete_report()`

**变量命名**：
- 使用小写字母和下划线：`stock_symbol`, `user_id`
- 布尔值用 `is_` 或 `has_` 开头：`is_active`, `has_permission`

#### 2. 代码组织

**每个文件的结构**：
```python
"""
文件说明（这个文件是做什么的）
"""

# 1. 标准库导入
from datetime import datetime
from typing import List, Optional

# 2. 第三方库导入
from sqlalchemy.orm import Session
from fastapi import APIRouter

# 3. 本地导入
from app.models.user import User
from app.schemas.user import UserResponse

# 4. 类或函数定义
class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        """初始化"""
        self.db = db
    
    def create_user(self, user_data):
        """创建用户"""
        pass
```

#### 3. 注释规范

**类注释**：
```python
class StockService:
    """
    股票服务类
    
    负责处理股票相关的业务逻辑，包括：
    - 股票追踪
    - 股票查询
    - 股票搜索
    """
```

**函数注释**：
```python
def track_stock(self, user_id: int, symbol: str):
    """
    添加股票到用户追踪列表
    
    Args:
        user_id: 用户ID
        symbol: 股票代码（如 "AAPL"）
        
    Returns:
        Stock: 股票对象
        
    Raises:
        InvalidStockSymbolException: 股票代码无效
        AlreadyTrackedException: 已经在追踪列表中
    """
```

#### 4. 错误处理

**使用自定义异常**：
```python
# 不好的做法
if not stock:
    return {"error": "Stock not found"}

# 好的做法
if not stock:
    raise StockNotFoundException(f"Stock {symbol} not found")
```

**在API层捕获异常**：
```python
@router.post("/track")
async def track_stock(...):
    try:
        result = stock_service.track_stock(...)
        return {"success": True, "data": result}
    except StockNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AlreadyTrackedException as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

### 常用开发命令

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动应用（开发模式，自动重载）
uvicorn app.main:app --reload

# 5. 启动应用（指定端口）
uvicorn app.main:app --reload --port 8080

# 6. 查看API文档
# 浏览器访问：http://localhost:8000/docs

# 7. 数据库相关
# 创建数据库
mysql -u root -p
CREATE DATABASE stock_analysis;

# 8. Git相关
git add .
git commit -m "描述你的改动"
git push origin main
```

---

## 常见问题

### Q1: 什么时候应该创建新的Service？
**A**: 当你有一组相关的业务逻辑时。例如：
- `AuthService` - 所有认证相关的逻辑
- `StockService` - 所有股票管理相关的逻辑
- `ReportService` - 所有报告生成相关的逻辑

### Q2: Repository和Service有什么区别？
**A**: 
- **Repository**：只做数据库操作，不包含业务逻辑
  ```python
  # Repository - 简单的数据库操作
  def get_user_by_id(self, user_id):
      return self.db.query(User).filter(User.id == user_id).first()
  ```
  
- **Service**：包含业务逻辑，可以调用多个Repository
  ```python
  # Service - 包含业务逻辑
  def update_user_profile(self, user_id, profile_data):
      # 1. 验证权限
      if not self.has_permission(user_id):
          raise UnauthorizedException()
      
      # 2. 验证数据
      if not self.validate_profile(profile_data):
          raise InvalidDataException()
      
      # 3. 更新数据库
      return self.user_repo.update(user_id, profile_data)
  ```

### Q3: 什么时候使用Agent？
**A**: 当需要AI分析或复杂计算时：
- 股票风险分析 → RiskAnalysisAgent
- 新闻情感分析 → EmotionalAnalysisAgent
- 技术指标计算 → AnalysisAgent

普通的CRUD操作不需要Agent，直接在Service中处理。

### Q4: 如何调试代码？
**A**: 
1. **使用print调试**：
   ```python
   print(f"User ID: {user_id}, Stock: {symbol}")
   ```

2. **使用日志**：
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.info(f"Processing stock: {symbol}")
   ```

3. **使用FastAPI文档**：
   访问 http://localhost:8000/docs 直接测试API

4. **使用断点调试**：
   在IDE中设置断点，逐步执行代码

### Q5: 如何添加新的API接口？
**A**: 按照以下步骤：
1. 在 `app/schemas/` 定义请求和响应格式
2. 在 `app/repositories/` 添加数据库操作（如果需要）
3. 在 `app/services/` 添加业务逻辑
4. 在 `app/api/` 添加API路由
5. 在 `app/main.py` 中注册路由（如果是新文件）

### Q6: 如何处理异步操作？
**A**: 
- 使用 `async/await` 关键字
- 外部API调用使用异步
- 数据库操作可以是同步的（SQLAlchemy默认同步）

```python
# 异步函数
async def get_stock_data(symbol: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/stock/{symbol}")
        return response.json()

# 在API中调用
@router.get("/stock/{symbol}")
async def get_stock(symbol: str):
    data = await get_stock_data(symbol)
    return data
```

### Q7: 如何测试我的代码？
**A**: 
1. **手动测试**：使用 http://localhost:8000/docs
2. **单元测试**：编写测试文件（未来添加）
3. **集成测试**：测试完整的业务流程

---

## 学习资源

### 推荐学习顺序
1. **Python基础** → 了解类、函数、异步编程
2. **FastAPI教程** → 官方文档：https://fastapi.tiangolo.com/
3. **SQLAlchemy** → ORM基础
4. **本项目架构** → 阅读本文档

### 有用的文档链接
- FastAPI官方文档：https://fastapi.tiangolo.com/
- SQLAlchemy文档：https://docs.sqlalchemy.org/
- Pydantic文档：https://docs.pydantic.dev/
- Python异步编程：https://docs.python.org/3/library/asyncio.html

---

## 总结

### 核心原则
1. **分层清晰**：API → Service → Repository → Database
2. **职责单一**：每个类只做一件事
3. **依赖注入**：通过参数传递依赖
4. **错误处理**：使用异常而不是返回错误码
5. **代码复用**：相同的逻辑提取到公共函数

### 开发检查清单
- [ ] 代码是否遵循MVC架构？
- [ ] 每个函数是否有清晰的注释？
- [ ] 是否有适当的错误处理？
- [ ] 变量和函数命名是否有意义？
- [ ] 是否遵循了命名规范？
- [ ] 代码是否可以被其他人理解？

---

**最后更新**：2024年
**维护者**：开发团队
**问题反馈**：在GitHub Issues中提出


