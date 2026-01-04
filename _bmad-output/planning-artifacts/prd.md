---
stepsCompleted: [1, 2, 3, 4, 6, 7, 8, 9, 10, 11]
inputDocuments:
  - _bmad-output/planning-artifacts/docs/brief.md
  - _bmad-output/analysis/brainstorming-session-2025-12-29.md
  - _bmad-output/planning-artifacts/docs/brainstorming-session-results.md
  - _bmad-output/planning-artifacts/docs/project-planning/brainstorming-documentation.md
  - _bmad-output/planning-artifacts/architecture/index.md
  - _bmad-output/planning-artifacts/docs/project-planning/epic-virtual-ai-interview-room.md
  - _bmad-output/planning-artifacts/stories/8.1.story.md
  - _bmad-output/planning-artifacts/stories/8.2.story.md
  - _bmad-output/planning-artifacts/stories/8.3.story.md
  - _bmad-output/planning-artifacts/stories/8.4.story.md
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/docs/brownfield-architecture.md
  - _bmad-output/planning-artifacts/docs/project-planning/epic-advanced-job-search-application.md
  - _bmad-output/planning-artifacts/docs/project-planning/epic-realtime-messaging.md
workflowType: 'prd'
lastStep: 0
briefCount: 1
researchCount: 0
brainstormingCount: 3
projectDocsCount: 125
---

# Product Requirements Document - datn

**Author:** Lem
**Date:** 2025-12-30

## Executive Summary

Dự án này sẽ phát triển Nền tảng Tuyển dụng AI từ một hệ thống xác thực người dùng cơ bản thành một hệ sinh thái tuyển dụng **"tất cả trong một" (all-in-one)**, được thiết kế để trở thành công cụ làm việc không thể thiếu hàng ngày cho cả ứng viên và nhà tuyển dụng.

Trọng tâm của bản phát hành này bao gồm bốn trụ cột chính:
1.  **Phân tích & Gợi ý CV bằng AI:** Cung cấp cho ứng viên những phân tích sâu sắc để cải thiện CV.
2.  **Phòng phỏng vấn AI ảo:** Một môi trường luyện tập phỏng vấn thích ứng, giúp ứng viên tự tin hơn và cung cấp cho nhà tuyển dụng một công cụ sàng lọc kỹ năng mềm.
3.  **Trò chuyện Trực tuyến:** Xây dựng kênh giao tiếp tức thời, giúp tăng tốc độ tuyển dụng và tạo ra thói quen sử dụng, giữ chân nhà tuyển dụng trên nền tảng.
4.  **Tìm kiếm & Ứng tuyển Nâng cao:** Trao quyền cho ứng viên không chỉ để tìm việc mà còn để **khám phá thị trường** và **định hướng phát triển sự nghiệp**, cho phép họ chủ động kết nối với các cơ hội phù hợp và "khát vọng".

### Điều gì làm nên sự đặc biệt

Điểm khác biệt của nền tảng này nằm ở việc tạo ra một vòng lặp giá trị khép kín: Ứng viên sử dụng công cụ AI để **hiểu và cải thiện** bản thân, sau đó chủ động **khám phá và ứng tuyển** vào các cơ hội, và cuối cùng sử dụng công cụ **chat** để kết nối nhanh chóng. Sự tích hợp liền mạch này giúp người dùng thành thạo có thể đáp ứng mọi nhu cầu của họ một cách nhanh chóng và hiệu quả, tạo ra sự gắn bó lâu dài và mang lại tỷ lệ thành công cao hơn so với các nền tảng thụ động khác.

## Phân loại dự án

**Loại hình kỹ thuật:** Web App & API Backend
**Lĩnh vực:** Khoa học (Scientific - AI/ML)
**Mức độ phức tạp:** Trung bình (Medium)
**Bối cảnh dự án:** Brownfield - mở rộng hệ thống hiện có

## Success Criteria

### User Success

Người dùng của chúng ta sẽ nói "nền tảng này rất xứng đáng" khi:
*   Người tìm việc cải thiện CV, hiểu rõ hơn về kỹ năng của mình và nhận được nhiều lời mời phỏng vấn hơn.
*   Nhà tuyển dụng tìm được ứng viên phù hợp nhanh hơn, chất lượng hơn và giảm thiểu thời gian sàng lọc.
*   Ứng viên tự tin hơn trong các buổi phỏng vấn và cảm thấy được trao quyền trong hành trình phát triển sự nghiệp của mình.

### Business Success

Chúng ta sẽ coi là thành công từ góc độ kinh doanh khi đạt được các chỉ số sau:
*   **Ổn định hệ thống:** Không có lỗi nghiêm trọng nào được ghi nhận trong 1 tháng đầu tiên sau khi ra mắt.
*   **Chất lượng sản phẩm:** Đạt điểm đánh giá trung bình 4/5 sao từ người dùng.
*   **Tăng trưởng người dùng:** Duy trì mức tăng trưởng 8% người dùng mới mỗi tháng.
*   **Triển khai:** Toàn bộ các tính năng cốt lõi được triển khai đầy đủ trên môi trường production.

