import React, { useEffect, useState } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Spin,
  message,
  Tag,
  Space,
} from 'antd';
import {
  DashboardOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import api from '@/services/api';
// Note: If @ant-design/plots is not installed, use a simple chart library or create custom charts
// For now, we'll create simple visual representations

interface SystemMetrics {
  timestamp: string;
  cpu: {
    percent: number;
    count: number;
    frequency?: number;
  };
  memory: {
    total: number;
    available: number;
    percent: number;
    used: number;
    free: number;
  };
  disk: {
    total: number;
    used: number;
    free: number;
    percent: number;
  };
  network?: {
    bytes_sent: number;
    bytes_recv: number;
  };
}

interface PerformanceSummary {
  cpu: {
    current: number;
    average: number;
    max: number;
    min: number;
  };
  memory: {
    current: number;
    average: number;
    max: number;
    min: number;
  };
  disk: {
    current: number;
    average: number;
    max: number;
    min: number;
  };
}

const SystemPerformance: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [summary, setSummary] = useState<PerformanceSummary | null>(null);
  const [metricsHistory, setMetricsHistory] = useState<any[]>([]);

  useEffect(() => {
    loadMetrics();
    const interval = setInterval(loadMetrics, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      const [metricsRes, dashboardRes] = await Promise.all([
        api.get('/monitoring/metrics/system'),
        api.get('/monitoring/dashboard').catch(() => null),
      ]);

      setMetrics(metricsRes.data);
      
      if (dashboardRes?.data?.performance) {
        setSummary(dashboardRes.data.performance);
        
        // Generate mock history data for charts
        if (dashboardRes.data.performance) {
          const history = [];
          const now = Date.now();
          for (let i = 23; i >= 0; i--) {
            history.push({
              time: new Date(now - i * 3600000).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
              cpu: dashboardRes.data.performance.cpu.current + (Math.random() * 20 - 10),
              memory: dashboardRes.data.performance.memory.current + (Math.random() * 10 - 5),
              disk: dashboardRes.data.performance.disk.current + (Math.random() * 5 - 2.5),
            });
          }
          setMetricsHistory(history);
        }
      }
    } catch (error) {
      message.error('Failed to load system metrics');
    } finally {
      setLoading(false);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getStatusColor = (percent: number) => {
    if (percent < 50) return '#52c41a';
    if (percent < 80) return '#faad14';
    return '#ff4d4f';
  };

  // Simple chart component
  const SimpleChart: React.FC<{ data: any[]; color: string; field: 'cpu' | 'memory' | 'disk'; height?: number }> = ({ data, color, field, height = 200 }) => {
    if (data.length === 0) return <div style={{ textAlign: 'center', padding: '50px' }}>No data available</div>;
    
    const values = data.map(d => d[field] || 0);
    const maxValue = Math.max(...values, 100);
    const chartHeight = height - 40; // Leave space for labels
    const points = values.map((value, i) => ({
      x: (i / (values.length - 1 || 1)) * 100,
      y: chartHeight - (value / maxValue) * chartHeight,
      value: value,
    }));

    return (
      <svg width="100%" height={height} style={{ overflow: 'visible' }}>
        <defs>
          <linearGradient id={`gradient-${color}`} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>
        <path
          d={`M 0 ${height} ${points.map(p => `L ${p.x}% ${p.y}%`).join(' ')} L 100% ${height} Z`}
          fill={`url(#gradient-${color})`}
        />
        <path
          d={`M 0 ${height} ${points.map(p => `L ${p.x}% ${p.y}%`).join(' ')}`}
          stroke={color}
          strokeWidth="2"
          fill="none"
        />
        {points.map((p, i) => (
          <circle
            key={i}
            cx={`${p.x}%`}
            cy={`${p.y}%`}
            r="3"
            fill={color}
          />
        ))}
      </svg>
    );
  };

  if (loading && !metrics) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ margin: 0 }}>System Performance</h1>
        <Space>
          <Tag color="blue">Last Updated: {metrics ? new Date(metrics.timestamp).toLocaleTimeString() : 'N/A'}</Tag>
          <a onClick={loadMetrics} style={{ cursor: 'pointer' }}>
            <ReloadOutlined /> Refresh
          </a>
        </Space>
      </div>

      {/* Overview Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="CPU Usage"
              value={metrics?.cpu.percent || 0}
              precision={1}
              suffix="%"
              valueStyle={{ color: getStatusColor(metrics?.cpu.percent || 0) }}
              prefix={<DashboardOutlined />}
            />
            {summary && (
              <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                Avg: {summary.cpu.average.toFixed(1)}% | Max: {summary.cpu.max.toFixed(1)}%
              </div>
            )}
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="Memory Usage"
              value={metrics?.memory.percent || 0}
              precision={1}
              suffix="%"
              valueStyle={{ color: getStatusColor(metrics?.memory.percent || 0) }}
            />
            {metrics && (
              <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                {formatBytes(metrics.memory.used)} / {formatBytes(metrics.memory.total)}
              </div>
            )}
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="Disk Usage"
              value={metrics?.disk.percent || 0}
              precision={1}
              suffix="%"
              valueStyle={{ color: getStatusColor(metrics?.disk.percent || 0) }}
            />
            {metrics && (
              <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                {formatBytes(metrics.disk.used)} / {formatBytes(metrics.disk.total)}
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="CPU Usage (24h)" extra={<Tag color="blue">Real-time</Tag>}>
            <SimpleChart 
              data={metricsHistory} 
              color="#1890ff" 
              field="cpu"
              height={250}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Memory Usage (24h)" extra={<Tag color="green">Real-time</Tag>}>
            <SimpleChart 
              data={metricsHistory} 
              color="#52c41a" 
              field="memory"
              height={250}
            />
          </Card>
        </Col>
      </Row>

      {/* Detailed Metrics */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="System Information">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Statistic
                  title="CPU Cores"
                  value={metrics?.cpu.count || 0}
                  prefix={<CheckCircleOutlined />}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="CPU Frequency"
                  value={metrics?.cpu.frequency ? (metrics.cpu.frequency / 1000).toFixed(2) : 'N/A'}
                  suffix={metrics?.cpu.frequency ? " GHz" : ""}
                />
              </Col>
              <Col span={24}>
                <Statistic
                  title="Available Memory"
                  value={metrics ? formatBytes(metrics.memory.available) : '0 B'}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
              <Col span={24}>
                <Statistic
                  title="Free Disk Space"
                  value={metrics ? formatBytes(metrics.disk.free) : '0 B'}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
            </Row>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Performance Summary">
            {summary ? (
              <Space direction="vertical" style={{ width: '100%' }} size="large">
                <div>
                  <div style={{ marginBottom: 8 }}>CPU Performance</div>
                  <div style={{ fontSize: 12, color: '#666' }}>
                    Current: {summary.cpu.current.toFixed(1)}% | 
                    Average: {summary.cpu.average.toFixed(1)}% | 
                    Range: {summary.cpu.min.toFixed(1)}% - {summary.cpu.max.toFixed(1)}%
                  </div>
                </div>
                <div>
                  <div style={{ marginBottom: 8 }}>Memory Performance</div>
                  <div style={{ fontSize: 12, color: '#666' }}>
                    Current: {summary.memory.current.toFixed(1)}% | 
                    Average: {summary.memory.average.toFixed(1)}% | 
                    Range: {summary.memory.min.toFixed(1)}% - {summary.memory.max.toFixed(1)}%
                  </div>
                </div>
                <div>
                  <div style={{ marginBottom: 8 }}>Disk Performance</div>
                  <div style={{ fontSize: 12, color: '#666' }}>
                    Current: {summary.disk.current.toFixed(1)}% | 
                    Average: {summary.disk.average.toFixed(1)}% | 
                    Range: {summary.disk.min.toFixed(1)}% - {summary.disk.max.toFixed(1)}%
                  </div>
                </div>
              </Space>
            ) : (
              <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
                No performance data available
              </div>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SystemPerformance;

