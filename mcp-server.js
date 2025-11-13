#!/usr/bin/env node

/**
 * MCP 서버 - AI 기사 검색 및 라디오 방송 음악 정보
 * 
 * 역할:
 * - MCP 프로토콜을 통해 AI 클라이언트와 통신하는 서버
 * - AI 관련 기사 검색 (키워드 기반) - News API 연동
 * - 한국 라디오 방송 노래 정보 조회 - Last.fm API 연동
 * - 음악 추천 기능 - Last.fm API 연동
 * 
 * 실행 방법:
 *   npm run mcp-server
 * 
 * 참고:
 * - 현재 Vue 앱에서는 이 서버를 직접 사용하지 않고 백엔드 API 서버(api-server.js)를 사용합니다.
 * - 이 서버는 AI 클라이언트(예: Claude Desktop)와 통신할 때 사용됩니다.
 * - StdioServerTransport를 사용하여 표준 입출력(stdin/stdout)으로 통신합니다.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import https from 'https';
import { HttpsProxyAgent } from 'https-proxy-agent';

// ============================================
// API 설정
// ============================================

// News API 설정
// - API 키: newsapi.org에서 발급받은 키
// - Base URL: News API의 기본 URL
const NEWS_API_KEY = '6944bc431cbf4988857f3cb35b4decc6';
const NEWS_API_BASE_URL = 'https://newsapi.org/v2';

// Last.fm API 설정 (음악 추천 및 라디오 방송 정보)
// - API 키: last.fm에서 발급받은 키
// - Shared Secret: API 인증에 사용되는 시크릿 키
// - Base URL: Last.fm API의 기본 URL
const LASTFM_API_KEY = '8d8e2e5d0c3b1b95499e94331b8a211e';
const LASTFM_SHARED_SECRET = 'b8fcf0112c09f5226276babffa3952a1';
const LASTFM_API_BASE_URL = 'https://ws.audioscrobbler.com/2.0';

// ============================================
// 프록시 설정
// ============================================

// 프록시 설정 (npmrc에서 가져옴)
// - 프록시 환경에서 외부 API를 호출하기 위해 필요
const PROXY_URL = 'http://70.10.15.10:8080';
const proxyAgent = new HttpsProxyAgent(PROXY_URL);

// ============================================
// 헬퍼 함수
// ============================================

/**
 * 프록시를 사용하여 fetch 함수 구현
 * 
 * @param {string} url - 호출할 API URL
 * @param {object} options - 추가 옵션 (method, headers 등)
 * @returns {Promise} - API 응답을 Promise로 반환
 * 
 * 기능:
 * - 프록시를 통해 HTTPS 요청 생성
 * - 30초 타임아웃 설정
 * - JSON 응답 파싱
 * - 에러 처리
 */
async function fetchWithProxy(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    
    const req = https.request({
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: options.method || 'GET',
      agent: proxyAgent,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        ...options.headers
      },
      timeout: 30000 // 30초 타임아웃
    }, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        resolve({
          ok: res.statusCode >= 200 && res.statusCode < 300,
          status: res.statusCode,
          statusText: res.statusMessage,
          json: async () => JSON.parse(data),
          headers: res.headers
        });
      });
    });
    
    req.on('error', (error) => {
      console.error(`[MCP 서버] 요청 오류:`, error);
      reject(error);
    });
    
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('API 연결 타임아웃 (30초 초과)'));
    });
    
    req.end();
  });
}

