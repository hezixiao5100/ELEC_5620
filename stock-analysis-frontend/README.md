# Stock Analysis System - Frontend

## Overview

A React + TypeScript + Ant Design frontend application for the stock analysis system, supporting three different user role interfaces.

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5.0.8
- **UI Library**: Ant Design 5.12.0 - Enterprise-level UI component library for React
- **Routing**: React Router DOM 6.20.0
- **State Management**: Zustand 4.4.7 (lightweight state management)
- **HTTP Client**: Axios 1.6.2
- **Charts**: Ant Design Charts + Recharts 2.10.3
- **Date Handling**: Day.js 1.11.10

## Project Structure

```
stock-analysis-frontend/
├── public/                 # Static assets
├── src/
│   ├── pages/             # Page components
│   │   ├── auth/          # Authentication pages
│   │   │   ├── Login.tsx
│   │   │   └── Register.tsx
│   │   ├── investor/      # Investor interface
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Portfolio.tsx
│   │   │   ├── StockDetail.tsx
│   │   │   ├── StockSearch.tsx
│   │   │   ├── Alerts.tsx
│   │   │   ├── Reports.tsx
│   │   │   └── AIAssistant.tsx
│   │   ├── advisor/       # Advisor interface
│   │   │   ├── AdvisorDashboard.tsx
│   │   │   ├── ClientManagement.tsx
│   │   │   ├── ClientPortfolio.tsx
│   │   │   ├── Portfolios.tsx
│   │   │   ├── Reports.tsx
│   │   │   ├── ReportDetail.tsx
│   │   │   ├── Analytics.tsx
│   │   │   └── AIAssistant.tsx
│   │   └── admin/         # Admin interface
│   │       ├── AdminDashboard.tsx
│   │       ├── UserManagement.tsx
│   │       ├── RoleManagement.tsx
│   │       ├── SystemPerformance.tsx
│   │       ├── BackgroundTasks.tsx
│   │       ├── SystemLogs.tsx
│   │       └── Settings.tsx
│   ├── services/          # API service layer
│   │   ├── api.ts         # Axios configuration
│   │   ├── authService.ts
│   │   ├── stockService.ts
│   │   ├── alertService.ts
│   │   ├── reportService.ts
│   │   ├── advisorService.ts
│   │   └── chatService.ts
│   ├── stores/            # Zustand state management
│   │   └── authStore.ts
│   ├── types/             # TypeScript type definitions
│   │   └── index.ts
│   ├── utils/             # Utility functions
│   │   └── tokenRefresh.ts
│   ├── App.tsx            # Root component
│   ├── main.tsx           # Entry point
│   └── index.css          # Global styles
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Three User Interface Designs

### 1. INVESTOR (Individual Investor)

**Features:**
- View personal investment portfolio
- Add/remove tracked stocks
- View stock details and analysis
- Set up price alerts
- View alert notifications
- Generate personal investment reports
- AI assistant for investment queries

**Main Pages:**
- Dashboard: Portfolio overview, profit charts
- Portfolio: Tracked stocks list with P&L calculation
- Stock Search: Search and add stocks to track
- Stock Detail: Stock details, technical analysis, news
- Alerts: Alert management and configuration
- Reports: View generated analysis reports
- AI Assistant: Chat with AI for investment advice

### 2. ADVISOR (Financial Advisor)

**Features:**
- View all client list
- View and modify client portfolios
- Generate analysis reports for clients
- Provide investment recommendations
- Batch manage client stocks
- Monitor client alerts
- View client analytics and insights

**Main Pages:**
- Dashboard: All clients overview with metrics
- Client Management: Client list management
- Client Portfolio: Detailed client portfolio (editable)
- Portfolios: Multi-client portfolio view
- Reports: Generate and manage client reports
- Report Detail: View comprehensive client reports
- Analytics: Client performance analytics
- AI Assistant: Investment recommendations

### 3. ADMIN (System Administrator)

**Features:**
- User management (create, update, delete, activate/deactivate)
- Role management and assignment
- System performance monitoring (CPU, Memory, Disk)
- Background task management (Celery task status)
- System logs viewing with filtering
- System configuration

**Main Pages:**
- Dashboard: System overview, key metrics
- User Management: User list, role assignment, status management
- Role Management: Role definitions, permission management
- System Performance: Real-time metrics, performance charts
- Background Tasks: Task monitoring and management
- System Logs: Operation logs, error logs with search
- Settings: System configuration

## Installation and Running

### 1. Install Dependencies

```bash
cd stock-analysis-frontend
npm install
```

### 2. Configure Environment Variables

Create a `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm run dev
```

Access the application at `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Core Features

### 1. Authentication and Authorization

- JWT Token authentication
- Automatic token refresh
- Role-based route protection
- Permission control

### 2. State Management (Zustand)

