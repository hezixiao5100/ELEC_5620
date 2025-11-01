import React, { useState, useEffect } from 'react';
import { Card, Form, Select, Button, message, Alert, Space, Typography, Spin } from 'antd';
import { SettingOutlined, CheckCircleOutlined } from '@ant-design/icons';
import api from '@/services/api';

const { Title, Text } = Typography;

interface ModelOption {
  value: string;
  label: string;
}

const Settings: React.FC = () => {
  const [model, setModel] = useState<string>('gpt-4o-mini');
  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(true);
  const [availableModels, setAvailableModels] = useState<ModelOption[]>([]);

  useEffect(() => {
    fetchCurrentModel();
  }, []);

  const fetchCurrentModel = async () => {
    setFetchLoading(true);
    try {
      const response = await api.get('/admin/config/model');
      setModel(response.data.model);
      setAvailableModels(response.data.available_models);
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to fetch model configuration');
    } finally {
      setFetchLoading(false);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await api.put('/admin/config/model', { model });
      message.success({
        content: 'Global AI model updated successfully! All users will use this model.',
        duration: 3,
        icon: <CheckCircleOutlined style={{ color: '#52c41a' }} />
      });
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'Failed to update model');
    } finally {
      setLoading(false);
    }
  };

  if (fetchLoading) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Spin size="large" tip="Loading settings..." />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card 
        title={
          <Space>
            <SettingOutlined />
            <span>System Settings - AI Model Configuration</span>
          </Space>
        }
        style={{ maxWidth: 800 }}
      >
        <Alert
          message="Administrator Only"
          description="Changes made here will affect ALL users (Investors, Advisors, and Admins). The selected model will be used for all AI analysis and chat features across the entire system."
          type="warning"
          showIcon
          style={{ marginBottom: 24 }}
        />

        <Form layout="vertical">
          <Form.Item 
            label={
              <Space direction="vertical" size={0}>
                <Text strong style={{ fontSize: '16px' }}>Global AI Model</Text>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  Select the OpenAI model that will be used system-wide
                </Text>
              </Space>
            }
          >
            <Select
              value={model}
              onChange={setModel}
              size="large"
              options={availableModels}
              style={{ width: '100%' }}
            />
            <div style={{ marginTop: '12px' }}>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                Current model: <Text code strong>{model}</Text>
              </Text>
            </div>
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              size="large"
              onClick={handleSave}
              loading={loading}
              icon={<CheckCircleOutlined />}
            >
              Update Global Model Configuration
            </Button>
          </Form.Item>
        </Form>

        <div style={{ marginTop: '32px', padding: '20px', background: '#f5f5f5', borderRadius: '8px' }}>
          <Title level={5}>Model Descriptions:</Title>
          <ul style={{ marginBottom: 0, lineHeight: '2' }}>
            <li>
              <Text strong>GPT-4o Mini:</Text> Fast and cost-effective, suitable for most analysis tasks. 
              <Text type="secondary"> (Recommended for daily use)</Text>
            </li>
            <li>
              <Text strong>GPT-4o:</Text> More powerful and accurate, better for complex financial analysis
            </li>
            <li>
              <Text strong>GPT-3.5 Turbo:</Text> Classic model with balanced performance and speed
            </li>
            <li>
              <Text strong>GPT-4 Turbo:</Text> Most advanced model with enhanced reasoning capabilities
            </li>
            <li>
              <Text strong>GPT-4:</Text> Premium model with highest quality analysis
            </li>
          </ul>
        </div>

        <Alert
          message="Note"
          description="Model changes take effect immediately for new chat sessions. Existing chat sessions may need to be restarted to use the new model."
          type="info"
          showIcon
          style={{ marginTop: 16 }}
        />
      </Card>
    </div>
  );
};

export default Settings;

