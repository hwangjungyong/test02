#!/usr/bin/env node

/**
 * 데이터베이스 유틸리티 - SQLite 기반 (sql.js 사용)
 * 
 * 역할:
 * - SQLite 데이터베이스를 사용한 사용자 데이터 저장 및 조회
 * - 순수 JavaScript 기반 (네이티브 모듈 불필요)
 * - 사용자, 뉴스, 음악, 도서 데이터 관리
 */

import initSqlJs from 'sql.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 데이터베이스 파일 경로
const DB_DIR = path.join(__dirname, 'data');
const DB_FILE = path.join(DB_DIR, 'database.db');

// SQLite 인스턴스
let SQL;
let db = null;

// 데이터베이스 초기화
async function initDatabase() {
  try {
    // 데이터 디렉토리 생성
    if (!fs.existsSync(DB_DIR)) {
      fs.mkdirSync(DB_DIR, { recursive: true });
    }

    // SQL.js 초기화
    const sqlJsPath = path.join(__dirname, 'node_modules', 'sql.js', 'dist');
    SQL = await initSqlJs({
      locateFile: (file) => path.join(sqlJsPath, file)
    });

    // 데이터베이스 파일이 있으면 로드, 없으면 새로 생성
    if (fs.existsSync(DB_FILE)) {
      const buffer = fs.readFileSync(DB_FILE);
      db = new SQL.Database(buffer);
      console.log('[DB] 기존 데이터베이스 로드 완료');
    } else {
      db = new SQL.Database();
      console.log('[DB] 새 데이터베이스 생성 완료');
    }

    // 테이블 생성
    createTables();
    
    // 테이블 마이그레이션 (기존 테이블에 컬럼 추가)
    migrateTables();
    
    console.log('[DB] 데이터베이스 초기화 완료');
  } catch (error) {
    console.error('[DB] 데이터베이스 초기화 오류:', error);
    throw error;
  }
}

// 테이블 생성
function createTables() {
  const tables = [
    // 사용자 테이블
    `CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      name TEXT,
      createdAt TEXT NOT NULL,
      updatedAt TEXT NOT NULL
    )`,
    
    // 뉴스 히스토리 테이블
    `CREATE TABLE IF NOT EXISTS news (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      userId INTEGER,
      title TEXT NOT NULL,
      summary TEXT,
      date TEXT,
      source TEXT,
      category TEXT,
      keyword TEXT,
      url TEXT,
      collectedAt TEXT NOT NULL,
      publishedDate TEXT,
      importanceStars INTEGER,
      importanceValue INTEGER,
      FOREIGN KEY (userId) REFERENCES users(id)
    )`,
    
    // 라디오 노래 히스토리 테이블
    `CREATE TABLE IF NOT EXISTS radioSongs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      userId INTEGER,
      title TEXT NOT NULL,
      artist TEXT,
      genre TEXT,
      count INTEGER DEFAULT 1,
      lastPlayed TEXT,
      firstPlayed TEXT,
      dates TEXT,
      stations TEXT,
      collectedAt TEXT NOT NULL,
      FOREIGN KEY (userId) REFERENCES users(id)
    )`,
    
    // 도서 히스토리 테이블
    `CREATE TABLE IF NOT EXISTS books (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      userId INTEGER,
      title TEXT NOT NULL,
      authors TEXT,
      description TEXT,
      imageUrl TEXT,
      previewLink TEXT,
      publishedDate TEXT,
      categories TEXT,
      collectedAt TEXT NOT NULL,
      FOREIGN KEY (userId) REFERENCES users(id)
    )`,
    
    // API 키 테이블
    `CREATE TABLE IF NOT EXISTS apiKeys (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      userId INTEGER NOT NULL,
      apiKey TEXT UNIQUE NOT NULL,
      name TEXT,
      description TEXT,
      isActive INTEGER DEFAULT 1,
      lastUsedAt TEXT,
      createdAt TEXT NOT NULL,
      expiresAt TEXT,
      FOREIGN KEY (userId) REFERENCES users(id)
    )`,
    
    // API 키 사용 이력 테이블
    `CREATE TABLE IF NOT EXISTS apiKeyUsage (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      apiKeyId INTEGER NOT NULL,
      endpoint TEXT NOT NULL,
      method TEXT NOT NULL,
      ipAddress TEXT,
      userAgent TEXT,
      statusCode INTEGER,
      createdAt TEXT NOT NULL,
      FOREIGN KEY (apiKeyId) REFERENCES apiKeys(id)
    )`,
    
    // 에러 로그 테이블
    `CREATE TABLE IF NOT EXISTS error_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      log_content TEXT NOT NULL,
      log_type TEXT,
      parsed_data TEXT,
      system_type TEXT,
      severity TEXT,
      resource_type TEXT,
      service_name TEXT,
      file_path TEXT,
      line_number INTEGER,
      error_type TEXT,
      error_category TEXT,
      timestamp TEXT,
      created_at TEXT DEFAULT (datetime('now', 'localtime')),
      updated_at TEXT DEFAULT (datetime('now', 'localtime'))
    )`,
    
    // SR 요청 테이블
    `CREATE TABLE IF NOT EXISTS sr_requests (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      userId INTEGER,
      sr_number TEXT UNIQUE,
      title TEXT NOT NULL,
      description TEXT,
      confluence_url TEXT,
      confluence_key TEXT,
      confluence_page_id TEXT,
      confluence_content TEXT,
      source_type TEXT DEFAULT 'confluence',
      status TEXT DEFAULT 'open',
      priority TEXT DEFAULT 'medium',
      category TEXT,
      tags TEXT,
      related_error_log_ids TEXT,
      created_at TEXT DEFAULT (datetime('now', 'localtime')),
      updated_at TEXT DEFAULT (datetime('now', 'localtime')),
      FOREIGN KEY (userId) REFERENCES users(id)
    )`,
    
    // SR 처리 이력 테이블
    `CREATE TABLE IF NOT EXISTS sr_history (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      sr_request_id INTEGER NOT NULL,
      action TEXT NOT NULL,
      description TEXT,
      performed_by INTEGER,
      git_commit_hash TEXT,
      git_commit_message TEXT,
      git_author TEXT,
      git_date TEXT,
      related_files TEXT,
      related_programs TEXT,
      created_at TEXT DEFAULT (datetime('now', 'localtime')),
      FOREIGN KEY (sr_request_id) REFERENCES sr_requests(id),
      FOREIGN KEY (performed_by) REFERENCES users(id)
    )`,
    
    // Confluence 캐시 테이블
    `CREATE TABLE IF NOT EXISTS confluence_cache (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      confluence_key TEXT UNIQUE NOT NULL,
      page_id TEXT,
      title TEXT,
      content TEXT,
      url TEXT,
      space_key TEXT,
      last_modified TEXT,
      cached_at TEXT DEFAULT (datetime('now', 'localtime')),
      expires_at TEXT
    )`,
    
    // Git 커밋 정보 테이블
    `CREATE TABLE IF NOT EXISTS git_commits (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      commit_hash TEXT UNIQUE NOT NULL,
      author TEXT,
      author_email TEXT,
      commit_date TEXT,
      commit_message TEXT,
      repository_path TEXT,
      branch TEXT,
      files_changed TEXT,
      insertions INTEGER,
      deletions INTEGER,
      related_sr_id INTEGER,
      similarity_score REAL,
      created_at TEXT DEFAULT (datetime('now', 'localtime')),
      FOREIGN KEY (related_sr_id) REFERENCES sr_requests(id)
    )`,
    
    // DB 변경 이력 테이블
    `CREATE TABLE IF NOT EXISTS db_changes (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      change_type TEXT NOT NULL,
      table_name TEXT NOT NULL,
      column_name TEXT,
      old_value TEXT,
      new_value TEXT,
      change_description TEXT,
      sql_query TEXT,
      related_sr_id INTEGER,
      detected_at TEXT DEFAULT (datetime('now', 'localtime')),
      FOREIGN KEY (related_sr_id) REFERENCES sr_requests(id)
    )`
  ];

  tables.forEach(sql => {
    db.run(sql);
  });
}

