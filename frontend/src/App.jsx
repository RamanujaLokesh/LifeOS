import { useEffect, useRef, useState } from "react";
import { getMessages, listConversations, sendChat } from "./api/chat";
import "./App.css";

export default function App() {
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  // On first load, open the most recent conversation (if any).
  useEffect(() => {
    (async () => {
      try {
        const convs = await listConversations();
        if (convs.length > 0) {
          setConversationId(convs[0].id);
          setMessages(await getMessages(convs[0].id));
        }
      } catch (err) {
        setError(err.message);
      }
    })();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function handleNewChat() {
    setConversationId(null);
    setMessages([]);
    setError("");
  }

  async function handleSend(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    const next = [...messages, { role: "user", content: text }];
    setMessages(next);
    setInput("");
    setError("");
    setLoading(true);

    try {
      const data = await sendChat(conversationId, text);
      setConversationId(data.conversation_id);
      setMessages([...next, { role: "assistant", content: data.reply }]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat">
      <header className="chat-header">
        <span>LifeOS</span>
        <button onClick={handleNewChat}>New chat</button>
      </header>

      <main className="chat-messages">
        {messages.length === 0 && (
          <p className="hint">Say hello to start chatting.</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.role}`}>
            {m.content}
          </div>
        ))}
        {loading && <div className="bubble assistant">Thinking…</div>}
        {error && <div className="error">{error}</div>}
        <div ref={bottomRef} />
      </main>

      <form className="chat-input" onSubmit={handleSend}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Message LifeOS"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}