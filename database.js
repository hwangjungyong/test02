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
    )`
  ];

  tables.forEach(sql => {
    db.run(sql);
  });
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
  
  const tables = ['users', 'news', 'radioSongs', 'books', 'apiKeys', 'apiKeyUsage'];
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

// 기본 내보내기
export default {
  init,
  userDB,
  newsDB,
  radioSongsDB,
  booksDB,
  apiKeysDB,
  apiKeyUsageDB,
  getSchema,
  getTables
};