### Technical Success

Thành công về mặt kỹ thuật sẽ được đo lường bằng các tiêu chí sau:
*   **Tỷ lệ phân tích CV thành công:** Lớn hơn 95%.
*   **Thời gian xử lý AI (phân tích CV/JD):** Dưới 30 giây (không đồng bộ).
*   **Thời gian phản hồi API (các endpoint quan trọng):** Dưới 500ms cho 95% các yêu cầu.
*   **Thời gian hoạt động của hệ thống (Uptime):** Lớn hơn 99%.
*   **Chất lượng mã nguồn:** Tuân thủ kiến trúc module và các tiêu chuẩn coding của dự án.
*   **Bảo mật dữ liệu:** Tất cả quá trình xử lý dữ liệu nhạy cảm của người dùng (CV, JD) được thực hiện cục bộ bằng Ollama LLM.

## Product Scope

### MVP - Minimum Viable Product

MVP của dự án này sẽ bao gồm việc triển khai đầy đủ và vận hành ổn định bốn trụ cột chính sau:
1.  **Phân tích & Gợi ý CV bằng AI:** Cho phép tải CV, phân tích, chấm điểm chất lượng và đưa ra phản hồi.
2.  **Phòng phỏng vấn AI ảo:** Cho phép ứng viên thiết lập, thực hiện và nhận báo cáo đánh giá sau phỏng vấn.
3.  **Trò chuyện Trực tuyến:** Cho phép nhà tuyển dụng và ứng viên khởi tạo, gửi/nhận tin nhắn real-time.
4.  **Tìm kiếm & Ứng tuyển Nâng cao:** Cung cấp giao diện tìm kiếm nâng cao và quy trình ứng tuyển liền mạch cho ứng viên.

### Growth Features (Post-MVP)

Các tính năng này sẽ được xem xét cho các giai đoạn phát triển tiếp theo:
*   Hệ thống cảnh báo và phân tích chuyên sâu cho nhà tuyển dụng.
*   Ứng dụng di động.
*   Tích hợp email và lịch trình phỏng vấn tự động.
*   Tính năng phân tích xu hướng thị trường lao động.
*   Hệ thống kiểm chứng kỹ năng (skill verification).

### Vision (Future)

Trở thành một hệ sinh thái phát triển sự nghiệp toàn diện, một nền tảng "tất cả trong một" nơi người dùng thành thạo có thể đáp ứng mọi nhu cầu của họ, từ việc tự đánh giá, học hỏi, đến tìm kiếm, ứng tuyển và kết nối, tạo ra sự gắn bó lâu dài và mang lại tỷ lệ thành công cao hơn so với các nền tảng thụ động khác.

## User Journeys

### Hành trình 1: Minh Anh - Từ Lo Lắng Đến Tự Tin (Ứng viên)
Minh Anh là một Lập trình viên Python có 3 năm kinh nghiệm, đang muốn tìm kiếm cơ hội mới ở vị trí cấp cao hơn. Cô cảm thấy lo lắng khi CV của mình không biết đã đủ tốt chưa, và các buổi phỏng vấn trước đây thường khiến cô mất tự tin. Minh Anh tìm thấy nền tảng tuyển dụng AI của chúng ta và quyết định dùng thử.

**Khung cảnh mở đầu:** Minh Anh vừa nhận được email từ một công ty mơ ước, mời cô phỏng vấn. Cô rất vui nhưng cũng đầy lo lắng vì không biết liệu CV của mình có đủ mạnh và kỹ năng phỏng vấn có đáp ứng được yêu cầu của vị trí Senior hay không.

**Hành động phát triển:**
1.  Minh Anh tải CV của mình lên nền tảng. Hệ thống **phân tích CV bằng AI** và trả về điểm chất lượng cao, cùng với phản hồi chi tiết về các kỹ năng nổi bật và một vài gợi ý nhỏ để cải thiện cấu trúc câu từ trong phần tóm tắt kinh nghiệm. Cô cảm thấy yên tâm hơn rất nhiều.
2.  Để chuẩn bị cho buổi phỏng vấn sắp tới, Minh Anh quyết định tạo một **phòng phỏng vấn AI ảo** cho vị trí "Senior Python Developer". AI đặt những câu hỏi thử thách về kiến trúc hệ thống và giải quyết vấn đề. Cô tương tác bằng giọng nói, đôi khi AI đưa ra gợi ý giúp cô trả lời tốt hơn. Sau buổi phỏng vấn, cô nhận được báo cáo đánh giá chi tiết, chỉ ra điểm mạnh trong tư duy logic và những điểm cần cải thiện trong cách trình bày dự án.
3.  Trong khi chờ đợi phản hồi từ công ty mơ ước, Minh Anh quyết định khám phá các cơ hội khác. Cô sử dụng tính năng **Tìm kiếm & Ứng tuyển Nâng cao**, nhập vào "Data Engineer cần kinh nghiệm về cloud và AI". Hệ thống trả về nhiều kết quả, bao gồm cả những công việc mà cô nghĩ mình chưa đủ điều kiện nhưng lại có nhiều điểm phù hợp về kỹ năng cốt lõi. Cô thấy mình có thêm nhiều lựa chọn và động lực để học hỏi.
4.  Một tuần sau, Minh Anh nhận được tin nhắn từ nhà tuyển dụng của công ty mơ ước thông qua tính năng **Trò chuyện Trực tuyến** của nền tảng. Nhà tuyển dụng muốn làm rõ một điểm trong CV và sắp xếp lịch phỏng vấn vòng 2. Minh Anh nhanh chóng phản hồi và xác nhận lịch hẹn chỉ trong vài phút.

