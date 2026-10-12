# AI Testcase Agent — multi-provider project mẫu

Project Python biến requirement/user story thành testcase dạng CSV + JSON để QA review. Có thể chọn **một provider cho mỗi lần chạy**: OpenAI, Anthropic Claude, Google Gemini hoặc một endpoint tương thích OpenAI Chat Completions. Logic viết/validate testcase không phụ thuộc vào một SDK cụ thể.

> Lưu ý: đây là bản nháp hỗ trợ QA. Người có trách nhiệm vẫn cần duyệt testcase, expected result và các business rule trước khi sử dụng.

## 1. Yêu cầu
- Python 3.10+
- API key và quyền sử dụng model tương ứng; hoặc endpoint model nội bộ/local đã được phê duyệt
- Mạng truy cập tới API nếu sử dụng model hosted

## 2. Cài đặt (macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Mở `.env`, chỉ điền các secret cần thiết cho provider bạn định dùng. Không commit file `.env`.

## 3. Cấu hình provider

Các biến cốt lõi:

- `AI_PROVIDER`: provider mặc định (`openai`, `anthropic`, `gemini`, `openai_compatible`).
- `AI_MODEL`: model override tùy chọn, áp dụng cho provider đang chọn. Nếu để trống, ứng dụng dùng biến model riêng của provider.
- Mỗi provider có biến model và API key riêng; model ID phải là model mà tài khoản/endpoint của bạn được phép truy cập.

### A. OpenAI

```dotenv
AI_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
```

Adapter dùng OpenAI Responses API.

### B. Anthropic Claude

```dotenv
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=...
ANTHROPIC_MODEL=your_claude_model_id
ANTHROPIC_MAX_TOKENS=8192
```

Thay `your_claude_model_id` bằng model ID hiện có trong tài khoản Anthropic.

### C. Google Gemini

```dotenv
AI_PROVIDER=gemini
GOOGLE_API_KEY=...
GEMINI_MODEL=your_gemini_model_id
```

Thay `your_gemini_model_id` bằng model ID có trong môi trường Google AI/Gemini được phép sử dụng.

### D. Endpoint tương thích OpenAI Chat Completions

Dùng cho một số gateway hoặc model server nội bộ/local có hỗ trợ endpoint tương thích. Không phải mọi dịch vụ quảng cáo “OpenAI-compatible” đều hỗ trợ cùng một tập tính năng; kiểm tra tài liệu endpoint cụ thể.

```dotenv
AI_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_API_KEY=your_endpoint_key
OPENAI_COMPATIBLE_BASE_URL=https://your-approved-endpoint.example/v1
OPENAI_COMPATIBLE_MODEL=your_endpoint_model_id
```

Ví dụ endpoint local có thể dùng base URL như `http://localhost:11434/v1` nếu model server của bạn có bật tương thích API đó. Endpoint và model ID cần khớp đúng cài đặt local.

### Quy tắc chọn model

Ưu tiên từ cao xuống thấp:
1. Tham số `--model` trên lệnh chạy.
2. Biến `AI_MODEL` trong `.env`.
3. Biến model riêng của provider, ví dụ `GEMINI_MODEL`.

## 4. Chạy sinh testcase

Dùng provider mặc định trong `.env`:

```bash
python -m agents.testcase_agent
```

Chọn requirement và thư mục output:

```bash
python -m agents.testcase_agent \
  --input data/raw/login_requirements.md \
  --output-dir data/processed
```

Ghi đè provider cho một lần chạy:

```bash
python -m agents.testcase_agent --provider openai
python -m agents.testcase_agent --provider anthropic
python -m agents.testcase_agent --provider gemini
python -m agents.testcase_agent --provider openai_compatible
```

Ghi đè cả provider và model:

```bash
python -m agents.testcase_agent --provider gemini --model your_gemini_model_id
```

Lệnh ghi đè provider chỉ chọn provider cho **lần chạy đó**, không sửa file `.env`. Các lần chạy có thể cho số lượng hoặc cách diễn đạt testcase khác nhau; vẫn phải so sánh chất lượng trước khi chọn dùng.

## 5. Kết quả

- `data/processed/<input>_testcases.csv`: mở bằng Excel để QA review.
- `data/processed/<input>_testcases.json`: dữ liệu có cấu trúc dùng cho tích hợp về sau.
- `data/processed/<input>_review_notes.md`: assumptions và requirement gaps.
- `evals/traces/traces.jsonl`: metadata của lần chạy như provider, model, thời gian và số testcase; không lưu toàn bộ requirement đầu vào.

## 6. Cấu trúc code provider

```text
agents/
├── providers/
│   ├── base.py                       # interface chung
│   ├── factory.py                    # chọn adapter + resolve model
│   ├── openai_provider.py            # OpenAI Responses API
│   ├── anthropic_provider.py         # Anthropic Messages API
│   ├── gemini_provider.py            # Google Gen AI SDK
│   └── openai_compatible_provider.py # Chat Completions endpoint tương thích
├── testcase_agent.py                 # điều phối workflow
├── skills/                           # build prompt + validate JSON
└── tools/                             # đọc requirement + xuất báo cáo
```

Khi thêm provider mới, tạo adapter tuân theo hàm `generate(system_prompt, user_input, model) -> str`, đăng ký adapter trong `agents/providers/factory.py`, bổ sung cấu hình và unit test. Agent và logic ghi báo cáo không cần biết SDK cụ thể.

## 7. Chạy unit test không gọi API

```bash
python -m unittest discover -s evals/tests -v
```

Unit test dùng fake provider để không phát sinh API call hoặc chi phí.

## 8. Đề xuất dùng nhiều AI trong QA

Bản mẫu này chọn **một provider mỗi lần chạy**. Cách triển khai ban đầu nên là chạy cùng một requirement qua hai provider, rồi so sánh:
- AC nào được bao phủ;
- expected result có căn cứ trong requirement không;
- testcase trùng lặp;
- boundary/negative case có bị bỏ sót;
- latency và chi phí theo log/billing của nhà cung cấp.

Chỉ sau khi đánh giá ổn định mới thêm chế độ chạy song song, voting hoặc fallback tự động. Không nên coi kết quả đa số là đúng nếu các model cùng suy đoán một business rule chưa được đặc tả.

## Bảo mật

Không gửi API key, dữ liệu khách hàng, thông tin production hoặc tài liệu nội bộ tới nhà cung cấp bên ngoài nếu chưa được công ty phê duyệt. Dùng requirement đã ẩn danh và kiểm tra điều khoản lưu trữ dữ liệu của endpoint/model trước khi triển khai.
