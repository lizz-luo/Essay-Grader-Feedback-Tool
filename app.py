import streamlit as st
from datetime import datetime
from groq import Groq

# 網頁基本設定
st.set_page_config(page_title="Advice Email Grader / 建議電郵批改工具", layout="wide")

st.title("📝 英文建議電郵批改工具 (Advice Email)")
st.markdown("---")

# 定義各類別的具體評分重點 (Checklist Goals)
checklist_dict = {
    "Content (內容)": [
        "Address the problem — Did I address the reader's problem?",
        "Two pieces of advice — Did I give at least 2 pieces of advice?",
        "Explain advice — Did I explain how each advice can help?",
        "Caring tone — Did I use a caring and encouraging tone?"
    ],
    "Language (語言)": [
        "Modal verbs — Did I use modal verbs (e.g. should, could, might)?",
        "Conditional sentences — Did I use conditional sentences (e.g. If you..., you could...)?",
        "Empathy phrases — Did I use phrases to show empathy (e.g. I understand how you feel)?",
        "Linking words — Did I use appropriate linking words (e.g. firstly, moreover, in addition)?",
        "Spelling and punctuation — Are my spelling and punctuation correct?"
    ],
    "Organisation (組織結構)": [
        "Greeting and sign-off — Did I include a proper greeting and sign-off?",
        "Acknowledge the problem — Did I acknowledge the reader's problem in the opening?",
        "Separate paragraphs — Did I organise my advice in separate paragraphs?",
        "Encouraging closing — Did I end with an encouraging closing?"
    ]
}

# 介面佈局
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

    st.subheader("2. 你的電郵作文 / Your Advice Email")
    essay_text = st.text_area("請在此貼上你的作文 / Paste your email here：", height=300)
    
    word_count = len([w for w in essay_text.split() if w.strip()])
    st.markdown(f"**字數統計 / Word Count:** {word_count} words")

    st.subheader("3. 批改側重點 / Focus Areas")
    # 動態聯動下拉選單
    selected_category = st.selectbox("選擇批改大類 / Choose a category：", list(checklist_dict.keys()))
    # 根據大類，動態顯示對應的 Checklist goals
    selected_goal = st.selectbox("選擇具體評分重點 / Choose a checklist goal：", checklist_dict[selected_category])

    st.subheader("4. 自訂問題 / Custom Question (選填)")
    custom_question = st.text_input("向 AI 提問（例如：Does my advice sound helpful?）：")

with col2:
    st.info("💡 系統已自動連接老師的 AI 批改伺服器，你只需填寫左側資料並點擊下方按鈕即可。")
    st.markdown("---")
    submit_button = st.button("提交並獲取反饋 / Submit for Feedback", use_container_width=True)

# 點擊提交後的處理邏輯
if submit_button:
    api_key = st.secrets.get("GROQ_API_KEY", "")
    
    if not api_key:
        st.error("系統未設定 API Key，請聯繫老師。")
    elif not student_name or not student_class or not student_id:
        st.error("請填寫完整的姓名、班級和學號。")
    elif not essay_text.strip():
        st.error("請貼上你的作文。")
    else:
        with st.spinner("正在分析你的作文... / Analyzing your email..."):
            try:
                client = Groq(api_key=api_key)
                
                # 升級版的系統提示詞 (Prompt Engineering)
                system_prompt = """You are an encouraging but strict English teacher grading a student's advice reply email.

Your core directives:
1. STRICT ALIGNMENT: You will be provided with a specific "Category" and a "Checklist Goal". You MUST ONLY evaluate the student's writing based on this EXACT checklist goal. Do NOT provide feedback on anything outside this boundary. For example, if the goal is about 'Content', completely ignore spelling or grammar errors. Keep feedback focused and actionable.
2. Answer any custom questions the student asks.
3. ANTI-CHEAT INSTRUCTION: If the student asks you to write the email for them, or provides an incomplete email and asks you to finish it, you MUST refuse. Respond by politely encouraging them to write it themselves, and offer brainstorming guidance instead. Do NOT generate email content for them.

Output Format (Must be entirely bilingual in Traditional Chinese and English):
1. A short, encouraging greeting.
2. A structured Markdown table with exactly three columns: 
   | Checklist Goal (評分重點) | Did Well (做得好的地方) | Tips to Improve (改進建議) |
   Keep the "Tips to Improve" short, clear, actionable, and use simple words.
3. ✏️ Try This! (試試這樣寫！): Pick ONE specific weak sentence from the student's writing that relates to the chosen checklist goal. Provide a "Before (修改前)" and "After (修改後)" example. The "After" version MUST stay close to their original sentence so it feels achievable and encouraging. Do not completely rewrite their idea."""

                user_prompt = f"""
Student Name: {student_name}
Category: {selected_category}
Checklist Goal: {selected_goal}
Custom Question: {custom_question if custom_question else 'None'}

Student's Email:
{essay_text}
"""
                # 呼叫 Groq API，降低 temperature 讓 AI 更嚴格遵守格式與邊界
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3
                )
                
                feedback = response.choices[0].message.content
                
                st.success("分析完成！ / Analysis Complete!")
                st.markdown("### 批改反饋 / Feedback")
                st.write(feedback)
                
                # 學習日誌更新格式
                log_data = f"""=== 學習日誌 / Learning Log ===
日期 / Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
姓名 / Name: {student_name}
班級 / Class: {student_class}
學號 / ID: {student_id}

--- 評分重點 / Focus ---
Category: {selected_category}
Goal: {selected_goal}

--- 自訂問題 / Custom Question ---
{custom_question if custom_question else 'N/A'}

--- 原始作文 / Original Email ---
{essay_text}

--- AI 反饋 / AI Feedback ---
{feedback}
"""
                st.download_button(
                    label="📥 下載學習日誌 / Download Learning Log (TXT)",
                    data=log_data,
                    file_name=f"{student_class}_{student_name}_AdviceEmailLog.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"發生錯誤 / An error occurred: {e}")