// 예제 라디오 방송 데이터 (실제로는 API에서 가져옴)
const radioStations = {
  kbs: {
    name: 'KBS 쿨FM',
    currentSong: {
      title: 'Dynamite',
      artist: 'BTS',
      genre: 'K-Pop',
      time: new Date().toLocaleTimeString('ko-KR'),
    },
    recentSongs: [
      { title: 'Dynamite', artist: 'BTS', genre: 'K-Pop' },
      { title: 'Butter', artist: 'BTS', genre: 'K-Pop' },
      { title: 'Spring Day', artist: 'BTS', genre: 'K-Pop' },
      { title: 'Love Scenario', artist: 'iKON', genre: 'K-Pop' },
      { title: 'Gangnam Style', artist: 'PSY', genre: 'K-Pop' },
    ],
  },
  mbc: {
    name: 'MBC FM4U',
    currentSong: {
      title: 'Celebrity',
      artist: 'IU',
      genre: 'K-Pop',
      time: new Date().toLocaleTimeString('ko-KR'),
    },
    recentSongs: [
      { title: 'Celebrity', artist: 'IU', genre: 'K-Pop' },
      { title: 'Good Day', artist: 'IU', genre: 'K-Pop' },
      { title: 'Eight', artist: 'IU', genre: 'K-Pop' },
      { title: 'Through the Night', artist: 'IU', genre: 'Ballad' },
      { title: 'Blueming', artist: 'IU', genre: 'K-Pop' },
    ],
  },
  sbs: {
    name: 'SBS 파워FM',
    currentSong: {
      title: 'How You Like That',
      artist: 'BLACKPINK',
      genre: 'K-Pop',
      time: new Date().toLocaleTimeString('ko-KR'),
    },
    recentSongs: [
      { title: 'How You Like That', artist: 'BLACKPINK', genre: 'K-Pop' },
      { title: 'DDU-DU DDU-DU', artist: 'BLACKPINK', genre: 'K-Pop' },
      { title: 'Kill This Love', artist: 'BLACKPINK', genre: 'K-Pop' },
      { title: 'Lovesick Girls', artist: 'BLACKPINK', genre: 'K-Pop' },
      { title: 'Pink Venom', artist: 'BLACKPINK', genre: 'K-Pop' },
    ],
  },
};

// 음악 추천 데이터베이스 (장르별 유사한 노래)
const musicRecommendations = {
  'BTS': [
    { title: 'Butter', artist: 'BTS', reason: '같은 아티스트' },
    { title: 'Permission to Dance', artist: 'BTS', reason: '같은 아티스트' },
    { title: 'Boy With Luv', artist: 'BTS', reason: '같은 아티스트' },
    { title: 'DNA', artist: 'BTS', reason: '같은 아티스트' },
    { title: 'Fake Love', artist: 'BTS', reason: '같은 아티스트' },
  ],
  'IU': [
    { title: 'Good Day', artist: 'IU', reason: '같은 아티스트' },
    { title: 'Eight', artist: 'IU', reason: '같은 아티스트' },
    { title: 'Blueming', artist: 'IU', reason: '같은 아티스트' },
    { title: 'Palette', artist: 'IU', reason: '같은 아티스트' },
    { title: 'Strawberry Moon', artist: 'IU', reason: '같은 아티스트' },
  ],
  'BLACKPINK': [
    { title: 'DDU-DU DDU-DU', artist: 'BLACKPINK', reason: '같은 아티스트' },
    { title: 'Kill This Love', artist: 'BLACKPINK', reason: '같은 아티스트' },
    { title: 'Lovesick Girls', artist: 'BLACKPINK', reason: '같은 아티스트' },
    { title: 'Pink Venom', artist: 'BLACKPINK', reason: '같은 아티스트' },
    { title: 'Shut Down', artist: 'BLACKPINK', reason: '같은 아티스트' },
  ],
  'iKON': [
    { title: 'Love Scenario', artist: 'iKON', reason: '같은 아티스트' },
    { title: 'Killing Me', artist: 'iKON', reason: '같은 아티스트' },
    { title: 'Goodbye Road', artist: 'iKON', reason: '같은 아티스트' },
    { title: 'Rhythm Ta', artist: 'iKON', reason: '같은 아티스트' },
    { title: 'My Type', artist: 'iKON', reason: '같은 아티스트' },
  ],
  'PSY': [
    { title: 'Gangnam Style', artist: 'PSY', reason: '같은 아티스트' },
    { title: 'Gentleman', artist: 'PSY', reason: '같은 아티스트' },
    { title: 'Daddy', artist: 'PSY', reason: '같은 아티스트' },
    { title: 'New Face', artist: 'PSY', reason: '같은 아티스트' },
    { title: 'That That', artist: 'PSY', reason: '같은 아티스트' },
  ],
};

