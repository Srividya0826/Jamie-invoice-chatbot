import streamlit as st
import pandas as pd
import re
import time

st.set_page_config(page_title="Jamie 🤖 Invoice Assistant", page_icon="📄", layout="wide")

# Custom styling for background animation, chat bubbles, mobile responsiveness, and typing dots
st.markdown("""
<style>
    /* Background animated gradient */
    body, .main {
        background: linear-gradient(270deg, #f8f9fa, #e3f2fd, #d1c4e9, #f8f9fa);
        background-size: 800% 800%;
        animation: GradientShift 20s ease infinite;
        margin: 0 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    @keyframes GradientShift {
        0% {background-position:0% 50%;}
        50% {background-position:100% 50%;}
        100% {background-position:0% 50%;}
    }

    /* Chat bubble styling */
    .chat-user, .chat-bot {
        max-width: 85%;
        margin: 5px 0;
        padding: 12px 20px;
        border-radius: 25px;
        font-size: 1rem;
        line-height: 1.4;
        word-wrap: break-word;
        clear: both;
    }
    .chat-user {
        background-color: #1976d2;
        color: white;
        align-self: flex-end;
        border-bottom-right-radius: 5px;
        float: right;
    }
    .chat-bot {
        background-color: #e3f2fd;
        color: #0d47a1;
        align-self: flex-start;
        border-bottom-left-radius: 5px;
        float: left;
    }

    /* Container for chat messages flexbox */
    .chat-container {
        display: flex;
        flex-direction: column;
        padding: 10px 15px;
        height: 70vh;
        overflow-y: auto;
        scroll-behavior: smooth;
        border: 1px solid #bbb;
        border-radius: 10px;
        background-color: rgba(255,255,255,0.8);
    }

    /* Typing bubble animation with pulsing dots */
    .typing-bubble {
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 12px 20px;
        border-radius: 25px;
        max-width: 40%;
        font-style: italic;
        position: relative;
        border-bottom-left-radius: 5px;
        align-self: flex-start;
        float: left;
    }
    .typing-dots span {
        display: inline-block;
        width: 8px;
        height: 8px;
        margin: 0 2px;
        background-color: #0d47a1;
        border-radius: 50%;
        animation: blink 1.4s infinite ease-in-out both;
    }
    .typing-dots span:nth-child(1) {
        animation-delay: 0s;
    }
    .typing-dots span:nth-child(2) {
        animation-delay: 0.2s;
    }
    .typing-dots span:nth-child(3) {
        animation-delay: 0.4s;
    }
    @keyframes blink {
        0%, 80%, 100% {
            opacity: 0;
        }
        40% {
            opacity: 1;
        }
    }

    /* Responsive adjustments */
    @media (max-width: 600px) {
        .chat-container {
            height: 60vh;
            padding: 8px 10px;
        }
        .chat-user, .chat-bot, .typing-bubble {
            max-width: 95%;
            font-size: 0.9rem;
            padding: 10px 15px;
        }
        .stTextInput>div>div>input {
            font-size: 1.1rem !important;
            padding: 12px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Page title
st.title("Jamie 🤖 Invoice Assistant")

# Help sidebar
st.sidebar.markdown("""
## ℹ️ How to Use Jamie
- Type your name or say 'hi' to start
- Ask for an invoice status using an ID (e.g., INV001)
- Try 'list invoices' to view a few sample invoices
- Type 'help' if you're stuck!
""")

# Load invoice data
@st.cache_data
def load_invoices(file_path):
    try:
        df = pd.read_excel(file_path)
        df = df.dropna(subset=["Invoice_ID"])
        df["Invoice_ID"] = df["Invoice_ID"].astype(str).str.upper()
        return df
    except FileNotFoundError:
        st.error(f"Invoice file not found at: {file_path}")
        return pd.DataFrame()

invoice_df = load_invoices("/Users/srividyamanikonda/Desktop/ERP_Chatbot_Project/invoice_status.xlsx")

def extract_name(text):
    # Replace this with your actual extract_name function code
    text = text.lower()
    patterns = [
        r"\bmy name is ([a-zA-Z ]+)\b",
        r"\bi am ([a-zA-Z ]+)\b",
        r"\bi'm ([a-zA-Z ]+)\b",
        r"\bthis is ([a-zA-Z ]+)\b",
        r"\biam ([a-zA-Z ]+)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip().title()
    return None

def get_bot_response(user_text):
    # Replace this with your actual get_bot_response function code
    user_text_strip = user_text.strip()
    if not user_text_strip:
        return "Please type something so I can help you."

    name = extract_name(user_text_strip)
    if name:
        st.session_state.user_name = name
        return f"Nice to meet you, {name}! 👋 How can I assist you today?"

    name = st.session_state.get("user_name", None)
    user_text_upper = user_text_strip.upper()
    user_text_lower = user_text_strip.lower()

    if user_text_lower in ["help", "?"]:
        return ("I can help you check invoice statuses! 🧾\n\n"
                "- Type an invoice ID like `INV001` to see its status\n"
                "- Say 'list invoices' to preview some invoices\n"
                "- Or just say hi, thank you, or goodbye\n"
                "- I’m always learning, so try different phrases!")

    if user_text_lower in ["list invoices", "show invoices", "display invoices"]:
        if invoice_df.empty:
            return "Oops! The invoice list is currently unavailable. Please try again later."
        preview = invoice_df[["Invoice_ID", "Vendor_Name", "Amount"]].head(5)
        preview_table = preview.to_markdown(index=False)
        return f"Here are a few invoices:\n\n{preview_table}\n\nLet me know if you want to check a specific invoice ID!"

    if re.match(r"^INV\d+$", user_text_upper):
        invoice_row = invoice_df[invoice_df["Invoice_ID"] == user_text_upper]
        if not invoice_row.empty:
            data = invoice_row.iloc[0]
            return (f"Here's the status for invoice **{data['Invoice_ID']}** from vendor **{data['Vendor_Name']}**:\n"
                    f"- Amount: {data['Amount']}\n- Invoice Date: {data['Invoice_Date'].strftime('%Y-%m-%d')}\n"
                    f"- Due Date: {data['Due_Date'].strftime('%Y-%m-%d')}\n- Status: {data['Payment_Status']}\n\n"
                    "Let me know if you want to check another invoice!")
        else:
            return "I couldn't find that invoice. Please double-check the ID and try again."

    if user_text_lower in ["hi", "hello", "hey"]:
        return f"Hello{', ' + name if name else ''}! 👋 I'm Jamie, your friendly invoice assistant. How can I help you today?"

    if user_text_lower in ["thanks", "thank you", "thank u", "thx"]:
        return f"You're very welcome{', ' + name if name else ''}! 😊 Is there anything else I can help you with?"

    if user_text_lower in ["no", "nothing", "exit", "bye", "goodbye"]:
        return "Alright! 👋 Have a great day. If you need anything else, just type here."

    if user_text_lower in ["yes", "yeah", "yep", "sure", "ok", "okay"]:
        return "Great! Please provide the invoice ID you'd like to check."

    if user_text_lower in ["no", "nope", "nah"]:
        return "Okay, let me know if you need help with anything else!"

    return ("Hmm, I’m not sure about that yet 🤔. Could you try rephrasing or provide a valid invoice ID?\n\n"
            "_Tip: Invoice IDs look like INV001, INV002, etc._")

def process_user_input():
    user_input = st.session_state.user_input
    if user_input:
        placeholder = st.empty()
        with placeholder.container():
            st.markdown("""
                <div class="typing-bubble">
                    Jamie is typing
                    <span class="typing-dots">
                        <span></span><span></span><span></span>
                    </span>
                </div>
                """, unsafe_allow_html=True)
        time.sleep(1.5)
        response = get_bot_response(user_input)
        placeholder.empty()
        st.session_state.messages.append({"user": user_input, "bot": response})
        st.session_state.user_input = ""

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"user": None, "bot": "👋 Welcome! I’m Jamie, your invoice assistant. Ask me about invoice statuses or try 'list invoices'."}
    ]
if "user_name" not in st.session_state:
    st.session_state.user_name = None

# Input box
st.text_input(
    "Ask Jamie anything about invoices or say hi!",
    key="user_input",
    on_change=process_user_input,
    placeholder="Type here and press Enter"
)

# Reset button
if st.button("🔄 Reset Chat"):
    st.session_state.messages = []

# Chat display container
chat_html = '<div class="chat-container">'
for msg in st.session_state.messages[::-1]:
    if msg["user"] is not None:
        chat_html += f'<div class="chat-user">{msg["user"]}</div>'
    chat_html += f'<div class="chat-bot">{msg["bot"]}</div>'
chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)
