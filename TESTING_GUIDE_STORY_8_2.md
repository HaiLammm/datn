# Testing Guide for Story 8.2 - Voice Interaction Components

## 🚀 Quick Start

### Prerequisites

1. **Node.js & npm** installed
2. **Browser**: Chrome or Edge (recommended for full voice support)
3. **Microphone**: Connected and working
4. **Frontend server**: Running

### Step 1: Start Frontend Development Server

```bash
cd /home/luonghailam/Projects/datn/frontend
npm run dev
```

Server should start at: `http://localhost:3000`

### Step 2: Access Test Page

Open your browser and navigate to:

```
http://localhost:3000/test/voice-components
```

You should see a page with 3 tabs:
- **Voice Input**: Test speech recognition
- **AI Response**: Test text-to-speech
- **Transcript**: Test conversation history display

---

## 🧪 Test Scenarios

### Test 1: Voice Input Component (Speech Recognition)

**Tab**: Voice Input

**Steps:**
1. Click the microphone button (big round button)
2. Grant microphone permission if prompted
3. Speak in Vietnamese or English
4. Watch the "Transcript Preview" update in real-time
5. Stop recording by clicking the button again
6. Check "Transcript Result" section for final text

**Expected Results:**
- ✅ Button shows "Listening..." badge when active
- ✅ Waveform animation appears while recording
- ✅ Real-time transcript preview updates as you speak
- ✅ Final transcript appears in green box
- ✅ Console logs: `✅ Transcript received: [your text]`

**Test Cases:**
- ✅ Short phrase: "Xin chào"
- ✅ Long sentence: "Tôi có 5 năm kinh nghiệm làm việc với React và Node.js"
- ✅ English: "I have experience with microservices architecture"

**Browser Compatibility Check:**
- Chrome/Edge: Should work fully ✅
- Firefox: Should show "not supported" and offer manual input ⚠️
- Safari: May work on iOS 14.5+, otherwise manual input ⚠️

---

### Test 2: AI Response Component (Text-to-Speech)

**Tab**: AI Response

**Steps:**
1. Read the default Vietnamese text in the card
2. Click "Play Audio" button
3. Listen to the AI voice
4. Test pause/resume/stop controls
5. Try editing the text in the textarea
6. Click "Voice Settings" to change voice (if multiple available)
7. Replay with different voice

**Expected Results:**
- ✅ Audio plays Vietnamese text correctly
- ✅ Badge shows "Speaking..." while playing
- ✅ Waveform animation appears during playback
- ✅ Pause/Resume buttons work
- ✅ Stop button immediately halts playback
- ✅ Console logs: `🔊 TTS started` and `✅ TTS ended`

**Test Cases:**
- ✅ Default Vietnamese text
- ✅ English text: "Your answer demonstrates good understanding of the topic."
- ✅ Mixed language: "Bạn đã đề cập đến SOLID principles rất tốt."
- ✅ Long text (2-3 paragraphs)

---

### Test 3: Interview Transcript Component

**Tab**: Transcript

**Steps:**
1. View the pre-populated conversation history
2. Go back to "Voice Input" tab
3. Submit an answer (voice or manual)
4. Return to "Transcript" tab
5. Verify new turn appears at bottom
6. Check turn scores are displayed

**Expected Results:**
- ✅ Previous turns display correctly with timestamps
- ✅ AI messages in blue/primary color
- ✅ Candidate messages in gray/muted color
- ✅ Scores shown as colored badges:
  - Green: 8-10 (Excellent)
  - Blue: 6-7.9 (Good)
  - Gray: 5-5.9 (Average)
  - Red: <5 (Needs Improvement)
- ✅ Auto-scrolls to latest message
- ✅ New turns appear after submission

---

### Test 4: Error Handling

**Microphone Permission Denied:**
1. Click voice input
2. Deny microphone permission in browser
3. Expected: Red error alert with instructions

**Browser Not Supported (Firefox):**
1. Open test page in Firefox
2. Expected: Auto-switch to manual input mode
3. Alert shows: "Voice input not supported..."

**Network Error Simulation:**
- This will be tested in full integration (requires backend)

---

## 🔍 Debug Info Panel

At the bottom of the test page, you'll see a "Debug Info" card showing:

- **Browser**: Your current browser
- **Speech Recognition**: Supported ✓ / Not Supported ✗
- **Speech Synthesis**: Supported ✓ / Not Supported ✗
- **Total Turns**: Number of conversation turns

Use this to verify browser compatibility.