**Đỉnh điểm:** Minh Anh hoàn thành buổi phỏng vấn vòng 2 một cách tự tin, cô đã chuẩn bị rất kỹ nhờ các buổi luyện tập với AI và nhận được phản hồi tích cực.

**Giải pháp:** Minh Anh nhận được lời mời làm việc từ công ty mơ ước. Cô nhận ra rằng nền tảng đã giúp cô không chỉ tìm được việc mà còn phát triển bản thân, từ một người lo lắng trở thành một ứng viên tự tin và có định hướng rõ ràng.

### Hành trình 2: Khải Minh - Sàng Lọc Thông Minh, Tuyển Dụng Nhanh Chóng (Nhà tuyển dụng)
Khải Minh là một Trưởng phòng Tuyển dụng tại một công ty công nghệ đang phát triển nhanh chóng. Anh thường xuyên phải đối mặt với hàng trăm CV gửi về cho một vị trí, nhưng chỉ một phần nhỏ trong số đó thực sự phù hợp. Việc sàng lọc thủ công tốn thời gian và dễ bỏ sót ứng viên tiềm năng. Anh luôn tìm kiếm các giải pháp để cải thiện hiệu suất của mình.

**Khung cảnh mở đầu:** Khải Minh vừa đăng một tin tuyển dụng cho vị trí "Senior Data Scientist". Chỉ sau vài giờ, hàng chục CV đã đổ về. Anh cảm thấy choáng váng và lo lắng về việc sẽ phải dành bao nhiêu thời gian để sàng lọc tất cả.

**Hành động phát triển:**
1.  Khải Minh tải **Mô tả công việc (JD)** lên nền tảng. Hệ thống sử dụng AI để phân tích JD, trích xuất các kỹ năng yêu cầu, kinh nghiệm tối thiểu và tự động phân tích ngữ nghĩa.
2.  Ngay lập tức, nền tảng hiển thị một danh sách các ứng viên đã đăng ký và có CV trên hệ thống, được **xếp hạng theo mức độ phù hợp** với JD của anh. Anh thấy ứng viên tên Minh Anh ở vị trí hàng đầu với điểm số rất cao.
3.  Khi xem chi tiết hồ sơ của Minh Anh, Khải Minh không chỉ thấy điểm số phù hợp tổng thể mà còn có thể xem **báo cáo phân tích CV chi tiết của AI** và **báo cáo kết quả từ phòng phỏng vấn AI ảo** của cô. Anh ấn tượng với khả năng giải quyết vấn đề của Minh Anh qua phần phỏng vấn thử.
4.  Khải Minh muốn xác nhận thêm một vài điểm nhỏ trước khi gửi lời mời phỏng vấn chính thức. Anh nhấp vào nút "Trò chuyện" trên hồ sơ của Minh Anh, và một cửa sổ **Trò chuyện Trực tuyến** hiện ra. Anh gửi một tin nhắn ngắn gọn. Minh Anh phản hồi gần như ngay lập tức. Khải Minh nhanh chóng làm rõ thắc mắc và đề xuất lịch phỏng vấn vòng 2.
5.  Trong khi đó, Khải Minh muốn tìm kiếm thêm các ứng viên có kinh nghiệm tương tự. Anh sử dụng tính năng **Tìm kiếm & Ứng tuyển Nâng cao**, nhập vào "Data Scientist có kinh nghiệm làm việc với Machine Learning và triển khai mô hình". Hệ thống hiển thị các CV phù hợp, không chỉ dựa trên từ khóa mà còn dựa trên ngữ nghĩa, giúp anh khám phá những ứng viên mà anh có thể đã bỏ lỡ bằng các phương pháp tìm kiếm thông thường.
6.  Trong quá trình sử dụng **Tìm kiếm Nâng cao**, Khải Minh tìm thấy một vài ứng viên rất tiềm năng nhưng chưa phù hợp ngay với vị trí hiện tại. Anh sử dụng tính năng mới **"Bộ sưu tập Ứng viên"** để lưu những hồ sơ này vào một danh sách riêng có tên "Data Engineers - Tương lai", giúp anh xây dựng một nguồn talent pool chất lượng cao cho các nhu cầu tuyển dụng sau này. Anh có thể toàn quyền quản lý các bộ sưu tập này.

