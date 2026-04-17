import { useCallback, useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getJSON, postForm } from '../api.js'
import { useAuth } from '../context/AuthContext.jsx'

export default function Profile() {
  const { username } = useParams()
  const { user: current } = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showFollowers, setShowFollowers] = useState(false)
  const [showFollowing, setShowFollowing] = useState(false)

  const load = useCallback(async () => {
    try {
      setLoading(true)
      const d = await getJSON(`/api/profile/${encodeURIComponent(username)}`)
      setData(d)
      setError(null)
    } catch {
      setError('Profil bulunamadı.')
    } finally {
      setLoading(false)
    }
  }, [username])

  useEffect(() => { load() }, [load])

  const follow = async () => {
    await postForm(`/follow/${username}`, {})
    await load()
  }
  const unfollow = async () => {
    await postForm(`/unfollow/${username}`, {})
    await load()
  }
  const deleteComment = async (id) => {
    if (!confirm('Silinsin mi?')) return
    await postForm(`/delete_comment/${id}`, {})
    await load()
  }

  if (loading) return <div className="panel"><p>Profil yükleniyor…</p></div>
  if (error)   return <div className="panel"><div className="alert danger">{error}</div></div>
  if (!data)   return null

  const {
    username: uname,
    profile_image,
    followers = [],
    following = [],
    comments = [],
    is_followed_by_current = false
  } = data

  const isSelf = current && current.username === uname

  return (
    <>
      <div className="panel">
        <div className="profile-header">
          {profile_image ? (
            <img
              src={`/static/profile_images/${profile_image}`}
              alt={uname}
              style={{
                width: 80, height: 80, borderRadius: '50%',
                objectFit: 'cover', border: '3px solid var(--brand-b)'
              }}
            />
          ) : (
            <div className="profile-avatar">{uname.charAt(0).toUpperCase()}</div>
          )}
          <div style={{ flex: 1 }}>
            <h2 style={{ margin: 0 }}>{uname}</h2>
            {current && !isSelf && (
              <div style={{ marginTop: 8 }}>
                {is_followed_by_current ? (
                  <button className="btn danger small" onClick={unfollow}>Takipten Çık</button>
                ) : (
                  <button className="btn primary small" onClick={follow}>Takip Et</button>
                )}
              </div>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', gap: 24 }}>
          <button className="btn outline small" onClick={() => setShowFollowers(v => !v)}>
            Takipçi: {followers.length}
          </button>
          <button className="btn outline small" onClick={() => setShowFollowing(v => !v)}>
            Takip Edilen: {following.length}
          </button>
        </div>

        {showFollowers && (
          <div style={{ marginTop: 14, padding: 14, background: '#f8fafc', borderRadius: 10 }}>
            <h4 style={{ marginTop: 0 }}>Takipçiler</h4>
            {followers.length === 0
              ? <p style={{ margin: 0 }}>Henüz takipçisi yok.</p>
              : <ul style={{ margin: 0, paddingLeft: 20 }}>
                  {followers.map(f => (
                    <li key={f}><Link to={`/profile/${f}`}>{f}</Link></li>
                  ))}
                </ul>
            }
          </div>
        )}
        {showFollowing && (
          <div style={{ marginTop: 14, padding: 14, background: '#f8fafc', borderRadius: 10 }}>
            <h4 style={{ marginTop: 0 }}>Takip Edilenler</h4>
            {following.length === 0
              ? <p style={{ margin: 0 }}>Henüz kimseyi takip etmiyor.</p>
              : <ul style={{ margin: 0, paddingLeft: 20 }}>
                  {following.map(f => (
                    <li key={f}><Link to={`/profile/${f}`}>{f}</Link></li>
                  ))}
                </ul>
            }
          </div>
        )}
      </div>

      <div className="panel">
        <h3 className="panel-title">Yorumlar</h3>
        {comments.length === 0
          ? <p>Henüz yorum yapılmamış.</p>
          : comments.map(c => (
              <div key={c.id} className="comment-card">
                <div className="comment-meta">
                  {new Date(c.timestamp).toLocaleString('tr-TR')}
                </div>
                <div style={{ whiteSpace: 'pre-wrap' }}>{c.content}</div>
                <div className="comment-actions">
                  <span className="badge up">👍 {c.like_count}</span>
                  <span className="badge down">👎 {c.dislike_count}</span>
                  {isSelf && (
                    <button className="btn outline small" onClick={() => deleteComment(c.id)}>
                      Sil
                    </button>
                  )}
                </div>
              </div>
            ))
        }
      </div>
    </>
  )
}