---

## 📱 Browser Support Matrix

| Browser | Speech Recognition | Speech Synthesis | Notes |
|---------|-------------------|------------------|-------|
| Chrome 88+ | ✅ Full | ✅ Full | **Recommended** |
| Edge 88+ | ✅ Full | ✅ Full | **Recommended** |
| Firefox 100+ | ❌ None | ✅ Full | Manual input only |
| Safari 14.5+ | ⚠️ Limited | ✅ Full | iOS 14.5+ only |
| Safari <14.5 | ❌ None | ✅ Full | Manual input only |

---

## 🐛 Common Issues & Solutions

### Issue 1: "Microphone not found"
**Solution:**
- Check microphone is connected
- Restart browser
- Check system microphone permissions (System Settings > Privacy > Microphone)

### Issue 2: "Recognition already started"
**Solution:**
- This is a harmless warning
- Reload page if voice input stops working

### Issue 3: No sound from TTS
**Solution:**
- Check system volume
- Check browser isn't muted (right-click browser tab)
- Try a different voice in "Voice Settings"

### Issue 4: Components not loading
**Solution:**
```bash
# Clear Next.js cache
cd /home/luonghailam/Projects/datn/frontend
rm -rf .next
npm run dev
```

### Issue 5: TypeScript errors in editor
**Solution:**
- These are temporary cache issues
- Run: `npx tsc --noEmit` to verify actual errors
- Restart TypeScript server in your editor

---

## 🎯 Full Integration Test (With Backend)

**Once backend is running**, you can test the full flow:

### Prerequisites:
1. Ollama running: `ollama serve`
2. Backend running: `cd backend && uvicorn app.main:app --reload`
3. Create an interview session (via frontend or API)

### Test Full Flow:
1. Navigate to actual interview room: `/interviews/[session-id]/room`
2. Start interview
3. Use voice input to answer questions
4. Verify AI processes answer and responds
5. Check scores appear after each turn
6. Complete interview and view evaluation

**This will test:**
- ✅ API integration (`processTurn()`)
- ✅ Authentication flow
- ✅ Database persistence
- ✅ AI evaluation (DialogFlow AI)
- ✅ Error handling (503, 500, network)

---

## 📊 Test Checklist

### Voice Input Component
- [ ] Microphone button clickable
- [ ] Permission request appears
- [ ] Real-time transcription preview
- [ ] Waveform animation during recording
- [ ] Final transcript saved
- [ ] Manual input fallback works
- [ ] Browser compatibility check works

### AI Response Component
- [ ] Play button works
- [ ] Audio plays correctly
- [ ] Pause/Resume works
- [ ] Stop button works
- [ ] Replay works
- [ ] Voice selection works
- [ ] Waveform animation during playback

### Transcript Component
- [ ] Displays conversation history
- [ ] Shows AI and candidate messages separately
- [ ] Displays scores with correct colors
- [ ] Auto-scrolls to latest
- [ ] Updates when new turn added

### Error Handling
- [ ] Microphone denied shows error
- [ ] Unsupported browser shows fallback
- [ ] Clear error messages

---

## ✅ Success Criteria

You've successfully tested the components if:

1. ✅ Voice input captures your speech accurately (Chrome/Edge)
2. ✅ AI response speaks text clearly with controls working
3. ✅ Transcript displays all turns with scores
4. ✅ Manual input fallback works in unsupported browsers
5. ✅ Waveform animations appear smoothly
6. ✅ No console errors (except TypeScript cache warnings)

---

## 🆘 Need Help?

If components don't work:

1. **Check console logs** (F12 > Console tab)
2. **Verify files exist**:
   ```bash
   ls -la /home/luonghailam/Projects/datn/frontend/features/interviews/hooks/
   ls -la /home/luonghailam/Projects/datn/frontend/features/interviews/components/
   ```
3. **Check browser support** in Debug Info panel
4. **Try different browser** (Chrome recommended)
5. **Clear cache**: Ctrl+Shift+R (hard reload)

---

## 📝 Test Report Template

After testing, note your results:

```
✅ Browser: Chrome 120
✅ Voice Input: Works perfectly
✅ AI Response: Works, Vietnamese voice clear
✅ Transcript: Updates correctly
✅ Waveform animation: Smooth
⚠️ Issue: [describe any issue]
```

---

**Ready to test?** Open: http://localhost:3000/test/voice-components

**Questions?** Check story file: `_bmad-output/implementation-artifacts/8-2-voice-interaction.md`