**Đỉnh điểm:** Nhờ nền tảng, Khải Minh đã tìm thấy 3 ứng viên tiềm năng hàng đầu chỉ trong vòng vài giờ, thay vì vài ngày như trước đây. Anh cảm thấy tự tin rằng mình đang tuyển dụng hiệu quả hơn bao giờ hết.

**Giải pháp:** Khải Minh và đội ngũ của anh đã rút ngắn đáng kể thời gian tuyển dụng, tìm được những ứng viên chất lượng cao, và giảm bớt gánh nặng sàng lọc thủ công. Anh biết rằng nền tảng này là một công cụ không thể thiếu để anh luôn dẫn đầu trong cuộc đua giành nhân tài.

### Hành trình 3: Anh Hùng - Đảm Bảo Vận Hành, Giám Sát Sức Khỏe (Quản trị viên)
Anh Hùng là một System Administrator, chịu trách nhiệm vận hành và duy trì nền tảng tuyển dụng AI. Công việc của anh là đảm bảo mọi thứ hoạt động ổn định, hiệu quả và an toàn, để cả ứng viên và nhà tuyển dụng đều có trải nghiệm tốt nhất. Anh là người hùng thầm lặng đứng sau mọi hoạt động của hệ thống.

**Khung cảnh mở đầu:** Anh Hùng nhận được thông báo từ hệ thống giám sát về việc độ trễ của các yêu cầu AI (inference latency) đang tăng nhẹ trong giờ cao điểm. Anh biết rằng nếu không xử lý kịp thời, điều này có thể ảnh hưởng đến trải nghiệm của người dùng và làm giảm độ tin cậy của nền tảng.

**Hành động phát triển:**
1.  Anh Hùng truy cập vào **Admin Monitoring Dashboard** của nền tảng. Tại đây, anh thấy biểu đồ sử dụng GPU và RAM của dịch vụ Ollama (Local LLM) đang ở mức cao. Biểu đồ độ trễ hiển thị một vài đỉnh điểm trong vòng 30 phút qua.
2.  Anh kiểm tra **log hệ thống** thông qua dashboard và phát hiện một số lỗi nhỏ liên quan đến quá trình xử lý CV, cho thấy một số ứng viên gặp khó khăn khi tải lên các định dạng CV đặc biệt.
3.  Trong quá trình kiểm tra, anh phát hiện một vài tin tuyển dụng có nội dung không phù hợp. Anh sử dụng **công cụ Quản lý Nội dung** để tạm ẩn bài đăng đó và gửi thông báo cho nhà tuyển dụng để họ chỉnh sửa.
4.  Anh tiếp tục vào khu vực **Quản lý Người dùng**, rà soát tài khoản của các ứng viên và nhà tuyển dụng mới đăng ký để đảm bảo chất lượng người dùng trên nền tảng và lọc các tài khoản spam.
5.  Để giải quyết vấn đề độ trễ, Anh Hùng quyết định **điều chỉnh các tham số tạo sinh (generation parameters)** của mô hình LLM thông qua giao diện quản lý mô hình trên dashboard. Anh giảm `num_predict` và tăng `temperature` một chút để ưu tiên tốc độ phản hồi hơn là độ chi tiết quá mức trong giai đoạn này.
6.  Sau khi thực hiện các điều chỉnh, Anh Hùng tiếp tục theo dõi dashboard và thấy rằng việc sử dụng tài nguyên đã ổn định trở lại và độ trễ đã giảm xuống mức chấp nhận được.

**Đỉnh điểm:** Nhờ sự can thiệp kịp thời và thông minh của Anh Hùng, nền tảng tiếp tục hoạt động mượt mà, không một ứng viên hay nhà tuyển dụng nào nhận ra vấn đề đã xảy ra.

**Giải pháp:** Anh Hùng đảm bảo nền tảng luôn hoạt động ổn định, bảo vệ trải nghiệm của người dùng và giữ vững độ tin cậy của hệ thống. Anh sử dụng các công cụ giám sát và quản lý của nền tảng để chủ động giải quyết các vấn đề, từ đó gián tiếp đóng góp vào việc giữ chân người dùng và tạo ra doanh thu.

