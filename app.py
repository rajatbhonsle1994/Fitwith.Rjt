import streamlit as st
import sqlite3
import uuid

# 1. ऐप का सेटअप और कस्टम CSS (लुक बदलने के लिए)
st.set_page_config(page_title="FitMatch Premium", layout="wide", page_icon="🏋️‍♂️")

# ऐप को सुंदर और अट्रैक्टिव बनाने के लिए कस्टम स्टाइलिंग
st.markdown("""
    <style>
        /* बैकग्राउंड और मुख्य फॉन्ट */
        .stApp {
            background-color: #0e1117;
            color: #ecf0f1;
        }
        
        /* मुख्य हेडर स्टाइल */
        .main-title {
            text-align: center;
            font-size: 42px;
            font-weight: 800;
            background: linear-gradient(45deg, #ff4b4b, #ff7676);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        /* सब-टाइटल स्टाइल */
        .sub-title {
            text-align: center;
            font-size: 18px;
            color: #a0aec0;
            margin-bottom: 40px;
        }
        
        /* ट्रेनर कार्ड डिज़ाइन */
        .trainer-card {
            background: linear-gradient(145deg, #1a1f2c, #141822);
            border-left: 5px solid #ff4b4b;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
            margin-bottom: 20px;
            transition: transform 0.2s;
        }
        .trainer-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 25px rgba(255, 75, 75, 0.15);
        }
        
        /* चैट बॉक्स स्टाइल */
        .chat-box {
            background-color: #1a1f2c;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            border: 1px solid #2d3748;
        }
        
        /* इनपुट बॉक्स को सुंदर बनाना */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            background-color: #1f2430 !important;
            color: white !important;
            border: 1px solid #4a5568 !important;
            border-radius: 8px !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==================== DATABASE SETUP ====================
def init_db():
    conn = sqlite3.connect("fitmatch.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trainers (
            id TEXT PRIMARY KEY, name TEXT, specialty TEXT, price TEXT, bio TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT, sender TEXT, message TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def add_trainer(t_id, name, specialty, price, bio):
    conn = sqlite3.connect("fitmatch.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO trainers VALUES (?, ?, ?, ?, ?)", (t_id, name, specialty, price, bio))
    conn.commit()
    conn.close()

def get_all_trainers():
    conn = sqlite3.connect("fitmatch.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trainers")
    data = cursor.fetchall()
    conn.close()
    return data

def save_message(chat_id, sender, message):
    conn = sqlite3.connect("fitmatch.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chats (chat_id, sender, message) VALUES (?, ?, ?)", (chat_id, sender, message))
    conn.commit()
    conn.close()

def get_chat_messages(chat_id):
    conn = sqlite3.connect("fitmatch.db")
    cursor = conn.cursor()
    cursor.execute("SELECT sender, message FROM chats WHERE chat_id = ?", (chat_id,))
    messages = cursor.fetchall()
    conn.close()
    return messages

def get_trainer_chats(trainer_id):
    conn = sqlite3.connect("fitmatch.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT chat_id FROM chats WHERE chat_id LIKE ?", (f'%{trainer_id}',))
    chats = cursor.fetchall()
    conn.close()
    return [c[0] for c in chats]

# ==================== UI HEADER ====================
st.markdown('<div class="main-title">⚡ FITMATCH PREMIUM ⚡</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Find Your Perfect Personal Trainer & Start Your Transformation</div>', unsafe_allow_html=True)

# आकर्षक साइडबार डिज़ाइन
st.sidebar.markdown("<h2 style='color: #ff4b4b; text-align:center;'>🎯 NAVIGATION</h2>", unsafe_allow_html=True)
user_role = st.sidebar.radio("आप कौन हैं? (Select Role)", ["🙋‍♂️ क्लाइंट (Client / User)", "💪 ट्रेनर (Fitness Trainer)"])
st.sidebar.markdown("---")

# ==================== TRAINER SIDE ====================
if user_role == "💪 ट्रेनर (Fitness Trainer)":
    st.markdown("<h2 style='color: #ff4b4b;'>🏆 Trainer Dashboard</h2>", unsafe_allow_html=True)
    
    with st.expander("📝 नया ट्रेनर अकाउंट बनाएं (Register Now)", expanded=False):
        t_name = st.text_input("आपका पूरा नाम (Full Name)")
        t_spec = st.selectbox("आपकी स्पेशलिटी", ["Weight Loss", "Muscle Gain", "Yoga & Flexibility", "Powerlifting"])
        t_price = st.text_input("अपनी मंथली फीस (e.g., ₹4,999/month)")
        t_bio = st.text_area("अपने बारे में कुछ बताएं (Short Bio)")
        
        if st.button("🚀 प्रोफाइल लाइव करें"):
            if t_name and t_price:
                new_id = f"TRN-{uuid.uuid4().hex[:4].upper()}"
                add_trainer(new_id, t_name, t_spec, t_price, t_bio)
                st.success(f"🎉 प्रोफाइल लाइव हो चुकी है! आपकी ID है: {new_id}")
                st.rerun()
            else:
                st.error("कृपया नाम और फीस जरूर भरें।")

    st.markdown("---")
    st.subheader("📥 क्लाइंट्स के इनबॉक्स मैसेजेस")
    
    all_trainers = get_all_trainers()
    if all_trainers:
        trainer_options = {t[0]: t[1] for t in all_trainers}
        active_trainer_id = st.selectbox("अपनी Trainer ID चुनकर लॉगिन करें", list(trainer_options.keys()))
        
        trainer_chats = get_trainer_chats(active_trainer_id)
        if trainer_chats:
            for chat_key in trainer_chats:
                client_name = chat_key.split("-")[0]
                
                st.markdown(f'<div class="chat-box">', unsafe_allow_html=True)
                st.markdown(f"🗣️ **Client: {client_name}**")
                
                msgs = get_chat_messages(chat_key)
                for msg in msgs:
                    color = "#ff4b4b" if msg[0] == "Trainer" else "#10b981"
                    st.markdown(f"<span style='color:{color}; font-weight:bold;'>{msg[0]}:</span> {msg[1]}", unsafe_allow_html=True)
                    
                reply_text = st.text_input("जवाब टाइप करें...", key=f"reply_{chat_key}")
                if st.button("✉️ भेजें", key=f"btn_{chat_key}"):
                    if reply_text:
                        save_message(chat_key, "Trainer", reply_text)
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("अभी तक किसी क्लाइंट ने आपसे चैट शुरू नहीं की है।")
    else:
        st.warning("डेटाबेस में अभी कोई ट्रेनर नहीं है।")

# ==================== CLIENT SIDE ====================
else:
    st.markdown("<h2 style='color: #10b981;'>🔍 हमारे बेस्ट फिटनेस ट्रेनर्स</h2>", unsafe_allow_html=True)
    c_name = st.text_input("अपना नाम दर्ज करें (Your Name)", "Rahul").strip().replace("-", "")
    
    st.markdown("---")
    all_trainers = get_all_trainers()
    
    if not all_trainers:
        st.warning("अभी कोई ट्रेनर उपलब्ध नहीं है। कृपया पहले ट्रेनर मोड में जाकर एक प्रोफाइल बनाएं।")
    else:
        for t in all_trainers:
            t_id, t_name, t_spec, t_price, t_bio = t
            
            # HTML कार्ड फॉर्मेट में ट्रेनर्स को दिखाना
            st.markdown(f"""
                <div class="trainer-card">
                    <span style="background-color: #ff4b4b; padding: 3px 8px; border-radius: 5px; font-size: 12px; font-weight: bold;">ID: {t_id}</span>
                    <h3 style="margin: 10px 0 5px 0; color: white;">{t_name}</h3>
                    <p style="margin: 0; font-size: 14px; color: #10b981;">🎯 <b>स्पेशलिटी:</b> {t_spec} &nbsp;|&nbsp; 💰 <b>फीस:</b> {t_price}</p>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #a0aec0; font-style: italic;">"{t_bio}"</p>
                </div>
            """, unsafe_allow_html=True)
            
            # चैट बटन कार्ड के ठीक नीचे
            if st.button(f"💬 Chat with {t_name.split()[0]}", key=f"chat_{t_id}"):
                st.session_state["active_chat_with"] = t_id
            st.markdown("<br>", unsafe_allow_html=True)

    # लाइव चैट विंडो
    if "active_chat_with" in st.session_state:
        target_id = st.session_state["active_chat_with"]
        t_name = next((t[1] for t in all_trainers if t[0] == target_id), "")
                
        chat_id = f"{c_name}-{target_id}"
        st.markdown(f'<div class="chat-box">', unsafe_allow_html=True)
        st.markdown(f"### 💬 {t_name} के साथ बातचीत")
        
        current_msgs = get_chat_messages(chat_id)
        for msg in current_msgs:
            color = "#10b981" if msg[0] == "Client" else "#ff4b4b"
            label = "You" if msg[0] == "Client" else t_name
            st.markdown(f"<p style='margin:5px 0;'><b>{label}:</b> {msg[1]}</p>", unsafe_allow_html=True)
            
        client_msg = st.text_input("अपना सवाल यहाँ लिखें...", key="client_msg_input")
        if st.button("🚀 संदेश भेजें"):
            if client_msg:
                save_message(chat_id, "Client", client_msg)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
