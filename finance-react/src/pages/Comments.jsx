import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { getJSON, postForm } from '../api.js'

/**
 * /api/comments endpoint'ini kullanır (README'de eklenecek mini Flask yaması).
 * Yorum ekleme / beğenme / silme orijinal form endpoint'lerine POST eder.
 */

export default function Comments() {
  const { user } = useAuth()
  const [comments, setComments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [text, setText] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [msg, setMsg] = useState(null)

  const load = useCallback(async () => {
    try {
      setLoading(true)
      const list = await getJSON('/api/comments')
      setComments(list)
      setError(null)
    } catch (e) {
      setError('Yorumlar yüklenemedi. (Backend\'e /api/comments endpoint\'i eklenmeli — README\'ye bakın.)')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!text.trim()) return
    setSubmitting(true)
    try {
      await postForm('/add_comment', { comment: text })
      setText('')
      setMsg({ kind: 'success', text: 'Yorum eklendi.' })
      await load()
    } catch {
      setMsg({ kind: 'danger', text: 'Yorum eklenemedi.' })
    } finally {
      setSubmitting(false)
      setTimeout(() => setMsg(null), 3000)
    }
  }

  const onLike = async (id) => {
    await postForm(`/like_comment/${id}`, {})
    await load()
  }
  const onDislike = async (id) => {
    await postForm(`/dislike_comment/${id}`, {})
    await load()
  }
  const onDelete = async (id) => {
    if (!confirm('Bu yorumu silmek istediğinize emin misiniz?')) return
    await postForm(`/delete_comment/${id}`, {})
    await load()
  }
  const onReply = async (parentId, content) => {
    if (!content.trim()) return
    await postForm('/add_comment', { comment: content, parent_id: parentId })
    await load()
  }

  return (
    <div className="panel">
      <h2 className="panel-title">Yorumlar</h2>

      {msg && <div className={`alert ${msg.kind}`}>{msg.text}</div>}
      {error && <div className="alert warning">{error}</div>}

      {user ? (
        <form onSubmit={onSubmit} style={{ marginBottom: 20 }}>
          <div className="form-row">
            <textarea
              rows={3}
              placeholder="Yorumunuzu yazın…"
              value={text}
              onChange={e => setText(e.target.value)}
            />
          </div>
          <button className="btn primary" disabled={submitting || !text.trim()}>
            {submitting ? 'Gönderiliyor…' : 'Yorum Gönder'}
          </button>
        </form>
      ) : (
        <div className="alert info">
          Yorum yapabilmek için <Link to="/login">giriş yapmalısınız</Link>.
        </div>
      )}

      {loading ? <p>Yorumlar yükleniyor…</p> : (
        comments.length === 0
          ? <p>Henüz yorum yapılmamış.</p>
          : comments.map(c => (
              <CommentCard
                key={c.id}
                comment={c}
                currentUser={user}
                onLike={onLike}
                onDislike={onDislike}
                onDelete={onDelete}
                onReply={onReply}
              />
            ))
      )}
    </div>
  )
}

function CommentCard({ comment, currentUser, onLike, onDislike, onDelete, onReply }) {
  const [showReplies, setShowReplies] = useState(false)
  const [showReplyForm, setShowReplyForm] = useState(false)
  const [replyText, setReplyText] = useState('')

  const isOwn = currentUser && currentUser.username === comment.author

  return (
    <div className="comment-card">
      <div className="comment-meta">
        <Link to={`/profile/${comment.author}`}>{comment.author}</Link>
        <span>· {new Date(comment.timestamp).toLocaleString('tr-TR')}</span>
      </div>

      <div style={{ whiteSpace: 'pre-wrap' }}>{comment.content}</div>

      <div className="comment-actions">
        <button className="btn success small" onClick={() => onLike(comment.id)}>
          👍 {comment.like_count}
        </button>
        <button className="btn danger small" onClick={() => onDislike(comment.id)}>
          👎 {comment.dislike_count}
        </button>
        {isOwn && (
          <button className="btn outline small" onClick={() => onDelete(comment.id)}>
            Sil
          </button>
        )}
        {currentUser && (
          <button className="btn outline small" onClick={() => setShowReplyForm(v => !v)}>
            Cevapla
          </button>
        )}
        {comment.replies?.length > 0 && (
          <button className="btn outline small" onClick={() => setShowReplies(v => !v)}>
            {showReplies ? 'Cevapları Gizle' : `Cevaplar (${comment.replies.length})`}
          </button>
        )}
      </div>

      {showReplyForm && currentUser && (
        <div style={{ marginTop: 10 }}>
          <div className="form-row">
            <textarea
              rows={2}
              placeholder="Cevabınızı yazın…"
              value={replyText}
              onChange={e => setReplyText(e.target.value)}
            />
          </div>
          <button
            className="btn primary small"
            onClick={async () => {
              await onReply(comment.id, replyText)
              setReplyText('')
              setShowReplyForm(false)
              setShowReplies(true)
            }}
          >
            Gönder
          </button>
        </div>
      )}

      {showReplies && comment.replies?.length > 0 && (
        <div className="comment-replies">
          {comment.replies.map(r => (
            <CommentCard
              key={r.id}
              comment={r}
              currentUser={currentUser}
              onLike={onLike}
              onDislike={onDislike}
              onDelete={onDelete}
              onReply={onReply}
            />
          ))}
        </div>
      )}
    </div>
  )
}