### Tóm tắt Yêu cầu từ các Hành trình
Các hành trình trên cho thấy sự cần thiết của các nhóm tính năng sau:
*   **Phân hệ cho Ứng viên:** Phân tích CV, Luyện tập phỏng vấn, Tìm kiếm & Ứng tuyển Nâng cao, Chat.
*   **Phân hệ cho Nhà tuyển dụng:** Đăng tin, Tìm kiếm & Sàng lọc ứng viên bằng AI, Chat, Quản lý "Bộ sưu tập ứng viên".
*   **Phân hệ cho Quản trị viên:** Dashboard giám sát hệ thống, Công cụ quản lý người dùng và nội dung.

## Innovation & Novel Patterns

### Detected Innovation Areas

Nền tảng tuyển dụng AI này thể hiện sự đổi mới đáng kể trong cách tiếp cận các vấn đề tuyển dụng truyền thống, đặc biệt ở các khía cạnh sau:

1.  **Phòng phỏng vấn AI ảo như một công cụ huấn luyện thích ứng:**
    *   **Thách thức giả định:** Vượt xa mô hình phỏng vấn thử truyền thống chỉ để đánh giá.
    *   **Cách tiếp cận mới:** AI đóng vai trò là "huấn luyện viên" năng động, điều chỉnh độ khó câu hỏi dựa trên hiệu suất của ứng viên và cung cấp gợi ý, khuyến khích để tối ưu hóa trải nghiệm học tập và phát triển sự tự tin.
    *   **Giá trị độc đáo:** Biến quá trình chuẩn bị phỏng vấn thành một cơ hội học hỏi liên tục và có phản hồi ngay lập tức, giúp ứng viên không chỉ luyện tập mà còn thực sự cải thiện.

2.  **Quy trình làm việc tích hợp "tất cả trong một" (All-in-One Ecosystem):**
    *   **Thách thức giả định:** Các nền tảng hiện có thường cung cấp các công cụ riêng lẻ.
    *   **Cách tiếp cận mới:** Tích hợp chặt chẽ các tính năng chính (phân tích CV, phòng phỏng vấn AI, tìm kiếm & ứng tuyển nâng cao, trò chuyện trực tuyến) thành một vòng lặp giá trị liền mạch.
    *   **Giá trị độc đáo:** Cung cấp trải nghiệm người dùng thống nhất, giảm thiểu việc chuyển đổi giữa các công cụ và nền tảng khác nhau. Điều này giúp cả ứng viên và nhà tuyển dụng tập trung tối đa, cải thiện hiệu suất và tạo ra sự gắn bó lâu dài với nền tảng.

3.  **Xử lý LLM cục bộ (Ollama) vì quyền riêng tư:**
    *   **Thách thức giả định:** Nhiều giải pháp AI dựa trên tuyển dụng sử dụng các dịch vụ LLM trên đám mây có thể gây lo ngại về quyền riêng tư dữ liệu nhạy cảm.
    *   **Cách tiếp cận mới:** Tận dụng mô hình LLM cục bộ (Ollama) để thực hiện tất cả các tác vụ AI, đảm bảo dữ liệu nhạy cảm (như CV và JD) không rời khỏi môi trường kiểm soát của người dùng.
    *   **Giá trị độc đáo:** Cung cấp một lợi thế cạnh tranh mạnh mẽ về quyền riêng tư và bảo mật dữ liệu, đặc biệt quan trọng trong các lĩnh vực có yêu cầu cao về tuân thủ.

### Market Context & Competitive Landscape

Các điểm đổi mới này giúp nền tảng tạo ra một vị thế độc đáo trên thị trường tuyển dụng bằng cách giải quyết các điểm yếu của các nền tảng truyền thống (thụ động, thiếu phản hồi tức thì, rủi ro bảo mật dữ liệu) và mang lại giá trị gia tăng rõ rệt cho người dùng.

### Validation Approach

Các khía cạnh đổi mới sẽ được xác thực thông qua:
*   **User Testing:** Thu thập phản hồi trực tiếp từ ứng viên và nhà tuyển dụng về trải nghiệm với phòng phỏng vấn AI, hiệu quả của quy trình tích hợp, và sự tự tin về quyền riêng tư.
*   **A/B Testing:** So sánh hiệu quả của các phiên bản tính năng khác nhau.
*   **Metrics Tracking:** Giám sát các chỉ số thành công liên quan đến mức độ gắn bó, tỷ lệ hoàn thành phỏng vấn, sự hài lòng của người dùng và hiệu quả tuyển dụng.

### Risk Mitigation

Các rủi ro liên quan đến đổi mới (ví dụ: hiệu suất AI không như mong đợi, độ phức tạp của tích hợp) sẽ được giảm thiểu thông qua:
*   **Phát triển lặp lại:** Triển khai từng bước, thu thập phản hồi và điều chỉnh.
*   **Mô hình dự phòng:** Luôn có các phương án dự phòng hoặc cách tiếp cận thủ công nếu công nghệ AI không đạt yêu cầu.
*   **Đội ngũ đa chức năng:** Đảm bảo sự hợp tác chặt chẽ giữa các bên liên quan để quản lý kỳ vọng và giải quyết vấn đề.