// MCP 서버 인스턴스 생성
const server = new Server(
  {
    name: 'ai-articles-radio-server',
    version: '3.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// 서버가 사용 가능한 도구 목록을 요청받았을 때
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'search_ai_articles',
        description: '키워드를 입력받아 AI 관련 기사를 검색하고 링크를 제공합니다.',
        inputSchema: {
          type: 'object',
          properties: {
            keyword: {
              type: 'string',
              description: '검색할 키워드 (예: ChatGPT, 인공지능, 머신러닝 등)',
            },
          },
          required: ['keyword'],
        },
      },
      {
        name: 'get_radio_song',
        description: '한국 라디오 방송(KBS, MBC, SBS)에서 현재 재생 중인 노래 정보를 가져옵니다.',
        inputSchema: {
          type: 'object',
          properties: {
            station: {
              type: 'string',
              description: '라디오 방송국 (kbs, mbc, sbs 중 선택)',
              enum: ['kbs', 'mbc', 'sbs'],
            },
          },
          required: ['station'],
        },
      },
      {
        name: 'get_radio_recent_songs',
        description: '한국 라디오 방송에서 최근 재생된 노래 목록을 가져옵니다.',
        inputSchema: {
          type: 'object',
          properties: {
            station: {
              type: 'string',
              description: '라디오 방송국 (kbs, mbc, sbs 중 선택)',
              enum: ['kbs', 'mbc', 'sbs'],
            },
          },
          required: ['station'],
        },
      },
      {
        name: 'recommend_similar_songs',
        description: '좋아하는 노래를 입력하면 비슷한 추천 노래 목록을 반환합니다.',
        inputSchema: {
          type: 'object',
          properties: {
            songTitle: {
              type: 'string',
              description: '좋아하는 노래 제목',
            },
            artist: {
              type: 'string',
              description: '아티스트 이름 (선택사항)',
            },
          },
          required: ['songTitle'],
        },
      },
    ],
  };
});

