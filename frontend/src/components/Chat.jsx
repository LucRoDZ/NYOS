import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Plus, Trash2, MessageSquare } from 'lucide-react';
import { api } from '../api';

function parseMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br/>');
}

export default function Chat() {
  const [conversations, setConversations] = useState([]);
  const [currentConvId, setCurrentConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => { loadConversations(); }, []);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  async function loadConversations() {
    try {
      const convs = await api.getConversations();
      setConversations(convs);
      if (convs.length > 0 && !currentConvId) selectConversation(convs[0].id);
    } catch (e) { console.error(e); }
  }

  async function selectConversation(convId) {
    setCurrentConvId(convId);
    try {
      const history = await api.getChatHistory(convId);
      setMessages(history);
    } catch (e) { setMessages([]); }
  }

  async function createNewConversation() {
    try {
      const conv = await api.createConversation();
      setConversations(prev => [conv, ...prev]);
      setCurrentConvId(conv.id);
      setMessages([]);
    } catch (e) { console.error(e); }
  }

  async function deleteConversation(convId) {
    try {
      await api.deleteConversation(convId);
      setConversations(prev => prev.filter(c => c.id !== convId));
      if (currentConvId === convId) { setCurrentConvId(null); setMessages([]); }
    } catch (e) { console.error(e); }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!input.trim() || loading) return;
    let convId = currentConvId;
    if (!convId) {
      const conv = await api.createConversation();
      setConversations(prev => [conv, ...prev]);
      convId = conv.id;
      setCurrentConvId(convId);
    }
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    try {
      const response = await api.chat(convId, input);
      setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
      loadConversations();
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Erreur de connexion." }]);
    } finally { setLoading(false); }
  }

  const suggestions = ["Quel est l'état général ?", "Tendances inquiétantes ?", "Plaintes clients", "Performance Press-A"];

  return (
    <div className="flex h-[calc(100vh-180px)] gap-4">
      <div className="w-64 bg-white rounded-xl border border-gray-200 flex flex-col">
        <div className="p-3 border-b border-gray-200">
          <button onClick={createNewConversation} className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
            <Plus size={18} /> Nouvelle conversation
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {conversations.map(conv => (
            <div key={conv.id} className={`group flex items-center gap-2 p-2 rounded-lg cursor-pointer ${currentConvId === conv.id ? 'bg-primary-100' : 'hover:bg-gray-100'}`} onClick={() => selectConversation(conv.id)}>
              <MessageSquare size={16} className="text-gray-400 flex-shrink-0" />
              <span className="flex-1 text-sm truncate">{conv.title}</span>
              <button onClick={(e) => { e.stopPropagation(); deleteConversation(conv.id); }} className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded">
                <Trash2 size={14} className="text-red-500" />
              </button>
            </div>
          ))}
          {conversations.length === 0 && <p className="text-sm text-gray-400 text-center py-4">Aucune conversation</p>}
        </div>
      </div>

      <div className="flex-1 bg-white rounded-xl border border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="font-semibold text-gray-900 flex items-center gap-2"><Bot className="text-primary-600" size={20} /> Assistant NYOS</h2>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-8">
              <Bot className="mx-auto text-gray-300 mb-4" size={64} />
              <p className="text-gray-500 mb-6">Commencez par poser une question</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {suggestions.map((s, i) => (<button key={i} onClick={() => setInput(s)} className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200">{s}</button>))}
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'user' ? 'bg-primary-600' : 'bg-gray-200'}`}>
                {msg.role === 'user' ? <User size={16} className="text-white" /> : <Bot size={16} className="text-gray-600" />}
              </div>
              <div className={`max-w-[70%] rounded-xl px-4 py-3 ${msg.role === 'user' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
                <div dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.content) }} />
              </div>
            </div>
          ))}
          {loading && (<div className="flex gap-3"><div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center"><Bot size={16} className="text-gray-600" /></div><div className="bg-gray-100 rounded-xl px-4 py-3"><Loader2 className="animate-spin text-gray-500" size={20} /></div></div>)}
          <div ref={messagesEndRef} />
        </div>
        <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
          <div className="flex gap-2">
            <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Posez une question..." className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" disabled={loading} />
            <button type="submit" disabled={loading || !input.trim()} className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"><Send size={20} /></button>
          </div>
        </form>
      </div>
    </div>
  );
}