// 테이블 마이그레이션 (기존 테이블에 컬럼 추가)
function migrateTables() {
  try {
    // error_logs 테이블 마이그레이션
    const checkTableStmt = db.prepare(`
      SELECT name FROM sqlite_master 
      WHERE type='table' AND name='error_logs'
    `);
    const tableExists = checkTableStmt.step();
    checkTableStmt.free();
    
    if (tableExists) {
      // 테이블이 존재하면 컬럼 추가 시도
      const migrations = [
        { column: 'system_type', type: 'TEXT' },
        { column: 'severity', type: 'TEXT' },
        { column: 'resource_type', type: 'TEXT' },
        { column: 'service_name', type: 'TEXT' },
        { column: 'file_path', type: 'TEXT' },
        { column: 'line_number', type: 'INTEGER' },
        { column: 'error_type', type: 'TEXT' },
        { column: 'error_category', type: 'TEXT' },
        { column: 'timestamp', type: 'TEXT' }
      ];
      
      for (const migration of migrations) {
        try {
          // 컬럼이 이미 있는지 확인하기 위해 테이블 정보 조회
          const pragmaStmt = db.prepare(`PRAGMA table_info(error_logs)`);
          let columnExists = false;
          
          while (pragmaStmt.step()) {
            const row = pragmaStmt.getAsObject();
            if (row.name === migration.column) {
              columnExists = true;
              break;
            }
          }
          pragmaStmt.free();
          
          // 컬럼이 없으면 추가
          if (!columnExists) {
            const alterStmt = db.prepare(
              `ALTER TABLE error_logs ADD COLUMN ${migration.column} ${migration.type}`
            );
            alterStmt.step();
            alterStmt.free();
            console.log(`[DB] error_logs 테이블에 ${migration.column} 컬럼 추가 완료`);
          }
        } catch (error) {
          // 컬럼이 이미 존재하거나 다른 오류인 경우 무시
          if (!error.message.includes('duplicate column')) {
            console.warn(`[DB] error_logs 테이블 마이그레이션 경고 (${migration.column}):`, error.message);
          }
        }
      }
      
      saveDatabase();
    }
  } catch (error) {
    console.error('[DB] 테이블 마이그레이션 오류:', error);
    // 마이그레이션 실패해도 계속 진행
  }
}

// 데이터베이스 저장
function saveDatabase() {
  try {
    const data = db.export();
    const buffer = Buffer.from(data);
    fs.writeFileSync(DB_FILE, buffer);
  } catch (error) {
    console.error('[DB] 데이터베이스 저장 오류:', error);
  }
}

// 사용자 관련 함수
export const userDB = {
  // 모든 사용자 조회
  findAll() {
    const stmt = db.prepare('SELECT * FROM users ORDER BY id');
    const users = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      users.push({
        id: row.id,
        email: row.email,
        password: row.password,
        name: row.name,
        createdAt: row.createdAt,
        updatedAt: row.updatedAt
      });
    }
    stmt.free();
    return users;
  },

  // ID로 사용자 조회
  findById(id) {
    const stmt = db.prepare('SELECT * FROM users WHERE id = ?');
    stmt.bind([id]);
    let user = null;
    if (stmt.step()) {
      const row = stmt.getAsObject();
      user = {
        id: row.id,
        email: row.email,
        password: row.password,
        name: row.name,
        createdAt: row.createdAt,
        updatedAt: row.updatedAt
      };
    }
    stmt.free();
    return user;
  },

  // 이메일로 사용자 조회
  findByEmail(email) {
    const stmt = db.prepare('SELECT * FROM users WHERE email = ?');
    stmt.bind([email]);
    let user = null;
    if (stmt.step()) {
      const row = stmt.getAsObject();
      user = {
        id: row.id,
        email: row.email,
        password: row.password,
        name: row.name,
        createdAt: row.createdAt,
        updatedAt: row.updatedAt
      };
    }
    stmt.free();
    return user;
  },

  // 사용자 생성
  create(userData) {
    const now = new Date().toISOString();
    const stmt = db.prepare(
      'INSERT INTO users (email, password, name, createdAt, updatedAt) VALUES (?, ?, ?, ?, ?)'
    );
    stmt.run([
      userData.email,
      userData.password,
      userData.name || null,
      now,
      now
    ]);
    stmt.free();
    saveDatabase();

    // 생성된 사용자 조회
    const stmt2 = db.prepare('SELECT * FROM users WHERE email = ?');
    stmt2.bind([userData.email]);
    let user = null;
    if (stmt2.step()) {
      const row = stmt2.getAsObject();
      user = {
        id: row.id,
        email: row.email,
        password: row.password,
        name: row.name,
        createdAt: row.createdAt,
        updatedAt: row.updatedAt
      };
    }
    stmt2.free();
    return user;
  },

  // 사용자 업데이트
  update(id, updateData) {
    const now = new Date().toISOString();
    const fields = [];
    const values = [];

    if (updateData.email) {
      fields.push('email = ?');
      values.push(updateData.email);
    }
    if (updateData.password) {
      fields.push('password = ?');
      values.push(updateData.password);
    }
    if (updateData.name !== undefined) {
      fields.push('name = ?');
      values.push(updateData.name);
    }
    fields.push('updatedAt = ?');
    values.push(now);
    values.push(id);

    const sql = `UPDATE users SET ${fields.join(', ')} WHERE id = ?`;
    const stmt = db.prepare(sql);
    stmt.run(values);
    stmt.free();
    saveDatabase();

    return this.findById(id);
  },

  // 사용자 삭제
  delete(id) {
    // 삭제 전 존재 여부 확인
    const checkStmt = db.prepare('SELECT id FROM users WHERE id = ?');
    checkStmt.bind([id]);
    const exists = checkStmt.step();
    checkStmt.free();
    
    if (!exists) {
      return false; // 존재하지 않음
    }
    
    // 삭제 실행
    const stmt = db.prepare('DELETE FROM users WHERE id = ?');
    stmt.run([id]);
    stmt.free();
    saveDatabase();
    return true;
  }
};