## Project-Type Specific Requirements

### Tổng quan
Dự án này là một **Web App & API Backend** phức tạp. Phần Frontend sẽ là một ứng dụng web được render phía máy chủ (SSR) để tối ưu hóa hiệu suất và SEO, trong khi phần Backend sẽ cung cấp một bộ API mạnh mẽ, có phiên bản và được bảo vệ để hỗ trợ các hoạt động của nền tảng.

### Yêu cầu Kỹ thuật - Frontend (Web App)
*   **Kiến trúc Rendering:** Hệ thống sẽ sử dụng Server-Side Rendering (SSR) để đảm bảo thời gian tải trang ban đầu nhanh và thân thiện với các công cụ tìm kiếm.
*   **Tối ưu hóa SEO:** SEO sẽ được tập trung ưu tiên cho các trang tin tuyển dụng công khai do nhà tuyển dụng đăng tải để thu hút ứng viên từ các công cụ tìm kiếm. Các trang quản trị và trang cá nhân của ứng viên không yêu cầu tối ưu SEO.
*   **Tính năng Real-time:** Giao diện người dùng phải hỗ trợ cập nhật theo thời gian thực cho tính năng "Trò chuyện Trực tuyến" để đảm bảo tin nhắn được gửi và nhận ngay lập tức.
*   **Hỗ trợ trình duyệt:** Nền tảng sẽ hỗ trợ các phiên bản mới nhất của các trình duyệt hiện đại (Chrome, Firefox, Safari, Edge).
*   **Khả năng truy cập (Accessibility):** Giao diện phải tuân thủ các tiêu chuẩn WCAG ở mức AA để đảm bảo người dùng khuyết tật có thể sử dụng được.

### Yêu cầu Kỹ thuật - Backend (API)
*   **Xác thực & Ủy quyền:** Tất cả các endpoint được bảo vệ sẽ tiếp tục sử dụng phương thức xác thực dựa trên JWT được lưu trữ trong HttpOnly Cookie.
*   **Định dạng dữ liệu:** API sẽ chỉ sử dụng định dạng `JSON` cho tất cả các yêu cầu và phản hồi. `multipart/form-data` sẽ được hỗ trợ cho các endpoint tải tệp lên. XML sẽ không được hỗ trợ.
*   **Giới hạn Tần suất gọi API (Rate Limiting):** Để đảm bảo sự ổn định và chống lạm dụng, hệ thống sẽ triển khai giới hạn tần suất gọi API ở mức 20 yêu cầu mỗi phút cho mỗi người dùng.
*   **Versioning:** API sẽ tuân thủ chiến lược versioning với tiền tố `/api/v1` cho tất cả các endpoint.
*   **SDK:** Sẽ không có SDK công khai nào được phát triển cho bên thứ ba trong phạm vi của dự án này.

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**Triết lý MVP:** Sự kết hợp giữa **"Giải quyết Vấn đề"** và **"Nền tảng"**. Phiên bản đầu tiên sẽ giải quyết một vấn đề thực sự của người dùng trên một nền tảng kỹ thuật vững chắc, sẵn sàng cho việc mở rộng trong tương lai.

**Yêu cầu về Nguồn lực:** Dự án sẽ được phát triển bởi một nhà phát triển duy nhất. Điều này đòi hỏi việc quản lý phạm vi và ưu tiên hóa một cách chặt chẽ để đảm bảo tiến độ.

### MVP Feature Set (Phase 1)

**Core User Journeys Supported:**
*   **Ứng viên (Minh Anh):** Trải nghiệm vòng lặp khép kín từ phân tích CV, luyện tập phỏng vấn, đến tìm kiếm và kết nối với nhà tuyển dụng.
*   **Nhà tuyển dụng (Khải Minh):** Quy trình làm việc hiệu quả từ việc đăng tin, sàng lọc ứng viên bằng AI, đến việc quản lý và tương tác trực tiếp.
*   **Quản trị viên (Anh Hùng):** Khả năng giám sát và quản lý cơ bản để đảm bảo hệ thống hoạt động ổn định.

**Must-Have Capabilities:**
1.  Phân tích & Tìm kiếm CV bằng AI
2.  Phòng phỏng vấn AI ảo (được xác định là thách thức kỹ thuật chính)
3.  Tìm kiếm Ứng viên Nâng cao
4.  Trò chuyện Trực tuyến (Real-time Chat)
5.  Quản lý "Bộ sưu tập Ứng viên"
6.  Dashboard quản trị toàn diện

### Post-MVP Features

**Phase 2 (Tăng trưởng):**
*   **Hệ thống Kiểm chứng Kỹ năng (Skill Verification):** Sẽ được xem xét sau khi MVP đã ổn định.
*   **Tích hợp Email và Lịch trình tự động:** Cải thiện quy trình làm việc của nhà tuyển dụng.

