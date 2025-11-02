import React, { useEffect, useState } from 'react';
import {
  Card,
  Form,
  Input,
  Switch,
  Button,
  InputNumber,
  message,
  Space,
  Divider,
  Typography,
  Row,
  Col,
  Select,
} from 'antd';
import {
  SaveOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import api from '@/services/api';

const { Option } = Select;
const { Title, Paragraph } = Typography;

interface SystemSettings {
  // Monitoring settings
  monitoring_enabled: boolean;
  metrics_collection_interval: number;
  log_retention_days: number;
  
  // Alert settings
  alert_check_interval: number;
  max_alerts_per_user: number;
  
  // Stock data settings
  stock_update_interval: number;
  news_update_interval: number;
  
  // System settings
  maintenance_mode: boolean;
  max_concurrent_tasks: number;
}

const Settings: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      // In a real implementation, this would fetch from the backend
      // For now, we'll use default values
      const defaultSettings: SystemSettings = {
        monitoring_enabled: true,
        metrics_collection_interval: 300, // 5 minutes
        log_retention_days: 30,
        alert_check_interval: 60, // 1 minute
        max_alerts_per_user: 100,
        stock_update_interval: 900, // 15 minutes
        news_update_interval: 3600, // 1 hour
        maintenance_mode: false,
        max_concurrent_tasks: 10,
      };

      form.setFieldsValue(defaultSettings);
    } catch (error) {
      message.error('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (values: SystemSettings) => {
    try {
      setSaving(true);
      // In a real implementation, this would save to the backend
      // await api.put('/admin/settings', values);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      message.success('Settings saved successfully');
    } catch (error) {
      message.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1 style={{ margin: 0 }}>System Settings</h1>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadSettings} loading={loading}>
            Reload
          </Button>
        </Space>
      </div>

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
        initialValues={{
          monitoring_enabled: true,
          metrics_collection_interval: 300,
          log_retention_days: 30,
          alert_check_interval: 60,
          max_alerts_per_user: 100,
          stock_update_interval: 900,
          news_update_interval: 3600,
          maintenance_mode: false,
          max_concurrent_tasks: 10,
        }}
      >
        {/* Monitoring Settings */}
        <Card title="Monitoring Settings" style={{ marginBottom: 24 }}>
          <Row gutter={[24, 0]}>
            <Col xs={24} lg={12}>
              <Form.Item
                name="monitoring_enabled"
                label="Enable System Monitoring"
                valuePropName="checked"
              >
                <Switch checkedChildren="Enabled" unCheckedChildren="Disabled" />
              </Form.Item>
            </Col>
            <Col xs={24} lg={12}>
              <Form.Item
                name="metrics_collection_interval"
                label="Metrics Collection Interval (seconds)"
                rules={[{ required: true, message: 'Please enter interval' }]}
              >
                <InputNumber min={60} max={3600} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} lg={12}>
              <Form.Item
                name="log_retention_days"
                label="Log Retention Period (days)"
                rules={[{ required: true, message: 'Please enter retention period' }]}
              >
                <InputNumber min={1} max={365} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* Alert Settings */}
        <Card title="Alert Settings" style={{ marginBottom: 24 }}>
          <Row gutter={[24, 0]}>
            <Col xs={24} lg={12}>
              <Form.Item
                name="alert_check_interval"
                label="Alert Check Interval (seconds)"
                rules={[{ required: true, message: 'Please enter interval' }]}
              >
                <InputNumber min={30} max={600} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} lg={12}>
              <Form.Item
                name="max_alerts_per_user"
                label="Maximum Alerts Per User"
                rules={[{ required: true, message: 'Please enter maximum alerts' }]}
              >
                <InputNumber min={1} max={1000} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* Data Update Settings */}
        <Card title="Data Update Settings" style={{ marginBottom: 24 }}>
          <Row gutter={[24, 0]}>
            <Col xs={24} lg={12}>
              <Form.Item
                name="stock_update_interval"
                label="Stock Data Update Interval (seconds)"
                rules={[{ required: true, message: 'Please enter interval' }]}
              >
                <InputNumber min={300} max={3600} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} lg={12}>
              <Form.Item
                name="news_update_interval"
                label="News Data Update Interval (seconds)"
                rules={[{ required: true, message: 'Please enter interval' }]}
              >
                <InputNumber min={600} max={7200} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* System Settings */}
        <Card title="System Settings" style={{ marginBottom: 24 }}>
          <Row gutter={[24, 0]}>
            <Col xs={24} lg={12}>
              <Form.Item
                name="maintenance_mode"
                label="Maintenance Mode"
                valuePropName="checked"
              >
                <Switch checkedChildren="Enabled" unCheckedChildren="Disabled" />
              </Form.Item>
              <Paragraph type="secondary" style={{ fontSize: 12 }}>
                When enabled, the system will be in maintenance mode and only admins can access it.
              </Paragraph>
            </Col>
            <Col xs={24} lg={12}>
              <Form.Item
                name="max_concurrent_tasks"
                label="Maximum Concurrent Tasks"
                rules={[{ required: true, message: 'Please enter maximum tasks' }]}
              >
                <InputNumber min={1} max={50} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* Action Buttons */}
        <Card>
          <Space>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              htmlType="submit"
              loading={saving}
              size="large"
            >
              Save Settings
            </Button>
            <Button onClick={loadSettings} disabled={loading || saving}>
              Reset
            </Button>
          </Space>
        </Card>
      </Form>
    </div>
  );
};

export default Settings;

