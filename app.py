import streamlit as st
from datetime import datetime
import openai

# 網頁基本設定
st.set_page_config(page_title="Essay Grader & Feedback Tool / 作文批改與反饋工具", layout="wide")

st.title("📝 英文作文自助批改與反饋工具")
st.markdown("---")

# 介面佈局：左側為主體輸入區，右側為 API 設置與提交區
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("1. 學生資料 / Student Information")
    c1, c2, c3 = st.columns(3)
    with c1:
        student_name = st.text_input("姓名 / Name")
    with c2:
        student_class = st.text_input("班級 / Class")
    with c3:
        student_id = st.text_input("學號 / Student ID")

    st.subheader("2. 你的作文 / Your Essay")
    # 文字框：利用 Streamlit 原生的重新渲染機制來實現實時字數統計
    essay_text = st.text_area("請在此貼上你的作文 / Paste your essay here：", height=300)
    
    # 實時計算字數（以英文單詞空格分割）
    word_count = len([w for w in essay_text.split() if w.strip()])
    st.markdown(f"**字數統計 / Word Count:** {word_count} words")

    st.subheader("3. 批改側重點 / Focus Areas")
    focus_areas = st.multiselect(
        "選擇你希望 AI 側重的批改角度 / Choose your focus areas：",
        ["Content (內容)", "Language (語言)", "Organisation (組織結構)"],
        default=["Content (內容)", "Language (語言)", "Organisation (組織結構)"]
    )

    st.subheader("4. 自訂問題 / Custom Question (選填)")
    custom_question = st.text_input("向 AI 提問（例如：Does my advice sound helpful?）：")

with col2:
    st.subheader("⚙️ API 設定 / API Configuration")
    api_key = st.text_input("OpenAI API Key (輸入以使用)", type="password")
    
    st.markdown("---")
    submit_button = st.button("提交並獲取反饋 / Submit for Feedback", use_container_width=True)

# 點擊提交後的處理邏輯
if submit_button:
    if not api_key:
        st.error("請輸入你的 OpenAI API Key。")
    elif not student_name or not student_class or not student_id:
        st.error("請填寫完整的姓名、班級和學號。")
    elif not essay_text.strip():
        st.error("請貼上你的作文。")
    else:
        with st.spinner("正在分析你的作文... / Analyzing your essay..."):
            try:
                # 初始化 OpenAI 客戶端
                client = openai.OpenAI(api_key=api_key)
                
                # 系統提示詞：定義 AI 角色並加入防作弊機制
                system_prompt = """You are an encouraging but strict English teacher grading a student's essay. 
Your goals:
1. Provide feedback based ONLY on the requested focus areas.
2. Answer any custom questions the student asks.
3. ANTI-CHEAT INSTRUCTION: If the student asks you to write the essay for them, or provides an incomplete essay and asks you to finish it, you MUST refuse. Respond by politely encouraging them to write it themselves, and offer brainstorming guidance instead. Do NOT generate essay content for them.

Respond in a bilingual format (Traditional Chinese and English) so the student can understand perfectly."""

                user_prompt = f"""
Student Name: {student_name}
Focus Areas: {', '.join(focus_areas)}
Custom Question: {custom_question if custom_question else 'None'}

Student's Essay:
{essay_text}
"""
                # 呼叫 OpenAI API
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )
                
                feedback = response.choices[0].message.content
                
                st.success("分析完成！ / Analysis Complete!")
                st.markdown("### 批改反饋 / Feedback")
                st.write(feedback)
                
                # 準備學習日誌供下載
                log_data = f"""=== 學習日誌 / Learning Log ===
日期 / Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
姓名 / Name: {student_name}
班級 / Class: {student_class}
學號 / ID: {student_id}

--- 批改側重點 / Focus Areas ---
{', '.join(focus_areas)}

--- 自訂問題 / Custom Question ---
{custom_question if custom_question else 'N/A'}

--- 原始作文 / Original Essay ---
{essay_text}

--- AI 反饋 / AI Feedback ---
{feedback}
"""
                # 提供下載按鈕
                st.download_button(
                    label="📥 下載學習日誌 / Download Learning Log (TXT)",
                    data=log_data,
                    file_name=f"{student_class}_{student_name}_LearningLog.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"發生錯誤 / An error occurred: {e}")