**Phase 3 (Mở rộng):**
*   **Ứng dụng di động**
*   Các công cụ phân tích xu hướng thị trường lao động.

### Risk Mitigation Strategy (Chiến lược Giảm thiểu Rủi ro)

*   **Rủi ro Kỹ thuật:** Thách thức lớn nhất là **Phòng phỏng vấn AI ảo**. Để giảm thiểu rủi ro, chúng ta sẽ ưu tiên nguồn lực và thời gian cho tính năng này, có thể bắt đầu với một phiên bản đơn giản hơn và cải tiến dần.
*   **Rủi ro Thị trường:** Được giảm thiểu vì dự án ban đầu tập trung vào việc xây dựng nội bộ, cho phép chúng ta tinh chỉnh sản phẩm dựa trên phản hồi trực tiếp trước khi ra mắt rộng rãi.
*   **Rủi ro Nguồn lực:** Vì dự án phụ thuộc vào một nhà phát triển duy nhất, rủi ro về tiến độ là rất cao. Để giảm thiểu, chúng ta sẽ tuân thủ nghiêm ngặt phạm vi MVP đã xác định và tránh "scope creep" (phát sinh yêu cầu). Việc ghi chép tài liệu cẩn thận trong suốt quá trình cũng rất quan trọng để dễ dàng chuyển giao hoặc mở rộng đội ngũ trong tương lai.

## Functional Requirements

### Quản lý Người dùng & Xác thực
*   **FR1:** Một người dùng có thể đăng ký tài khoản với vai trò là 'Người tìm việc' hoặc 'Nhà tuyển dụng'.
*   **FR2:** Một người dùng có thể đăng nhập bằng email và mật khẩu để nhận một cookie xác thực an toàn (HttpOnly).
*   **FR3:** Một người dùng đã xác thực có thể xem thông tin cá nhân của mình (email, ngày tham gia).
*   **FR4:** Một người dùng đã xác thực có thể thay đổi mật khẩu của mình.
*   **FR5:** Một người dùng đã xác thực có thể xóa tài khoản của mình và tất cả dữ liệu liên quan.

### Quản lý CV (Cho Người tìm việc)
*   **FR6:** Người tìm việc có thể tải lên tệp CV (định dạng PDF, DOCX).
*   **FR7:** Người tìm việc có thể xem danh sách tất cả các CV đã tải lên của mình.
*   **FR8:** Người tìm việc có thể xem kết quả phân tích chi tiết cho một CV cụ thể.
*   **FR9:** Người tìm việc có thể xóa một CV cụ thể và dữ liệu phân tích liên quan của nó.
*   **FR10:** Người tìm việc có thể tải xuống tệp gốc của một CV đã tải lên.
*   **FR11:** Người tìm việc có thể kiểm soát trạng thái hiển thị công khai (public/private) cho CV của mình.

### Phân tích AI & Phỏng vấn
*   **FR12:** Hệ thống có thể phân tích một CV được tải lên để trích xuất văn bản và kỹ năng.
*   **FR13:** Hệ thống có thể cung cấp điểm chất lượng chi tiết và phản hồi cải thiện cho một CV.
*   **FR14:** Người tìm việc có thể thiết lập một phòng phỏng vấn AI ảo cho một mô tả công việc hoặc vai trò cụ thể.
*   **FR15:** Người tìm việc có thể tương tác với AI phỏng vấn bằng giọng nói.
*   **FR16:** Người tìm việc có thể nhận được báo cáo hiệu suất chi tiết sau một buổi phỏng vấn AI.
*   **FR17:** Người tìm việc có thể xem lịch sử các buổi phỏng vấn AI đã thực hiện.

### Quản lý Công việc & Ứng viên (Cho Nhà tuyển dụng)
*   **FR18:** Nhà tuyển dụng có thể tải lên một Mô tả Công việc (JD).
*   **FR19:** Hệ thống có thể phân tích một JD được tải lên để trích xuất các yêu cầu.
*   **FR20:** Nhà tuyển dụng có thể xem danh sách tất cả các JD đã tải lên của mình.
*   **FR21:** Nhà tuyển dụng có thể xem danh sách các ứng viên đã được xếp hạng phù hợp với một JD cụ thể.
*   **FR22:** Nhà tuyển dụng có thể tìm kiếm ứng viên bằng các truy vấn ngôn ngữ tự nhiên.
*   **FR23:** Nhà tuyển dụng có thể tạo và quản lý các "bộ sưu tập" ứng viên cho các vai trò hiện tại hoặc tương lai.
*   **FR24:** Nhà tuyển dụng có thể xem kết quả phân tích CV và phỏng vấn AI công khai của một ứng viên.

### Giao tiếp (Trò chuyện)
*   **FR25:** Nhà tuyển dụng có thể bắt đầu một cuộc trò chuyện thời gian thực với một ứng viên.
*   **FR26:** Ứng viên có thể nhận và trả lời tin nhắn thời gian thực từ nhà tuyển dụng.
*   **FR27:** Người dùng có thể xem danh sách tất cả các cuộc trò chuyện của mình.

