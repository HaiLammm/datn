---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/docs/prd.md
  - _bmad-output/planning-artifacts/docs/brief.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/docs/brainstorming-session-results.md
  - _bmad-output/planning-artifacts/docs/brownfield-architecture.md
  - _bmad-output/planning-artifacts/docs/doc-out.md
  - _bmad-output/planning-artifacts/docs/po-validation-report.md
  - _bmad-output/planning-artifacts/stories/1.1.story.md
  - _bmad-output/planning-artifacts/stories/1.2.story.md
  - _bmad-output/planning-artifacts/stories/2.1.story.md
  - _bmad-output/planning-artifacts/stories/2.2.story.md
  - _bmad-output/planning-artifacts/stories/2.3.story.md
  - _bmad-output/planning-artifacts/stories/3.1.story.md
  - _bmad-output/planning-artifacts/stories/3.2.1.story.md
  - _bmad-output/planning-artifacts/stories/3.2.story.md
  - _bmad-output/planning-artifacts/stories/3.3.story.md
  - _bmad-output/planning-artifacts/stories/3.4.story.md
  - _bmad-output/planning-artifacts/stories/3.5.story.md
  - _bmad-output/planning-artifacts/stories/3.6.story.md
  - _bmad-output/planning-artifacts/stories/3.7.story.md
  - _bmad-output/planning-artifacts/stories/3.8.story.md
  - _bmad-output/planning-artifacts/stories/4.1.1.story.md
  - _bmad-output/planning-artifacts/stories/4.1.story.md
  - _bmad-output/planning-artifacts/stories/5.1.story.md
  - _bmad-output/planning-artifacts/stories/5.2.story.md
  - _bmad-output/planning-artifacts/stories/5.3.story.md
  - _bmad-output/planning-artifacts/stories/5.4.story.md
  - _bmad-output/planning-artifacts/stories/5.5.story.md
  - _bmad-output/planning-artifacts/stories/5.6.story.md
  - _bmad-output/planning-artifacts/stories/5.7.story.md
  - _bmad-output/planning-artifacts/stories/5.8.story.md
  - _bmad-output/planning-artifacts/stories/6.1.story.md
  - _bmad-output/planning-artifacts/stories/6.2.story.md
  - _bmad-output/planning-artifacts/stories/6.3.story.md
  - _bmad-output/planning-artifacts/stories/6.4.story.md
  - _bmad-output/planning-artifacts/stories/6.5.story.md
  - _bmad-output/planning-artifacts/stories/6.6.story.md
  - _bmad-output/planning-artifacts/stories/6.7.story.md
  - _bmad-output/planning-artifacts/stories/6.8.story.md
  - _bmad-output/planning-artifacts/stories/7.1.story.md
  - _bmad-output/planning-artifacts/stories/7.2.story.md
  - _bmad-output/planning-artifacts/stories/7.3.story.md
  - _bmad-output/planning-artifacts/stories/7.4.story.md
  - _bmad-output/planning-artifacts/stories/8.1.story.md
  - _bmad-output/planning-artifacts/stories/8.2.story.md
  - _bmad-output/planning-artifacts/stories/8.3.story.md
  - _bmad-output/planning-artifacts/stories/8.4.story.md
  - _bmad-output/planning-artifacts/stories/9.1.story.md
  - _bmad-output/planning-artifacts/stories/9.2.story.md
  - _bmad-output/planning-artifacts/stories/9.3.story.md
  - _bmad-output/planning-artifacts/stories/9.4.story.md
---

# UX Design Specification datn

**Author:** Lem
**Date:** 2025-12-31

---

<!-- UX design content will be appended sequentially through collaborative workflow steps -->

## Tóm tắt chung

### Tầm nhìn dự án

Tạo ra một hệ sinh thái tuyển dụng thông minh, "tất cả trong một", giúp ứng viên tối ưu hóa hồ sơ và kỹ năng, đồng thời hỗ trợ nhà tuyển dụng khám phá và sàng lọc tài năng một cách hiệu quả thông qua AI. Nền tảng này tập trung vào sự hiểu biết ngữ nghĩa, phản hồi liên tục và bảo mật dữ liệu với LLM cục bộ.

### Người dùng mục tiêu

*   **Người tìm việc (Job Seekers):** Sinh viên mới tốt nghiệp đến chuyên gia cấp trung muốn cải thiện CV, chuẩn bị phỏng vấn, tìm kiếm cơ hội và phát triển sự nghiệp. Họ cần sự rõ ràng về chất lượng hồ sơ, các khoảng trống kỹ năng và phương pháp chuẩn bị phỏng vấn.
*   **Nhà tuyển dụng (Recruiters):** Các nhà quản lý nhân sự và nhà tuyển dụng kỹ thuật muốn giảm thời gian tuyển dụng, tìm kiếm ứng viên phù hợp hiệu quả hơn và tự động hóa quy trình sàng lọc.
*   **Quản trị viên (Administrators):** Chịu trách nhiệm duy trì ổn định hệ thống, giám sát hiệu suất AI và quản lý nội dung/người dùng.

