# Epic 8 AI Sub-Agents - README

## 📋 Tổng quan

Đây là bộ 3 AI Sub-Agents được phát triển cho **Epic 8: Virtual AI Interview Room** trong hệ thống AI Recruitment Platform (DATN). Các agents chạy trên **Ollama** (self-hosted) và tích hợp vào backend Python FastAPI.

### Các Sub-Agents

1. **QuestionCraft AI** (Question Generator) ❓
   - Tạo câu hỏi phỏng vấn từ JD và CV
   - Model: llama3.2:3b-instruct-fp16
   - Latency: ~4s

2. **DialogFlow AI** (Conversation Agent) 💬
   - Quản lý cuộc hội thoại phỏng vấn
   - Đánh giá từng turn, tạo follow-up questions
   - Model:Human-Like-Qwen2.5-1.5B-Instruct
   - Latency: ~3s
   

3. **EvalMaster AI** (Performance Evaluator) 📊
   - Đánh giá tổng thể hiệu suất phỏng vấn
   - Tạo báo cáo chi tiết với khuyến nghị tuyển dụng
   - Model: llama3.2-uncensored
   - Latency: ~6s

## 🏗️ Kiến trúc

```
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                       │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │ Question    │  │ Conversation │  │ Performance   │ │
│  │ Generator   │  │ Agent        │  │ Evaluator     │ │
│  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘ │
│         │                │                   │          │
│         └────────────────┼───────────────────┘          │
│                          │                              │
└──────────────────────────┼──────────────────────────────┘
                           │
                    ┌──────▼───────┐
                    │   Ollama     │
                    │   Server     │
                    │ (localhost)  │
                    └──────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼────┐  ┌───▼────┐  ┌───▼────┐
         │ Llama   │  │ Qwen   │  │ Llama  │
         │ 3.2-3B  │  │ 2.5    │  │ 3.2-3B │
         │ (Q Gen) │  │ (Conv) │  │ (Eval) │
         └─────────┘  └────────┘  └────────┘
```

## 📁 Cấu trúc Thư mục

```
_sub-agents/
├── agents/                      # Python implementation
│   ├── base_agent.py           # Base class cho tất cả agents
│   ├── question_generator.py   # QuestionCraft AI
│   ├── conversation_agent.py   # DialogFlow AI
│   └── performance_evaluator.py # EvalMaster AI
│
├── configs/                     # JSON configurations
│   ├── question_generator_config.json
│   ├── conversation_agent_config.json
│   └── performance_evaluator_config.json
│
├── prompts/                     # System prompts
│   ├── question_generator_prompt.txt
│   ├── conversation_agent_prompt.txt
│   └── performance_evaluator_prompt.txt
│
├── api_examples/                # API request templates
│   ├── question_generator_example.json
│   ├── conversation_agent_example.json
│   └── performance_evaluator_example.json
│
├── samples/                     # Sample data for testing
│   ├── sample_job_descriptions.md
│   ├── sample_cvs.md
│   └── sample_interview_transcripts.md
│
├── tests/                       # Unit tests
│   ├── test_base_agent.py
│   ├── test_question_generator.py
│   ├── test_conversation_agent.py
│   └── test_performance_evaluator.py
│
├── README.md                    # This file
├── INTEGRATION_GUIDE.md         # Backend integration guide
├── TESTING_GUIDE.md             # Testing procedures
└── PROMPT_TUNING.md             # Prompt customization guide
```

## 🚀 Quick Start

### 1. Cài đặt Ollama và Models

```bash
# Install Ollama (nếu chưa có)
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull llama3.2:3b-instruct-fp16
ollama pull qwen2.5:1.5b-instruct-fp16

# Verify models
ollama list
```

### 2. Cài đặt Dependencies

```bash
# Install required Python packages
pip install requests  # For Ollama API calls

# Or add to requirements.txt
echo "requests>=2.31.0" >> requirements.txt
```

### 3. Test Agents

```python
# Test QuestionCraft AI
from _sub_agents.agents.question_generator import QuestionGeneratorAgent

agent = QuestionGeneratorAgent()
result = agent.generate_questions(
    job_description="Backend Developer với 2+ năm kinh nghiệm Python...",
    cv_content="Nguyễn Văn A, 3 năm kinh nghiệm...",
    position_level="middle",
    num_questions=5
)

print(result)
```

### 4. Tích hợp vào FastAPI

Xem chi tiết trong `INTEGRATION_GUIDE.md`

## 🎯 Use Cases

