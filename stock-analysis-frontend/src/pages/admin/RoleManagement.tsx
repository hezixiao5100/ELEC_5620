import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  message,
  Modal,
  Form,
  Select,
  Descriptions,
  Divider,
  Typography,
} from 'antd';
import {
  SafetyOutlined,
  UserOutlined,
  EditOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import api from '@/services/api';
import { UserRole } from '@/types';

const { Option } = Select;
const { Title, Paragraph } = Typography;

interface RoleInfo {
  role: UserRole;
  name: string;
  description: string;
  permissions: string[];
  userCount: number;
}

const RoleManagement: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState<any[]>([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<any | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/admin/users');
      setUsers(response.data);
    } catch (error) {
      message.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleEditRole = (user: any) => {
    setEditingUser(user);
    form.setFieldsValue({ role: user.role });
    setIsModalVisible(true);
  };

  const handleSubmit = async (values: any) => {
    try {
      if (editingUser) {
        await api.put(`/admin/users/${editingUser.id}`, {
          ...editingUser,
          role: values.role,
        });
        message.success('User role updated successfully');
      }
      setIsModalVisible(false);
      form.resetFields();
      setEditingUser(null);
      loadUsers();
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to update role');
    }
  };

  const getRoleColor = (role: UserRole) => {
    switch (role) {
      case 'ADMIN':
        return 'red';
      case 'ADVISOR':
        return 'blue';
      case 'INVESTOR':
        return 'green';
      default:
        return 'default';
    }
  };

  const roleDefinitions: RoleInfo[] = [
    {
      role: UserRole.ADMIN,
      name: 'Administrator',
      description: 'Full system access with all permissions',
      permissions: [
        'User Management',
        'Role Management',
        'System Configuration',
        'Data Access',
        'Report Generation',
        'Alert Management',
        'System Monitoring',
      ],
      userCount: users.filter((u) => u.role === UserRole.ADMIN || u.role === 'ADMIN').length,
    },
    {
      role: UserRole.ADVISOR,
      name: 'Financial Advisor',
      description: 'Access to client portfolios and advisory features',
      permissions: [
        'View Client Portfolios',
        'Generate Reports',
        'Create Investment Recommendations',
        'Monitor Client Alerts',
        'Chat with AI Assistant',
      ],
      userCount: users.filter((u) => u.role === UserRole.ADVISOR || u.role === 'ADVISOR').length,
    },
    {
      role: UserRole.INVESTOR,
      name: 'Investor',
      description: 'Basic access for personal portfolio management',
      permissions: [
        'View Own Portfolio',
        'Track Stocks',
        'Set Alerts',
        'View Reports',
        'Chat with AI Assistant',
      ],
      userCount: users.filter((u) => u.role === UserRole.INVESTOR || u.role === 'INVESTOR').length,
    },
  ];

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'Username',
      dataIndex: 'username',
      key: 'username',
      render: (username: string) => (
        <Space>
          <UserOutlined />
          {username}
        </Space>
      ),
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: 'Current Role',
      dataIndex: 'role',
      key: 'role',
      render: (role: UserRole) => (
        <Tag color={getRoleColor(role)}>{role}</Tag>
      ),
      filters: [
        { text: 'ADMIN', value: 'ADMIN' },
        { text: 'ADVISOR', value: 'ADVISOR' },
        { text: 'INVESTOR', value: 'INVESTOR' },
      ],
      onFilter: (value: any, record: any) => record.role === value,
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'status',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? (
            <>
              <CheckCircleOutlined /> Active
            </>
          ) : (
            <>
              <CloseCircleOutlined /> Inactive
            </>
          )}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: any) => (
        <Button
          type="link"
          icon={<EditOutlined />}
          onClick={() => handleEditRole(record)}
        >
          Edit Role
        </Button>
      ),
    },
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: 8 }}>
        Role Management
      </Title>
      <Paragraph type="secondary" style={{ marginBottom: 24 }}>
        Manage user roles and permissions.
      </Paragraph>

      {/* Role Definitions */}
      <Card title="Role Definitions" style={{ marginBottom: 24 }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {roleDefinitions.map((roleInfo) => (
            <Card
              key={roleInfo.role}
              type="inner"
              title={
                <Space>
                  <SafetyOutlined />
                  <Tag color={getRoleColor(roleInfo.role)}>
                    {roleInfo.role}
                  </Tag>
                  <span>{roleInfo.name}</span>
                </Space>
              }
              extra={
                <Tag color="blue">
                  {roleInfo.userCount} {roleInfo.userCount === 1 ? 'user' : 'users'}
                </Tag>
              }
            >
              <Descriptions column={1} size="small">
                <Descriptions.Item label="Description">
                  {roleInfo.description}
                </Descriptions.Item>
                <Descriptions.Item label="Permissions">
                  <Space wrap>
                    {roleInfo.permissions.map((permission, index) => (
                      <Tag key={index} color="geekblue">
                        {permission}
                      </Tag>
                    ))}
                  </Space>
                </Descriptions.Item>
              </Descriptions>
            </Card>
          ))}
        </Space>
      </Card>

      <Divider />

      {/* User Role Management Table */}
      <Card
        title={
          <Space>
            <UserOutlined />
            <span>User Role Assignment</span>
          </Space>
        }
      >
        <Table
          dataSource={users}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showTotal: (total) => `Total ${total} users`,
          }}
        />
      </Card>

      {/* Edit Role Modal */}
      <Modal
        title="Edit User Role"
        open={isModalVisible}
        onCancel={() => {
          setIsModalVisible(false);
          form.resetFields();
          setEditingUser(null);
        }}
        footer={null}
        width={600}
      >
        {editingUser && (
          <div style={{ marginBottom: 24 }}>
            <Descriptions column={1} size="small" bordered>
              <Descriptions.Item label="Username">
                {editingUser.username}
              </Descriptions.Item>
              <Descriptions.Item label="Email">
                {editingUser.email}
              </Descriptions.Item>
              <Descriptions.Item label="Current Role">
                <Tag color={getRoleColor(editingUser.role)}>
                  {editingUser.role}
                </Tag>
              </Descriptions.Item>
            </Descriptions>
          </div>
        )}

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="role"
            label="Select New Role"
            rules={[{ required: true, message: 'Please select a role' }]}
          >
            <Select placeholder="Select role" size="large">
              <Option value="INVESTOR">
                <Space>
                  <Tag color="green">INVESTOR</Tag>
                  <span>Investor - Basic portfolio access</span>
                </Space>
              </Option>
              <Option value="ADVISOR">
                <Space>
                  <Tag color="blue">ADVISOR</Tag>
                  <span>Financial Advisor - Client management</span>
                </Space>
              </Option>
              <Option value="ADMIN">
                <Space>
                  <Tag color="red">ADMIN</Tag>
                  <span>Administrator - Full system access</span>
                </Space>
              </Option>
            </Select>
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={() => setIsModalVisible(false)}>
                Cancel
              </Button>
              <Button type="primary" htmlType="submit">
                Update Role
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default RoleManagement;