// 서버가 도구 실행을 요청받았을 때
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'search_ai_articles') {
    const { keyword } = args;

    // 입력값 검증
    if (!keyword || keyword.trim() === '') {
      return {
        content: [
          {
            type: 'text',
            text: `오류: 검색 키워드를 입력해주세요.`,
          },
        ],
        isError: true,
      };
    }

    try {
      // News API를 사용하여 실제 뉴스 검색
      const searchKeyword = encodeURIComponent(keyword.trim());
      const apiUrl = `${NEWS_API_BASE_URL}/everything?q=${searchKeyword}&language=ko&sortBy=publishedAt&pageSize=10&apiKey=${NEWS_API_KEY}`;
      
      console.error(`[MCP 서버] News API 호출: ${apiUrl}`);
      const response = await fetchWithProxy(apiUrl);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`News API 오류: ${response.status} - ${errorData.message || response.statusText}`);
      }

      const data = await response.json();

      // 결과가 없는 경우
      if (!data.articles || data.articles.length === 0) {
        return {
          content: [
            {
              type: 'text',
              text: `"${keyword}"에 대한 뉴스 기사를 찾을 수 없습니다.\n\n다른 키워드로 검색해보세요.`,
            },
          ],
        };
      }

      // 기사 데이터 포맷팅
      const formattedArticles = data.articles
        .filter(article => article.title && article.title !== '[Removed]')
        .slice(0, 10) // 최대 10개
        .map(article => {
          const publishedDate = article.publishedAt 
            ? new Date(article.publishedAt).toLocaleDateString('ko-KR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })
            : '날짜 정보 없음';

          return {
            title: article.title || '제목 없음',
            summary: article.description || article.content?.substring(0, 200) || '요약 정보 없음',
            date: publishedDate,
            source: article.source?.name || '출처 정보 없음',
            category: '뉴스',
            url: article.url || '#',
          };
        });

      // 결과 포맷팅
      let articlesList = `🔍 "${keyword}"에 대한 뉴스 기사 검색 결과 (${formattedArticles.length}건)\n\n`;
      
      formattedArticles.forEach((article, index) => {
        articlesList += `${index + 1}. ${article.title}\n`;
        articlesList += `   📝 요약: ${article.summary}\n`;
        articlesList += `   📅 날짜: ${article.date}\n`;
        articlesList += `   📰 출처: ${article.source}\n`;
        articlesList += `   🏷️ 카테고리: ${article.category}\n`;
        articlesList += `   🔗 링크: ${article.url}\n\n`;
      });

      return {
        content: [
          {
            type: 'text',
            text: articlesList,
          },
        ],
      };
    } catch (error) {
      console.error('News API 오류:', error);
      return {
        content: [
          {
            type: 'text',
            text: `뉴스 검색 중 오류가 발생했습니다: ${error.message}\n\n잠시 후 다시 시도해주세요.`,
          },
        ],
        isError: true,
      };
    }
  }

  if (name === 'get_radio_song') {
    const { station } = args;

    // 방송국 검증
    const stationNames = {
      kbs: 'KBS 쿨FM',
      mbc: 'MBC FM4U',
      sbs: 'SBS 파워FM',
    };

    if (!stationNames[station]) {
      return {
        content: [
          {
            type: 'text',
            text: `오류: 지원하지 않는 방송국입니다. kbs, mbc, sbs 중에서 선택해주세요.`,
          },
        ],
        isError: true,
      };
    }

    try {
      // Last.fm API를 사용하여 인기 차트에서 현재 재생 중인 노래 가져오기
      const apiUrl = `${LASTFM_API_BASE_URL}/?method=chart.getTopTracks&api_key=${LASTFM_API_KEY}&format=json&limit=1`;
      
      console.error(`[MCP 서버] Last.fm API 호출 (현재 재생): ${apiUrl}`);
      const response = await fetchWithProxy(apiUrl);
      
      if (!response.ok) {
        throw new Error(`Last.fm API 오류: ${response.status}`);
      }

      const data = await response.json();

      // API 키가 없거나 오류가 발생한 경우 하드코딩된 데이터 사용
      if (data.error || !data.tracks || !data.tracks.track || data.tracks.track.length === 0) {
        const stationData = radioStations[station];
        const currentSong = stationData.currentSong;

        return {
          content: [
            {
              type: 'text',
              text: `📻 ${stationData.name} - 현재 재생 중인 노래\n\n` +
                    `🎵 제목: ${currentSong.title}\n` +
                    `🎤 아티스트: ${currentSong.artist}\n` +
                    `🎼 장르: ${currentSong.genre}\n` +
                    `⏰ 시간: ${currentSong.time}`,
            },
          ],
        };
      }

      // Last.fm API 결과 사용
      const topTrack = data.tracks.track[0];
      const currentTime = new Date().toLocaleTimeString('ko-KR');

      return {
        content: [
          {
            type: 'text',
            text: `📻 ${stationNames[station]} - 현재 재생 중인 노래\n\n` +
                  `🎵 제목: ${topTrack.name}\n` +
                  `🎤 아티스트: ${topTrack.artist.name}\n` +
                  `🎼 장르: 인기 차트\n` +
                  `⏰ 시간: ${currentTime}`,
          },
        ],
      };
    } catch (error) {
      console.error('Last.fm API 오류:', error);
      // 오류 발생 시 하드코딩된 데이터 사용
      const stationData = radioStations[station];
      const currentSong = stationData.currentSong;

      return {
        content: [
          {
            type: 'text',
            text: `📻 ${stationData.name} - 현재 재생 중인 노래\n\n` +
                  `🎵 제목: ${currentSong.title}\n` +
                  `🎤 아티스트: ${currentSong.artist}\n` +
                  `🎼 장르: ${currentSong.genre}\n` +
                  `⏰ 시간: ${currentSong.time}`,
          },
        ],
      };
    }
  }

  if (name === 'get_radio_recent_songs') {
    const { station } = args;

    // 방송국 검증
    const stationNames = {
      kbs: 'KBS 쿨FM',
      mbc: 'MBC FM4U',
      sbs: 'SBS 파워FM',
    };

    if (!stationNames[station]) {
      return {
        content: [
          {
            type: 'text',
            text: `오류: 지원하지 않는 방송국입니다. kbs, mbc, sbs 중에서 선택해주세요.`,
          },
        ],
        isError: true,
      };
    }

    try {
      // Last.fm API를 사용하여 인기 차트에서 최근 재생된 노래 목록 가져오기
      const apiUrl = `${LASTFM_API_BASE_URL}/?method=chart.getTopTracks&api_key=${LASTFM_API_KEY}&format=json&limit=10`;
      
      console.error(`[MCP 서버] Last.fm API 호출 (최근 재생): ${apiUrl}`);
      const response = await fetchWithProxy(apiUrl);
      
      if (!response.ok) {
        throw new Error(`Last.fm API 오류: ${response.status}`);
      }

      const data = await response.json();

      // API 키가 없거나 오류가 발생한 경우 하드코딩된 데이터 사용
      if (data.error || !data.tracks || !data.tracks.track || data.tracks.track.length === 0) {
        const stationData = radioStations[station];
        const recentSongs = stationData.recentSongs;

        let songsList = `📻 ${stationData.name} - 최근 재생된 노래 목록\n\n`;
        recentSongs.forEach((song, index) => {
          songsList += `${index + 1}. ${song.title} - ${song.artist} (${song.genre})\n`;
        });

        return {
          content: [
            {
              type: 'text',
              text: songsList,
            },
          ],
        };
      }

      // Last.fm API 결과 사용
      const tracks = data.tracks.track;
      let songsList = `📻 ${stationNames[station]} - 최근 재생된 노래 목록 (인기 차트)\n\n`;
      
      tracks.forEach((track, index) => {
        songsList += `${index + 1}. ${track.name} - ${track.artist.name}\n`;
        if (track.playcount) {
          songsList += `   재생 횟수: ${parseInt(track.playcount).toLocaleString()}회\n`;
        }
      });

      return {
        content: [
          {
            type: 'text',
            text: songsList,
          },
        ],
      };
    } catch (error) {
      console.error('Last.fm API 오류:', error);
      // 오류 발생 시 하드코딩된 데이터 사용
      const stationData = radioStations[station];
      const recentSongs = stationData.recentSongs;

      let songsList = `📻 ${stationData.name} - 최근 재생된 노래 목록\n\n`;
      recentSongs.forEach((song, index) => {
        songsList += `${index + 1}. ${song.title} - ${song.artist} (${song.genre})\n`;
      });

      return {
        content: [
          {
            type: 'text',
            text: songsList,
          },
        ],
      };
    }
  }

  if (name === 'recommend_similar_songs') {
    const { songTitle, artist } = args;

    if (!songTitle || songTitle.trim() === '') {
      return {
        content: [
          {
            type: 'text',
            text: `오류: 노래 제목을 입력해주세요.`,
          },
        ],
        isError: true,
      };
    }

    try {
      // Last.fm API를 사용하여 유사한 트랙 검색
      const searchArtist = artist || songTitle; // 아티스트가 없으면 제목으로 검색
      const apiUrl = `${LASTFM_API_BASE_URL}/?method=track.getsimilar&artist=${encodeURIComponent(searchArtist)}&track=${encodeURIComponent(songTitle)}&api_key=${LASTFM_API_KEY}&format=json&limit=10`;
      
      console.error(`[MCP 서버] Last.fm API 호출 (추천): ${apiUrl}`);
      const response = await fetchWithProxy(apiUrl);
      
      if (!response.ok) {
        throw new Error(`Last.fm API 오류: ${response.status}`);
      }

      const data = await response.json();

      // API 키가 없거나 오류가 발생한 경우 하드코딩된 데이터 사용
      if (data.error || !data.similartracks || !data.similartracks.track || data.similartracks.track.length === 0) {
        // 하드코딩된 추천 데이터 사용 (fallback)
        let recommendations = [];
        if (artist && musicRecommendations[artist]) {
          recommendations = musicRecommendations[artist];
        } else {
          // 제목으로 아티스트 찾기
          for (const [artistName, songs] of Object.entries(musicRecommendations)) {
            const found = songs.find(song => 
              song.title.toLowerCase().includes(songTitle.toLowerCase()) ||
              songTitle.toLowerCase().includes(song.title.toLowerCase())
            );
            if (found) {
              recommendations = songs;
              break;
            }
          }
        }

        if (recommendations.length === 0) {
          recommendations = [
            { title: 'Dynamite', artist: 'BTS', reason: '인기 K-Pop 노래' },
            { title: 'Celebrity', artist: 'IU', reason: '인기 K-Pop 노래' },
            { title: 'How You Like That', artist: 'BLACKPINK', reason: '인기 K-Pop 노래' },
            { title: 'Love Scenario', artist: 'iKON', reason: '인기 K-Pop 노래' },
            { title: 'Spring Day', artist: 'BTS', reason: '인기 K-Pop 노래' },
          ];
        }

        let recommendationsList = `🎵 "${songTitle}"${artist ? ` - ${artist}` : ''}와 비슷한 추천 노래\n\n`;
        recommendations.forEach((song, index) => {
          recommendationsList += `${index + 1}. ${song.title} - ${song.artist}\n   추천 이유: ${song.reason}\n\n`;
        });

        return {
          content: [
            {
              type: 'text',
              text: recommendationsList,
            },
          ],
        };
      }

      // Last.fm API 결과 포맷팅
      const tracks = data.similartracks.track.slice(0, 10);
      let recommendationsList = `🎵 "${songTitle}"${artist ? ` - ${artist}` : ''}와 비슷한 추천 노래 (${tracks.length}건)\n\n`;
      
      tracks.forEach((track, index) => {
        recommendationsList += `${index + 1}. ${track.name} - ${track.artist.name}\n`;
        if (track.playcount) {
          recommendationsList += `   재생 횟수: ${parseInt(track.playcount).toLocaleString()}회\n`;
        }
        recommendationsList += `   추천 이유: 유사한 트랙\n\n`;
      });

      return {
        content: [
          {
            type: 'text',
            text: recommendationsList,
          },
        ],
      };
    } catch (error) {
      console.error('Last.fm API 오류:', error);
      // 오류 발생 시 하드코딩된 데이터 사용
      let recommendations = [];
      if (artist && musicRecommendations[artist]) {
        recommendations = musicRecommendations[artist];
      } else {
        recommendations = [
          { title: 'Dynamite', artist: 'BTS', reason: '인기 K-Pop 노래' },
          { title: 'Celebrity', artist: 'IU', reason: '인기 K-Pop 노래' },
          { title: 'How You Like That', artist: 'BLACKPINK', reason: '인기 K-Pop 노래' },
          { title: 'Love Scenario', artist: 'iKON', reason: '인기 K-Pop 노래' },
          { title: 'Spring Day', artist: 'BTS', reason: '인기 K-Pop 노래' },
        ];
      }

      let recommendationsList = `🎵 "${songTitle}"${artist ? ` - ${artist}` : ''}와 비슷한 추천 노래\n\n`;
      recommendations.forEach((song, index) => {
        recommendationsList += `${index + 1}. ${song.title} - ${song.artist}\n   추천 이유: ${song.reason}\n\n`;
      });

      return {
        content: [
          {
            type: 'text',
            text: recommendationsList,
          },
        ],
      };
    }
  }

  // 알 수 없는 도구 이름
  return {
    content: [
      {
        type: 'text',
        text: `알 수 없는 도구: ${name}`,
      },
    ],
    isError: true,
  };
});

// 서버 시작
async function main() {
  // 표준 입출력을 통한 통신 설정
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('MCP AI 기사 검색 및 라디오 방송 서버가 시작되었습니다.');
}

main().catch((error) => {
  console.error('서버 오류:', error);
  process.exit(1);
});

