export default function Sidebar({
  conversations,
  activeId,
  disabled,
  open,
  onSelect,
  onNew,
  onDelete,
  onClose,
}) {
  return (
    <>
      {open && <div className="backdrop" onClick={onClose} />}
      <aside className={`sidebar ${open ? "open" : ""}`}>
        <button className="new-chat" onClick={onNew} disabled={disabled}>
          + New chat
        </button>
        <ul>
          {conversations.map((c) => (
            <li key={c.id} className={c.id === activeId ? "active" : ""}>
              <button
                className="conv-title"
                disabled={disabled}
                onClick={() => onSelect(c.id)}
              >
                {c.title}
              </button>
              <button
                className="conv-delete"
                disabled={disabled}
                onClick={() => onDelete(c.id)}
                aria-label="Delete conversation"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      </aside>
    </>
  );
}