# 허브(index.html) '업데이트 기록' 자동 갱신
# 저장소의 각 도구 파일(*.html) 맨 아래 <footer class="ver" data-tool="도구이름"> 안의
# <li data-date="YYYY.MM.DD">바뀐 내용</li> 들을 모아서, index.html의
# <!--CHANGELOG:START--> ~ <!--CHANGELOG:END--> 사이를 새로 만듭니다.
# 도구 파일이 없는 항목(다른 저장소 등)은 .github/changelog-extra.json 에 적습니다.
# 표준 라이브러리만 사용 · 개인정보 없음 (파일 안의 기록 문구만 읽음)
import glob, html, json, os, re, sys
from html.parser import HTMLParser

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
SHOW = 5          # 허브에 먼저 보여줄 줄 수 (나머지는 '더 보기')

class FooterReader(HTMLParser):
    """<footer class="ver" data-tool="..."> 안의 <li data-date="..."> 텍스트를 모은다"""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tool = None; self.date = None; self.buf = []; self.items = []; self.depth = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'footer' and 'ver' in (a.get('class') or '').split() and a.get('data-tool'):
            self.tool = a['data-tool'].strip(); self.depth = 1; return
        if self.tool and tag == 'footer': self.depth += 1
        if self.tool and tag == 'li' and a.get('data-date'):
            self.date = a['data-date'].strip(); self.buf = []
    def handle_endtag(self, tag):
        if self.tool and tag == 'li' and self.date:
            text = re.sub(r'\s+', ' ', ''.join(self.buf)).strip()
            text = re.sub(r'^\d{4}\.\d{1,2}\.\d{1,2}\s*[—-]\s*', '', text)   # 앞에 날짜를 같이 적었으면 뗌
            if text: self.items.append((self.date, self.tool, text))
            self.date = None
        if self.tool and tag == 'footer':
            self.depth -= 1
            if self.depth <= 0: self.tool = None
    def handle_data(self, data):
        if self.date is not None: self.buf.append(data)

def norm_date(d):
    m = re.match(r'(\d{4})\D+(\d{1,2})\D+(\d{1,2})', d)
    return f'{m.group(1)}.{int(m.group(2)):02d}.{int(m.group(3)):02d}' if m else d

def collect():
    items = []
    for path in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        if os.path.basename(path).lower() == 'index.html': continue
        r = FooterReader()
        # 큰 파일이라 footer 부분만 잘라서 읽음
        s = open(path, encoding='utf-8', errors='replace').read()
        for m in re.finditer(r'<footer[^>]*class="[^"]*\bver\b[^"]*"[^>]*>.*?</footer>', s, re.S):
            r.feed(m.group(0))
        items += r.items
    extra = os.path.join(ROOT, '.github', 'changelog-extra.json')
    if os.path.exists(extra):
        for x in json.load(open(extra, encoding='utf-8')):
            items.append((x['date'], x['tool'], x['text']))
    seen = set(); out = []
    for d, t, c in items:
        k = (norm_date(d), t, c)
        if k not in seen: seen.add(k); out.append(k)
    out.sort(key=lambda x: x[0], reverse=True)            # 최신 날짜가 위 (같은 날은 파일 순서 유지)
    return out

def block(items):
    e = html.escape
    li = lambda d, t, c: (f'<li style="display:grid;grid-template-columns:86px 130px 1fr;gap:10px;padding:7px 0;'
                          f'border-bottom:1px solid var(--line);font-size:12.5px"><span class="muted">{e(d)}</span><b>{e(t)}</b><span>{e(c)}</span></li>')
    first = ''.join(li(*x) for x in items[:SHOW]); rest = ''.join(li(*x) for x in items[SHOW:])
    more = (f'<details style="margin-top:4px"><summary style="cursor:pointer;font-size:12.5px;color:var(--brand-ink);font-weight:600;padding:6px 0">'
            f'이전 기록 {len(items) - SHOW}건 더 보기</summary><ul style="list-style:none;margin:0;padding:0">{rest}</ul></details>') if rest else ''
    return ('<!--CHANGELOG:START (자동 생성 — 직접 고치지 마세요. 각 도구 파일 맨 아래 기록을 고치면 반영됩니다)-->\n'
            '  <section class="section" style="margin-top:22px" aria-labelledby="chlog-title">\n'
            '    <h2 id="chlog-title" style="font-size:14px;margin:0 0 6px">📝 업데이트 기록</h2>\n'
            f'    <ul style="list-style:none;margin:0;padding:0">{first}</ul>{more}\n'
            '  </section>\n<!--CHANGELOG:END-->')

def main():
    idx = os.path.join(ROOT, 'index.html')
    raw = open(idx, encoding='utf-8', newline='').read()
    crlf = '\r\n' in raw; s = raw.replace('\r\n', '\n')
    m = re.search(r'<!--CHANGELOG:START.*?<!--CHANGELOG:END-->', s, re.S)
    if not m: print('index.html 에 CHANGELOG 표시가 없어 건너뜀'); return
    items = collect()
    new = s[:m.start()] + block(items) + s[m.end():]
    if new == s: print('바뀐 기록 없음'); return
    open(idx, 'w', encoding='utf-8', newline='').write(new.replace('\n', '\r\n') if crlf else new)
    print(f'업데이트 기록 {len(items)}건으로 갱신')

if __name__ == '__main__':
    main()
