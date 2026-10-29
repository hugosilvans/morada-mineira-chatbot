"""Conexão e criação do SQLite. Não contém regras de atendimento."""

import os
import sqlite3
from seed_data import seed_sample_data

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "db.sqlite"))


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        name TEXT NOT NULL,
        base_price REAL NOT NULL,
        description TEXT,
        picture_url TEXT,
        bestseller INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS option_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        menu_item_id INTEGER NOT NULL,
        `key` TEXT NOT NULL,
        type TEXT NOT NULL DEFAULT 'single',
        FOREIGN KEY(menu_item_id) REFERENCES menu_items(id)
    );

    CREATE TABLE IF NOT EXISTS options (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        menu_item_id INTEGER NOT NULL,
        option_group_id INTEGER,
        name TEXT NOT NULL,
        price_modifier REAL DEFAULT 0.0,
        FOREIGN KEY(menu_item_id) REFERENCES menu_items(id),
        FOREIGN KEY(option_group_id) REFERENCES option_groups(id)
    );

    CREATE TABLE IF NOT EXISTS best_sellers (
        menu_item_id INTEGER PRIMARY KEY,
        count INTEGER DEFAULT 0,
        FOREIGN KEY(menu_item_id) REFERENCES menu_items(id)
    );

    CREATE TABLE IF NOT EXISTS carts (
        id TEXT PRIMARY KEY,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS cart_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id TEXT,
        menu_item_id INTEGER,
        selected_options TEXT,
        quantity INTEGER,
        unit_price REAL,
        FOREIGN KEY(cart_id) REFERENCES carts(id),
        FOREIGN KEY(menu_item_id) REFERENCES menu_items(id)
    );
    """)
    conn.commit()

    cur.execute("SELECT COUNT(1) as cnt FROM menu_items")
    cnt = 0
    try:
        cnt = cur.fetchone()["cnt"]
    except Exception:
        cnt = 0
    if cnt == 0:
        seed_sample_data(conn)

    conn.close()
