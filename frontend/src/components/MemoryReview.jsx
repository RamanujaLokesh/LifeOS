export default function MemoryReview({ memories, onApprove, onDismiss, onClose }) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <strong>Suggested memories</strong>
          <button onClick={onClose} aria-label="Close">✕</button>
        </div>
        {memories.length === 0 ? (
          <p className="hint">Nothing to review.</p>
        ) : (
          <ul className="memory-list">
            {memories.map((m) => (
              <li key={m.id}>
                <span className="tag">{m.category}</span>
                <p>{m.content}</p>
                <div className="memory-actions">
                  <button onClick={() => onApprove(m.id)}>Save</button>
                  <button onClick={() => onDismiss(m.id)}>Dismiss</button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}