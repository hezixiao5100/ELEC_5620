import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Tag,
  Space,
  Button,
  message,
  Descriptions,
  Popover,
  Typography,
  Empty,
} from 'antd';
import {
  ReloadOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import api from '@/services/api';

const { Text } = Typography;

interface Task {
  id: string;
  name: string;
  state: string;
  worker?: string;
  args?: any[];
  kwargs?: any;
  time_start?: number;
  eta?: string;
}

const BackgroundTasks: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [workers, setWorkers] = useState<string[]>([]);
  const [registeredTasks, setRegisteredTasks] = useState<string[]>([]);
  const [taskStatus, setTaskStatus] = useState<any>(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [tasksRes, statusRes] = await Promise.all([
        api.get('/admin/tasks/list'),
        api.get('/tasks/status').catch(() => null),
      ]);

      setTasks(tasksRes.data.tasks || []);
      setWorkers(tasksRes.data.workers || []);
      setRegisteredTasks(tasksRes.data.registered_tasks || []);
      
      if (statusRes) {
        setTaskStatus(statusRes.data);
      }
    } catch (error: any) {
      if (error.response?.status !== 404) {
        message.error('Failed to load tasks');
      }
    } finally {
      setLoading(false);
    }
  };

  const getStateColor = (state: string) => {
    switch (state.toUpperCase()) {
      case 'SUCCESS':
      case 'COMPLETED':
        return 'green';
      case 'FAILURE':
      case 'FAILED':
        return 'red';
      case 'PENDING':
      case 'SCHEDULED':
      case 'RESERVED':
        return 'blue';
      case 'ACTIVE':
      case 'PROGRESS':
        return 'orange';
      default:
        return 'default';
    }
  };

  const getStateIcon = (state: string) => {
    switch (state.toUpperCase()) {
      case 'SUCCESS':
      case 'COMPLETED':
        return <CheckCircleOutlined />;
      case 'FAILURE':
      case 'FAILED':
        return <CloseCircleOutlined />;
      case 'PENDING':
      case 'SCHEDULED':
        return <ClockCircleOutlined />;
      case 'ACTIVE':
      case 'PROGRESS':
        return <LoadingOutlined />;
      default:
        return <InfoCircleOutlined />;
    }
  };

  const formatTaskName = (name: string) => {
    return name.split('.').pop() || name;
  };

  const columns = [
    {
      title: 'Task ID',
      dataIndex: 'id',
      key: 'id',
      width: 150,
      render: (id: string) => (
        <Text code style={{ fontSize: 11 }}>
          {id?.substring(0, 8)}...
        </Text>
      ),
    },
    {
      title: 'Task Name',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => (
        <Popover
          content={<Text code>{name}</Text>}
          title="Full Task Name"
        >
          <Text>{formatTaskName(name)}</Text>
        </Popover>
      ),
    },
    {
      title: 'State',
      dataIndex: 'state',
      key: 'state',
      render: (state: string) => (
        <Tag color={getStateColor(state)} icon={getStateIcon(state)}>
          {state}
        </Tag>
      ),
      filters: [
        { text: 'ACTIVE', value: 'ACTIVE' },
        { text: 'SCHEDULED', value: 'SCHEDULED' },
        { text: 'RESERVED', value: 'RESERVED' },
        { text: 'SUCCESS', value: 'SUCCESS' },
        { text: 'FAILURE', value: 'FAILURE' },
      ],
      onFilter: (value: any, record: Task) => record.state === value,
    },
    {
      title: 'Worker',
      dataIndex: 'worker',
      key: 'worker',
      render: (worker: string) => worker || 'N/A',
    },
    {
      title: 'Started',
      dataIndex: 'time_start',
      key: 'time_start',
      render: (time: number) => {
        if (!time) return 'N/A';
        return new Date(time * 1000).toLocaleString();
      },
    },
    {
      title: 'ETA',
      dataIndex: 'eta',
      key: 'eta',
      render: (eta: string) => {
        if (!eta) return 'N/A';
        return new Date(eta).toLocaleString();
      },
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ margin: 0 }}>Background Tasks</h1>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadData} loading={loading}>
            Refresh
          </Button>
        </Space>
      </div>

      {/* System Status */}
      {taskStatus && (
        <Card style={{ marginBottom: 24 }}>
          <Descriptions title="Task System Status" column={3} bordered size="small">
            <Descriptions.Item label="Overall Status">
              <Tag color={taskStatus.status === 'healthy' ? 'green' : 'red'}>
                {taskStatus.status?.toUpperCase()}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Active Tasks">
              {taskStatus.active_tasks || 0}
            </Descriptions.Item>
            <Descriptions.Item label="Scheduled Tasks">
              {taskStatus.scheduled_tasks || 0}
            </Descriptions.Item>
            <Descriptions.Item label="Registered Tasks">
              {taskStatus.registered_tasks || 0}
            </Descriptions.Item>
            <Descriptions.Item label="Workers" span={2}>
              {taskStatus.workers?.length || 0} worker(s)
            </Descriptions.Item>
          </Descriptions>
        </Card>
      )}

      {/* Workers Info */}
      {workers.length > 0 && (
        <Card style={{ marginBottom: 24 }} title="Active Workers">
          <Space wrap>
            {workers.map((worker, index) => (
              <Tag key={index} color="blue">
                {worker}
              </Tag>
            ))}
          </Space>
        </Card>
      )}

      {/* Tasks Table */}
      <Card
        title={`Tasks (${tasks.length})`}
        extra={
          <Space>
            <Text type="secondary">
              Auto-refresh every 10 seconds
            </Text>
          </Space>
        }
      >
        {tasks.length === 0 ? (
          <Empty
            description={
              <div>
                <p>No active tasks found</p>
                <Text type="secondary">
                  {registeredTasks.length > 0 && (
                    <div>
                      <p>Registered tasks:</p>
                      <Space wrap>
                        {registeredTasks.slice(0, 10).map((task, index) => (
                          <Tag key={index} color="default">
                            {formatTaskName(task)}
                          </Tag>
                        ))}
                        {registeredTasks.length > 10 && (
                          <Tag>+{registeredTasks.length - 10} more</Tag>
                        )}
                      </Space>
                    </div>
                  )}
                </Text>
              </div>
            }
          />
        ) : (
          <Table
            dataSource={tasks}
            columns={columns}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 20,
              showTotal: (total) => `Total ${total} tasks`,
            }}
          />
        )}
      </Card>

      {/* Registered Tasks Info */}
      {registeredTasks.length > 0 && (
        <Card title="Registered Tasks" style={{ marginTop: 24 }}>
          <Space wrap>
            {registeredTasks.map((task, index) => (
              <Tag key={index} color="default">
                {formatTaskName(task)}
              </Tag>
            ))}
          </Space>
        </Card>
      )}
    </div>
  );
};

export default BackgroundTasks;

