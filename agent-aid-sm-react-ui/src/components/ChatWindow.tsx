import React, { useState, useRef, useEffect } from 'react';
import { Send, Image as ImageIcon, Search, Loader2, X, Volume2 } from 'lucide-react';
import { sendChat } from '../services/api';
import type { ChatResponse } from '../types';

interface ChatWindowProps {
  role: string;
  externalQuery?: string;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ role, externalQuery }) => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<{ role: string; text: string; isAI: boolean, voice?: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [deepSearch, setDeepSearch] = useState(false);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (externalQuery) {
        setQuery(externalQuery);
        triggerChat(externalQuery);
    }
  }, [externalQuery]);

  const triggerChat = async (text: string) => {
    if (!text.trim() && !selectedImage) return;

    const userMessage = { role, text: text, isAI: false };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const result = await sendChat(text, role, deepSearch, selectedImage || undefined);
      setMessages(prev => [...prev, {
          role: 'AI',
          text: result.response,
          isAI: true,
          voice: result.voice_summary
      }]);
      setQuery('');
      setSelectedImage(null);
      setImagePreview(null);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'AI', text: 'Sorry, I encountered an error processing your request.', isAI: true }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    triggerChat(query);
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="fixed bottom-0 right-0 w-[400px] bg-white shadow-2xl rounded-tl-2xl border border-gray-200 flex flex-col max-h-[600px] z-50">
      <div className="p-4 border-b border-gray-200 bg-slate-900 text-white rounded-tl-2xl flex justify-between items-center">
        <div className="font-bold flex items-center">
            <Search className="w-4 h-4 mr-2" />
            AI Delivery Agent
        </div>
        <div className="flex items-center space-x-2">
            <label className="text-xs flex items-center cursor-pointer">
                <input
                    type="checkbox"
                    checked={deepSearch}
                    onChange={(e) => setDeepSearch(e.target.checked)}
                    className="mr-1"
                />
                Deep Research
            </label>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-[300px]">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-10">
            Ask me anything about your project's status, blockers, or metrics.
          </div>
        )}
        {messages.map((m, idx) => (
          <div key={idx} className={`flex flex-col ${m.isAI ? 'items-start' : 'items-end'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg ${
              m.isAI ? 'bg-gray-100 text-gray-800' : 'bg-blue-600 text-white'
            }`}>
              <div className="text-[10px] uppercase font-bold mb-1 opacity-70">{m.role}</div>
              <div className="text-sm whitespace-pre-wrap">{m.text}</div>
            </div>
            {m.isAI && m.voice && (
                <button
                    onClick={() => {
                        const utterance = new SpeechSynthesisUtterance(m.voice);
                        window.speechSynthesis.speak(utterance);
                    }}
                    className="mt-1 text-blue-600 flex items-center text-[10px] hover:underline"
                >
                    <Volume2 className="w-3 h-3 mr-1" /> Play Summary
                </button>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 p-3 rounded-lg">
              <Loader2 className="w-5 h-5 animate-spin text-gray-500" />
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-gray-200">
        {imagePreview && (
          <div className="relative inline-block mb-2">
            <img src={imagePreview} alt="Preview" className="h-20 w-20 object-cover rounded border" />
            <button
              onClick={() => { setSelectedImage(null); setImagePreview(null); }}
              className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 shadow-lg"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        )}
        <form onSubmit={handleSend} className="flex items-center space-x-2">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors"
          >
            <ImageIcon className="w-5 h-5" />
          </button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleImageSelect}
            className="hidden"
            accept="image/*"
          />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type your query..."
            className="flex-1 border border-gray-300 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
          />
          <button
            type="submit"
            disabled={loading}
            className="p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-md"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatWindow;