// 뉴스 히스토리 관련 함수
export const newsDB = {
  // 사용자별 뉴스 조회
  findByUserId(userId) {
    const stmt = db.prepare('SELECT * FROM news WHERE userId = ? ORDER BY collectedAt DESC');
    stmt.bind([userId]);
    const news = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      news.push({
        id: row.id,
        userId: row.userId,
        title: row.title,
        summary: row.summary,
        date: row.date,
        source: row.source,
        category: row.category,
        keyword: row.keyword,
        url: row.url,
        collectedAt: row.collectedAt,
        publishedDate: row.publishedDate,
        importanceStars: row.importanceStars,
        importanceValue: row.importanceValue
      });
    }
    stmt.free();
    return news;
  },

  // 뉴스 추가
  create(newsData) {
    const now = new Date().toISOString();
    const stmt = db.prepare(
      'INSERT INTO news (userId, title, summary, date, source, category, keyword, url, collectedAt, publishedDate, importanceStars, importanceValue) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    );
    stmt.run([
      newsData.userId || null,
      newsData.title,
      newsData.summary || null,
      newsData.date || null,
      newsData.source || null,
      newsData.category || null,
      newsData.keyword || null,
      newsData.url || null,
      now,
      newsData.publishedDate || null,
      newsData.importanceStars || null,
      newsData.importanceValue || null
    ]);
    stmt.free();
    saveDatabase();

    // 생성된 뉴스 조회
    const stmt2 = db.prepare('SELECT * FROM news WHERE id = last_insert_rowid()');
    let news = null;
    if (stmt2.step()) {
      const row = stmt2.getAsObject();
      news = {
        id: row.id,
        userId: row.userId,
        title: row.title,
        summary: row.summary,
        date: row.date,
        source: row.source,
        category: row.category,
        keyword: row.keyword,
        url: row.url,
        collectedAt: row.collectedAt,
        publishedDate: row.publishedDate,
        importanceStars: row.importanceStars,
        importanceValue: row.importanceValue
      };
    }
    stmt2.free();
    return news;
  },

  // 뉴스 삭제
  delete(id) {
    // 삭제 전 존재 여부 확인
    const checkStmt = db.prepare('SELECT id FROM news WHERE id = ?');
    checkStmt.bind([id]);
    const exists = checkStmt.step();
    checkStmt.free();
    
    if (!exists) {
      return false; // 존재하지 않음
    }
    
    // 삭제 실행
    const stmt = db.prepare('DELETE FROM news WHERE id = ?');
    stmt.run([id]);
    stmt.free();
    saveDatabase();
    return true;
  },

  // 사용자별 뉴스 삭제
  deleteByUserId(userId) {
    const stmt = db.prepare('DELETE FROM news WHERE userId = ?');
    stmt.run([userId]);
    stmt.free();
    saveDatabase();
    return true; // sql.js에서는 삭제된 행 수를 직접 확인할 수 없으므로 항상 true 반환
  }
};

// 라디오 노래 히스토리 관련 함수
export const radioSongsDB = {
  // 사용자별 라디오 노래 조회
  findByUserId(userId) {
    const stmt = db.prepare('SELECT * FROM radioSongs WHERE userId = ? ORDER BY collectedAt DESC');
    stmt.bind([userId]);
    const songs = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      songs.push({
        id: row.id,
        userId: row.userId,
        title: row.title,
        artist: row.artist,
        genre: row.genre,
        count: row.count,
        lastPlayed: row.lastPlayed,
        firstPlayed: row.firstPlayed,
        dates: row.dates ? JSON.parse(row.dates) : [],
        stations: row.stations ? JSON.parse(row.stations) : [],
        collectedAt: row.collectedAt
      });
    }
    stmt.free();
    return songs;
  },

  // 라디오 노래 추가
  create(songData) {
    const now = new Date().toISOString();
    const stmt = db.prepare(
      'INSERT INTO radioSongs (userId, title, artist, genre, count, lastPlayed, firstPlayed, dates, stations, collectedAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    );
    stmt.run([
      songData.userId || null,
      songData.title,
      songData.artist || null,
      songData.genre || null,
      songData.count || 1,
      songData.lastPlayed || null,
      songData.firstPlayed || null,
      songData.dates ? JSON.stringify(songData.dates) : null,
      songData.stations ? JSON.stringify(songData.stations) : null,
      now
    ]);
    stmt.free();
    saveDatabase();

    // 생성된 노래 조회
    const stmt2 = db.prepare('SELECT * FROM radioSongs WHERE id = last_insert_rowid()');
    let song = null;
    if (stmt2.step()) {
      const row = stmt2.getAsObject();
      song = {
        id: row.id,
        userId: row.userId,
        title: row.title,
        artist: row.artist,
        genre: row.genre,
        count: row.count,
        lastPlayed: row.lastPlayed,
        firstPlayed: row.firstPlayed,
        dates: row.dates ? JSON.parse(row.dates) : [],
        stations: row.stations ? JSON.parse(row.stations) : [],
        collectedAt: row.collectedAt
      };
    }
    stmt2.free();
    return song;
  },

  // 사용자별 라디오 노래 삭제
  deleteByUserId(userId) {
    const stmt = db.prepare('DELETE FROM radioSongs WHERE userId = ?');
    stmt.run([userId]);
    stmt.free();
    saveDatabase();
    return true; // sql.js에서는 삭제된 행 수를 직접 확인할 수 없으므로 항상 true 반환
  }
};

// 도서 히스토리 관련 함수
export const booksDB = {
  // 사용자별 도서 조회
  findByUserId(userId) {
    const stmt = db.prepare('SELECT * FROM books WHERE userId = ? ORDER BY collectedAt DESC');
    stmt.bind([userId]);
    const books = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      books.push({
        id: row.id,
        userId: row.userId,
        title: row.title,
        authors: row.authors ? JSON.parse(row.authors) : [],
        description: row.description,
        imageUrl: row.imageUrl,
        previewLink: row.previewLink,
        publishedDate: row.publishedDate,
        categories: row.categories ? JSON.parse(row.categories) : [],
        collectedAt: row.collectedAt
      });
    }
    stmt.free();
    return books;
  },

  // 도서 추가
  create(bookData) {
    const now = new Date().toISOString();
    const stmt = db.prepare(
      'INSERT INTO books (userId, title, authors, description, imageUrl, previewLink, publishedDate, categories, collectedAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
    );
    stmt.run([
      bookData.userId || null,
      bookData.title,
      bookData.authors ? JSON.stringify(bookData.authors) : null,
      bookData.description || null,
      bookData.imageUrl || null,
      bookData.previewLink || null,
      bookData.publishedDate || null,
      bookData.categories ? JSON.stringify(bookData.categories) : null,
      now
    ]);
    stmt.free();
    saveDatabase();

    // 생성된 도서 조회
    const stmt2 = db.prepare('SELECT * FROM books WHERE id = last_insert_rowid()');
    let book = null;
    if (stmt2.step()) {
      const row = stmt2.getAsObject();
      book = {
        id: row.id,
        userId: row.userId,
        title: row.title,
        authors: row.authors ? JSON.parse(row.authors) : [],
        description: row.description,
        imageUrl: row.imageUrl,
        previewLink: row.previewLink,
        publishedDate: row.publishedDate,
        categories: row.categories ? JSON.parse(row.categories) : [],
        collectedAt: row.collectedAt
      };
    }
    stmt2.free();
    return book;
  },

  // 사용자별 도서 삭제
  deleteByUserId(userId) {
    const stmt = db.prepare('DELETE FROM books WHERE userId = ?');
    stmt.run([userId]);
    stmt.free();
    saveDatabase();
    return true; // sql.js에서는 삭제된 행 수를 직접 확인할 수 없으므로 항상 true 반환
  }
};

// 데이터베이스 초기화 (비동기)
let initPromise = null;
export async function init() {
  if (!initPromise) {
    initPromise = initDatabase();
  }
  return initPromise;
}

