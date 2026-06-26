import streamlit as st
import sqlite3
import uuid
import urllib.parse

# ऐप का सेटअप
st.set_page_config(page_title="FitMatch Pro - Permanent Database", layout="wide")

# ==================== DATABASE SETUP ====================
def init_db():
    conn = sqlite3.connect("fitmatch.db")
    cursor = conn.cursor()
    # ट्रेनर्स की टेबल
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trainers (
            id TEXT PRIMARY KEY,
            name TEXT,
            specialty TEXT,
            price TEXT,
            bio TEXT
        )
    """)
    # चैट की टेबल
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            sender TEXT,
            message TEXT
        )
    """)
    conn.commit()
    conn.close()

# डेटाबेस शुरू करना
init_db()

# डेटाबेस फंक्शन्स
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

# ==================== UI SETUP ====================
st.title("🏋️‍♂️ FitMatch Pro: Connect with Personal Trainers")
st.write("डेटाबेस के साथ सुरक्षित ऐप - यहाँ आपका डेटा कभी डिलीट नहीं होगा।")

# रोल सिलेक्शन
st.sidebar.header("🚪 ऐप में प्रवेश करें")
user_role = st.sidebar.radio("आप कौन हैं? (Select Role)", ["🙋‍♂️ क्लाइंट (Client / User)", "💪 ट्रेनर (Fitness Trainer)"])
st.sidebar.markdown("---")

# ==================== TRAINER SIDE ====================
if user_role == "💪 ट्रेनर (Fitness Trainer)":
    st.header("🛠️ Trainer Registration & Dashboard")
    
    with st.expander("📝 नया ट्रेनर अकाउंट बनाएं", expanded=False):
        t_name = st.text_input("आपका पूरा नाम (Full Name)")
        t_spec = st.selectbox("आपकी स्पेशलिटी", ["Weight Loss", "Muscle Gain", "Yoga & Flexibility", "Powerlifting"])
        t_price = st.text_input("अपनी मंथली फीस (e.g., ₹5000/month)")
        t_bio = st.text_area("अपने बारे में कुछ बताएं (Short Bio)")
        
        if st.button("रजिस्टर करें"):
            if t_name and t_price:
                new_id = f"TRN-{uuid.uuid4().hex[:4].upper()}"
                add_trainer(new_id, t_name, t_spec, t_price, t_bio)
                st.success(f"🎉 आप रजिस्टर हो चुके हैं! आपकी परमानेंट आईडी है: **{new_id}**")
                st.rerun()
            else:
                st.error("कृपया नाम और फीस जरूर भरें।")

    st.markdown("---")
    st.subheader("📥 आपके क्लाइंट्स के मैसेजेस")
    
    all_trainers = get_all_trainers()
    if all_trainers:
        trainer_options = {t[0]: t[1] for t in all_trainers}
        active_trainer_id = st.selectbox("अपनी Trainer ID चुनें", list(trainer_options.keys()))
        st.info(f"लॉगिन: {trainer_options[active_trainer_id]} ({active_trainer_id})")
        
        trainer_chats = get_trainer_chats(active_trainer_id)
        if trainer_chats:
            for chat_key in trainer_chats:
                client_name = chat_key.split("-")[0]
                st.markdown(f"**💬 Client [{client_name}] के साथ बातचीत:**")
                
                # मैसेज दिखाना
                msgs = get_chat_messages(chat_key)
                for msg in msgs:
                    st.write(f"**{msg[0]}:** {msg[1]}")
                    
                # रिप्लाई बॉक्स
                reply_text = st.text_input("जवाब लिखें...", key=f"reply_{chat_key}")
                if st.button("भेजें (Send)", key=f"btn_{chat_key}"):
                    if reply_text:
                        save_message(chat_key, "Trainer", reply_text)
                        st.rerun()
        else:
            st.write("अभी तक किसी क्लाइंट ने आपसे चैट शुरू नहीं की है।")
    else:
        st.warning("डेटाबेस में अभी कोई ट्रेनर नहीं है।")

# ==================== CLIENT SIDE ====================
else:
    st.header("🔍 उपलब्ध पर्सनल ट्रेनर्स की लिस्ट")
    c_name = st.text_input("आपका नाम (Client Name)", "Rahul").strip().replace("-", "")
    
    st.markdown("---")
    all_trainers = get_all_trainers()
    
    if not all_trainers:
        st.warning("अभी कोई ट्रेनर उपलब्ध नहीं है।")
    else:
        for t in all_trainers:
            t_id, t_name, t_spec, t_price, t_bio = t
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {t_name} *(ID: {t_id})*")
                    st.markdown(f"🎯 **स्पेशलिटी:** {t_spec} | 💰 **फीस:** `{t_price}`")
                    st.write(f"📝 {t_bio}")
                with col2:
                    st.write("")
                    if st.button(f"💬 Chat with {t_name.split()[0]}", key=f"chat_{t_id}"):
                        st.session_state["active_chat_with"] = t_id
                st.markdown("<hr style='border:1px dashed #eee'>", unsafe_allow_html=True)

    if "active_chat_with" in st.session_state:
        target_id = st.session_state["active_chat_with"]
        
        # ट्रेनर का नाम ढूंढना
        t_name = ""
        for t in all_trainers:
            if t[0] == target_id:
                t_name = t[1]
                
        chat_id = f"{c_name}-{target_id}"
        st.markdown("---")
        st.header(f"💬 {t_name} के साथ लाइव चैट")
        
        # मैसेजेस लोड करना
        current_msgs = get_chat_messages(chat_id)
        for msg in current_msgs:
            sender_label = "Client" if msg[0] == "Client" else f"Trainer ({t_name})"
            st.write(f"**{sender_label}:** {msg[1]}")
            
        # मैसेज इनपुट
        client_msg = st.text_input("अपनी रिक्वायरमेंट यहाँ लिखें...", key="client_msg_input")
        if st.button("मैसेज भेजें"):
            if client_msg:
                save_message(chat_id, "Client", client_msg)
                st.rerun()