### Thách thức thiết kế chính

*   **Tích hợp AI mượt mà:** Làm thế nào để các tính năng AI (phân tích CV, phỏng vấn ảo, tìm kiếm ngữ nghĩa) được tích hợp một cách tự nhiên và dễ hiểu trong giao diện người dùng mà không làm người dùng choáng ngợp.
*   **Phản hồi thời gian thực và tương tác:** Thiết kế giao diện cho phòng phỏng vấn AI ảo và trò chuyện trực tuyến để đảm bảo trải nghiệm tương tác giọng nói mượt mà và phản hồi tức thì, đồng thời hiển thị dữ liệu phân tích phức tạp một cách trực quan.
*   **Quản lý dữ liệu phức tạp:** Hiển thị và cho phép quản lý thông tin CV chi tiết, kết quả phân tích AI, lịch sử phỏng vấn, và danh sách ứng viên/JD một cách rõ ràng và dễ điều hướng.
*   **Bảo mật & Quyền riêng tư:** Đảm bảo người dùng tin tưởng vào việc xử lý dữ liệu nhạy cảm (CV, JD) một cách cục bộ và riêng tư, đồng thời cung cấp quyền kiểm soát rõ ràng về khả năng hiển thị dữ liệu.
*   **Tính nhất quán và Khả năng truy cập:** Duy trì tính nhất quán về UI/UX trên toàn bộ nền tảng (sử dụng Shadcn/ui, Tailwind CSS) và đảm bảo khả năng truy cập cơ bản (WCAG AA) cho tất cả người dùng.

### Cơ hội thiết kế

*   **AI làm "huấn luyện viên":** Tận dụng phòng phỏng vấn AI ảo không chỉ để đánh giá mà còn để huấn luyện thích ứng, giúp người dùng học hỏi và cải thiện liên tục.
*   **Hệ sinh thái "tất cả trong một"::** Tạo ra một trải nghiệm người dùng liền mạch, giảm thiểu việc chuyển đổi giữa các công cụ, xây dựng lòng trung thành và sự gắn bó lâu dài.
*   **Cá nhân hóa và gợi ý chủ động:** Sử dụng AI để cung cấp các gợi ý cá nhân hóa về cải thiện CV, lộ trình sự nghiệp và cơ hội việc làm, tạo ra giá trị gia tăng vượt trội.
*   **Trực quan hóa dữ liệu AI:** Thiết kế các dashboard và báo cáo trực quan, dễ hiểu để người dùng (ứng viên, nhà tuyển dụng, quản trị viên) có thể nhanh chóng nắm bắt các thông tin phức tạp từ AI.
*   **Tương tác đa phương thức:** Khám phá các tương tác bằng giọng nói (voice UI) và các yếu tố thời gian thực để làm cho trải nghiệm trở nên năng động và hấp dẫn hơn.

## Trải nghiệm người dùng cốt lõi

### Định nghĩa Trải nghiệm
Trải nghiệm cốt lõi của chúng ta xoay quanh việc **tự động hóa phân tích và kết nối**, giúp cả hai bên (ứng viên và nhà tuyển dụng) **tiết kiệm thời gian** và **đưa ra quyết định tốt hơn** dựa trên dữ liệu thông minh. Trọng tâm không phải là một hành động đơn lẻ, mà là một **vòng lặp giá trị** khép kín: Phân tích -> Cải thiện -> Khám phá -> Kết nối.

### Chiến lược Nền tảng
- **Nền tảng chính:** Một **ứng dụng web hiện đại** và **hoàn toàn đáp ứng (fully responsive)**, ưu tiên trải nghiệm trên máy tính để bàn nhưng vẫn đảm bảo hoạt động mượt mà trên thiết bị di động.
- **Yêu cầu kỹ thuật:** Yêu cầu kết nối Internet ổn định và sẽ tận dụng các tính năng của thiết bị như **microphone** (cho phỏng vấn AI) và **thông báo trình duyệt** (cho chat).

### Các tương tác dễ dàng
- **Tải và Phân tích:** Việc tải CV hoặc JD và nhận lại kết quả phân tích phải diễn ra gần như ngay lập tức và không cần nỗ lực.
- **Kết nối ban đầu:** Bắt đầu một cuộc trò chuyện với ứng viên tiềm năng chỉ bằng một cú nhấp chuột.
- **Tự động hóa là mặc định:** Hệ thống tự động thực hiện các tác vụ nặng nề (phân tích, đối sánh, xếp hạng), người dùng chỉ cần tập trung vào kết quả.

