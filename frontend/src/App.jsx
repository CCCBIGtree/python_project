import { useEffect, useMemo, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

function App() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [token, setToken] = useState(localStorage.getItem('token') || '')
  const [habits, setHabits] = useState([])
  const [habitName, setHabitName] = useState('')
  const [habitDescription, setHabitDescription] = useState('')
  const [selectedStats, setSelectedStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const authHeaders = useMemo(
    () => (token ? { Authorization: `Bearer ${token}` } : {}),
    [token],
  )

  useEffect(() => {
    if (!token) return
    fetchHabits()
  }, [token])

  async function request(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    })

    const payload = await response.json().catch(() => ({}))
    if (!response.ok) {
      throw new Error(payload.detail || '请求失败')
    }
    return payload
  }

  async function register() {
    setLoading(true)
    setMessage('')
    try {
      await request('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      setMessage('注册成功，请登录')
    } catch (err) {
      setMessage(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function login() {
    setLoading(true)
    setMessage('')
    try {
      const result = await request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      setToken(result.access_token)
      localStorage.setItem('token', result.access_token)
      setMessage('登录成功')
    } catch (err) {
      setMessage(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function fetchHabits() {
    try {
      const result = await request('/habits', { headers: authHeaders })
      setHabits(result)
    } catch (err) {
      setMessage(err.message)
    }
  }

  async function createHabit(e) {
    e.preventDefault()
    setLoading(true)
    setMessage('')
    try {
      await request('/habits', {
        method: 'POST',
        headers: authHeaders,
        body: JSON.stringify({
          name: habitName,
          description: habitDescription || null,
        }),
      })
      setHabitName('')
      setHabitDescription('')
      await fetchHabits()
      setMessage('习惯创建成功')
    } catch (err) {
      setMessage(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function checkIn(habitId) {
    setLoading(true)
    setMessage('')
    try {
      await request(`/habits/${habitId}/checkin`, {
        method: 'POST',
        headers: authHeaders,
        body: JSON.stringify({}),
      })
      setMessage('打卡成功')
    } catch (err) {
      setMessage(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function loadStats(habitId) {
    setLoading(true)
    setMessage('')
    try {
      const result = await request(`/habits/${habitId}/stats`, {
        headers: authHeaders,
      })
      setSelectedStats(result)
    } catch (err) {
      setMessage(err.message)
    } finally {
      setLoading(false)
    }
  }

  function logout() {
    localStorage.removeItem('token')
    setToken('')
    setHabits([])
    setSelectedStats(null)
    setMessage('已退出登录')
  }

  return (
    <div className="container">
      <h1>Habit Tracker 可视化面板</h1>
      <p className="subtitle">用于实习展示的最小可用前端（React + JS）</p>

      {!token ? (
        <section className="card">
          <h2>登录 / 注册</h2>
          <div className="form-row">
            <input
              placeholder="邮箱"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <input
              type="password"
              placeholder="密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div className="actions">
            <button disabled={loading} onClick={register}>注册</button>
            <button disabled={loading} onClick={login}>登录</button>
          </div>
        </section>
      ) : (
        <>
          <section className="card">
            <div className="split">
              <h2>习惯管理</h2>
              <button onClick={logout}>退出登录</button>
            </div>
            <form className="form-row" onSubmit={createHabit}>
              <input
                placeholder="习惯名称（例如：每天跑步）"
                value={habitName}
                onChange={(e) => setHabitName(e.target.value)}
                required
              />
              <input
                placeholder="描述（可选）"
                value={habitDescription}
                onChange={(e) => setHabitDescription(e.target.value)}
              />
              <button disabled={loading} type="submit">新增习惯</button>
            </form>
          </section>

          <section className="card">
            <div className="split">
              <h2>我的习惯</h2>
              <button onClick={fetchHabits}>刷新</button>
            </div>
            {habits.length === 0 ? (
              <p>暂无习惯，请先创建。</p>
            ) : (
              habits.map((habit) => (
                <div className="habit-row" key={habit.id}>
                  <div>
                    <strong>{habit.name}</strong>
                    <p>{habit.description || '无描述'}</p>
                  </div>
                  <div className="actions">
                    <button disabled={loading} onClick={() => checkIn(habit.id)}>今日打卡</button>
                    <button disabled={loading} onClick={() => loadStats(habit.id)}>查看统计</button>
                  </div>
                </div>
              ))
            )}
          </section>

          {selectedStats && (
            <section className="card">
              <h2>统计面板：{selectedStats.habit_name}</h2>
              <div className="stats-grid">
                <Stat label="总天数" value={selectedStats.total_days} />
                <Stat label="完成天数" value={selectedStats.completed_days} />
                <Stat label="完成率" value={`${selectedStats.completion_rate}%`} />
                <Stat label="当前连续" value={selectedStats.current_streak} />
                <Stat label="最长连续" value={selectedStats.longest_streak} />
              </div>
            </section>
          )}
        </>
      )}

      {message && <p className="message">{message}</p>}
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="stat">
      <p>{label}</p>
      <strong>{value}</strong>
    </div>
  )
}

export default App