### Flow 1: Tạo Câu hỏi Phỏng vấn
```
1. HR tạo interview session mới
2. System gọi QuestionCraft AI với JD + CV
3. Agent trả về 10-15 câu hỏi phù hợp
4. HR review và chọn câu hỏi (hoặc auto-select)
5. Lưu vào database cho interview session
```

### Flow 2: Tiến hành Phỏng vấn
```
1. Candidate join interview room
2. System hiển thị câu hỏi đầu tiên
3. Candidate trả lời (text hoặc voice-to-text)
4. System gọi DialogFlow AI để:
   - Đánh giá câu trả lời
   - Quyết định next action (continue/follow-up/next)
5. Lặp lại cho đến hết câu hỏi hoặc hết thời gian
```

### Flow 3: Đánh giá Kết quả
```
1. Interview kết thúc
2. System compile full transcript + turn evaluations
3. Gọi EvalMaster AI để tạo comprehensive report
4. HR xem report với:
   - Overall score (0-10)
   - Dimension scores (Technical/Communication/Behavioral)
   - Hiring recommendation
   - Detailed analysis với evidence
5. HR quyết định final hiring decision
```

## ⚙️ Configuration

Mỗi agent có file config JSON riêng:

```json
{
  "model": "llama3.2:3b-instruct-fp16",
  "model_parameters": {
    "temperature": 0.7,
    "top_p": 0.9,
    "num_predict": 2048
  },
  "ollama_settings": {
    "host": "http://localhost:11434",
    "timeout": 30
  },
  "performance_settings": {
    "target_latency_ms": 4000,
    "max_retries": 2
  }
}
```

Thay đổi các parameters để tune performance hoặc output quality.

## 📊 Performance

### Target Latency (P95)
- QuestionCraft AI: < 5s (generates 10 questions)
- DialogFlow AI: < 3s (per turn)
- EvalMaster AI: < 8s (full evaluation)

### Resource Requirements
- **RAM**: ~4GB cho Llama-3.2-3B, ~2GB cho Qwen2.5-1.5B
- **CPU**: 4+ cores recommended
- **Storage**: ~10GB total cho cả 2 models

### Scaling
- Ollama hỗ trợ concurrent requests (queue internally)
- Có thể deploy multiple Ollama instances với load balancer
- Consider GPU acceleration cho production (latency giảm 5-10x)

## 🐛 Troubleshooting

### Issue: "Connection refused to localhost:11434"
**Solution:** 
```bash
# Kiểm tra Ollama đang chạy
systemctl status ollama

# Hoặc start manually
ollama serve
```

### Issue: "Model not found"
**Solution:**
```bash
# Pull model lại
ollama pull llama3.2:3b-instruct-fp16
ollama pull qwen2.5:1.5b-instruct-fp16
```

### Issue: "Response timeout"
**Solution:**
- Tăng `timeout` trong config (default: 30s)
- Kiểm tra CPU/RAM usage (có thể máy đang overload)
- Xem xét dùng model nhỏ hơn

### Issue: "Invalid JSON in response"
**Solution:**
- Đây là lỗi phổ biến với LLM generation
- Agent đã có retry logic (max 2 retries)
- Nếu vẫn lỗi, có thể tune prompt hoặc temperature

## 📚 Documentation

- **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)**: Hướng dẫn tích hợp vào FastAPI backend
- **[TESTING_GUIDE.md](./TESTING_GUIDE.md)**: Hướng dẫn testing và quality assurance
- **[PROMPT_TUNING.md](./PROMPT_TUNING.md)**: Hướng dẫn customize prompts cho domain-specific

## 🔐 Security Considerations

1. **Input Validation**: Validate tất cả inputs trước khi gửi cho agents
2. **Output Sanitization**: Sanitize agent outputs trước khi hiển thị cho users
3. **Rate Limiting**: Implement rate limiting để tránh abuse
4. **Logging**: Log tất cả agent calls (nhưng **KHÔNG** log sensitive data)
5. **Timeout**: Luôn set timeout để tránh hanging requests

## 🤝 Contributing

Khi customize hoặc improve agents:

1. Test thoroughly với sample data
2. Measure performance impact
3. Document changes trong code comments
4. Update relevant documentation
5. Add unit tests cho new functionality

## 📝 License

Internal use only - DATN Project

## 👥 Authors

- **Developer**: [Your Name]
- **Project**: DATN - AI Recruitment Platform
- **Epic**: Epic 8 - Virtual AI Interview Room
- **Date**: January 2026

## 📞 Support

Nếu gặp vấn đề, check các tài liệu sau:
1. README.md (this file)
2. INTEGRATION_GUIDE.md
3. TESTING_GUIDE.md
4. Ollama documentation: https://ollama.com/docs

Hoặc raise issue trong project repository.
