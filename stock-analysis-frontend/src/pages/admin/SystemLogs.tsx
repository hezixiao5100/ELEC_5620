import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Input,
  Select,
  Space,
  Tag,
  message,
  Button,
  Typography,
  Row,
  Col,
} from 'antd';
import {
  ReloadOutlined,
  SearchOutlined,
  ClearOutlined,
} from '@ant-design/icons';
import api from '@/services/api';

const { Option } = Select;
const { Text } = Typography;
const { Search } = Input;

interface LogEntry {
  timestamp: string;
  level: string;
  logger: string;
  message: string;
  module: string;
  function: string;
  line: number;
  raw: string;
}

const SystemLogs: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 50,
  });
  const [filters, setFilters] = useState({
    level: undefined as string | undefined,
    search: undefined as string | undefined,
  });

  useEffect(() => {
    loadLogs();
  }, [pagination.current, pagination.pageSize, filters.level]);

  const loadLogs = async () => {
    try {
      setLoading(true);
      const params: any = {
        limit: pagination.pageSize,
        offset: (pagination.current - 1) * pagination.pageSize,
      };

      if (filters.level) {
        params.level = filters.level;
      }

      if (filters.search) {
        params.search = filters.search;
      }

      const response = await api.get('/admin/logs', { params });
      setLogs(response.data.logs || []);
      setTotal(response.data.total || 0);
    } catch (error) {
      message.error('Failed to load logs');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setFilters({ ...filters, search: value || undefined });
    setPagination({ ...pagination, current: 1 });
  };

  const handleLevelFilter = (level: string) => {
    setFilters({ ...filters, level: level || undefined });
    setPagination({ ...pagination, current: 1 });
  };

  const clearFilters = () => {
    setFilters({ level: undefined, search: undefined });
    setPagination({ ...pagination, current: 1 });
  };

  const getLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'ERROR':
        return 'red';
      case 'WARNING':
      case 'WARN':
        return 'orange';
      case 'INFO':
        return 'blue';
      case 'DEBUG':
        return 'default';
      default:
        return 'default';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  const columns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (timestamp: string) => (
        <Text style={{ fontSize: 12 }}>{formatTimestamp(timestamp)}</Text>
      ),
      sorter: (a: LogEntry, b: LogEntry) =>
        a.timestamp.localeCompare(b.timestamp),
    },
    {
      title: 'Level',
      dataIndex: 'level',
      key: 'level',
      width: 100,
      render: (level: string) => (
        <Tag color={getLevelColor(level)}>{level}</Tag>
      ),
      filters: [
        { text: 'ERROR', value: 'ERROR' },
        { text: 'WARNING', value: 'WARNING' },
        { text: 'INFO', value: 'INFO' },
        { text: 'DEBUG', value: 'DEBUG' },
      ],
      onFilter: (value: any, record: LogEntry) =>
        record.level.toUpperCase() === value,
    },
    {
      title: 'Logger',
      dataIndex: 'logger',
      key: 'logger',
      width: 120,
      render: (logger: string) => (
        <Text code style={{ fontSize: 11 }}>
          {logger}
        </Text>
      ),
    },
    {
      title: 'Message',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
      render: (message: string, record: LogEntry) => (
        <div>
          <Text>{message}</Text>
          {record.module && (
            <Text type="secondary" style={{ fontSize: 11, marginLeft: 8 }}>
              [{record.module}.{record.function}:{record.line}]
            </Text>
          )}
        </div>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ margin: 0 }}>System Logs</h1>
        <Button icon={<ReloadOutlined />} onClick={loadLogs} loading={loading}>
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={12} md={8}>
            <Search
              placeholder="Search logs..."
              allowClear
              enterButton={<SearchOutlined />}
              onSearch={handleSearch}
              style={{ width: '100%' }}
            />
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Select
              placeholder="Filter by level"
              allowClear
              style={{ width: '100%' }}
              value={filters.level}
              onChange={handleLevelFilter}
            >
              <Option value="ERROR">ERROR</Option>
              <Option value="WARNING">WARNING</Option>
              <Option value="INFO">INFO</Option>
              <Option value="DEBUG">DEBUG</Option>
            </Select>
          </Col>
          <Col xs={24} sm={24} md={8}>
            <Button icon={<ClearOutlined />} onClick={clearFilters}>
              Clear Filters
            </Button>
          </Col>
        </Row>
      </Card>

      {/* Logs Table */}
      <Card>
        <Table
          dataSource={logs}
          columns={columns}
          rowKey={(record, index) => `${record.timestamp}-${index}`}
          loading={loading}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: total,
            showSizeChanger: true,
            showTotal: (total) => `Total ${total} log entries`,
            pageSizeOptions: ['20', '50', '100', '200'],
            onChange: (page, pageSize) => {
              setPagination({ current: page, pageSize: pageSize || 50 });
            },
          }}
          scroll={{ x: 'max-content' }}
        />
      </Card>
    </div>
  );
};

export default SystemLogs;