// API 키 관리 함수
export const apiKeysDB = {
  // 사용자별 API 키 조회
  findByUserId(userId) {
    const stmt = db.prepare('SELECT * FROM apiKeys WHERE userId = ? ORDER BY createdAt DESC');
    stmt.bind([userId]);
    const keys = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      keys.push({
        id: row.id,
        userId: row.userId,
        apiKey: row.apiKey,
        name: row.name,
        description: row.description,
        isActive: row.isActive === 1,
        lastUsedAt: row.lastUsedAt,
        createdAt: row.createdAt,
        expiresAt: row.expiresAt
      });
    }
    stmt.free();
    return keys;
  },

  // API 키로 조회
  findByApiKey(apiKey) {
    const stmt = db.prepare('SELECT * FROM apiKeys WHERE apiKey = ? AND isActive = 1');
    stmt.bind([apiKey]);
    let key = null;
    if (stmt.step()) {
      const row = stmt.getAsObject();
      // 만료 확인
      if (row.expiresAt) {
        const expiresAt = new Date(row.expiresAt);
        if (expiresAt < new Date()) {
          stmt.free();
          return null; // 만료됨
        }
      }
      key = {
        id: row.id,
        userId: row.userId,
        apiKey: row.apiKey,
        name: row.name,
        description: row.description,
        isActive: row.isActive === 1,
        lastUsedAt: row.lastUsedAt,
        createdAt: row.createdAt,
        expiresAt: row.expiresAt
      };
    }
    stmt.free();
    return key;
  },

  // API 키 생성
  create(keyData) {
    const now = new Date().toISOString();
    const stmt = db.prepare(
      'INSERT INTO apiKeys (userId, apiKey, name, description, isActive, createdAt, expiresAt) VALUES (?, ?, ?, ?, ?, ?, ?)'
    );
    stmt.run([
      keyData.userId,
      keyData.apiKey,
      keyData.name || null,
      keyData.description || null,
      keyData.isActive !== false ? 1 : 0,
      now,
      keyData.expiresAt || null
    ]);
    stmt.free();
    saveDatabase();

    // 생성된 키 조회
    const stmt2 = db.prepare('SELECT * FROM apiKeys WHERE apiKey = ?');
    stmt2.bind([keyData.apiKey]);
    let key = null;
    if (stmt2.step()) {
      const row = stmt2.getAsObject();
      key = {
        id: row.id,
        userId: row.userId,
        apiKey: row.apiKey,
        name: row.name,
        description: row.description,
        isActive: row.isActive === 1,
        lastUsedAt: row.lastUsedAt,
        createdAt: row.createdAt,
        expiresAt: row.expiresAt
      };
    }
    stmt2.free();
    return key;
  },

  // API 키 사용 시간 업데이트
  updateLastUsed(apiKeyId) {
    const now = new Date().toISOString();
    const stmt = db.prepare('UPDATE apiKeys SET lastUsedAt = ? WHERE id = ?');
    stmt.run([now, apiKeyId]);
    stmt.free();
    saveDatabase();
  },

  // API 키 삭제
  delete(id, userId) {
    // 삭제 전 존재 여부 확인
    const checkStmt = db.prepare('SELECT id FROM apiKeys WHERE id = ? AND userId = ?');
    checkStmt.bind([id, userId]);
    const exists = checkStmt.step();
    checkStmt.free();
    
    if (!exists) {
      return false; // 존재하지 않음
    }
    
    // 삭제 실행
    const stmt = db.prepare('DELETE FROM apiKeys WHERE id = ? AND userId = ?');
    stmt.run([id, userId]);
    stmt.free();
    saveDatabase();
    return true;
  },

  // API 키 비활성화/활성화
  toggleActive(id, userId, isActive) {
    // 업데이트 전 존재 여부 확인
    const checkStmt = db.prepare('SELECT id FROM apiKeys WHERE id = ? AND userId = ?');
    checkStmt.bind([id, userId]);
    const exists = checkStmt.step();
    checkStmt.free();
    
    if (!exists) {
      return false; // 존재하지 않음
    }
    
    // 업데이트 실행
    const stmt = db.prepare('UPDATE apiKeys SET isActive = ? WHERE id = ? AND userId = ?');
    stmt.run([isActive ? 1 : 0, id, userId]);
    stmt.free();
    saveDatabase();
    return true;
  }
};

// API 키 사용 이력 관리 함수
export const apiKeyUsageDB = {
  // 사용 이력 추가
  create(usageData) {
    const now = new Date().toISOString();
    const stmt = db.prepare(
      'INSERT INTO apiKeyUsage (apiKeyId, endpoint, method, ipAddress, userAgent, statusCode, createdAt) VALUES (?, ?, ?, ?, ?, ?, ?)'
    );
    stmt.run([
      usageData.apiKeyId,
      usageData.endpoint,
      usageData.method,
      usageData.ipAddress || null,
      usageData.userAgent || null,
      usageData.statusCode || null,
      now
    ]);
    stmt.free();
    saveDatabase();
  },

  // API 키별 사용 이력 조회
  findByApiKeyId(apiKeyId, limit = 100) {
    const stmt = db.prepare('SELECT * FROM apiKeyUsage WHERE apiKeyId = ? ORDER BY createdAt DESC LIMIT ?');
    stmt.bind([apiKeyId, limit]);
    const usages = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      usages.push({
        id: row.id,
        apiKeyId: row.apiKeyId,
        endpoint: row.endpoint,
        method: row.method,
        ipAddress: row.ipAddress,
        userAgent: row.userAgent,
        statusCode: row.statusCode,
        createdAt: row.createdAt
      });
    }
    stmt.free();
    return usages;
  }
};

// 데이터베이스 스키마 조회 함수
export function getSchema() {
  if (!db) {
    console.error('[DB] 데이터베이스가 초기화되지 않았습니다.');
    return {};
  }
  
  const tables = ['users', 'news', 'radioSongs', 'books', 'apiKeys', 'apiKeyUsage', 'error_logs', 'sr_requests', 'sr_history', 'confluence_cache', 'git_commits', 'db_changes'];
  const schema = {};
  
  tables.forEach(tableName => {
    try {
      // sql.js에서는 PRAGMA가 제대로 작동하지 않을 수 있으므로
      // CREATE TABLE 문을 파싱하여 스키마 정보 추출
      const stmt = db.prepare(`
        SELECT sql FROM sqlite_master 
        WHERE type='table' AND name=?
      `);
      stmt.bind([tableName]);
      
      let createSql = null;
      if (stmt.step()) {
        const row = stmt.getAsObject();
        createSql = row.sql;
      }
      stmt.free();
      
      if (createSql) {
        // CREATE TABLE 문에서 컬럼 정보 추출
        const columns = parseTableSchema(createSql);
        schema[tableName] = columns;
      } else {
        // 테이블이 없으면 빈 배열
        schema[tableName] = [];
      }
    } catch (error) {
      console.error(`[DB] 테이블 ${tableName} 스키마 조회 오류:`, error);
      // 오류 발생 시 기본 스키마 정보 반환
      schema[tableName] = getDefaultSchema(tableName);
    }
  });
  
  return schema;
}

