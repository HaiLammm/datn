# CV 15.pdf Analysis Report

## 📊 Summary

**Actual Experience**: ~19.2 years (Feb 1996 - Aug 2015)  
**LLM Extracted**: 15-17 years  
**Error Rate**: ~16-20% (3-4 years difference)

---

## 🔍 Detailed Experience Breakdown

| # | Position | Period | Duration | Company |
|---|----------|--------|----------|---------|
| 1 | **Director of Information Technology** | Nov 2012 - Aug 2015 | **2.8 years** (33 months) | MSBA |
| 2 | **Team Leader** | May 2005 - Nov 2012 | **7.5 years** (90 months) | Cardiovascular Program |
| 3 | **Chief Information Officer** | Jul 2000 - Feb 2005 | **4.6 years** (55 months) | Dept of Mental Retardation (MA) |
| 4 | **Director of Applications Development** | Feb 1996 - Jun 2000 | **4.3 years** (52 months) | Dept of Youth Services |

**Total**: 230 months = **19.2 years**

---

## ❓ Why LLM Extracted Wrong (15-17 years instead of 19.2)?

### Possible Reasons:

1. **Date Format Complexity**
   - Dates are in format: `MM/YYYY to MM/YYYY`
   - LLM may have trouble parsing this format accurately

2. **Truncation Issue**
   - CV content was truncated to 3000 chars in prompt
   - Position #4 (oldest, 1996-2000) may have been cut off!
   
   ```python
   # From service.py line 227:
   truncated_cv = cv_content[:self.MAX_CV_CONTENT_LENGTH]  # 3000 chars
   ```

3. **LLM Calculation Error**
   - LLM might calculate: 2015 - 2000 = 15 years (missing 1996-2000)
   - Or: 2015 - 1998 = 17 years (partial oldest position)

4. **Position Overlap Not Considered**
   - All positions are sequential (no overlap)
   - LLM should sum durations, not just (latest - earliest)

---

## 🐛 ROOT CAUSE IDENTIFIED

### **PRIMARY ISSUE: Content Truncation**

Looking at the CV structure:
- **Position 1-3**: Within first ~2500 characters ✅
- **Position 4** (1996-2000): Appears around char 2800-3000 ⚠️
- **Truncation at 3000 chars**: May cut off or partially include Position 4 ❌

**Evidence**:
```
Line 52: Director of Applications Development 02/1996 to 06/2000
```
This is near the END of the experience section, close to truncation point!

### **SECONDARY ISSUE: LLM Prompt Quality**

Current prompt doesn't explicitly ask LLM to:
- ✅ Sum all position durations
- ✅ Parse date ranges carefully
- ✅ Count from FIRST job to LAST job

---

## 💡 RECOMMENDATIONS

### 1. **Fix Content Truncation** (HIGH PRIORITY)

```python
# Option A: Increase truncation limit
MAX_CV_CONTENT_LENGTH = 5000  # Instead of 3000

# Option B: Smart truncation - preserve experience section
def smart_truncate(cv_content, max_length=3000):
    # Extract experience section fully
    exp_section = extract_experience_section(cv_content)
    
    # Truncate other sections if needed
    # But keep ALL experience data
    ...
```

### 2. **Improve LLM Prompt** (HIGH PRIORITY)

```python
analysis_prompt = f"""Analyze this CV and respond with ONLY a JSON object.

IMPORTANT FOR EXPERIENCE CALCULATION:
1. Find ALL job positions with dates (MM/YYYY format)
2. Calculate duration for EACH position separately
3. SUM all durations to get total_years
4. Format: {{"total_years": <sum of all positions>}}

CV:
{cv_content}

JSON format:
{{"experience_breakdown":{{"total_years":<sum_all_positions>,"key_roles":[...]}},...}}
"""
```

### 3. **Add Post-Processing Validation** (MEDIUM PRIORITY)

```python
# After LLM extraction
if extracted_years < 10:
    # Re-extract using regex fallback
    positions = extract_dates_regex(cv_content)
    total_years = sum_position_durations(positions)
    
    if total_years > extracted_years:
        logger.warning(f"LLM underestimated: {extracted_years} vs {total_years}")
        # Use regex result
        return total_years
```

---

## 🎯 Action Items

- [ ] Increase `MAX_CV_CONTENT_LENGTH` from 3000 to 5000
- [ ] Update LLM prompt with explicit instructions for summing experience
- [ ] Add regex-based fallback for date extraction
- [ ] Add validation: warn if total_years seems too low
- [ ] Test with CV 15.pdf again to verify fix

---

## 📈 Expected Impact

**Before Fix**:
- CV 15.pdf: 19.2 years → LLM extracts 15-17 years (❌ 16-20% error)

**After Fix**:
- CV 15.pdf: 19.2 years → LLM should extract 18-20 years (✅ <10% error)
