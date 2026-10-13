# 안부 문자 도우미

가까운 가족·친구에게 보낼 **안부 문자를 자동으로 만들고**, 휴대폰 **메시지 앱을 받는 사람·내용이 채워진 상태로 열어** 주는 서비스입니다.
보내기 버튼은 직접 누릅니다. 실수로 문자가 나가는 일이 없도록 일부러 그렇게 만들었습니다.

- 연락 주기(`every_days`)가 지난 사람부터 보여 줍니다
- 존댓말/반말, 호칭, 계절·시간대에 맞춘 문장
- `ANTHROPIC_API_KEY`가 있으면 Claude가 근황 메모를 반영해 더 자연스럽게 작성하고, 없으면 내장 템플릿을 사용합니다
- iPhone(`sms:번호&body=`)과 안드로이드(`sms:번호?body=`) 링크 형식을 자동으로 맞춥니다

## 시작하기

```bash
cp contacts.example.json contacts.json   # 내 연락처로 수정
python3 -m greeter list --all --no-ai    # 터미널에서 초안 확인
```

### 휴대폰에서 쓰기

PC와 휴대폰을 같은 Wi-Fi에 연결하고 실행합니다.

```bash
python3 -m greeter serve --host 0.0.0.0 --port 8000
```

휴대폰 브라우저에서 `http://<PC의 IP>:8000`을 열고 **메시지 앱 열기**를 누르세요.
(홈 화면에 추가하면 앱처럼 쓸 수 있습니다.)

> ⚠️ `--host 0.0.0.0`은 같은 네트워크의 누구나 연락처 목록을 볼 수 있게 합니다. 집 Wi-Fi에서만 쓰고, 다 쓰면 끄세요.

### Claude로 맞춤 문자 만들기 (선택)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python3 -m greeter serve --host 0.0.0.0
```

모델은 `GREETER_MODEL` 환경변수로 바꿀 수 있습니다 (기본값 `claude-opus-5-5`).

## contacts.json 형식

| 필드 | 설명 | 예 |
|---|---|---|
| `id` | 고유 식별자 | `"mom"` |
| `name` | 이름 | `"엄마"` |
| `phone` | 전화번호 | `"010-1234-5678"` |
| `relation` | `family` 또는 `friend` | `"family"` |
| `call_name` | 문자에서 부를 호칭 | `"민수야"` |
| `polite` | 존댓말 여부 | `true` |
| `notes` | 근황 메모 (AI만 참고) | `"최근 이직함"` |
| `every_days` | 안부 주기(일) | `7` |

마지막 연락일은 **메시지 앱 열기**를 누를 때 `state.json`에 기록됩니다. `contacts.json`과 `state.json`은 개인정보라 `.gitignore`에 들어 있습니다.

## 테스트

```bash
python3 -m unittest discover -s tests
```