// CREATE TABLE 문 파싱 헬퍼 함수
function parseTableSchema(createSql) {
  const columns = [];
  
  try {
    if (!createSql) {
      return columns;
    }
    
    // CREATE TABLE 문에서 컬럼 정의 부분 추출
    // 여러 줄과 괄호를 고려한 정규식
    const match = createSql.match(/CREATE\s+TABLE[^(]*\(([\s\S]+)\)/i);
    if (!match) {
      return columns;
    }
    
    // 괄호 안의 내용 추출 (FOREIGN KEY 제약 조건 제외)
    let columnDefs = match[1];
    
    // FOREIGN KEY 제약 조건 제거
    columnDefs = columnDefs.replace(/FOREIGN\s+KEY[^,)]+/gi, '');
    
    // 쉼표로 분리 (단순 분리)
    const defs = columnDefs.split(',').map(s => s.trim()).filter(s => s.length > 0);
    let cid = 0;
    
    defs.forEach(def => {
      // 빈 문자열이나 FOREIGN KEY만 있는 경우 제외
      if (!def || def.length === 0 || def.toUpperCase().trim().startsWith('FOREIGN')) {
        return;
      }
      
      const parts = def.trim().split(/\s+/);
      if (parts.length === 0) return;
      
      const name = parts[0].replace(/["`\[\]]/g, '');
      if (!name || name.length === 0) return;
      
      let type = 'TEXT';
      let notnull = false;
      let pk = false;
      let dflt_value = null;
      
      // 타입 추출
      if (parts.length > 1) {
        type = parts[1].toUpperCase().replace(/[()]/g, '');
      }
      
      // 제약 조건 확인
      const defUpper = def.toUpperCase();
      notnull = defUpper.includes('NOT NULL');
      pk = defUpper.includes('PRIMARY KEY') || (defUpper.includes('PRIMARY') && defUpper.includes('KEY'));
      
      // 기본값 추출
      const defaultMatch = def.match(/DEFAULT\s+([^\s,)]+)/i);
      if (defaultMatch) {
        dflt_value = defaultMatch[1].replace(/['"]/g, '');
      }
      
      columns.push({
        cid: cid++,
        name: name,
        type: type,
        notnull: notnull,
        dflt_value: dflt_value,
        pk: pk
      });
    });
  } catch (error) {
    console.error('[DB] CREATE TABLE 파싱 오류:', error);
    console.error('[DB] CREATE SQL:', createSql);
  }
  
  return columns;
}

// 기본 스키마 정보 반환 (파싱 실패 시)
function getDefaultSchema(tableName) {
  const defaultSchemas = {
    users: [
      { cid: 0, name: 'id', type: 'INTEGER', notnull: true, dflt_value: null, pk: true },
      { cid: 1, name: 'email', type: 'TEXT', notnull: true, dflt_value: null, pk: false },
      { cid: 2, name: 'password', type: 'TEXT', notnull: true, dflt_value: null, pk: false },
      { cid: 3, name: 'name', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 4, name: 'createdAt', type: 'TEXT', notnull: true, dflt_value: null, pk: false },
      { cid: 5, name: 'updatedAt', type: 'TEXT', notnull: true, dflt_value: null, pk: false }
    ],
    news: [
      { cid: 0, name: 'id', type: 'INTEGER', notnull: true, dflt_value: null, pk: true },
      { cid: 1, name: 'userId', type: 'INTEGER', notnull: false, dflt_value: null, pk: false },
      { cid: 2, name: 'title', type: 'TEXT', notnull: true, dflt_value: null, pk: false },
      { cid: 3, name: 'summary', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 4, name: 'date', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 5, name: 'source', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 6, name: 'category', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 7, name: 'keyword', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 8, name: 'url', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 9, name: 'collectedAt', type: 'TEXT', notnull: true, dflt_value: null, pk: false },
      { cid: 10, name: 'publishedDate', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 11, name: 'importanceStars', type: 'INTEGER', notnull: false, dflt_value: null, pk: false },
      { cid: 12, name: 'importanceValue', type: 'INTEGER', notnull: false, dflt_value: null, pk: false }
    ],
    radioSongs: [
      { cid: 0, name: 'id', type: 'INTEGER', notnull: true, dflt_value: null, pk: true },
      { cid: 1, name: 'userId', type: 'INTEGER', notnull: false, dflt_value: null, pk: false },
      { cid: 2, name: 'title', type: 'TEXT', notnull: true, dflt_value: null, pk: false },
      { cid: 3, name: 'artist', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 4, name: 'genre', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 5, name: 'count', type: 'INTEGER', notnull: false, dflt_value: '1', pk: false },
      { cid: 6, name: 'lastPlayed', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 7, name: 'firstPlayed', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 8, name: 'dates', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 9, name: 'stations', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 10, name: 'collectedAt', type: 'TEXT', notnull: true, dflt_value: null, pk: false }
    ],
    books: [
      { cid: 0, name: 'id', type: 'INTEGER', notnull: true, dflt_value: null, pk: true },
      { cid: 1, name: 'userId', type: 'INTEGER', notnull: false, dflt_value: null, pk: false },
      { cid: 2, name: 'title', type: 'TEXT', notnull: true, dflt_value: null, pk: false },
      { cid: 3, name: 'authors', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 4, name: 'description', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 5, name: 'imageUrl', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 6, name: 'previewLink', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 7, name: 'publishedDate', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 8, name: 'categories', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 9, name: 'collectedAt', type: 'TEXT', notnull: true, dflt_value: null, pk: false }
    ],
    apiKeys: [
      { cid: 0, name: 'id', type: 'INTEGER', notnull: true, dflt_value: null, pk: true },
      { cid: 1, name: 'userId', type: 'INTEGER', notnull: true, dflt_value: null, pk: false },
      { cid: 2, name: 'apiKey', type: 'TEXT', notnull: true, dflt_value: null, pk: false },
      { cid: 3, name: 'name', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 4, name: 'description', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 5, name: 'isActive', type: 'INTEGER', notnull: false, dflt_value: '1', pk: false },
      { cid: 6, name: 'lastUsedAt', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 7, name: 'createdAt', type: 'TEXT', notnull: true, dflt_value: null, pk: false },
      { cid: 8, name: 'expiresAt', type: 'TEXT', notnull: false, dflt_value: null, pk: false }
    ],
    apiKeyUsage: [
      { cid: 0, name: 'id', type: 'INTEGER', notnull: true, dflt_value: null, pk: true },
      { cid: 1, name: 'apiKeyId', type: 'INTEGER', notnull: true, dflt_value: null, pk: false },
      { cid: 2, name: 'endpoint', type: 'TEXT', notnull: true, dflt_value: null, pk: false },
      { cid: 3, name: 'method', type: 'TEXT', notnull: true, dflt_value: null, pk: false },
      { cid: 4, name: 'ipAddress', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 5, name: 'userAgent', type: 'TEXT', notnull: false, dflt_value: null, pk: false },
      { cid: 6, name: 'statusCode', type: 'INTEGER', notnull: false, dflt_value: null, pk: false },
      { cid: 7, name: 'createdAt', type: 'TEXT', notnull: true, dflt_value: null, pk: false }
    ]
  };
  
  return defaultSchemas[tableName] || [];
}

// 테이블 목록 조회
export function getTables() {
  if (!db) {
    console.error('[DB] 데이터베이스가 초기화되지 않았습니다.');
    return [];
  }
  
  try {
    const stmt = db.prepare("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name");
    const tables = [];
    
    while (stmt.step()) {
      const row = stmt.getAsObject();
      tables.push(row.name);
    }
    
    stmt.free();
    return tables;
  } catch (error) {
    console.error('[DB] 테이블 목록 조회 오류:', error);
    return [];
  }
}

// 에러 로그 관련 함수
export const errorLogsDB = {
  // 모든 에러 로그 조회 (최신순)
  findAll(limit = 100, filters = {}) {
    let sql = 'SELECT * FROM error_logs WHERE 1=1';
    const params = [];
    
    // 필터 추가
    if (filters.system_type) {
      sql += ' AND system_type = ?';
      params.push(filters.system_type);
    }
    if (filters.severity) {
      sql += ' AND severity = ?';
      params.push(filters.severity);
    }
    if (filters.error_type) {
      sql += ' AND error_type = ?';
      params.push(filters.error_type);
    }
    if (filters.start_date) {
      sql += ' AND timestamp >= ?';
      params.push(filters.start_date);
    }
    if (filters.end_date) {
      sql += ' AND timestamp <= ?';
      params.push(filters.end_date);
    }
    
    sql += ' ORDER BY created_at DESC LIMIT ?';
    params.push(limit);
    
    const stmt = db.prepare(sql);
    stmt.bind(params);
    const logs = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      logs.push({
        id: row.id,
        log_content: row.log_content,
        log_type: row.log_type,
        parsed_data: row.parsed_data ? JSON.parse(row.parsed_data) : null,
        system_type: row.system_type,
        severity: row.severity,
        resource_type: row.resource_type,
        service_name: row.service_name,
        file_path: row.file_path,
        line_number: row.line_number,
        error_type: row.error_type,
        error_category: row.error_category,
        timestamp: row.timestamp,
        created_at: row.created_at,
        updated_at: row.updated_at
      });
    }
    stmt.free();
    return logs;
  },

  // ID로 에러 로그 조회
  findById(id) {
    const stmt = db.prepare('SELECT * FROM error_logs WHERE id = ?');
    stmt.bind([id]);
    let log = null;
    if (stmt.step()) {
      const row = stmt.getAsObject();
      log = {
        id: row.id,
        log_content: row.log_content,
        log_type: row.log_type,
        parsed_data: row.parsed_data ? JSON.parse(row.parsed_data) : null,
        system_type: row.system_type,
        severity: row.severity,
        resource_type: row.resource_type,
        service_name: row.service_name,
        file_path: row.file_path,
        line_number: row.line_number,
        error_type: row.error_type,
        error_category: row.error_category,
        timestamp: row.timestamp,
        created_at: row.created_at,
        updated_at: row.updated_at
      };
    }
    stmt.free();
    return log;
  },

  // 에러 로그 생성
  create(logData) {
    const now = new Date().toISOString();
    
    // parsed_data에서 메타데이터 추출
    const metadata = logData.parsed_data || {};
    const systemType = metadata.system_type || logData.system_type || null;
    const severity = metadata.severity || logData.severity || null;
    const resourceType = metadata.resource?.type || logData.resource_type || null;
    const serviceName = metadata.service?.name || logData.service_name || null;
    const filePath = metadata.location?.file || logData.file_path || null;
    const lineNumber = metadata.location?.line || logData.line_number || null;
    const errorType = metadata.error?.type || logData.error_type || null;
    const errorCategory = metadata.error?.category || logData.error_category || null;
    const timestamp = metadata.timestamp || logData.timestamp || now;
    
    const stmt = db.prepare(
      'INSERT INTO error_logs (log_content, log_type, parsed_data, system_type, severity, resource_type, service_name, file_path, line_number, error_type, error_category, timestamp, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    );
    stmt.run([
      logData.log_content,
      logData.log_type || null,
      logData.parsed_data ? JSON.stringify(logData.parsed_data) : null,
      systemType,
      severity,
      resourceType,
      serviceName,
      filePath,
      lineNumber,
      errorType,
      errorCategory,
      timestamp,
      now,
      now
    ]);
    stmt.free();
    saveDatabase();

    // 생성된 로그 조회
    const stmt2 = db.prepare('SELECT * FROM error_logs WHERE id = last_insert_rowid()');
    let log = null;
    if (stmt2.step()) {
      const row = stmt2.getAsObject();
      log = {
        id: row.id,
        log_content: row.log_content,
        log_type: row.log_type,
        parsed_data: row.parsed_data ? JSON.parse(row.parsed_data) : null,
        system_type: row.system_type,
        severity: row.severity,
        resource_type: row.resource_type,
        service_name: row.service_name,
        file_path: row.file_path,
        line_number: row.line_number,
        error_type: row.error_type,
        error_category: row.error_category,
        timestamp: row.timestamp,
        created_at: row.created_at,
        updated_at: row.updated_at
      };
    }
    stmt2.free();
    return log;
  },

  // 에러 로그 업데이트
  update(id, updateData) {
    const now = new Date().toISOString();
    const fields = [];
    const values = [];

    if (updateData.log_content) {
      fields.push('log_content = ?');
      values.push(updateData.log_content);
    }
    if (updateData.log_type !== undefined) {
      fields.push('log_type = ?');
      values.push(updateData.log_type);
    }
    if (updateData.parsed_data !== undefined) {
      fields.push('parsed_data = ?');
      values.push(updateData.parsed_data ? JSON.stringify(updateData.parsed_data) : null);
      
      // parsed_data에서 메타데이터 추출하여 업데이트
      const metadata = updateData.parsed_data || {};
      if (metadata.system_type) {
        fields.push('system_type = ?');
        values.push(metadata.system_type);
      }
      if (metadata.severity) {
        fields.push('severity = ?');
        values.push(metadata.severity);
      }
      if (metadata.resource?.type) {
        fields.push('resource_type = ?');
        values.push(metadata.resource.type);
      }
      if (metadata.service?.name) {
        fields.push('service_name = ?');
        values.push(metadata.service.name);
      }
      if (metadata.location?.file) {
        fields.push('file_path = ?');
        values.push(metadata.location.file);
      }
      if (metadata.location?.line) {
        fields.push('line_number = ?');
        values.push(metadata.location.line);
      }
      if (metadata.error?.type) {
        fields.push('error_type = ?');
        values.push(metadata.error.type);
      }
      if (metadata.error?.category) {
        fields.push('error_category = ?');
        values.push(metadata.error.category);
      }
      if (metadata.timestamp) {
        fields.push('timestamp = ?');
        values.push(metadata.timestamp);
      }
    }
    
    // 직접 필드 업데이트
    if (updateData.system_type !== undefined) {
      fields.push('system_type = ?');
      values.push(updateData.system_type);
    }
    if (updateData.severity !== undefined) {
      fields.push('severity = ?');
      values.push(updateData.severity);
    }
    if (updateData.resource_type !== undefined) {
      fields.push('resource_type = ?');
      values.push(updateData.resource_type);
    }
    if (updateData.service_name !== undefined) {
      fields.push('service_name = ?');
      values.push(updateData.service_name);
    }
    if (updateData.file_path !== undefined) {
      fields.push('file_path = ?');
      values.push(updateData.file_path);
    }
    if (updateData.line_number !== undefined) {
      fields.push('line_number = ?');
      values.push(updateData.line_number);
    }
    if (updateData.error_type !== undefined) {
      fields.push('error_type = ?');
      values.push(updateData.error_type);
    }
    if (updateData.error_category !== undefined) {
      fields.push('error_category = ?');
      values.push(updateData.error_category);
    }
    if (updateData.timestamp !== undefined) {
      fields.push('timestamp = ?');
      values.push(updateData.timestamp);
    }
    
    fields.push('updated_at = ?');
    values.push(now);
    values.push(id);

    const sql = `UPDATE error_logs SET ${fields.join(', ')} WHERE id = ?`;
    const stmt = db.prepare(sql);
    stmt.run(values);
    stmt.free();
    saveDatabase();

    return this.findById(id);
  },

  // 에러 로그 삭제
  delete(id) {
    const checkStmt = db.prepare('SELECT id FROM error_logs WHERE id = ?');
    checkStmt.bind([id]);
    const exists = checkStmt.step();
    checkStmt.free();
    
    if (!exists) {
      return false;
    }
    
    const stmt = db.prepare('DELETE FROM error_logs WHERE id = ?');
    stmt.run([id]);
    stmt.free();
    saveDatabase();
    return true;
  }
};

// SR 요청 관련 함수
export const srRequestsDB = {
  // 모든 SR 요청 조회
  findAll(limit = 100, filters = {}) {
    let sql = 'SELECT * FROM sr_requests WHERE 1=1';
    const params = [];
    
    if (filters.status) {
      sql += ' AND status = ?';
      params.push(filters.status);
    }
    if (filters.priority) {
      sql += ' AND priority = ?';
      params.push(filters.priority);
    }
    if (filters.userId) {
      sql += ' AND userId = ?';
      params.push(filters.userId);
    }
    
    sql += ' ORDER BY created_at DESC LIMIT ?';
    params.push(limit);
    
    const stmt = db.prepare(sql);
    stmt.bind(params);
    const requests = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      requests.push({
        id: row.id,
        userId: row.userId,
        sr_number: row.sr_number,
        title: row.title,
        description: row.description,
        confluence_url: row.confluence_url,
        confluence_key: row.confluence_key,
        confluence_page_id: row.confluence_page_id,
        confluence_content: row.confluence_content,
        source_type: row.source_type,
        status: row.status,
        priority: row.priority,
        category: row.category,
        tags: row.tags ? row.tags.split(',') : [],
        related_error_log_ids: row.related_error_log_ids ? row.related_error_log_ids.split(',').map(Number) : [],
        created_at: row.created_at,
        updated_at: row.updated_at
      });
    }
    stmt.free();
    return requests;
  },

  // ID로 SR 요청 조회
  findById(id) {
    const stmt = db.prepare('SELECT * FROM sr_requests WHERE id = ?');
    stmt.bind([id]);
    let request = null;
    if (stmt.step()) {
      const row = stmt.getAsObject();
      request = {
        id: row.id,
        userId: row.userId,
        sr_number: row.sr_number,
        title: row.title,
        description: row.description,
        confluence_url: row.confluence_url,
        confluence_key: row.confluence_key,
        confluence_page_id: row.confluence_page_id,
        confluence_content: row.confluence_content,
        source_type: row.source_type,
        status: row.status,
        priority: row.priority,
        category: row.category,
        tags: row.tags ? row.tags.split(',') : [],
        related_error_log_ids: row.related_error_log_ids ? row.related_error_log_ids.split(',').map(Number) : [],
        created_at: row.created_at,
        updated_at: row.updated_at
      };
    }
    stmt.free();
    return request;
  },

  // SR 요청 생성
  create(srData) {
    const now = new Date().toISOString();
    const srNumber = srData.sr_number || `SR-${Date.now()}`;
    
    const stmt = db.prepare(
      'INSERT INTO sr_requests (userId, sr_number, title, description, confluence_url, confluence_key, confluence_page_id, confluence_content, source_type, status, priority, category, tags, related_error_log_ids, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    );
    stmt.run([
      srData.userId || null,
      srNumber,
      srData.title,
      srData.description || null,
      srData.confluence_url || null,
      srData.confluence_key || null,
      srData.confluence_page_id || null,
      srData.confluence_content || null,
      srData.source_type || 'confluence',
      srData.status || 'open',
      srData.priority || 'medium',
      srData.category || null,
      srData.tags ? srData.tags.join(',') : null,
      srData.related_error_log_ids ? srData.related_error_log_ids.join(',') : null,
      now,
      now
    ]);
    stmt.free();
    saveDatabase();
    
    // 생성된 SR 조회 (sr_number로 조회)
    const stmt2 = db.prepare('SELECT * FROM sr_requests WHERE sr_number = ? ORDER BY id DESC LIMIT 1');
    stmt2.bind([srNumber]);
    let request = null;
    if (stmt2.step()) {
      const row = stmt2.getAsObject();
      request = {
        id: row.id,
        userId: row.userId,
        sr_number: row.sr_number,
        title: row.title,
        description: row.description,
        confluence_url: row.confluence_url,
        confluence_key: row.confluence_key,
        confluence_page_id: row.confluence_page_id,
        confluence_content: row.confluence_content,
        source_type: row.source_type,
        status: row.status,
        priority: row.priority,
        category: row.category,
        tags: row.tags ? row.tags.split(',') : [],
        related_error_log_ids: row.related_error_log_ids ? row.related_error_log_ids.split(',').map(Number) : [],
        created_at: row.created_at,
        updated_at: row.updated_at
      };
    }
    stmt2.free();
    return request;
  },

  // SR 요청 업데이트
  update(id, updateData) {
    const now = new Date().toISOString();
    const fields = [];
    const values = [];
    
    if (updateData.title) {
      fields.push('title = ?');
      values.push(updateData.title);
    }
    if (updateData.description !== undefined) {
      fields.push('description = ?');
      values.push(updateData.description);
    }
    if (updateData.status) {
      fields.push('status = ?');
      values.push(updateData.status);
    }
    if (updateData.priority) {
      fields.push('priority = ?');
      values.push(updateData.priority);
    }
    if (updateData.category !== undefined) {
      fields.push('category = ?');
      values.push(updateData.category);
    }
    if (updateData.tags) {
      fields.push('tags = ?');
      values.push(Array.isArray(updateData.tags) ? updateData.tags.join(',') : updateData.tags);
    }
    
    fields.push('updated_at = ?');
    values.push(now);
    values.push(id);
    
    const sql = `UPDATE sr_requests SET ${fields.join(', ')} WHERE id = ?`;
    const stmt = db.prepare(sql);
    stmt.run(values);
    stmt.free();
    saveDatabase();
    
    return this.findById(id);
  }
};

// SR 이력 관련 함수
export const srHistoryDB = {
  // SR 이력 조회
  findBySrRequestId(srRequestId) {
    const stmt = db.prepare('SELECT * FROM sr_history WHERE sr_request_id = ? ORDER BY created_at DESC');
    stmt.bind([srRequestId]);
    const history = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      history.push({
        id: row.id,
        sr_request_id: row.sr_request_id,
        action: row.action,
        description: row.description,
        performed_by: row.performed_by,
        git_commit_hash: row.git_commit_hash,
        git_commit_message: row.git_commit_message,
        git_author: row.git_author,
        git_date: row.git_date,
        related_files: row.related_files ? row.related_files.split(',') : [],
        related_programs: row.related_programs ? row.related_programs.split(',') : [],
        created_at: row.created_at
      });
    }
    stmt.free();
    return history;
  },

  // SR 이력 생성
  create(historyData) {
    const stmt = db.prepare(
      'INSERT INTO sr_history (sr_request_id, action, description, performed_by, git_commit_hash, git_commit_message, git_author, git_date, related_files, related_programs, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    );
    stmt.run([
      historyData.sr_request_id,
      historyData.action,
      historyData.description || null,
      historyData.performed_by || null,
      historyData.git_commit_hash || null,
      historyData.git_commit_message || null,
      historyData.git_author || null,
      historyData.git_date || null,
      historyData.related_files ? historyData.related_files.join(',') : null,
      historyData.related_programs ? historyData.related_programs.join(',') : null,
      new Date().toISOString()
    ]);
    stmt.free();
    saveDatabase();
    
    const stmt2 = db.prepare('SELECT * FROM sr_history WHERE id = last_insert_rowid()');
    let history = null;
    if (stmt2.step()) {
      const row = stmt2.getAsObject();
      history = {
        id: row.id,
        sr_request_id: row.sr_request_id,
        action: row.action,
        description: row.description,
        performed_by: row.performed_by,
        git_commit_hash: row.git_commit_hash,
        git_commit_message: row.git_commit_message,
        git_author: row.git_author,
        git_date: row.git_date,
        related_files: row.related_files ? row.related_files.split(',') : [],
        related_programs: row.related_programs ? row.related_programs.split(',') : [],
        created_at: row.created_at
      };
    }
    stmt2.free();
    return history;
  }
};

// Confluence 캐시 관련 함수
export const confluenceCacheDB = {
  // Confluence key로 조회
  findByKey(confluenceKey) {
    const stmt = db.prepare('SELECT * FROM confluence_cache WHERE confluence_key = ?');
    stmt.bind([confluenceKey]);
    let cache = null;
    if (stmt.step()) {
      const row = stmt.getAsObject();
      cache = {
        id: row.id,
        confluence_key: row.confluence_key,
        page_id: row.page_id,
        title: row.title,
        content: row.content,
        url: row.url,
        space_key: row.space_key,
        last_modified: row.last_modified,
        cached_at: row.cached_at,
        expires_at: row.expires_at
      };
    }
    stmt.free();
    return cache;
  },

  // Confluence 캐시 저장/업데이트
  upsert(cacheData) {
    const existing = this.findByKey(cacheData.confluence_key);
    const now = new Date().toISOString();
    const expiresAt = cacheData.expires_at || new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();
    
    if (existing) {
      const stmt = db.prepare(
        'UPDATE confluence_cache SET page_id = ?, title = ?, content = ?, url = ?, space_key = ?, last_modified = ?, cached_at = ?, expires_at = ? WHERE confluence_key = ?'
      );
      stmt.run([
        cacheData.page_id || existing.page_id,
        cacheData.title || existing.title,
        cacheData.content || existing.content,
        cacheData.url || existing.url,
        cacheData.space_key || existing.space_key,
        cacheData.last_modified || existing.last_modified,
        now,
        expiresAt,
        cacheData.confluence_key
      ]);
      stmt.free();
    } else {
      const stmt = db.prepare(
        'INSERT INTO confluence_cache (confluence_key, page_id, title, content, url, space_key, last_modified, cached_at, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
      );
      stmt.run([
        cacheData.confluence_key,
        cacheData.page_id || null,
        cacheData.title || null,
        cacheData.content || null,
        cacheData.url || null,
        cacheData.space_key || null,
        cacheData.last_modified || null,
        now,
        expiresAt
      ]);
      stmt.free();
    }
    saveDatabase();
    return this.findByKey(cacheData.confluence_key);
  }
};

// Git 커밋 관련 함수
export const gitCommitsDB = {
  // 커밋 해시로 조회
  findByHash(commitHash) {
    const stmt = db.prepare('SELECT * FROM git_commits WHERE commit_hash = ?');
    stmt.bind([commitHash]);
    let commit = null;
    if (stmt.step()) {
      const row = stmt.getAsObject();
      commit = {
        id: row.id,
        commit_hash: row.commit_hash,
        author: row.author,
        author_email: row.author_email,
        commit_date: row.commit_date,
        commit_message: row.commit_message,
        repository_path: row.repository_path,
        branch: row.branch,
        files_changed: row.files_changed ? row.files_changed.split(',') : [],
        insertions: row.insertions,
        deletions: row.deletions,
        related_sr_id: row.related_sr_id,
        similarity_score: row.similarity_score,
        created_at: row.created_at
      };
    }
    stmt.free();
    return commit;
  },

  // 유사 SR 검색
  findSimilar(keywords, limit = 10) {
    let sql = 'SELECT * FROM git_commits WHERE 1=1';
    const params = [];
    
    if (keywords && keywords.length > 0) {
      const keywordConditions = keywords.map(() => 'commit_message LIKE ?');
      sql += ` AND (${keywordConditions.join(' OR ')})`;
      keywords.forEach(keyword => {
        params.push(`%${keyword}%`);
      });
    }
    
    sql += ' ORDER BY similarity_score DESC, commit_date DESC LIMIT ?';
    params.push(limit);
    
    const stmt = db.prepare(sql);
    stmt.bind(params);
    const commits = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      commits.push({
        id: row.id,
        commit_hash: row.commit_hash,
        author: row.author,
        author_email: row.author_email,
        commit_date: row.commit_date,
        commit_message: row.commit_message,
        repository_path: row.repository_path,
        branch: row.branch,
        files_changed: row.files_changed ? row.files_changed.split(',') : [],
        insertions: row.insertions,
        deletions: row.deletions,
        related_sr_id: row.related_sr_id,
        similarity_score: row.similarity_score,
        created_at: row.created_at
      });
    }
    stmt.free();
    return commits;
  },

  // Git 커밋 저장
  create(commitData) {
    const existing = this.findByHash(commitData.commit_hash);
    if (existing) {
      return existing;
    }
    
    const stmt = db.prepare(
      'INSERT INTO git_commits (commit_hash, author, author_email, commit_date, commit_message, repository_path, branch, files_changed, insertions, deletions, related_sr_id, similarity_score, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    );
    stmt.run([
      commitData.commit_hash,
      commitData.author || null,
      commitData.author_email || null,
      commitData.commit_date || null,
      commitData.commit_message || null,
      commitData.repository_path || null,
      commitData.branch || null,
      commitData.files_changed ? commitData.files_changed.join(',') : null,
      commitData.insertions || 0,
      commitData.deletions || 0,
      commitData.related_sr_id || null,
      commitData.similarity_score || 0,
      new Date().toISOString()
    ]);
    stmt.free();
    saveDatabase();
    
    return this.findByHash(commitData.commit_hash);
  }
};

// DB 변경 이력 관련 함수
export const dbChangesDB = {
  // 모든 DB 변경 이력 조회
  findAll(limit = 100, filters = {}) {
    let sql = 'SELECT * FROM db_changes WHERE 1=1';
    const params = [];
    
    if (filters.change_type) {
      sql += ' AND change_type = ?';
      params.push(filters.change_type);
    }
    if (filters.table_name) {
      sql += ' AND table_name = ?';
      params.push(filters.table_name);
    }
    if (filters.related_sr_id) {
      sql += ' AND related_sr_id = ?';
      params.push(filters.related_sr_id);
    }
    
    sql += ' ORDER BY detected_at DESC LIMIT ?';
    params.push(limit);
    
    const stmt = db.prepare(sql);
    stmt.bind(params);
    const changes = [];
    while (stmt.step()) {
      const row = stmt.getAsObject();
      changes.push({
        id: row.id,
        change_type: row.change_type,
        table_name: row.table_name,
        column_name: row.column_name,
        old_value: row.old_value,
        new_value: row.new_value,
        change_description: row.change_description,
        sql_query: row.sql_query,
        related_sr_id: row.related_sr_id,
        detected_at: row.detected_at
      });
    }
    stmt.free();
    return changes;
  },

  // DB 변경 이력 생성
  create(changeData) {
    const stmt = db.prepare(
      'INSERT INTO db_changes (change_type, table_name, column_name, old_value, new_value, change_description, sql_query, related_sr_id, detected_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
    );
    stmt.run([
      changeData.change_type,
      changeData.table_name,
      changeData.column_name || null,
      changeData.old_value || null,
      changeData.new_value || null,
      changeData.change_description || null,
      changeData.sql_query || null,
      changeData.related_sr_id || null,
      new Date().toISOString()
    ]);
    stmt.free();
    saveDatabase();
    
    // 생성된 변경 이력 조회 (detected_at으로 최신 항목 조회)
    const detectedAt = new Date().toISOString();
    const stmt2 = db.prepare('SELECT * FROM db_changes WHERE detected_at = ? ORDER BY id DESC LIMIT 1');
    stmt2.bind([detectedAt]);
    let change = null;
    if (stmt2.step()) {
      const row = stmt2.getAsObject();
      change = {
        id: row.id,
        change_type: row.change_type,
        table_name: row.table_name,
        column_name: row.column_name,
        old_value: row.old_value,
        new_value: row.new_value,
        change_description: row.change_description,
        sql_query: row.sql_query,
        related_sr_id: row.related_sr_id,
        detected_at: row.detected_at
      };
    }
    stmt2.free();
    
    // detected_at으로 찾지 못한 경우, table_name과 change_type으로 조회
    if (!change) {
      const stmt3 = db.prepare('SELECT * FROM db_changes WHERE table_name = ? AND change_type = ? ORDER BY id DESC LIMIT 1');
      stmt3.bind([changeData.table_name, changeData.change_type]);
      if (stmt3.step()) {
        const row = stmt3.getAsObject();
        change = {
          id: row.id,
          change_type: row.change_type,
          table_name: row.table_name,
          column_name: row.column_name,
          old_value: row.old_value,
          new_value: row.new_value,
          change_description: row.change_description,
          sql_query: row.sql_query,
          related_sr_id: row.related_sr_id,
          detected_at: row.detected_at
        };
      }
      stmt3.free();
    }
    
    return change;
  }
};

// 기본 내보내기
export default {
  init,
  userDB,
  newsDB,
  radioSongsDB,
  booksDB,
  apiKeysDB,
  apiKeyUsageDB,
  errorLogsDB,
  srRequestsDB,
  srHistoryDB,
  confluenceCacheDB,
  gitCommitsDB,
  dbChangesDB,
  getSchema,
  getTables
};
