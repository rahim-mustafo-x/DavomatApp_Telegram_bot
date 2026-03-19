import sqlite3

DB_PATH = 'data/bot.db'


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_conn() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS required_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL UNIQUE,
                channel_name TEXT NOT NULL,
                invite_link TEXT NOT NULL
            )
        ''')
        conn.commit()


def add_channel(channel_id: str, channel_name: str, invite_link: str):
    with get_conn() as conn:
        conn.execute(
            'INSERT OR REPLACE INTO required_channels (channel_id, channel_name, invite_link) VALUES (?, ?, ?)',
            (channel_id, channel_name, invite_link)
        )
        conn.commit()


def remove_channel(channel_id: str):
    with get_conn() as conn:
        conn.execute('DELETE FROM required_channels WHERE channel_id = ?', (channel_id,))
        conn.commit()


def get_all_channels():
    with get_conn() as conn:
        rows = conn.execute('SELECT channel_id, channel_name, invite_link FROM required_channels').fetchall()
    return [{'channel_id': r[0], 'channel_name': r[1], 'invite_link': r[2]} for r in rows]