### Quản trị
*   **FR28:** Quản trị viên có thể xem một dashboard giám sát với các chỉ số sức khỏe hệ thống (GPU, RAM, độ trễ).
*   **FR29:** Quản trị viên có thể xem log hệ thống.
*   **FR30:** Quản trị viên có thể quản lý người dùng (xem, lọc, đình chỉ).
*   **FR31:** Quản trị viên có thể quản lý nội dung (xem và ẩn các tin tuyển dụng).

## Non-Functional Requirements

### Performance
*   **NFR1.1 (Phản hồi chung):** Hệ thống sẽ cung cấp phản hồi kịp thời cho các tương tác của người dùng, đảm bảo trải nghiệm người dùng cơ bản là mượt mà và không có độ trễ đáng kể trong các chức năng cốt lõi. Ưu tiên hàng đầu cho v1 là tính đúng đắn (correctness) của chức năng.
*   **NFR1.2 (Real-time Chat):** Tin nhắn trong tính năng trò chuyện thời gian thực sẽ được gửi và nhận gần như ngay lập tức.

### Security
*   **NFR2.1 (Bảo vệ dữ liệu):** Tất cả thông tin cá nhân của ứng viên, nội dung CV/JD, và thông tin đăng nhập phải được bảo vệ khỏi truy cập trái phép và lộ lọt dữ liệu.
*   **NFR2.2 (Kiểm soát truy cập dựa trên vai trò):** Hệ thống phải tuân thủ nghiêm ngặt mô hình phân quyền theo vai trò (Ứng viên, Nhà tuyển dụng, Quản trị viên).
    *   Ứng viên chỉ có thể xem và quản lý dữ liệu của chính mình (CV, phòng phỏng vấn).
    *   Nhà tuyển dụng chỉ có thể xem và quản lý JD của mình, và các CV công khai hoặc được phép truy cập của ứng viên.
    *   Quản trị viên có thể truy cập tất cả thông tin người dùng và nội dung để quản lý hệ thống.
*   **NFR2.3 (Bảo vệ chống tấn công):** Hệ thống phải có khả năng chống lại các cuộc tấn công từ chối dịch vụ (DoS) ở mức độ cơ bản thông qua cơ chế giới hạn tần suất gọi API.
*   **NFR2.4 (Mã hóa):** Dữ liệu nhạy cảm (ví dụ: mật khẩu) phải được mã hóa khi lưu trữ và truyền tải.

### Scalability
*   **NFR3.1 (Người dùng đồng thời):** Hệ thống phải hỗ trợ trên 100 người dùng đồng thời mà không làm giảm đáng kể trải nghiệm của người dùng.
*   **NFR3.2 (Mất dữ liệu):** Trong trường hợp vượt quá khả năng xử lý, hệ thống có thể tăng thời gian chờ từ phía người dùng nhưng tuyệt đối không được gây mất dữ liệu.

### Accessibility
*   **NFR4.1 (Cơ bản):** Hệ thống sẽ tuân thủ các nguyên tắc cơ bản về khả năng truy cập để đảm bảo tính dễ sử dụng và khả năng điều hướng chung cho tất cả người dùng, nhưng không cam kết tuân thủ các tiêu chuẩn WCAG cụ thể trong v1.

### Integration
*   **NFR5.1 (Ollama LLM):** Hệ thống phải tích hợp liền mạch với Ollama LLM cho tất cả các tác vụ phân tích và tạo sinh AI.
*   **NFR5.2 (Email SMTP):** Hệ thống phải tích hợp với một dịch vụ Email SMTP để gửi các thông báo giao dịch.
*   **NFR5.3 (Độ tin cậy tích hợp):** Các tích hợp phải có độ tin cậy cao; đặc biệt Ollama được giả định là luôn khả dụng.

### Reliability
*   **NFR6.1 (Bảo toàn dữ liệu):** Dữ liệu của người dùng và nhà tuyển dụng (bao gồm CV, JD, lịch sử phỏng vấn, tin nhắn) phải được bảo toàn tuyệt đối. Mất dữ liệu là một thất bại nghiêm trọng của hệ thống.
*   **NFR6.2 (Thời gian hoạt động):** Các chức năng cốt lõi (đăng nhập, tải CV, phân tích CV, đăng tuyển job, xem ứng viên phù hợp, tạo phòng phỏng vấn) phải luôn khả dụng với thời gian hoạt động tối thiểu là 99% để đảm bảo trải nghiệm người dùng không bị gián đoạn.
*   **NFR6.3 (Khả năng phục hồi):** Hệ thống phải có khả năng phục hồi sau các lỗi không nghiêm trọng mà không ảnh hưởng đến toàn vẹn dữ liệu.