```typescript
// authStore.ts
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
}
```

### 3. Route Protection

```typescript
// PrivateRoute implementation
<Route element={<PrivateRoute allowedRoles={[UserRole.INVESTOR]} />}>
  <Route path="/investor/*" element={<InvestorLayout />} />
</Route>
```

### 4. API Request Interception

- Automatically add Authorization Header
- Auto refresh token on 401 errors
- Unified error handling

### 5. Real-time Data Updates

- Polling for data updates
- Event-driven updates
- WebSocket support (optional)

## UI Component Library - Ant Design

### Why Ant Design?

1. **React Native Support**: Designed specifically for React, not a Vue port
2. **Enterprise-grade**: Developed by Alibaba, mature and stable
3. **Rich Components**: 60+ high-quality components
4. **TypeScript**: Complete TypeScript type definitions
5. **Theme Customization**: Flexible theme configuration
6. **Internationalization**: Built-in multi-language support

### Core Components Usage

```typescript
import { Table, Card, Button, Form, Input, Select, DatePicker, Modal } from 'antd';
import { Line, Column, Area } from '@ant-design/charts';
```

### Admin Panel Layout

```typescript
import { Layout, Menu, Breadcrumb } from 'antd';
const { Header, Sider, Content } = Layout;

// Sidebar menu
const menuItems = [
  { key: 'dashboard', icon: <DashboardOutlined />, label: 'Dashboard' },
  { key: 'users', icon: <UserOutlined />, label: 'User Management' },
  { key: 'system', icon: <SettingOutlined />, label: 'System Settings' },
];
```

## API Integration

### Backend API Base URL

```
Base URL: http://localhost:8000/api/v1
```

### Main Endpoints

```
POST   /auth/login          - User login
POST   /auth/register       - User registration
GET    /auth/me             - Get current user
GET    /auth/refresh        - Refresh access token
GET    /stocks              - Get stock list
GET    /stocks/{id}         - Get stock details
GET    /stocks/search       - Search stocks
GET    /portfolio           - Get user portfolio
POST   /portfolio           - Add stock to portfolio
PUT    /portfolio/{id}      - Update portfolio entry
DELETE /portfolio/{id}      - Remove from portfolio
GET    /alerts              - Get alert list
POST   /alerts              - Create alert
GET    /reports             - Get report list
POST   /reports/generate    - Generate report
GET    /admin/users         - Get user list (ADMIN)
POST   /admin/users         - Create user (ADMIN)
PUT    /admin/users/{id}    - Update user (ADMIN)
GET    /admin/logs          - System logs (ADMIN)
GET    /admin/tasks/list    - Background tasks (ADMIN)
GET    /monitoring/metrics  - System metrics (ADMIN)
POST   /chat                - AI chat
```

## Development Standards

### 1. Code Standards

- ESLint + TypeScript
- Prettier formatting
- Husky Git Hooks (optional)

### 2. Naming Conventions

- Components: PascalCase (e.g., `StockCard.tsx`)
- Files: camelCase (e.g., `stockService.ts`)
- Constants: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)

### 3. Component Standards

```typescript
// Functional Component with TypeScript
interface StockCardProps {
  stock: Stock;
  onTrack: (symbol: string) => void;
}

const StockCard: React.FC<StockCardProps> = ({ stock, onTrack }) => {
  return (
    <Card>
      <h3>{stock.name}</h3>
      <p>{stock.symbol}</p>
      <Button onClick={() => onTrack(stock.symbol)}>Track</Button>
    </Card>
  );
};

export default StockCard;
```

## Deployment

### Development Environment

```bash
npm run dev
```

### Production Environment

```bash
npm run build
npm run preview
```

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 5173
CMD ["npm", "run", "preview"]
```

## Development Status

### ✅ Completed Features

1. ✅ Project initialization and configuration
2. ✅ Type definitions and API services
3. ✅ Authentication pages (Login/Register)
4. ✅ INVESTOR interface development
5. ✅ ADVISOR interface development
6. ✅ ADMIN backend management system
7. ✅ Charts and data visualization
8. ✅ Real-time data updates
9. ✅ Responsive design

### 🔄 Future Enhancements

- Unit testing
- E2E testing
- Performance optimization
- PWA support
- WebSocket integration

## Notes

1. **Ant Design vs Element Plus**: 
   - Element Plus is Vue 3 exclusive, cannot be used with React
   - Ant Design is the best choice for React with more powerful features

2. **Admin Panel Style**:
   - Uses Ant Design components
   - Sidebar + top navigation layout
   - Breadcrumb navigation
   - Table + form-based management interface

3. **Permission Control**:
   - Frontend route-level permission control
   - Backend API permission verification
   - Button-level permission control

## License

MIT

## Contact

For questions, please contact the development team.

---

**Last Updated**: November 2025
**Version**: 1.0.0
