#!/usr/bin/env node
/**
 * 샘플 VOC 데이터 생성 스크립트
 * 
 * Confluence VOC 3개와 데이터 변경 VOC 3개를 생성합니다.
 */

import { init, srRequestsDB, dbChangesDB } from './database.js';

async function createSampleVocData() {
  try {
    // 데이터베이스 초기화
    await init();
    console.log('[VOC 샘플 데이터] 데이터베이스 초기화 완료');

    // Confluence VOC 샘플 데이터 3개 (현재 시스템 기반)
    const confluenceVocs = [
      {
        title: '뉴스 검색 기능 개선 요청 - 경제 뉴스 알람 기능 추가',
        description: '현재 시스템의 뉴스 검색 기능은 잘 작동하고 있으나, 경제 뉴스에 대한 실시간 알람 기능이 필요합니다.\n\n현재 상황:\n- 뉴스 검색 API는 정상 작동 중 (News API 연동)\n- 경제 뉴스 검색 기능 존재\n- 알람 기능은 UI에 버튼만 있고 실제 동작 미구현\n\n요구사항:\n- 경제 뉴스 알람 기능 실제 구현\n- 사용자별 알람 설정 저장 (users 테이블 또는 별도 설정 테이블)\n- 알람 발송 시 이메일 또는 시스템 알림 기능\n- 알람 이력 관리 기능',
        confluence_url: 'https://confluence.example.com/pages/viewpage.action?pageId=123456',
        confluence_key: '123456',
        confluence_page_id: '123456',
        confluence_content: '경제 뉴스 알람 기능 추가에 대한 상세 요구사항이 Confluence에 문서화되어 있습니다. 현재 App.vue에 알람 버튼이 있으나 실제 기능 구현이 필요합니다.',
        source_type: 'confluence',
        status: 'open',
        priority: 'high',
        category: '기능개선',
        tags: ['뉴스', '알람', '경제뉴스', '기능추가']
      },
      {
        title: 'API 키 사용량 모니터링 및 제한 기능 추가',
        description: '현재 apiKeys와 apiKeyUsage 테이블이 존재하지만, 사용량 제한 및 모니터링 기능이 부족합니다.\n\n현재 상황:\n- apiKeys 테이블: API 키 저장 및 관리\n- apiKeyUsage 테이블: 사용 이력 저장\n- 사용량 제한 기능 없음\n- 모니터링 대시보드 없음\n\n요구사항:\n- API 키별 일일/월간 사용량 제한 기능\n- 사용량 초과 시 자동 차단\n- 사용량 모니터링 대시보드\n- 사용량 알림 기능 (이메일 또는 시스템 알림)',
        confluence_url: 'https://confluence.example.com/pages/viewpage.action?pageId=234567',
        confluence_key: '234567',
        confluence_page_id: '234567',
        confluence_content: 'API 키 사용량 모니터링 및 제한 기능 추가에 대한 상세 요구사항이 Confluence에 문서화되어 있습니다. api-server.js의 API 키 검증 로직에 사용량 체크 기능을 추가해야 합니다.',
        source_type: 'confluence',
        status: 'in_progress',
        priority: 'critical',
        category: '보안강화',
        tags: ['API키', '모니터링', '사용량제한', '보안']
      },
      {
        title: '에러 로그 분석 결과와 SR 자동 연동 기능',
        description: '현재 error_logs 테이블에 에러 로그가 저장되고 있으나, 심각한 에러 발생 시 자동으로 SR을 생성하는 기능이 없습니다.\n\n현재 상황:\n- error_logs 테이블: 에러 로그 저장 및 분석\n- mcp-error-log-analyzer.py: 에러 로그 분석 MCP 서버\n- 심각한 에러 발생 시 수동으로 SR 생성 필요\n\n요구사항:\n- ERROR 또는 CRITICAL 레벨 에러 발생 시 자동 SR 생성\n- 에러 로그와 SR 자동 연결 (related_error_log_ids)\n- 에러 패턴 분석을 통한 유사 SR 자동 추천\n- 에러 해결 시 SR 자동 업데이트',
        confluence_url: 'https://confluence.example.com/pages/viewpage.action?pageId=345678',
        confluence_key: '345678',
        confluence_page_id: '345678',
        confluence_content: '에러 로그 분석 결과와 SR 자동 연동 기능에 대한 상세 요구사항이 Confluence에 문서화되어 있습니다. error_logs 테이블과 sr_requests 테이블을 연동하는 로직이 필요합니다.',
        source_type: 'confluence',
        status: 'open',
        priority: 'high',
        category: '자동화',
        tags: ['에러로그', 'SR연동', '자동화', '모니터링']
      }
    ];

    console.log('\n[VOC 샘플 데이터] Confluence VOC 데이터 생성 중...');
    for (const voc of confluenceVocs) {
      const sr = srRequestsDB.create(voc);
      console.log(`  ✓ SR 생성: ${sr.sr_number} - ${sr.title}`);
    }

    // 데이터 변경 VOC 샘플 데이터 3개 (현재 시스템 테이블 기반)
    const dbChangeVocs = [
      {
        title: 'users 테이블에 phone 컬럼 추가',
        description: '사용자 연락처 정보를 저장하기 위해 users 테이블에 phone 컬럼을 추가해야 합니다.\n\n현재 users 테이블 구조:\n- id, email, password, name, createdAt, updatedAt\n\n변경 사항:\n- 테이블: users\n- 컬럼명: phone\n- 데이터 타입: TEXT\n- NULL 허용: YES\n- 기본값: NULL\n\n영향도:\n- database.js의 users 테이블 스키마 변경 필요\n- userDB 관련 함수 수정 필요\n- 기존 사용자 데이터는 phone 값이 NULL로 설정됨',
        source_type: 'manual',
        status: 'open',
        priority: 'medium',
        category: '데이터베이스변경',
        tags: ['데이터베이스', '스키마변경', 'users테이블', '컬럼추가']
      },
      {
        title: 'news 테이블에 viewCount 컬럼 추가 및 인덱스 생성',
        description: '뉴스 조회수를 추적하기 위해 news 테이블에 viewCount 컬럼을 추가하고, 성능 향상을 위해 인덱스를 생성합니다.\n\n현재 news 테이블 구조:\n- id, userId, title, summary, date, source, category, keyword, url, collectedAt, publishedDate, importanceStars, importanceValue\n\n변경 사항:\n- 테이블: news\n- 컬럼명: viewCount\n- 데이터 타입: INTEGER\n- 기본값: 0\n- 인덱스: category, publishedDate에 복합 인덱스 추가\n\n영향도:\n- database.js의 news 테이블 스키마 변경 필요\n- newsDB 관련 함수 수정 필요\n- 뉴스 조회 시 viewCount 증가 로직 추가 필요\n- api-server.js의 뉴스 조회 API 수정 필요',
        source_type: 'manual',
        status: 'in_progress',
        priority: 'high',
        category: '데이터베이스변경',
        tags: ['데이터베이스', '스키마변경', 'news테이블', '인덱스', '성능개선']
      },
      {
        title: 'error_logs 테이블에 error_code 컬럼 추가',
        description: '에러를 분류하고 추적하기 쉽도록 error_logs 테이블에 error_code 컬럼을 추가합니다.\n\n현재 error_logs 테이블 구조:\n- id, log_content, log_type, parsed_data, system_type, severity, resource_type, service_name, file_path, line_number, error_type, error_category, timestamp, created_at, updated_at\n\n변경 사항:\n- 테이블: error_logs\n- 컬럼명: error_code\n- 데이터 타입: TEXT\n- NULL 허용: YES\n- 설명: 에러를 식별하기 위한 고유 코드 (예: ERR-DB-001, ERR-AUTH-002)\n\n영향도:\n- database.js의 error_logs 테이블 스키마 변경 필요\n- errorLogsDB 관련 함수 수정 필요\n- mcp-error-log-analyzer.py에서 error_code 생성 로직 추가 필요\n- 에러 코드 체계 정의 필요',
        source_type: 'manual',
        status: 'open',
        priority: 'medium',
        category: '데이터베이스변경',
        tags: ['데이터베이스', '스키마변경', 'error_logs테이블', '에러관리']
      }
    ];

    console.log('\n[VOC 샘플 데이터] 데이터 변경 VOC 데이터 생성 중...');
    for (const voc of dbChangeVocs) {
      const sr = srRequestsDB.create(voc);
      console.log(`  ✓ SR 생성: ${sr.sr_number} - ${sr.title}`);

      // 각 SR에 대한 DB 변경 이력도 생성
      let dbChange = null;
      if (sr.title.includes('phone 컬럼')) {
        dbChange = dbChangesDB.create({
          change_type: 'column_add',
          table_name: 'users',
          column_name: 'phone',
          change_description: 'users 테이블에 phone 컬럼 추가 - 사용자 연락처 정보 저장용',
          sql_query: 'ALTER TABLE users ADD COLUMN phone TEXT;',
          related_sr_id: sr.id
        });
        console.log(`    → DB 변경 이력 생성: ${dbChange.change_type} - ${dbChange.table_name}.${dbChange.column_name}`);
      } else if (sr.title.includes('viewCount')) {
        dbChange = dbChangesDB.create({
          change_type: 'column_add',
          table_name: 'news',
          column_name: 'viewCount',
          change_description: 'news 테이블에 viewCount 컬럼 추가 및 인덱스 생성 - 뉴스 조회수 추적 및 성능 향상',
          sql_query: 'ALTER TABLE news ADD COLUMN viewCount INTEGER DEFAULT 0; CREATE INDEX idx_news_category_date ON news(category, publishedDate);',
          related_sr_id: sr.id
        });
        console.log(`    → DB 변경 이력 생성: ${dbChange.change_type} - ${dbChange.table_name}.${dbChange.column_name}`);
      } else if (sr.title.includes('error_code')) {
        dbChange = dbChangesDB.create({
          change_type: 'column_add',
          table_name: 'error_logs',
          column_name: 'error_code',
          change_description: 'error_logs 테이블에 error_code 컬럼 추가 - 에러 분류 및 추적 용이성 향상',
          sql_query: 'ALTER TABLE error_logs ADD COLUMN error_code TEXT;',
          related_sr_id: sr.id
        });
        console.log(`    → DB 변경 이력 생성: ${dbChange.change_type} - ${dbChange.table_name}.${dbChange.column_name}`);
      }
    }

    console.log('\n[VOC 샘플 데이터] 샘플 데이터 생성 완료!');
    console.log(`  - Confluence VOC: ${confluenceVocs.length}개`);
    console.log(`  - 데이터 변경 VOC: ${dbChangeVocs.length}개`);
    console.log('\nVOC 관리 화면에서 확인할 수 있습니다.');

  } catch (error) {
    console.error('[VOC 샘플 데이터] 오류 발생:', error);
    process.exit(1);
  }
}

createSampleVocData();

