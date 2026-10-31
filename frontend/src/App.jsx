import { useEffect, useRef, useState } from "react";
import {
  deleteConversation,
  getMessages,
  listConversations,
  sendChat,
} from "./api/chat";
import Sidebar from "./components/Sidebar";
import "./App.css";

export default function App() {
  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const bottomRef = useRef(null);
  const latestOpen = useRef(null); // guards against slow, out-of-order responses

  async function refreshConversations() {
    const convs = await listConversations();
    setConversations(convs);
    return convs;
  }

  async function openConversation(id) {
    latestOpen.current = id;
    setActiveId(id);
    setMessages([]);
    setError("");
    setSidebarOpen(false);
    setLoadingMessages(true);
    try {
      const msgs = await getMessages(id);
      if (latestOpen.current === id) setMessages(msgs);
    } catch (err) {
      if (latestOpen.current === id) setError(err.message);
    } finally {
      if (latestOpen.current === id) setLoadingMessages(false);
    }
  }

  function handleNewChat() {
    latestOpen.current = null;
    setActiveId(null);
    setMessages([]);
    setError("");
    setLoadingMessages(false);
    setSidebarOpen(false);
  }

  useEffect(() => {
    (async () => {
      try {
        const convs = await refreshConversations();
        if (convs.length > 0) await openConversation(convs[0].id);
      } catch (err) {
        setError(err.message);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending, loadingMessages]);

  async function handleSend(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

    const previous = messages;
    setMessages([...previous, { role: "user", content: text }]);
    setInput("");
    setError("");
    setSending(true);

    try {
      const data = await sendChat(activeId, text);
      setMessages((m) => [...m, { role: "assistant", content: data.reply }]);
      if (activeId !== data.conversation_id) {
        latestOpen.current = data.conversation_id;
        setActiveId(data.conversation_id);
      }
      refreshConversations().catch(() => {}); // sidebar refresh must never undo a successful send
    } catch (err) {
      // The server saved nothing, so undo the optimistic message and return the text.
      setMessages(previous);
      setInput(text);
      setError(err.message);
    } finally {
      setSending(false);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete this conversation? This cannot be undone.")) return;
    try {
      await deleteConversation(id);
      const convs = await refreshConversations();
      if (id === activeId) {
        if (convs.length > 0) await openConversation(convs[0].id);
        else handleNewChat();
      }
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="app">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        disabled={sending}
        open={sidebarOpen}
        onSelect={openConversation}
        onNew={handleNewChat}
        onDelete={handleDelete}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="chat">
        <header className="chat-header">
          <button className="menu-btn" onClick={() => setSidebarOpen(true)} aria-label="Open menu">
            ☰
          </button>
          <span>LifeOS</span>
        </header>

        <main className="chat-messages">
          {loadingMessages && <p className="hint">Loading conversation…</p>}
          {!loadingMessages && messages.length === 0 && !activeId && (
            <p className="hint">Say hello to start chatting.</p>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`bubble ${m.role}`}>
              {m.content}
            </div>
          ))}
          {sending && <div className="bubble assistant">Thinking…</div>}
          {error && (
            <div className="error">
              <span>{error}</span>
              <button onClick={() => setError("")} aria-label="Dismiss error">✕</button>
            </div>
          )}
          <div ref={bottomRef} />
        </main>

        <form className="chat-input" onSubmit={handleSend}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Message LifeOS"
            disabled={sending}
          />
          <button type="submit" disabled={sending || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}