### Những khoảnh khắc thành công quan trọng
- **Khoảnh khắc "À há!" của Ứng viên:** Nhìn thấy điểm CV tăng vọt sau khi áp dụng gợi ý của AI.
- **Khoảnh khắc "Wow!" của Nhà tuyển dụng:** Tìm thấy ứng viên xuất sắc trong top 5 kết quả đầu tiên.
- **Khoảnh khắc "Tin tưởng":** Khi phân tích của AI khớp với đánh giá chuyên môn của người dùng.
- **Khoảnh khắc "Kết nối":** Khi một cuộc trò chuyện qua chat thay thế cho hàng loạt email qua lại.

### Nguyên tắc Trải nghiệm
1.  **Thông minh & Tự động:** Hệ thống chủ động làm việc, người dùng tập trung vào quyết định.
2.  **Tức thì & Có thể hành động:** Cung cấp thông tin chi tiết ngay lập tức và cho phép hành động ngay.
3.  **Trao quyền & Minh bạch:** Giúp người dùng hiểu *tại sao* và cung cấp công cụ để cải thiện.
4.  **Liền mạch & Tích hợp:** Tạo ra một luồng công việc mượt mà trên một nền tảng duy nhất.

## Phản hồi Cảm xúc Mong muốn

### Mục tiêu Cảm xúc Chính
Nền tảng phải khơi gợi những cảm xúc cốt lõi sau ở người dùng:
- **Tự tin:** Cảm thấy chắc chắn về năng lực bản thân và quyết định của mình.
- **Được trao quyền (Empowered):** Cảm thấy có trong tay công cụ mạnh mẽ để kiểm soát sự nghiệp/quy trình tuyển dụng.
- **Hiệu quả:** Cảm thấy thời gian và công sức được sử dụng một cách thông minh.
- **Tin cậy:** Tin tưởng vào các phân tích và đề xuất mà hệ thống đưa ra.
- **Nhẹ nhõm & Hài lòng:** Cảm thấy bớt đi gánh nặng và lo âu, hài lòng với kết quả đạt được.

### Bản đồ Hành trình Cảm xúc
- **Khám phá lần đầu:** Từ "Tò mò" và "Hy vọng" -> Cảm thấy "Được chào đón".
- **Thực hiện hành động cốt lõi:** Từ "Lo lắng" -> Cảm thấy "An toàn" và "An tâm" -> Kết thúc bằng cảm giác "Vỡ lẽ" (Illuminated).
- **Hoàn thành nhiệm vụ:** Cảm giác "Thành tựu" và "Hài lòng".
- **Khi gặp lỗi:** Từ "Bực bội" -> Cảm thấy "Được hỗ trợ" và "Trong tầm kiểm soát".
- **Khi quay trở lại:** Cảm giác "Quen thuộc" và "Hiệu quả".

### Các Cảm xúc Vi mô
Những cặp cảm xúc đối lập sau đây là trọng tâm trong thiết kế:
- **Tự tin** thay vì Bối rối.
- **Tin cậy** thay vì Nghi ngờ.
- Biến **Lo lắng** thành **Hứng khởi** và **Thành tựu**.
- **Hài lòng** thay vì Bực bội.

### Ý nghĩa đối với Thiết kế
- Để **Trao quyền**, chúng ta phải cung cấp phản hồi rõ ràng, có thể hành động và cho phép người dùng kiểm soát dữ liệu của họ.
- Để tạo ra **Hiệu quả**, chúng ta cần tự động hóa các tác vụ phức tạp và trình bày kết quả trên các dashboard tinh gọn.
- Để xây dựng **Sự tin cậy**, chúng ta cần minh bạch hóa *lý do* AI đưa ra đề xuất, hiển thị bằng chứng cụ thể (ví dụ: các kỹ năng khớp).
- Để xây dựng **Sự tự tin**, chúng ta cần sử dụng ngôn ngữ khích lệ và trực quan hóa sự tiến bộ (ví dụ: biểu đồ cải thiện điểm số CV).

### Nguyên tắc Thiết kế Cảm xúc
1.  **Gây dựng sự tự tin:** Mọi tương tác phải củng cố sự tự tin của người dùng vào bản thân và vào nền tảng.
2.  **Mang lại cảm giác kiểm soát:** Người dùng luôn cảm thấy họ là người ra quyết định cuối cùng, được AI hỗ trợ.
3.  **Tạo ra sự nhẹ nhõm và hiệu quả:** Giảm bớt gánh nặng và sự lo lắng trong quy trình tuyển dụng truyền thống.
4.  **Nuôi dưỡng niềm tin:** Minh bạch hóa cách AI hoạt động để xây dựng lòng tin, không phải là một "hộp đen".