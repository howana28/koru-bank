export default function Brand({ compact = false }) {
  return (
    <div className={`brand ${compact ? 'brand--compact' : ''}`} aria-label="Koru Bank">
      <span className="brand__mark" aria-hidden="true">
        <span className="brand__leaf brand__leaf--one" />
        <span className="brand__leaf brand__leaf--two" />
      </span>
      <span className="brand__name">KORU</span>
    </div>
  )
}
