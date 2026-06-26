import streamlit as st
import sqlite3
import uuid

# 1. ऐप का सेटअप और प्रीमियम मोबाइल-नेटीव CSS
st.set_page_config(page_title="FitMatch Elite", layout="wide", page_icon="⚡")

# यह स्टाइलिंग ऐप को पूरी तरह से एक महंगे इंटरनेशनल ऐप में बदल देगी
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
        
        /* पूरे ऐप का बैकग्राउंड और फॉन्ट चेंज */
        .stApp {
            background: radial-gradient(circle at 50% 50%, #11141e 0%, #08090d 100%);
            font-family: 'Poppins', sans-serif;
            color: #ffffff;
        }
        
        /* अल्टीमेट प्रीमियम एनिमेटेड हेडर */
        .premium-header-box {
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, rgba(255, 75, 75, 0.05), rgba(16, 185, 129, 0.05));
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.03);
            margin-bottom: 35px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        }
        
        .premium-title {
            font-size: 46px;
            font-weight: 800;
            letter-spacing: 2px;
            background: linear-gradient(90deg, #ff4b5c, #f9d423, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
            text-shadow: 0 0 30px rgba(255, 75, 92, 0.2);
        }
        
        .premium-tagline {
            font-size: 15px;
            color: #8fa0b7;
            font-weight: 300;
            text-transform: uppercase;
            letter-spacing: 4px;
        }

        /* काँच जैसा चमकदार ट्रेनर कार्ड (Glassmorphism Effect) */
        .lux-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
            position: relative;
            overflow: hidden;
        }
        
        /* कार्ड के पीछे एक हल्का सा नियॉन ग्लो */
        .lux-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(45deg, transparent, rgba(255, 75, 92, 0.03), transparent);
            transition: transform 0.6s;
            transform: translateX(-100%);
        }

        .lux-card:hover::before {
            transform: translateX(100%);
        }

        .lux-card:hover {
            transform: translateY(-5px);
            border: 1px solid rgba(255, 75, 92, 0.3);
            box-shadow: 0 20px 40px rgba(255, 75, 92, 0.1);
        }
        
        .trainer-id-badge {
            background: linear-gradient(90deg, #ff4b5c, #ff6b6b);
            color: white;
            font-size: 11px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 30px;
            letter-spacing: 1px;
            display: inline-block;
            margin-bottom: 12px;
            box-shadow: 0 4px 10px rgba(255, 75, 92, 0.3);
        }
        
        .price-tag {
            font-size: 18px;
            font-weight: 600;
            color: #10b981;
            background: rgba(16, 185, 129, 0.1);
            padding: 4px 14px;
            border-radius: 10px;
            border: 1px solid rgba(16, 185, 129, 0.2);
            float: right;
        }
        
        /* प्रीमियम चैट विंडो डिजाइन */
        .lux-chat-container {
            background: #0f121d;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 25px;
            box-shadow: inset 0 4px 20px rgba(0,0,0,0.6);
            margin-top: 30px;
        }
        
        /* बटन्स को अट्रैक्टिव और नियॉन ग्लोइंग बनाना */
        div.stButton > button {
            background: linear-gradient(90deg, #ff4b5c, #ff6b6b) !important;
            color: white !important;
            font-weight: 600 !important;
            letter-spacing: 1px !important;
            border: none !important;
            padding: 12px 30px !important;
            border-radius: 14px !important;
            box-shadow: 0 6px 20px rgba(255, 75, 92, 0.25) !important;
            transition: all 0.3s !important;
            width: 100%;
        }
        
        div.stButton > button:hover {
            transform: scale(1.02) !important;
            box-shadow: 0 10px 25px rgba(255, 75, 92, 0.45) !important;
            background: linear-gradient(90deg, #ff6b6b, #ff4b5c) !important;
        }
        
        /* साइडबार को डार्क प्रीमियम लुक देना */
        section[data-testid="stSidebar"] {
            background-color: #0b0d14 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.03);
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

# ==================== LUXURY UI HEADER ====================
st.markdown("""
    <div class="premium-header-box">
        <div class="premium-title">👑 FITMATCH ELITE</div>
        <div class="premium-tagline">The Luxury Fitness Network</div>
    </div>
""", unsafe_allow_html=True)

# साइडबार
st.sidebar.markdown("<h3 style='color: #ff4b5c; font-weight:800; text-align:center; letter-spacing:1px;'>🌟 WORKSPACE</h3>", unsafe_allow_html=True)
user_role = st.sidebar.radio("चुनें आप कौन हैं:", ["🙋‍♂️ क्लाइंट (VIP Access)", "💪 ट्रेनर (Elite Coach)"])
st.sidebar.markdown("---")

# ==================== TRAINER SIDE ====================
if user_role == "💪 ट्रेनर (Elite Coach)":
    st.markdown("<h2 style='color: #ff4b5c; font-weight:600;'>🏆 Coach Console</h2>", unsafe_allow_html=True)
    
    with st.expander("📝 नई एलीट प्रोफाइल रजिस्टर करें", expanded=False):
        t_name = st.text_input("आपका पूरा नाम (Full Name)")
        t_spec = st.selectbox("आपकी मास्टर स्पेशलिटी", ["Weight Loss", "Muscle Gain", "Yoga & Flexibility", "Powerlifting"])
        t_price = st.text_input("मंथली प्रीमियम फीस (e.g., ₹4,999 / Month)")
        t_bio = st.text_area("अपने बारे में कुछ खास बताएं (Short Bio)")
        
        if st.button("🚀 प्रोफाइल लाइव करें"):
            if t_name and t_price:
                new_id = f"TRN-{uuid.uuid4().hex[:4].upper()}"
                add_trainer(new_id, t_name, t_spec, t_price, t_bio)
                st.success(f"🎉 बधाई हो! आपकी प्रोफाइल लाइव हो चुकी है। आपकी ID है: {new_id}")
                st.rerun()
            else:
                st.error("कृपया आवश्यक जानकारी भरें।")

    st.markdown("---")
    st.subheader("📥 क्लाइंट्स की तरफ से आए रिक्वेस्ट")
    
    all_trainers = get_all_trainers()
    if all_trainers:
        trainer_options = {t[0]: t[1] for t in all_trainers}
        active_trainer_id = st.selectbox("अपनी Coach ID चुनें", list(trainer_options.keys()))
        
        trainer_chats = get_trainer_chats(active_trainer_id)
        if trainer_chats:
            for chat_key in trainer_chats:
                client_name = chat_key.split("-")[0]
                
                st.markdown('<div class="lux-chat-container">', unsafe_allow_html=True)
                st.markdown(f"🗣️ **Client: {client_name}**")
                
                msgs = get_chat_messages(chat_key)
                for msg in msgs:
                    color = "#ff4b5c" if msg[0] == "Trainer" else "#10b981"
                    st.markdown(f"<p style='margin:4px 0;'><span style='color:{color}; font-weight:bold;'>{msg[0]}:</span> {msg[1]}</p>", unsafe_allow_html=True)
                    
                reply_text = st.text_input("जवाब टाइप करें...", key=f"reply_{chat_key}")
                if st.button("✉️ सेंड रिप्लाई", key=f"btn_{chat_key}"):
                    if reply_text:
                        save_message(chat_key, "Trainer", reply_text)
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("अभी तक किसी वीआईपी क्लाइंट ने आपसे संपर्क नहीं किया है।")
    else:
        st.warning("अभी कोई कोच रजिस्टर नहीं है।")

# ==================== CLIENT SIDE ====================
else:
    st.markdown("<h2 style='color: #10b981; font-weight:600;'>🔍 हमारे वेरीफाइड एलीट कोचेस</h2>", unsafe_allow_html=True)
    c_name = st.text_input("अपना नाम दर्ज करें (Your Full Name)", "Rahul Kumar").strip().replace("-", "")
    
    st.markdown("---")
    all_trainers = get_all_trainers()
    
    if not all_trainers:
        st.warning("इस समय कोई कोच उपलब्ध नहीं है। कृपया पहले ट्रेनर मोड में जाकर एक प्रोफाइल बनाएं।")
    else:
        for t in all_trainers:
            t_id, t_name, t_spec, t_price, t_bio = t
            
            # प्रीमियम ग्लासमोर्फिज्म कार्ड डिजाइन
            st.markdown(f"""
                <div class="lux-card">
                    <span class="price-tag">{t_price}</span>
                    <span class="trainer-id-badge">🌟 ELITE COACH &bull; {t_id}</span>
                    <h3 style="margin: 5px 0; font-size: 24px; color: #ffffff; font-weight: 600;">{t_name}</h3>
                    <p style="margin: 5px 0 15px 0; font-size: 14px; color: #10b981; font-weight:400;">🎯 <b>स्पेशलिटी:</b> {t_spec}</p>
                    <p style="margin: 0; font-size: 14px; color: #b3c3d9; line-height:1.6; font-style: italic;">"{t_bio}"</p>
                </div>
            """, unsafe_allow_html=True)
            
            # चैट बटन
            if st.button(f"🤝 Connect & Chat with {t_name.split()[0]}", key=f"chat_{t_id}"):
                st.session_state["active_chat_with"] = t_id
            st.markdown("<br><br>", unsafe_allow_html=True)

    # लग्जरी लाइव चैट विंडो
    if "active_chat_with" in st.session_state:
        target_id = st.session_state["active_chat_with"]
        t_name = next((t[1] for t in all_trainers if t[0] == target_id), "")
                
        chat_id = f"{c_name}-{target_id}"
        st.markdown('<div class="lux-chat-container">', unsafe_allow_html=True)
        st.markdown(f"<h3 style='margin-top:0; color:#ff4b5c;'>💬 Conversation with {t_name}</h3>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
        
        current_msgs = get_chat_messages(chat_id)
        for msg in current_msgs:
            color = "#10b981" if msg[0] == "Client" else "#ff4b5c"
            label = "You (VIP Client)" if msg[0] == "Client" else f"Coach ({t_name})"
            st.markdown(f"<p style='margin:8px 0; font-size:15px;'><b style='color:{color};'>{label}:</b> {msg[1]}</p>", unsafe_allow_html=True)
            
        client_msg = st.text_input("अपनी फिटनेस रिक्वायरमेंट या सवाल यहाँ लिखें...", key="client_msg_input")
        if st.button("🚀 सेंड मैसेज"):
            if client_msg:
                save_message(chat_id, "Client", client_msg)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
