/**
 * AI Assistant Page
 * AI 分析助手页面 - 类似 ChatGPT 的对话界面
 */
import React, { useState, useEffect, useRef } from 'react';
import {
  Card,
  Input,
  Button,
  Space,
  Typography,
  Avatar,
  Spin,
  message,
  Tag,
  Tooltip,
  Empty
} from 'antd';
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  DeleteOutlined,
  PlusOutlined,
  ThunderboltOutlined
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { streamChatMessage, createNewSession } from '../../services/chatService';

const { TextArea } = Input;
const { Title, Text } = Typography;

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const AIAssistant: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [streamingContent, setStreamingContent] = useState('');

  // 建议的快捷问题
  const suggestedQuestions = [
    '我的投资组合风险大吗？',
    '现在市场情绪怎么样？',
    '分析一下我的持仓表现',
    '哪些预警快要触发了？',
    '给我一些投资建议'
  ];

  // 初始化会话
  useEffect(() => {
    const initSession = async () => {
      try {
        const newSessionId = await createNewSession();
        setSessionId(newSessionId);
        
        // 添加欢迎消息
        setMessages([{
          role: 'assistant',
          content: `👋 您好！我是 **AI 分析助手**，专门帮助您分析投资组合和市场趋势。

我可以帮您：
- 📊 分析投资组合风险
- 📈 评估市场情绪和趋势
- 💰 计算收益和表现
- ⚠️ 监控预警状态
- 💡 提供投资洞察

有什么我可以帮您分析的吗？`,
          timestamp: new Date()
        }]);
      } catch (error) {
        message.error('初始化会话失败');
      }
    };

    initSession();
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  // 发送消息
  const handleSend = async (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText || loading) return;

    // 添加用户消息
    const userMessage: Message = {
      role: 'user',
      content: messageText,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    // 添加空的 AI 消息用于流式更新
    const aiMessage: Message = {
      role: 'assistant',
      content: '',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, aiMessage]);

    try {
      let fullContent = '';

      await streamChatMessage(
        messageText,
        sessionId,
        // onChunk
        (chunk) => {
          fullContent += chunk;
          setStreamingContent(fullContent);
        },
        // onComplete
        () => {
          setMessages(prev => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1] = {
              ...newMessages[newMessages.length - 1],
              content: fullContent
            };
            return newMessages;
          });
          setStreamingContent('');
          setLoading(false);
        },
        // onError
        (error) => {
          message.error(`发送消息失败: ${error}`);
          setMessages(prev => prev.slice(0, -1)); // 移除空的 AI 消息
          setStreamingContent('');
          setLoading(false);
        }
      );
    } catch (error: any) {
      message.error(`发送消息失败: ${error.message}`);
      setMessages(prev => prev.slice(0, -1));
      setLoading(false);
    }
  };

  // 新建对话
  const handleNewChat = async () => {
    try {
      const newSessionId = await createNewSession();
      setSessionId(newSessionId);
      setMessages([{
        role: 'assistant',
        content: '👋 开始新的对话！有什么我可以帮您分析的吗？',
        timestamp: new Date()
      }]);
      message.success('已开始新对话');
    } catch (error) {
      message.error('创建新对话失败');
    }
  };

  // 渲染消息
  const renderMessage = (msg: Message, index: number) => {
    const isUser = msg.role === 'user';
    const isLastAIMessage = msg.role === 'assistant' && index === messages.length - 1;
    const displayContent = isLastAIMessage && streamingContent ? streamingContent : msg.content;

    return (
      <div
        key={index}
        style={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          marginBottom: '16px',
          animation: 'fadeIn 0.3s ease-in'
        }}
      >
        <Space align="start" direction={isUser ? 'horizontal' : 'horizontal-reverse'} style={{ maxWidth: '75%' }}>
          {/* Avatar */}
          <Avatar
            icon={isUser ? <UserOutlined /> : <RobotOutlined />}
            style={{
              backgroundColor: isUser ? '#1890ff' : '#52c41a',
              order: isUser ? 1 : 0
            }}
          />
          
          {/* Message Content */}
          <Card
            style={{
              backgroundColor: isUser ? '#e6f7ff' : '#f6ffed',
              borderRadius: '12px',
              border: 'none',
              boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
            }}
            bodyStyle={{ padding: '12px 16px' }}
          >
            {isUser ? (
              <Text>{displayContent}</Text>
            ) : (
              <div className="markdown-content">
                <ReactMarkdown>{displayContent}</ReactMarkdown>
                {isLastAIMessage && loading && (
                  <Spin size="small" style={{ marginLeft: '8px' }} />
                )}
              </div>
            )}
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#999' }}>
              {msg.timestamp.toLocaleTimeString()}
            </div>
          </Card>
        </Space>
      </div>
    );
  };

  return (
    <div style={{ height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column', padding: '24px', background: '#f0f2f5' }}>
      {/* Header */}
      <Card style={{ marginBottom: '16px' }} bodyStyle={{ padding: '16px 24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space>
            <RobotOutlined style={{ fontSize: '24px', color: '#52c41a' }} />
            <Title level={4} style={{ margin: 0 }}>AI 分析助手</Title>
            <Tag color="green">在线</Tag>
          </Space>
          <Button
            icon={<PlusOutlined />}
            onClick={handleNewChat}
            disabled={loading}
          >
            新对话
          </Button>
        </div>
      </Card>

      {/* Messages Area */}
      <Card
        style={{
          flex: 1,
          marginBottom: '16px',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column'
        }}
        bodyStyle={{
          padding: '24px',
          flex: 1,
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {messages.length === 0 ? (
          <Empty description="暂无消息" />
        ) : (
          <div style={{ flex: 1 }}>
            {messages.map((msg, index) => renderMessage(msg, index))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </Card>

      {/* Quick Actions */}
      {messages.length <= 1 && (
        <Card style={{ marginBottom: '16px' }} bodyStyle={{ padding: '16px' }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space>
              <ThunderboltOutlined style={{ color: '#faad14' }} />
              <Text strong>快捷提问：</Text>
            </Space>
            <Space wrap>
              {suggestedQuestions.map((q, index) => (
                <Tag
                  key={index}
                  style={{ cursor: 'pointer', padding: '4px 12px' }}
                  onClick={() => handleSend(q)}
                  color="blue"
                >
                  {q}
                </Tag>
              ))}
            </Space>
          </Space>
        </Card>
      )}

      {/* Input Area */}
      <Card bodyStyle={{ padding: '16px' }}>
        <Space.Compact style={{ width: '100%' }}>
          <TextArea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onPressEnter={(e) => {
              if (!e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="输入您的问题... (Shift+Enter 换行)"
            autoSize={{ minRows: 1, maxRows: 4 }}
            disabled={loading}
            style={{ flex: 1 }}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={() => handleSend()}
            loading={loading}
            disabled={!input.trim()}
            style={{ height: 'auto' }}
          >
            发送
          </Button>
        </Space.Compact>
        <Text type="secondary" style={{ fontSize: '12px', marginTop: '8px', display: 'block' }}>
          💡 提示：此界面仅提供分析功能，不能执行买卖或修改操作
        </Text>
      </Card>

      {/* Custom Styles */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .markdown-content {
          line-height: 1.6;
        }

        .markdown-content h1, .markdown-content h2, .markdown-content h3 {
          margin-top: 16px;
          margin-bottom: 8px;
        }

        .markdown-content ul, .markdown-content ol {
          margin-left: 20px;
        }

        .markdown-content code {
          background: #f5f5f5;
          padding: 2px 6px;
          border-radius: 3px;
          font-family: 'Courier New', monospace;
        }

        .markdown-content strong {
          color: #262626;
          font-weight: 600;
        }
      `}</style>
    </div>
  );
};

export default AIAssistant;

