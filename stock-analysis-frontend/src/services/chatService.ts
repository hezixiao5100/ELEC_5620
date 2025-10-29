/**
 * Chat Service
 * AI 分析助手的前端服务
 */
import api from './api';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  function_name?: string;
  function_args?: any;
  metadata?: any;
}

export interface ChatSession {
  session_id: string;
  message_count: number;
  last_message_at?: string;
  first_message_at?: string;
}

export interface ChatHistory {
  session_id: string;
  messages: ChatMessage[];
}

/**
 * 发送消息（非流式）
 */
export const sendMessage = async (
  message: string,
  sessionId: string
): Promise<ChatMessage> => {
  const response = await api.post('/chat/message', {
    message,
    session_id: sessionId
  });
  return response.data;
};

/**
 * 流式发送消息（SSE）
 */
export const streamChatMessage = async (
  message: string,
  sessionId: string,
  onChunk: (content: string) => void,
  onComplete: () => void,
  onError: (error: string) => void
) => {
  try {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${api.defaults.baseURL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        message,
        session_id: sessionId
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('Response body reader not available');
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          
          try {
            const parsed = JSON.parse(data);
            
            if (parsed.type === 'content' && parsed.content) {
              onChunk(parsed.content);
            } else if (parsed.type === 'done') {
              onComplete();
              return;
            } else if (parsed.type === 'error') {
              onError(parsed.content || 'Unknown error');
              return;
            }
          } catch (e) {
            // Skip invalid JSON
            console.warn('Failed to parse SSE data:', data);
          }
        }
      }
    }
  } catch (error: any) {
    onError(error.message || 'Failed to stream message');
  }
};

/**
 * 获取所有会话列表
 */
export const getSessions = async (): Promise<ChatSession[]> => {
  const response = await api.get('/chat/sessions');
  return response.data;
};

/**
 * 获取会话历史
 */
export const getSessionHistory = async (sessionId: string): Promise<ChatHistory> => {
  const response = await api.get(`/chat/sessions/${sessionId}`);
  return response.data;
};

/**
 * 删除会话
 */
export const deleteSession = async (sessionId: string): Promise<void> => {
  await api.delete(`/chat/sessions/${sessionId}`);
};

/**
 * 创建新会话
 */
export const createNewSession = async (): Promise<string> => {
  const response = await api.post('/chat/sessions/new');
  return response.data.session_id;
};

