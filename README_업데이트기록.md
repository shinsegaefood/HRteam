# 업데이트 기록 자동 갱신

도구 파일(`payroll.html`, `birthday.html`, `hyujik.html` …)을 저장소에 올리면,
GitHub가 1~2분 안에 허브(`index.html`) 아래 **📝 업데이트 기록**을 자동으로 고쳐 줍니다.

## 어떻게 동작하나요

1. 각 도구 파일 맨 아래에 `<footer class="ver" data-tool="도구 이름">` 기록 칸이 있어요.
2. 도구 파일을 올리면 `.github/workflows/changelog.yml` 이 실행돼요.
3. `.github/scripts/update_changelog.py` 가 모든 도구 파일의 기록을 모아
   `index.html` 의 `<!--CHANGELOG:START-->` ~ `<!--CHANGELOG:END-->` 사이를 새로 만들어 저장해요.
4. 허브에서 새로고침(Ctrl+F5)하면 보여요.

파일 안의 기록 문구만 읽어요. 개인정보와는 상관없어요.

## 도구를 직접 고쳤을 때 기록 남기는 법

도구 파일 맨 아래 기록 칸의 `<ul …>` 바로 아래에 한 줄을 추가하세요. (최신이 위)

```html
<li data-date="2026.11.05">J사번 퇴직자 표시 추가</li>
```

## 도구 파일이 없는 항목 (다른 저장소·계좌이체 등)

`.github/changelog-extra.json` 에 추가하세요.

```json
{"date": "2026.11.05", "tool": "인사이슈 보드", "text": "판례 필터 추가"}
```

## 처음 한 번 설정

1. 저장소에 아래 3개 파일을 만들어요 (Add file → Create new file 에서 이름 칸에 경로까지 그대로 입력).
   - `.github/workflows/changelog.yml`
   - `.github/scripts/update_changelog.py`
   - `.github/changelog-extra.json`
2. **Settings → Actions → General → Workflow permissions** 가 *Read and write permissions* 인지 확인해요.
   (읽기 전용이면 자동 저장 단계에서 403 오류가 나요.)
3. **Actions 탭 → 업데이트 기록 자동 갱신 → Run workflow** 로 한 번 돌려 확인해요.

## 직접 고치면 안 되는 곳

`index.html` 의 `<!--CHANGELOG:START …-->` ~ `<!--CHANGELOG:END-->` 사이는 자동으로 다시 만들어져요.
여기를 손으로 고치면 다음 실행 때 덮어써져요.
