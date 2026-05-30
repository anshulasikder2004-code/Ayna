import re
import streamlit as st
import random
import os
import json
import base64
import google.generativeai as genai

st.set_page_config(
    page_title="Ayna — মনের আয়না",
    page_icon="🪞",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════════
# LANGUAGE STRINGS
# ══════════════════════════════════════════════════════════════════
LANG = {
    "bn": {
        "start": "শুরু করো  →",
        "tagline": "A quiet space to sit with yourself<br>and gently notice what's within.",
        "stage1_pill": "Stage 1 of 4 · Visual Snap",
        "stage1_title": "👁️ একটু দেখো",
        "stage1_sub": "ছবিটা দেখো। যে line টা তোমার সাথে সবচেয়ে বেশি মিলে যায় সেটা বেছে নাও।",
        "stage1_q": "যে caption টা তোমার সবচেয়ে কাছের মনে হয় সেটা বেছে নাও",
        "stage1_done": "✓ তোমার choice নেওয়া হয়েছে।",
        "next": "পরের Stage →",
        "stage2_pill": "Stage 2 of 4 · Forced Choice",
        "stage2_title": "🃏 দুটো option",
        "stage2_sub": "কোনো সঠিক-ভুল নেই। যেটা বেশি তোমার মতো মনে হয় সেটা বেছে নাও।",
        "stage2_done": "✓ Forced Choice শেষ।",
        "stage3_pill": "Stage 3 of 4 · দৈনন্দিন মুহূর্ত",
        "stage3_title": "💬 কয়েকটা প্রশ্ন",
        "stage3_sub": "মনে যা আসে সেটাই বেছে নাও — কোনো সঠিক উত্তর নেই।",
        "stage3_done": "✓ এই stage শেষ।",
        "stage4_pill": "Stage 4 of 4 · Micro Journal",
        "stage4_title": "📝 মনের কথা",
        "stage4_sub": "আজকের দিনটা নিয়ে যা মনে আসে লেখো — ৩ থেকে ৫ লাইন। কোনো নিয়ম নেই, কেউ পড়বে না।",
        "stage4_placeholder": "আজকে...",
        "stage4_skip": "লিখতে না চাইলে এড়িয়ে যেতে পারো।",
        "stage4_voice": "🎤 কথা বলে লেখো",
        "stage4_voice_sub": "Microphone দিয়ে বলো — সে লিখে নেবে",
        "see_report": "Ayna Report দেখো →",
        "report_title": "🪞 তোমার Ayna Report",
        "report_sub": "এটা একটা pattern — রোগ নির্ণয় নয়",
        "report_found": "এই session এ যে patterns দেখা গেছে:",
        "report_none": "✨ তোমার এই session এ কোনো উল্লেখযোগ্য pattern দেখা যায়নি।\nতুমি ভালো আছ — এটা সুন্দর খবর।",
        "might_have": "তোমার এটি থাকতে পারে — এটা একটা সম্ভাবনা।",
        "today_step": "✦ আজকের জন্য একটা ছোট পদক্ষেপ",
        "helpline": "💚 কথা বলতে চাইলে কেউ আছে —\nKaan Pete Roi: 01779-554391\nবিনামূল্যে, গোপনীয়",
        "disclaimer": "* এই report টি clinical diagnosis নয়।\n\"might have\" মানে এই pattern গুলো তোমার মধ্যে থাকতে পারে —\nনিশ্চিত নয়। শুধু একটু নিজেকে দেখার আয়না।",
        "restart": "আবার শুরু করো",
        "share": "📤 এই report শেয়ার করো",
        "share_note": "একটা private link তৈরি হবে — শুধু তুমি যাকে দেবে সে দেখতে পাবে।",
        "low": "সামান্য লক্ষণ",
        "medium": "মাঝারি মাত্রায়",
        "high": "বেশি মাত্রায়",
        "card_of": "Card",
        "of": "/",
        "q_of": "প্রশ্ন",
        "words": "words",
        "all_done": "✓ সব card শেষ",
    },
    "en": {
        "start": "Begin  →",
        "tagline": "A quiet space to sit with yourself<br>and gently notice what's within.",
        "stage1_pill": "Stage 1 of 4 · Visual Snap",
        "stage1_title": "👁️ Take a look",
        "stage1_sub": "Look at the image. Choose the caption that resonates with you the most.",
        "stage1_q": "Choose the caption that feels closest to you",
        "stage1_done": "✓ Your choice has been recorded.",
        "next": "Next Stage →",
        "stage2_pill": "Stage 2 of 4 · Forced Choice",
        "stage2_title": "🃏 Two options",
        "stage2_sub": "There's no right or wrong. Choose whichever feels more like you.",
        "stage2_done": "✓ Forced Choice complete.",
        "stage3_pill": "Stage 3 of 4 · Daily Moments",
        "stage3_title": "💬 A few questions",
        "stage3_sub": "Go with what comes to mind — there are no correct answers.",
        "stage3_done": "✓ This stage is complete.",
        "stage4_pill": "Stage 4 of 4 · Micro Journal",
        "stage4_title": "📝 Your thoughts",
        "stage4_sub": "Write what comes to mind about today — 3 to 5 lines. No rules, no one will read it.",
        "stage4_placeholder": "Today...",
        "stage4_skip": "You can skip this if you don't want to write.",
        "stage4_voice": "🎤 Speak to write",
        "stage4_voice_sub": "Speak into your microphone — it will write for you",
        "see_report": "See Ayna Report →",
        "report_title": "🪞 Your Ayna Report",
        "report_sub": "This is a pattern — not a diagnosis",
        "report_found": "Patterns detected in this session:",
        "report_none": "✨ No significant patterns were detected in this session.\nYou seem to be doing well — that's wonderful.",
        "might_have": "You might have this — it's a possibility.",
        "today_step": "✦ One small step for today",
        "helpline": "💚 Someone is here if you want to talk —\nKaan Pete Roi: 01779-554391\nFree & confidential",
        "disclaimer": "* This report is not a clinical diagnosis.\n\"Might have\" means these patterns may exist in you —\nnot certain. Just a mirror to gently see yourself.",
        "restart": "Start again",
        "share": "📤 Share this report",
        "share_note": "A private link will be created — only those you share it with can see it.",
        "low": "Mild signal",
        "medium": "Moderate",
        "high": "Strong signal",
        "card_of": "Card",
        "of": "/",
        "q_of": "Question",
        "words": "words",
        "all_done": "✓ All cards complete",
    }
}

def T(key):
    lang = st.session_state.get("lang", "bn")
    return LANG[lang].get(key, key)

# ══════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,400&family=Hind+Siliguri:wght@300;400;500;600&display=swap');

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; max-width: 520px !important; }

:root {
    --cream: #FAF6F0;
    --green: #2C5F4A;
    --green2: #3D7A61;
    --gold:  #B8956A;
    --text:  #1C1C1E;
    --muted: #6B6B6B;
    --border:#D4C9B8;
}

html, body, .stApp, [class*="css"] {
    background: var(--cream) !important;
    font-family: 'Hind Siliguri', sans-serif;
    color: var(--text);
}

div[data-testid="stButton"] > button {
    width: 100% !important;
    background: #FFFFFF !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    color: #3D3530 !important;
    font-family: 'Hind Siliguri', sans-serif !important;
    font-size: 15px !important;
    padding: 14px 16px !important;
    text-align: left !important;
    line-height: 1.6 !important;
    margin-bottom: 6px !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stButton"] > button:hover {
    background: #EDE6DC !important;
    border-color: var(--green) !important;
    color: var(--green) !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #2C5F4A 0%, #3D7A61 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 50px !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    box-shadow: 0 8px 24px rgba(44,95,74,0.28) !important;
    text-align: center !important;
    padding: 14px 40px !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 14px 32px rgba(44,95,74,0.35) !important;
    color: #fff !important;
}

.pill {
    display: inline-block;
    background: #E8E0D5;
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 4px 16px;
    font-size: 11px;
    color: #7A6E62;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.sec-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 26px;
    font-weight: 400;
    color: var(--green);
    margin-bottom: 4px;
}
.sec-sub {
    font-size: 13px;
    color: var(--muted);
    margin-bottom: 24px;
    line-height: 1.6;
}

.div-row {
    display:flex; align-items:center; gap:10px;
    justify-content:center; margin-bottom:1.8rem;
}
.div-line  { width:55px;height:1px;background:linear-gradient(90deg,transparent,var(--gold)); }
.div-line.r{ background:linear-gradient(90deg,var(--gold),transparent); }
.div-dot   { width:4px;height:4px;border-radius:50%;background:var(--gold);opacity:.7; }

.info-box {
    background: #E8F0EB;
    border: 1px solid var(--green);
    border-radius: 12px;
    padding: 14px 18px;
    color: var(--green);
    font-size: 14px;
    margin: 14px 0;
    line-height: 1.6;
}

.q-text {
    font-size: 16px;
    font-weight: 600;
    color: var(--green);
    text-align: center;
    margin: 16px 0 18px;
    line-height: 1.6;
}

.lang-toggle {
    position: fixed;
    top: 14px;
    right: 18px;
    z-index: 9999;
    display: flex;
    gap: 6px;
}
.lang-btn {
    background: #FFFFFF;
    border: 1.5px solid var(--border);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    color: #3D3530;
    cursor: pointer;
    font-family: 'Hind Siliguri', sans-serif;
    transition: all 0.2s;
}
.lang-btn.active {
    background: var(--green);
    color: #fff;
    border-color: var(--green);
}

.voice-box {
    background: #F0F7F4;
    border: 1px dashed var(--green);
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
    text-align: center;
}
.voice-box p {
    font-size: 12px;
    color: var(--muted);
    margin: 6px 0 0;
}

.share-box {
    background: #FDF8F3;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px 18px;
    margin: 16px 0;
    font-size: 13px;
    color: var(--muted);
    line-height: 1.6;
}
.share-link {
    background: #E8F0EB;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12px;
    color: var(--green);
    word-break: break-all;
    margin-top: 8px;
    font-family: monospace;
}

@keyframes fadeUp {
    from{opacity:0;transform:translateY(24px)}
    to  {opacity:1;transform:translateY(0)}
}
@keyframes pulse {
    0%,100%{transform:translate(-50%,-50%) scale(1);opacity:.5}
    50%    {transform:translate(-50%,-50%) scale(1.3);opacity:1}
}
.mirror-container{
    position:relative;width:110px;height:110px;margin:0 auto 1.8rem;
}
.mirror-glow{
    position:absolute;top:50%;left:50%;
    width:130px;height:130px;border-radius:50%;
    background:radial-gradient(circle,rgba(184,149,106,.15) 0%,transparent 70%);
    animation:pulse 3s ease-in-out infinite;
}
.mirror-circle{
    width:110px;height:110px;border-radius:50%;
    background:linear-gradient(135deg,#F5EDE0,#E8DDD0);
    border:1.5px solid rgba(184,149,106,.3);
    display:flex;align-items:center;justify-content:center;
    font-size:48px;
    box-shadow:0 8px 32px rgba(44,95,74,.12),inset 0 1px 0 rgba(255,255,255,.6);
    position:relative;z-index:1;
}
.ayna-title{
    font-family:'Cormorant Garamond',serif;
    font-size:clamp(56px,9vw,78px);
    font-weight:300;color:var(--green);
    letter-spacing:.1em;line-height:1;
    margin-bottom:1.6rem;
    animation:fadeUp .7s ease both;
}
.tagline-en{
    font-size:13px;color:var(--muted);
    font-weight:300;letter-spacing:.03em;
    margin-bottom:1.6rem;
    animation:fadeUp 1.2s ease both;
}
.home-page{
    min-height:90vh;display:flex;flex-direction:column;
    align-items:center;justify-content:center;
    padding:3rem 1.5rem;text-align:center;
}

/* Result styles */
.report-header { text-align:center; padding:1.5rem 0 0.5rem; }
.report-name { font-family:'Cormorant Garamond',serif; font-size:2rem; color:#2C5F4A; font-weight:400; }
.report-sub { font-size:0.85rem; color:#6B6B6B; margin-top:0.3rem; }
.condition-card { background:#FFFFFF; border:1px solid #E8E0D5; border-radius:16px; padding:1.2rem 1.5rem; margin:0.8rem 0; border-left:4px solid #2C5F4A; }
.condition-card.medium { border-left-color:#B8956A; }
.condition-card.high   { border-left-color:#C0392B; }
.cond-top { display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem; }
.cond-name { font-weight:600; font-size:1rem; color:#1C1C1E; }
.cond-badge { font-size:0.72rem; padding:2px 10px; border-radius:20px; font-weight:500; background:#E8F0EB; color:#2C5F4A; }
.cond-badge.medium { background:#FDF3E7; color:#B8956A; }
.cond-badge.high   { background:#FDECEA; color:#C0392B; }
.meter-track { background:#F0EBE3; border-radius:10px; height:8px; margin:0.5rem 0; overflow:hidden; }
.meter-fill { height:100%; border-radius:10px; }
.might-have { font-size:0.82rem; color:#6B6B6B; font-style:italic; margin:0.3rem 0; }
.positive-box { background:#F0F7F4; border-radius:10px; padding:0.7rem 1rem; margin-top:0.6rem; font-size:0.85rem; color:#2C5F4A; line-height:1.6; }
.suggestion-box { background:#FDF8F3; border:1px solid #E8E0D5; border-radius:16px; padding:1.2rem 1.5rem; margin:1.5rem 0; }
.suggestion-title { font-family:'Cormorant Garamond',serif; font-size:1.2rem; color:#2C5F4A; margin-bottom:0.5rem; }
.suggestion-text { font-size:0.9rem; color:#3D3530; line-height:1.8; }
.disclaimer { font-size:0.72rem; color:#9B9B9B; text-align:center; margin-top:1.5rem; line-height:1.7; font-style:italic; }
.helpline-box { background:#E8F0EB; border-radius:12px; padding:1rem 1.2rem; text-align:center; margin:1rem 0; font-size:0.85rem; color:#2C5F4A; line-height:1.8; }
</style>
""", unsafe_allow_html=True)

# Voice input JS component
VOICE_JS = """
<div class="voice-box">
    <button onclick="startVoice()" style="background:linear-gradient(135deg,#2C5F4A,#3D7A61);color:#fff;border:none;border-radius:50px;padding:10px 28px;font-size:14px;cursor:pointer;">
        🎤 Start Speaking
    </button>
    <p id="voice-status">Click to start</p>
</div>
<script>
function startVoice() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        document.getElementById('voice-status').innerText = 'Sorry, your browser does not support voice input. Try Chrome.';
        return;
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SR();
    recognition.lang = 'bn-BD';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    document.getElementById('voice-status').innerText = '🔴 Listening...';
    recognition.start();
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('voice-status').innerText = '✓ Got it: ' + transcript;
        // Send to Streamlit via query param hack
        const url = new URL(window.location);
        url.searchParams.set('voice_input', transcript);
        window.history.replaceState({}, '', url);
        window.location.reload();
    };
    recognition.onerror = function(event) {
        document.getElementById('voice-status').innerText = 'Error: ' + event.error;
    };
}
</script>
"""

# ══════════════════════════════════════════════════════════════════
# CONDITIONS
# ══════════════════════════════════════════════════════════════════
CONDITIONS = [
    "anxiety","burnout","emotional_exhaustion","loneliness",
    "chronic_stress","emotional_suppression","low_self_worth",
    "caregiver_fatigue","social_withdrawal","emotional_numbness",
    "depression","identity_loss","hypervigilance","perfectionism_anxiety",
    "imposter_syndrome","emotional_dependency","grief",
    "rage_suppression","decision_fatigue","dissociation"
]

CONDITION_LABELS = {
    "anxiety":"Anxiety","burnout":"Burnout",
    "emotional_exhaustion":"Emotional Exhaustion","loneliness":"Loneliness",
    "chronic_stress":"Chronic Stress","emotional_suppression":"Emotional Suppression",
    "low_self_worth":"Low Self-Worth","caregiver_fatigue":"Caregiver Fatigue",
    "social_withdrawal":"Social Withdrawal","emotional_numbness":"Emotional Numbness",
    "depression":"Depression","identity_loss":"Identity Loss",
    "hypervigilance":"Hypervigilance","perfectionism_anxiety":"Perfectionism Anxiety",
    "imposter_syndrome":"Imposter Syndrome","emotional_dependency":"Emotional Dependency",
    "grief":"Grief / Unprocessed Loss","rage_suppression":"Rage Suppression",
    "decision_fatigue":"Decision Fatigue","dissociation":"Dissociation"
}

# ══════════════════════════════════════════════════════════════════
# PICTURES
# ══════════════════════════════════════════════════════════════════
PICTURES = [
    {
        "file": "scene_03_rooftop.jpeg",
        "captions": [
            {"text": "শহরটা এত বড়, তবু মনে হয় সব চেনা", "scores": {"chronic_stress": 0.5, "burnout": 0.5}},
            {"text": "এই সময়টা দিনের সবচেয়ে নিজের", "scores": {"social_withdrawal": 1.0, "caregiver_fatigue": 0.5}},
            {"text": "উঁচু থেকে দেখলে সব কেমন ছোট লাগে", "scores": {"dissociation": 1.5, "identity_loss": 0.5}},
            {"text": "আলোগুলো একটু একটু করে জ্বলে উঠছে", "scores": {"grief": 0.5, "depression": 0.5}},
            {"text": "এখানে দাঁড়িয়ে থাকলে সময় থামে মনে হয়", "scores": {"emotional_exhaustion": 1.0, "burnout": 0.5}},
            {"text": "নিচে কত কিছু চলছে, আমি শুধু দেখছি", "scores": {"loneliness": 1.0, "dissociation": 1.0, "social_withdrawal": 0.5}},
            {"text": "বাতাসটা একটু ঠান্ডা আজকে", "scores": {"emotional_numbness": 0.5, "depression": 0.5}},
            {"text": "এই মুহূর্তে কেউ জানে না আমি কোথায়", "scores": {"social_withdrawal": 1.5, "identity_loss": 1.0}},
            {"text": "রোজ এই আকাশটা একটু বদলায়", "scores": {"grief": 0.5, "emotional_suppression": 0.5}},
            {"text": "এত আলো একসাথে দেখলে অন্যরকম লাগে", "scores": {"dissociation": 1.0, "emotional_numbness": 1.0}},
            {"text": "এখান থেকে পুরো শহরটা একটা ছবির মতো", "scores": {"dissociation": 1.5, "social_withdrawal": 0.5}},
            {"text": "সন্ধ্যাটা কোথা থেকে আসে, কোথায় যায়", "scores": {"grief": 1.0, "identity_loss": 0.5, "depression": 0.5}},
        ]
    },
    {
        "file": "scene_01_balcony.jpeg",
        "captions": [
            {"text": "চায়ের কাপটা হাতে থাকলে সব ঠিক মনে হয়", "scores": {"anxiety": 1.0, "hypervigilance": 0.5}},
            {"text": "পাখিগুলো প্রতিদিন এই সময়ে আসে", "scores": {"grief": 0.5, "emotional_numbness": 0.5}},
            {"text": "গাছগুলো নিজে নিজে বেড়ে যায়", "scores": {"low_self_worth": 1.0, "imposter_syndrome": 0.5}},
            {"text": "এই বারান্দাটা পুরো বাসার সেরা জায়গা", "scores": {"social_withdrawal": 1.5, "anxiety": 0.5}},
            {"text": "বাচ্চাগুলো খেলছে, ওরা জানে না কত ভালো আছে", "scores": {"grief": 1.5, "depression": 0.5, "emotional_exhaustion": 0.5}},
            {"text": "একটু থামলেই দেখা যায় কত কিছু হচ্ছে", "scores": {"burnout": 1.5, "chronic_stress": 1.0}},
            {"text": "চা ঠান্ডা হওয়ার আগেই শেষ করতে হবে", "scores": {"anxiety": 1.0, "perfectionism_anxiety": 0.5}},
            {"text": "এই রঙটা প্রতিদিন একটু বদলায়", "scores": {"grief": 0.5, "depression": 0.5}},
            {"text": "এখানে বসলে ভাবতে ইচ্ছা করে", "scores": {"social_withdrawal": 1.0, "emotional_exhaustion": 0.5}},
            {"text": "আকাশটা আজকে অনেক বড় লাগছে", "scores": {"dissociation": 1.0, "identity_loss": 0.5}},
            {"text": "এই দৃশ্যটা কেউ না দেখলে মিস করত", "scores": {"loneliness": 1.5, "emotional_dependency": 1.0}},
            {"text": "মাটি থেকে উপরে থাকলে সব শান্ত", "scores": {"social_withdrawal": 1.0, "emotional_suppression": 0.5}},
        ]
    },
    {
        "file": "scene_06_couple.jpeg",
        "captions": [
            {"text": "একই জায়গায় দুটো আলাদা দুনিয়া", "scores": {"loneliness": 1.5, "emotional_suppression": 1.0}},
            {"text": "ফ্যানটা ঠিক একই গতিতে ঘুরছে", "scores": {"emotional_numbness": 1.5, "dissociation": 1.0}},
            {"text": "দেয়ালের ছবিগুলো পুরনো হয়ে গেছে", "scores": {"grief": 1.5, "identity_loss": 0.5}},
            {"text": "রাতের এই সময়টা সবার নিজের", "scores": {"social_withdrawal": 1.0, "emotional_suppression": 0.5}},
            {"text": "চায়ের কাপটা মাঝখানে পড়ে আছে", "scores": {"loneliness": 1.0, "emotional_exhaustion": 0.5}},
            {"text": "ঘরটা পরিচিত, তবু নতুন লাগে মাঝে মাঝে", "scores": {"dissociation": 1.5, "identity_loss": 1.0}},
            {"text": "দুজন একসাথে থাকলেই যথেষ্ট না?", "scores": {"emotional_suppression": 1.0, "loneliness": 1.0}},
            {"text": "ঘড়িটা ধীরে চলছে আজকে", "scores": {"depression": 1.0, "emotional_numbness": 0.5}},
            {"text": "এই ঘরে কত গল্প হয়েছে", "scores": {"grief": 1.0, "depression": 0.5}},
            {"text": "পর্দাটা একটু সরালে আলো আসে", "scores": {"emotional_suppression": 1.5, "rage_suppression": 0.5}},
            {"text": "নিজের ফোনে নিজের জগৎ", "scores": {"social_withdrawal": 1.5, "emotional_numbness": 1.0}},
            {"text": "সবকিছু ঠিকঠাক দেখায়", "scores": {"imposter_syndrome": 1.5, "emotional_suppression": 1.5}},
        ]
    },
    {
        "file": "scene_04_dining.jpeg",
        "captions": [
            {"text": "খাবার তৈরি, এখন শুধু সময়ের অপেক্ষা", "scores": {"caregiver_fatigue": 1.0, "anxiety": 0.5}},
            {"text": "ঘড়িটা একটু বেশি জোরে টিক করছে", "scores": {"anxiety": 1.5, "hypervigilance": 1.0}},
            {"text": "টেবিলটা সাজানো থাকলে ঘর পরিপাটি লাগে", "scores": {"caregiver_fatigue": 1.0, "identity_loss": 0.5}},
            {"text": "ধোঁয়া উঠছে মানে এখনো গরম আছে", "scores": {"anxiety": 1.0, "hypervigilance": 1.5}},
            {"text": "এই ঘরে অনেকের জায়গা আছে", "scores": {"identity_loss": 1.5, "caregiver_fatigue": 1.0}},
            {"text": "রান্নার গন্ধটা সারা বাসায় ছড়িয়ে যায়", "scores": {"caregiver_fatigue": 0.5, "emotional_exhaustion": 0.5}},
            {"text": "সব প্রস্তুত, বাকি শুধু মানুষ", "scores": {"emotional_dependency": 1.5, "loneliness": 1.0}},
            {"text": "এই চেয়ারগুলো প্রতিদিন একই জায়গায়", "scores": {"burnout": 1.0, "chronic_stress": 0.5}},
            {"text": "ভালো খাবার দেখলে মন ভালো হয়", "scores": {"emotional_exhaustion": 0.5, "caregiver_fatigue": 0.5}},
            {"text": "কতবার এই টেবিল সাজানো হয়েছে", "scores": {"caregiver_fatigue": 1.5, "rage_suppression": 1.0}},
            {"text": "আলোটা একটু হলুদ, ঘরোয়া লাগে", "scores": {"grief": 0.5, "depression": 0.5}},
            {"text": "সব কাজ শেষ, এখন একটু বসা যায়", "scores": {"burnout": 1.5, "emotional_exhaustion": 1.5}},
        ]
    },
    {
        "file": "scene_05_kitchen.jpeg",
        "captions": [
            {"text": "হাত দুটো নিজে নিজে কাজ করে", "scores": {"dissociation": 1.5, "burnout": 1.0}},
            {"text": "পানির শব্দটা ভালো লাগে", "scores": {"dissociation": 1.0, "emotional_numbness": 1.0}},
            {"text": "জানালা দিয়ে গাছটা দেখা যাচ্ছে", "scores": {"emotional_suppression": 1.0, "grief": 0.5}},
            {"text": "কাজ শেষ হলে পরের কাজ আসে", "scores": {"caregiver_fatigue": 1.5, "chronic_stress": 1.0, "burnout": 1.0}},
            {"text": "হাতের চুড়িটা একটু ভারী লাগছে", "scores": {"emotional_suppression": 1.5, "identity_loss": 1.0, "rage_suppression": 0.5}},
            {"text": "ফেনাটা বুদবুদ হয়ে মিলিয়ে যায়", "scores": {"grief": 1.0, "depression": 0.5}},
            {"text": "এই কাজটা করতে করতে অনেক ভাবা যায়", "scores": {"grief": 1.5, "identity_loss": 1.0}},
            {"text": "পানিটা একটু ঠান্ডা আজকে", "scores": {"emotional_numbness": 1.0, "depression": 0.5}},
            {"text": "কাজের মাঝে সময় কোথা দিয়ে যায়", "scores": {"burnout": 1.0, "dissociation": 1.0}},
            {"text": "গ্রিলের ফাঁক দিয়ে আলো আসে", "scores": {"identity_loss": 1.0, "emotional_suppression": 1.0}},
            {"text": "হাত পরিচ্ছন্ন থাকলে ভালো লাগে", "scores": {"perfectionism_anxiety": 1.0, "anxiety": 0.5}},
            {"text": "এই মুহূর্তটা শুধু হাতের কাজের", "scores": {"dissociation": 1.5, "emotional_numbness": 0.5}},
        ]
    },
    {
        "file": "scene_02_night_room.jpeg",
        "captions": [
            {"text": "বাইরের আলোগুলো রাতেও জেগে থাকে", "scores": {"anxiety": 1.0, "burnout": 0.5}},
            {"text": "বইয়ের পাতায় কত কিছু লেখা", "scores": {"perfectionism_anxiety": 0.5, "chronic_stress": 0.5}},
            {"text": "ল্যাম্পের আলোটা একটু হলুদ", "scores": {"loneliness": 1.0, "social_withdrawal": 0.5}},
            {"text": "রাতে পড়তে বসলে শহর চুপ থাকে", "scores": {"loneliness": 1.5, "burnout": 1.0}},
            {"text": "মশারিটা ঝুলিয়ে রাখলে ঘরটা আলাদা লাগে", "scores": {"social_withdrawal": 1.0, "emotional_suppression": 0.5}},
            {"text": "কলমটা একটু বেশি চাপে ধরা হচ্ছে", "scores": {"anxiety": 1.5, "perfectionism_anxiety": 1.0}},
            {"text": "এই টেবিলে কত রাত কেটেছে", "scores": {"burnout": 1.5, "chronic_stress": 1.0}},
            {"text": "চায়ের কাপটা পাশে থাকলে ভালো লাগে", "scores": {"anxiety": 1.0, "hypervigilance": 0.5}},
            {"text": "লেখাগুলো মিলিয়ে যাওয়ার আগেই ধরতে হয়", "scores": {"perfectionism_anxiety": 1.5, "anxiety": 1.0}},
            {"text": "জানালার ওপারে অন্য সব গল্প চলছে", "scores": {"loneliness": 1.0, "dissociation": 0.5}},
            {"text": "রাতটা এখানেই কাটবে", "scores": {"burnout": 1.0, "chronic_stress": 1.5}},
            {"text": "এই ঘরে শুধু আমি আর এই আলো", "scores": {"loneliness": 1.5, "social_withdrawal": 1.0}},
        ]
    },
    {
        "file": "scene_08_books.jpeg",
        "captions": [
            {"text": "বইগুলো সব একসাথে দেখলে মাথা গোলে", "scores": {"anxiety": 1.5, "decision_fatigue": 1.0}},
            {"text": "ক্যালকুলেটরটা সবসময় পাশে থাকে", "scores": {"anxiety": 1.0, "perfectionism_anxiety": 0.5}},
            {"text": "রাতের খাবারটা ঠান্ডা হয়ে গেছে", "scores": {"burnout": 1.5, "dissociation": 1.0}},
            {"text": "ঘড়িতে এই সময়টা একটু লম্বা লাগে", "scores": {"chronic_stress": 1.5, "burnout": 1.0}},
            {"text": "পাতাগুলো একটু বেশি ভরা", "scores": {"perfectionism_anxiety": 1.0, "decision_fatigue": 0.5}},
            {"text": "এত বিষয় একসাথে পড়তে হয়", "scores": {"chronic_stress": 1.5, "anxiety": 1.0, "decision_fatigue": 1.0}},
            {"text": "জানালার বাইরে রাত হয়ে গেছে", "scores": {"loneliness": 1.0, "burnout": 0.5}},
            {"text": "কলমটা হাতে নিলেই মাথা কাজ করে", "scores": {"perfectionism_anxiety": 1.0, "anxiety": 0.5}},
            {"text": "এই বইগুলোর ভেতরে অনেক উত্তর আছে", "scores": {"imposter_syndrome": 0.5, "anxiety": 0.5}},
            {"text": "টেবিলটা একটু গুছিয়ে নিতে হবে", "scores": {"perfectionism_anxiety": 1.5, "anxiety": 1.0}},
            {"text": "এই সময়ে বাইরে সব চুপ", "scores": {"loneliness": 1.5, "social_withdrawal": 1.0}},
            {"text": "সব মিলিয়ে কোথাও একটা পৌঁছাতে হবে", "scores": {"chronic_stress": 1.0, "imposter_syndrome": 1.0, "perfectionism_anxiety": 0.5}},
        ]
    },
    {
        "file": "scene_09_crossroad.jpeg",
        "captions": [
            {"text": "রাস্তাটা দুদিকে ভাগ হয়ে গেছে", "scores": {"decision_fatigue": 1.5, "identity_loss": 1.0}},
            {"text": "এত মানুষ একসাথে কোথায় যাচ্ছে", "scores": {"dissociation": 1.0, "loneliness": 1.0}},
            {"text": "রিকশার আলোগুলো একটু ঝাপসা", "scores": {"emotional_numbness": 1.0, "depression": 0.5}},
            {"text": "সন্ধ্যার পর শহরটা বদলে যায়", "scores": {"anxiety": 1.0, "hypervigilance": 0.5}},
            {"text": "এই রাস্তায় অনেকবার এসেছি", "scores": {"grief": 0.5, "burnout": 0.5}},
            {"text": "ডান না বাঁয়ে — দুটোই যায়", "scores": {"decision_fatigue": 1.5, "anxiety": 1.0}},
            {"text": "ভিড়ের মাঝে নিজের গতিতে হাঁটা যায়", "scores": {"social_withdrawal": 1.5, "dissociation": 1.0}},
            {"text": "আলো আর ছায়া মিলিয়ে একটা রঙ", "scores": {"emotional_numbness": 1.5, "dissociation": 1.0}},
            {"text": "এই সময়ে বাড়ি ফিরতে ইচ্ছা করে", "scores": {"social_withdrawal": 1.0, "anxiety": 0.5}},
            {"text": "শব্দটা একটু বেশি এই দিকে", "scores": {"hypervigilance": 1.5, "chronic_stress": 1.0}},
            {"text": "পথটা চেনা, তবু মাঝে মাঝে নতুন লাগে", "scores": {"dissociation": 1.5, "identity_loss": 1.0}},
            {"text": "সবাই যার যার দিকে চলে যাচ্ছে", "scores": {"loneliness": 1.5, "social_withdrawal": 1.0}},
        ]
    },
    {
        "file": "scene_10_window.jpeg",
        "captions": [
            {"text": "জানালার আলোটা সকালে অনেক নরম", "scores": {"depression": 0.5, "emotional_numbness": 0.5}},
            {"text": "বিছানায় বসে বাইরে তাকালে মন হালকা লাগে", "scores": {"social_withdrawal": 1.0, "depression": 0.5}},
            {"text": "আকাশে একটা বিমান যাচ্ছে", "scores": {"grief": 1.0, "identity_loss": 1.0}},
            {"text": "ঘরটা গোছানো থাকলে ভালো লাগে", "scores": {"perfectionism_anxiety": 1.0, "anxiety": 0.5}},
            {"text": "দেয়ালের ছবিগুলো পরিচিত মুখ", "scores": {"grief": 1.0, "identity_loss": 0.5}},
            {"text": "এই মুহূর্তে কোথাও যাওয়ার নেই", "scores": {"depression": 1.5, "social_withdrawal": 1.5}},
            {"text": "সকালটা ধীরে ধীরে শুরু হয়", "scores": {"depression": 1.0, "emotional_exhaustion": 1.0}},
            {"text": "জানালার গ্রিলটা ছায়া ফেলে মেঝেতে", "scores": {"emotional_suppression": 1.0, "dissociation": 0.5}},
            {"text": "এই ঘরটা অনেককিছু জানে", "scores": {"dissociation": 1.0, "grief": 0.5}},
            {"text": "পর্দাটা একটু সরালে বেশি আলো আসে", "scores": {"emotional_suppression": 1.5, "social_withdrawal": 1.0}},
            {"text": "এখানে বসে থাকলে সময় নিজেই যায়", "scores": {"depression": 1.5, "dissociation": 1.0, "emotional_numbness": 1.0}},
            {"text": "বাইরে পৃথিবী চলছে", "scores": {"social_withdrawal": 1.5, "dissociation": 1.5}},
        ]
    },
    {
        "file": "scene_07_missed_call.jpeg",
        "captions": [
            {"text": "ফোনটা একটু আগেই চুপ হয়ে গেছে", "scores": {"social_withdrawal": 1.0, "emotional_suppression": 1.0}},
            {"text": "রাত ১১টার পর ফোন বাজলে অন্যরকম লাগে", "scores": {"hypervigilance": 1.5, "anxiety": 1.5}},
            {"text": "স্ক্রিনের আলোটা অন্ধকারে অনেক বেশি", "scores": {"loneliness": 1.0, "depression": 0.5}},
            {"text": "বিছানার চাদরটা একটু কুঁচকে আছে", "scores": {"emotional_numbness": 1.0, "depression": 0.5}},
            {"text": "মিস কল মানে কেউ একটু আগে ছিল", "scores": {"loneliness": 1.5, "emotional_dependency": 1.5}},
            {"text": "এই সময়ে ফোন না ধরলে পরে জানানো যায়", "scores": {"social_withdrawal": 1.5, "emotional_suppression": 1.0}},
            {"text": "তিনটা নম্বর একই নাম", "scores": {"anxiety": 1.0, "hypervigilance": 1.0, "emotional_dependency": 0.5}},
            {"text": "রাতের এই সময়টা নিজের", "scores": {"social_withdrawal": 1.5, "depression": 0.5}},
            {"text": "ফোনটা একটু ঘুরিয়ে রাখলে স্ক্রিন দেখা যায় না", "scores": {"emotional_suppression": 1.5, "social_withdrawal": 1.0}},
            {"text": "কাল সকালে দেখলেই হবে", "scores": {"depression": 1.0, "social_withdrawal": 1.0, "emotional_numbness": 0.5}},
            {"text": "চার্জটা দিতে ভুলে গেছি", "scores": {"burnout": 1.0, "dissociation": 0.5}},
            {"text": "অন্ধকারে ফোনের আলোটা চোখে লাগে", "scores": {"anxiety": 1.0, "hypervigilance": 0.5}},
        ]
    },
]

FC_CARDS = [
    {"id":1,"question":"সন্ধ্যায় একটা notification এলো — পুরনো বন্ধু দাওয়াত দিচ্ছে।",
     "options":[
         {"text":"🌙 দেখি, মেজাজ বুঝে সিদ্ধান্ত নেব","w":1.5,"e":1.0,"o":0.5,"conditions":{"social_withdrawal":1.0,"anxiety":0.5,"decision_fatigue":0.5}},
         {"text":"🚪 যাব — বের হলে ভালোই লাগে সাধারণত","w":0.0,"e":2.0,"o":2.0,"conditions":{"loneliness":-0.5,"depression":-0.5}},
     ]},
    {"id":2,"question":"কাজের মাঝে হঠাৎ মাথা ভার লাগছে। হাতে ১৫ মিনিট আছে।",
     "options":[
         {"text":"🎧 হেডফোন লাগিয়ে চোখ বন্ধ করব","w":1.5,"e":0.5,"o":0.0,"conditions":{"burnout":1.0,"emotional_exhaustion":0.5,"dissociation":0.5}},
         {"text":"☕ উঠে একটু হাঁটব, কিছু খাব","w":0.5,"e":1.5,"o":1.0,"conditions":{"burnout":-0.5}},
     ]},
    {"id":3,"question":"পরিচিত কেউ রাস্তায় দেখল, হাত নাড়াচ্ছে।",
     "options":[
         {"text":"👋 হাত নাড়িয়ে এগিয়ে যাব","w":0.0,"e":1.5,"o":1.5,"conditions":{"social_withdrawal":-0.5,"loneliness":-0.5}},
         {"text":"🙂 হাসব, কিন্তু থামব না","w":1.5,"e":1.0,"o":0.5,"conditions":{"social_withdrawal":1.0,"emotional_suppression":0.5}},
     ]},
    {"id":4,"question":"বাসায় ফেরার পথে দুটো রাস্তা — একটা চেনা, একটা নতুন।",
     "options":[
         {"text":"🗺️ নতুনটা দিয়ে যাব, দেখি কেমন","w":0.0,"e":2.0,"o":2.0,"conditions":{"anxiety":-0.5,"decision_fatigue":-0.5}},
         {"text":"🏠 চেনা রাস্তাই ভালো, ক্লান্ত আছি","w":1.0,"e":0.5,"o":0.0,"conditions":{"burnout":0.5,"chronic_stress":0.5,"hypervigilance":0.5}},
     ]},
    {"id":5,"question":"গ্রুপ চ্যাটে কেউ মতামত চাইল — তোমার ভালো ধারণা আছে বিষয়টায়।",
     "options":[
         {"text":"💬 লিখব, অন্যরা কী বলে দেখি","w":0.0,"e":1.5,"o":1.5,"conditions":{"imposter_syndrome":-0.5,"low_self_worth":-0.5}},
         {"text":"👁️ পড়ব, কিন্তু কিছু বলব না এখন","w":1.5,"e":0.5,"o":0.0,"conditions":{"imposter_syndrome":1.0,"emotional_suppression":1.0,"social_withdrawal":0.5}},
     ]},
    {"id":6,"question":"সকালে উঠে দেখলে বাইরে বৃষ্টি। আজ কোনো বাধ্যবাধকতা নেই।",
     "options":[
         {"text":"🌧️ জানালার পাশে চুপ করে বসে থাকব","w":1.5,"e":0.5,"o":0.5,"conditions":{"social_withdrawal":1.0,"depression":0.5,"grief":0.5}},
         {"text":"📞 কাউকে ডাকব, এই আবহাওয়ায় আড্ডা জমে","w":0.0,"e":2.0,"o":1.5,"conditions":{"loneliness":-0.5,"depression":-0.5}},
     ]},
    {"id":7,"question":"অফিসে নতুন একজন এলো, কেউ পরিচয় করিয়ে দেয়নি।",
     "options":[
         {"text":"🤝 নিজেই এগিয়ে কথা বলব","w":0.0,"e":2.0,"o":2.0,"conditions":{"anxiety":-0.5,"low_self_worth":-0.5}},
         {"text":"⏳ সুযোগ হলে একসময় হবে","w":1.5,"e":0.5,"o":0.5,"conditions":{"anxiety":1.0,"social_withdrawal":0.5,"low_self_worth":0.5}},
     ]},
    {"id":8,"question":"একটা কাজ শেষ হলো যেটা অনেকদিন ধরে চলছিল।",
     "options":[
         {"text":"😮‍💨 হাঁফ ছাড়লাম — এখন একটু চুপ থাকব","w":1.0,"e":0.5,"o":0.5,"conditions":{"burnout":1.0,"emotional_exhaustion":0.5}},
         {"text":"🎉 কাউকে জানাব, ভালো লাগছে","w":0.0,"e":2.0,"o":1.5,"conditions":{"depression":-0.5,"loneliness":-0.5}},
     ]},
    {"id":9,"question":"রাতে খাওয়ার পর কী করতে ইচ্ছা করছে?",
     "options":[
         {"text":"📱 ফোন স্ক্রোল করতে করতে শুয়ে থাকব","w":1.5,"e":0.5,"o":0.0,"conditions":{"depression":0.5,"social_withdrawal":0.5,"emotional_numbness":0.5}},
         {"text":"🚶 বাইরে একটু হাঁটতে যাব","w":0.5,"e":1.5,"o":1.0,"conditions":{"burnout":-0.5,"depression":-0.5}},
     ]},
    {"id":10,"question":"কেউ তোমার কাজের প্রশংসা করল সবার সামনে।",
     "options":[
         {"text":"🙏 ধন্যবাদ বলে চুপ করে থাকব","w":1.0,"e":1.0,"o":0.5,"conditions":{"imposter_syndrome":0.5,"low_self_worth":0.5,"emotional_suppression":0.5}},
         {"text":"😊 বলব কীভাবে করলাম, গল্প করব","w":0.0,"e":2.0,"o":2.0,"conditions":{"imposter_syndrome":-0.5,"low_self_worth":-0.5}},
     ]},
    {"id":11,"question":"শনিবার সকাল — কোনো plan নেই। কী করবে?",
     "options":[
         {"text":"🛏️ যতক্ষণ ঘুম আসে শুয়ে থাকব","w":1.5,"e":0.5,"o":0.0,"conditions":{"depression":1.0,"burnout":0.5,"emotional_exhaustion":0.5}},
         {"text":"🌅 উঠে কোথাও একটু বেরিয়ে আসব","w":0.0,"e":2.0,"o":1.5,"conditions":{"depression":-0.5,"social_withdrawal":-0.5}},
     ]},
    {"id":12,"question":"একটা message এসেছে যার reply দিতে ভুলে গিয়েছিলে — ৩ দিন আগে।",
     "options":[
         {"text":"✍️ এখনই reply করব, দেরি হয়ে গেছে","w":0.0,"e":1.5,"o":1.5,"conditions":{"anxiety":0.5}},
         {"text":"🔇 পরে করব, এখন মন নেই","w":2.0,"e":0.5,"o":0.0,"conditions":{"depression":1.0,"social_withdrawal":1.0,"emotional_numbness":0.5}},
     ]},
    {"id":13,"question":"বন্ধু বলল 'তুমি ইদানীং চুপচাপ হয়ে গেছ।'",
     "options":[
         {"text":"🤷 হাসব, বলব 'এমনিই'","w":1.5,"e":0.5,"o":0.0,"conditions":{"emotional_suppression":1.5,"imposter_syndrome":0.5,"depression":0.5}},
         {"text":"💭 একটু বলব কী চলছে আসলে","w":0.0,"e":1.0,"o":2.0,"conditions":{"emotional_suppression":-1.0}},
     ]},
    {"id":14,"question":"দুপুরে খাওয়ার জন্য একা বসেছ। পাশে পরিচিত মুখ।",
     "options":[
         {"text":"🍱 নিজের মতো খেয়ে চলে যাব","w":1.5,"e":0.5,"o":0.0,"conditions":{"social_withdrawal":1.0,"depression":0.5,"loneliness":0.5}},
         {"text":"🪑 'বসতে পারি?' বলে পাশে বসব","w":0.0,"e":1.5,"o":2.0,"conditions":{"loneliness":-0.5,"social_withdrawal":-0.5}},
     ]},
    {"id":15,"question":"একটা নতুন hobby শুরু করার কথা ভাবছিলে।",
     "options":[
         {"text":"📋 আরেকটু ভাবব, তাড়া নেই","w":1.0,"e":0.5,"o":0.5,"conditions":{"decision_fatigue":1.0,"anxiety":0.5,"depression":0.5}},
         {"text":"🎯 আজকেই একটু শুরু করে দেখি","w":0.0,"e":2.0,"o":2.0,"conditions":{"decision_fatigue":-0.5,"depression":-0.5}},
     ]},
    {"id":16,"question":"রাতে হঠাৎ পুরনো একটা স্মৃতি মনে পড়ল।",
     "options":[
         {"text":"🌊 ডুবে থাকব কিছুক্ষণ, একা","w":1.5,"e":0.5,"o":0.5,"conditions":{"grief":1.5,"depression":0.5,"social_withdrawal":0.5}},
         {"text":"📲 যাকে নিয়ে স্মৃতি, তাকে জানাব","w":0.0,"e":1.5,"o":2.0,"conditions":{"grief":-0.5,"loneliness":-0.5}},
     ]},
    {"id":17,"question":"কাজে একটা ভুল হয়ে গেছে — ছোট, কিন্তু তুমি জানো।",
     "options":[
         {"text":"🤫 নিজে ঠিক করে নেব, কাউকে বলব না","w":1.0,"e":1.0,"o":0.0,"conditions":{"perfectionism_anxiety":1.0,"imposter_syndrome":1.0,"emotional_suppression":0.5}},
         {"text":"🗣️ বলে দেব, একসাথে ঠিক করব","w":0.0,"e":1.5,"o":2.0,"conditions":{"imposter_syndrome":-0.5,"low_self_worth":-0.5}},
     ]},
    {"id":18,"question":"সপ্তাহ শেষে মনে হলো কেমন গেল?",
     "options":[
         {"text":"😶 এমনিই গেছে, কিছু মনে নেই","w":1.5,"e":0.5,"o":0.0,"conditions":{"emotional_numbness":1.5,"depression":1.0,"burnout":0.5}},
         {"text":"🔍 ভালো-খারাপ দুটোই ছিল, মিলিয়ে ঠিকই আছে","w":0.0,"e":1.5,"o":1.5,"conditions":{"emotional_numbness":-0.5,"depression":-0.5}},
     ]},
]

SCENARIOS = [
    {"q":"দিনের শেষে নিজেকে কেমন লাগে সাধারণত?","options":[
        {"text":"😌 ঠিকঠাক — দিন গেছে, কাজ হয়েছে","scores":{"caregiver_fatigue":1.0,"emotional_numbness":0.5}},
        {"text":"💭 একটু ভারী, কিন্তু বলার মতো কিছু না","scores":{"emotional_suppression":1.5,"burnout":1.0}},
        {"text":"😶 এমনিই — কিছু মনে হয় না বিশেষ","scores":{"emotional_numbness":1.5,"dissociation":1.0}},
        {"text":"😮‍💨 অনেক কিছু করেছি, কিন্তু কী করেছি মনে নেই","scores":{"burnout":1.5,"dissociation":1.0}},
    ]},
    {"q":"কেউ তোমার কোনো কাজের কথা জিজ্ঞেস না করলে?","options":[
        {"text":"🤷 সবাই ব্যস্ত থাকে, এটা স্বাভাবিক","scores":{"emotional_suppression":1.0,"low_self_worth":1.0}},
        {"text":"💭 একটু হলেও জানতে চাইলে ভালো লাগত","scores":{"grief":1.0,"loneliness":1.0}},
        {"text":"😌 আমি এটা expect করি না আসলে","scores":{"low_self_worth":1.5,"identity_loss":1.0}},
        {"text":"😶 ভাবিনি এটা নিয়ে","scores":{"emotional_numbness":1.5,"dissociation":0.5}},
    ]},
    {"q":"উৎসবের সময় নিজের জন্য কিছু কেনা হয়?","options":[
        {"text":"😊 বাকিদের কিছু হলেই আমার হয়","scores":{"caregiver_fatigue":1.5,"identity_loss":1.0}},
        {"text":"💭 মাঝে মাঝে মনে হয়, কিন্তু পরে ভুলে যাই","scores":{"emotional_suppression":1.0,"grief":1.0}},
        {"text":"😶 এটা নিয়ে ভাবিইনি তেমন","scores":{"emotional_numbness":1.5,"identity_loss":1.5}},
        {"text":"😌 পরে একসময় নেব","scores":{"decision_fatigue":1.0,"low_self_worth":0.5}},
    ]},
    {"q":"কেউ তোমার পরিচয় দিলে কেমন লাগে?","options":[
        {"text":"😌 যেভাবেই হোক, ঠিকাছে","scores":{"emotional_suppression":1.0,"low_self_worth":1.0}},
        {"text":"💭 মাঝে মাঝে মনে হয় পুরোটা বলা হলো না","scores":{"identity_loss":1.5,"grief":1.0}},
        {"text":"😶 এটা নিয়ে ভাবি না আসলে","scores":{"emotional_numbness":1.5,"identity_loss":1.0}},
        {"text":"🤔 নিজে বলতে গেলে কী বলতাম জানি না","scores":{"identity_loss":1.5,"dissociation":1.0}},
    ]},
    {"q":"সংসারের বাইরে নিজের জন্য কিছু করার সময় হয়?","options":[
        {"text":"😮‍💨 হয় না তেমন, কিন্তু অভ্যাস হয়ে গেছে","scores":{"burnout":1.5,"caregiver_fatigue":1.5}},
        {"text":"💭 ইচ্ছা থাকে, সময় মেলে না","scores":{"chronic_stress":1.0,"identity_loss":1.0}},
        {"text":"😌 আমার এখন ওসব দরকার নেই","scores":{"emotional_suppression":1.5,"low_self_worth":1.0}},
        {"text":"😶 ভাবিনি এটা নিয়ে","scores":{"emotional_numbness":1.5,"burnout":1.0}},
    ]},
    {"q":"বাড়িতে বড় কোনো সিদ্ধান্ত হলে তোমার মতামত কতটা আসে?","options":[
        {"text":"😌 ওরা ভালোই জানে, আমি মেনে নিই","scores":{"emotional_dependency":1.5,"low_self_worth":1.0}},
        {"text":"💭 মত দিই, কতটা কাজে আসে জানি না","scores":{"low_self_worth":1.0,"emotional_suppression":1.0}},
        {"text":"😶 এটা নিয়ে আর মাথা ঘামাই না","scores":{"emotional_numbness":1.5,"grief":1.0}},
        {"text":"😤 ভেতরে কিছু একটা থাকে, বলা হয় না","scores":{"rage_suppression":1.5,"emotional_suppression":1.0}},
    ]},
    {"q":"অফিস আর বাড়ি — দুটো একসাথে চালাতে কেমন লাগে?","options":[
        {"text":"😮‍💨 কঠিন, কিন্তু করতে হয়","scores":{"burnout":1.5,"chronic_stress":1.5}},
        {"text":"😌 অভ্যাস হয়ে গেছে","scores":{"emotional_numbness":1.0,"burnout":1.0}},
        {"text":"💭 মাঝে মাঝে মনে হয় একটু বেশি","scores":{"emotional_exhaustion":1.5,"caregiver_fatigue":1.0}},
        {"text":"😶 এটাই তো জীবন","scores":{"emotional_suppression":1.5,"identity_loss":1.0}},
    ]},
    {"q":"নিজের কথা বললে বা মত দিলে কেমন feel হয়?","options":[
        {"text":"😌 বলার চেষ্টা করি","scores":{"emotional_suppression":0.5}},
        {"text":"💭 বলি, কিন্তু পরে ভাবি বলা ঠিক হলো কিনা","scores":{"hypervigilance":1.5,"anxiety":1.0}},
        {"text":"😶 কম বলি, ঝামেলা কম","scores":{"emotional_suppression":1.5,"rage_suppression":1.0}},
        {"text":"😮‍💨 কখন বলা যাবে, কখন না — হিসাব করতে ক্লান্ত","scores":{"decision_fatigue":1.5,"burnout":1.0}},
    ]},
    {"q":"নিজে অসুস্থ থাকলে কী হয় সাধারণত?","options":[
        {"text":"😮‍💨 কাজ থামে না, চালিয়ে যাই","scores":{"caregiver_fatigue":1.5,"burnout":1.5}},
        {"text":"💭 একটু rest নিই, তবে guilty লাগে","scores":{"low_self_worth":1.0,"anxiety":1.0}},
        {"text":"😌 একদিনেই ঠিক হয়ে যায়","scores":{"emotional_suppression":1.0,"burnout":0.5}},
        {"text":"😶 শরীর খারাপ হলেও এগিয়ে চলি","scores":{"emotional_numbness":1.5,"caregiver_fatigue":1.0}},
    ]},
    {"q":"নিজের qualification বা কাজ নিয়ে কেউ কিছু না বললে?","options":[
        {"text":"😌 আমি নিজের জন্যই করি","scores":{"emotional_suppression":1.0,"identity_loss":0.5}},
        {"text":"💭 একটু হলেও কেউ দেখলে ভালো লাগত","scores":{"grief":1.0,"low_self_worth":1.0}},
        {"text":"😶 এটা নিয়ে ভাবিনি","scores":{"emotional_numbness":1.5,"dissociation":0.5}},
        {"text":"😮‍💨 প্রমাণ করতে করতে ক্লান্ত","scores":{"burnout":1.5,"emotional_exhaustion":1.5}},
    ]},
    {"q":"কেউ তোমাকে অন্য কারো সাথে তুলনা করলে?","options":[
        {"text":"😌 শুনি, এগিয়ে যাই","scores":{"emotional_suppression":1.0,"low_self_worth":0.5}},
        {"text":"💭 মনে লাগে, বুঝতে দিই না","scores":{"grief":1.5,"rage_suppression":1.0}},
        {"text":"😶 অভ্যাস হয়ে গেছে এসব","scores":{"emotional_numbness":1.5,"chronic_stress":1.0}},
        {"text":"😤 ভেতরে রাগ হয়, চুপ থাকি","scores":{"rage_suppression":1.5,"low_self_worth":0.5}},
    ]},
    {"q":"রাতে নিজের জন্য সময় বের করলে কেমন লাগে?","options":[
        {"text":"😌 ভালো লাগে, deserve করি","scores":{}},
        {"text":"💭 একটু guilty লাগে, অন্যদের কথা মনে পড়ে","scores":{"low_self_worth":1.5,"caregiver_fatigue":1.0}},
        {"text":"😶 এমন সময় আসে না তেমন","scores":{"burnout":1.5,"identity_loss":1.0}},
        {"text":"😮‍💨 শুয়ে পড়ি, আর কিছু করার energy নেই","scores":{"emotional_exhaustion":1.5,"burnout":1.5}},
    ]},
    {"q":"পরিবারের বাইরে নিজের কোনো স্বপ্ন বা ইচ্ছার কথা মনে পড়ে?","options":[
        {"text":"💭 মাঝে মাঝে পড়ে, বলা হয় না","scores":{"grief":1.5,"identity_loss":1.0}},
        {"text":"😌 এখন আর সেসব ভাবি না","scores":{"emotional_numbness":1.5,"grief":1.5}},
        {"text":"😶 কী চেয়েছিলাম মনেই নেই","scores":{"dissociation":1.5,"identity_loss":1.5}},
        {"text":"😊 আছে, একদিন হবে","scores":{}},
    ]},
    {"q":"কেউ বলল 'তুমি একটু বেশি sensitive।' কেমন লাগল?","options":[
        {"text":"😌 হয়তো ঠিকই বলেছে","scores":{"low_self_worth":1.5,"emotional_dependency":1.0}},
        {"text":"💭 কিছু বললাম না, কিন্তু মনে রইল","scores":{"rage_suppression":1.0,"grief":1.0}},
        {"text":"😶 শুনলাম, ভুলে গেলাম","scores":{"emotional_numbness":1.5,"emotional_suppression":0.5}},
        {"text":"😤 বলতে চেয়েছিলাম, থেমে গেছি","scores":{"rage_suppression":1.5,"hypervigilance":1.0}},
    ]},
    {"q":"ঘরের কাজ হয় কিন্তু কেউ খেয়াল করে না — এলোমেলো হলে সবাই বলে।","options":[
        {"text":"😮‍💨 এটাই তো স্বাভাবিক","scores":{"emotional_suppression":1.5,"caregiver_fatigue":1.0}},
        {"text":"💭 মাঝে মাঝে একটু notice করলে ভালো লাগত","scores":{"grief":1.0,"loneliness":1.0}},
        {"text":"😶 আর feel হয় না এসব নিয়ে","scores":{"emotional_numbness":1.5,"burnout":1.0}},
        {"text":"😤 ভেতরে কষ্ট লাগে, বলা হয় না","scores":{"rage_suppression":1.5,"caregiver_fatigue":1.0}},
    ]},
    {"q":"সবার কথা ভেবেছ সারাদিন — নিজের জন্য একটু সময় নিতে গেলে?","options":[
        {"text":"😌 নিই, সবার পর","scores":{"caregiver_fatigue":1.0,"low_self_worth":0.5}},
        {"text":"💭 guilt লাগে একটু","scores":{"low_self_worth":1.5,"emotional_suppression":1.0}},
        {"text":"😶 ঘুমিয়ে পড়ি, নিজের কথা আর হয় না","scores":{"burnout":1.5,"identity_loss":1.0}},
        {"text":"😮‍💨 জানি দরকার, পারছি না বের করতে","scores":{"decision_fatigue":1.5,"emotional_exhaustion":1.0}},
    ]},
]

HEDGING = ["মনে হয়","হয়তো","জানি না","মনে হচ্ছে","বুঝি না","নিশ্চিত না","মনে হলো","হয়তোবা","সম্ভবত"]
ABSOLUTIST = ["সবসময়","কখনো না","কেউ না","সব","কিছুই না","সবাই","কখনো","একদম","মোটেই"]
NEGATIVE_WORDS = ["কষ্ট","ক্লান্ত","ভারী","একা","ভয়","রাগ","দুঃখ","বিরক্ত","অসহ্য","ব্যর্থ","হতাশ","শেষ","পারছি না","আর না","ভালো নেই","খারাপ","মন খারাপ","কান্না","কাঁদলাম"]
FIRST_PERSON = ["আমি","আমার","আমাকে","আমাতে","আমাদের"]
POSITIVE_WORDS = ["ভালো","সুন্দর","আনন্দ","খুশি","শান্তি","ভালোবাসি","মজা","হাসি","উৎসাহ","আশা"]

POSITIVE_REFRAME = {
    "anxiety":               ("তুমি অনেক কিছু নিয়ে care করো", "সেটাই তোমাকে thoughtful করে তোলে।"),
    "burnout":               ("তুমি অনেক কিছু বহন করছ", "rest নেওয়া weakness না — এটা তোমার প্রাপ্য।"),
    "emotional_exhaustion":  ("তুমি অনেকের জন্য অনেক দিয়েছ", "নিজেকেও সেই যত্নের একটু ভাগ দাও।"),
    "loneliness":            ("তোমার ভেতরে connection এর চাহিদা আছে", "সেটা তোমার strength — তুমি মানুষকে মূল্য দাও।"),
    "chronic_stress":        ("তুমি অনেক চাপের মধ্যেও এগিয়ে যাচ্ছ", "এটা সহজ কাজ না।"),
    "emotional_suppression": ("তুমি emotionally strong", "কিন্তু feel করাটাও তোমার অধিকার।"),
    "low_self_worth":        ("তুমি নিজেকে যতটা ছোট ভাবো", "তুমি আসলে ততটা না।"),
    "caregiver_fatigue":     ("তুমি অনেকের জন্য অনেক করো", "নিজের জন্যও সেই ভালোবাসাটুকু রাখো।"),
    "social_withdrawal":     ("তুমি নিজের সাথে comfortable", "introvert strength — নিজেকে চেনো তুমি।"),
    "emotional_numbness":    ("তুমি হয়তো অনেকদিন ধরে অনেক কিছু সামলেছ", "feel করার জায়গা খুঁজে নেওয়া দরকার।"),
    "depression":            ("তুমি এখনো এখানে আছ", "সেটাই অনেক বড় — তুমি যতটা ভাবো তার চেয়ে শক্তিশালী।"),
    "identity_loss":         ("তুমি অনেক role এ আছ", "কিন্তু তার বাইরেও একটা 'তুমি' আছ।"),
    "hypervigilance":        ("তুমি সবকিছু সম্পর্কে সচেতন", "এই awareness তোমার — শুধু নিজের জন্যও ব্যবহার করো।"),
    "perfectionism_anxiety": ("তোমার standards high", "সেটা admirable — কিন্তু নিজেকেও সেই standard এ মাপতে হবে না সবসময়।"),
    "imposter_syndrome":     ("তুমি যতটা doubt করো নিজেকে", "ততটা যোগ্য না হলে এই doubt আসত না।"),
    "emotional_dependency":  ("তোমার কাছের মানুষদের মতামত তোমার কাছে গুরুত্বপূর্ণ", "নিজের মতামতটাও সমান গুরুত্বপূর্ণ।"),
    "grief":                 ("তুমি feel করতে পারো", "সেটা তোমার sensitivity র প্রমাণ — এটা weakness না।"),
    "rage_suppression":      ("তোমার ভেতরে strong opinions আছে", "সেটা তোমার power — একদিন সঠিক জায়গায় বলার সুযোগ আসবে।"),
    "decision_fatigue":      ("তুমি অনেক decision নিচ্ছ প্রতিদিন", "কিছু কিছু সিদ্ধান্ত অন্যদের দেওয়া যায় — সব তোমার একা না।"),
    "dissociation":          ("তুমি হয়তো অনেকদিন ধরে autopilot এ আছ", "নিজেকে ফিরে পাওয়ার সময় এসেছে।"),
}

SUGGESTIONS = {
    "anxiety":               "প্রতিদিন ৫ মিনিট শুধু breathing এ মনোযোগ দাও। কিছু করতে হবে না।",
    "burnout":               "একটা দিন শুধু নিজের জন্য রাখো — কোনো কাজ না, কোনো দায়িত্ব না।",
    "emotional_exhaustion":  "কাউকে বলো 'আজকে আমি ক্লান্ত।' শুধু এটুকু।",
    "loneliness":            "একজন মানুষকে আজকে message করো — শুধু 'কেমন আছ?' লিখলেও হবে।",
    "chronic_stress":        "একটা কাজ list করো — সবচেয়ে ছোটটা আগে করো। বাকিটা পরে।",
    "emotional_suppression": "একটা diary তে আজকের একটা কথা লিখে রাখো — কেউ পড়বে না।",
    "low_self_worth":        "আজকে একটা কাজ করো শুধু নিজের জন্য — ছোট হলেও।",
    "caregiver_fatigue":     "আজকে ১৫ মিনিট শুধু তোমার — ফোন বন্ধ, কেউ নেই।",
    "social_withdrawal":     "একজনকে আজকে দেখতে যাও বা call করো — মন না চাইলেও।",
    "emotional_numbness":    "এমন কিছু করো যেটায় আগে ভালো লাগত — গান, রান্না, হাঁটা।",
    "depression":            "আজকে একটাই কাজ — বাইরে গিয়ে ১০ মিনিট হাঁটো।",
    "identity_loss":         "একটা কাগজে লিখো — পরিবারের বাইরে তুমি কে? তিনটা জিনিস।",
    "hypervigilance":        "আজকে একটা ছোট কাজ করো যেটায় কোনো consequence নেই।",
    "perfectionism_anxiety": "একটা কাজ ৮০% করে ছেড়ে দাও। দেখো কী হয়।",
    "imposter_syndrome":     "তোমার একটা achievement লিখো — ছোট হলেও। সেটা real।",
    "emotional_dependency":  "আজকে একটা সিদ্ধান্ত নাও — ছোট — কাউকে না জিজ্ঞেস করে।",
    "grief":                 "যে কষ্টটা বলা হয়নি — আজকে সেটা লিখো। শুধু নিজের জন্য।",
    "rage_suppression":      "একটা কাগজে রাগের কথাটা লিখে ছিঁড়ে ফেলো। শরীরে হালকা লাগবে।",
    "decision_fatigue":      "আজকে তিনটার বেশি বড় সিদ্ধান্ত নেবে না। বাকিটা কাল।",
    "dissociation":          "৫টা জিনিস দেখো, ৪টা স্পর্শ করো, ৩টা শোনো — এখনই।",
}

# ══════════════════════════════════════════════════════════════════
# SHARE REPORT HELPERS
# ══════════════════════════════════════════════════════════════════
def encode_scores(scores: dict) -> str:
    filtered = {k: v for k, v in scores.items() if v > 0}
    top5 = dict(sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:5])
    json_str = json.dumps(top5)
    return base64.urlsafe_b64encode(json_str.encode()).decode()

def decode_scores(encoded: str) -> dict:
    try:
        json_str = base64.urlsafe_b64decode(encoded.encode()).decode()
        return json.loads(json_str)
    except:
        return {}

# ══════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════
def _init():
    defaults = {
        "page": "home",
        "lang": "bn",
        "condition_scores": {c: 0.0 for c in CONDITIONS},
        "vs_picture": None, "vs_captions": None, "vs_done": False,
        "fc_cards": None, "fc_index": 0,
        "fc_scores": {"withdrawal":0.0,"energy":0.0,"openness":0.0},
        "fc_done": False,
        "share_link_shown": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# Check for shared report in URL
params = st.query_params
if "r" in params and st.session_state.page == "home":
    decoded = decode_scores(params["r"])
    if decoded:
        st.session_state.condition_scores = {c: decoded.get(c, 0.0) for c in CONDITIONS}
        st.session_state.page = "result"

# Check for voice input in URL
if "voice_input" in params:
    st.session_state["voice_captured"] = params["voice_input"]

def _add_scores(scores: dict):
    for c, v in scores.items():
        if c in st.session_state.condition_scores:
            st.session_state.condition_scores[c] = max(0.0, st.session_state.condition_scores[c] + v)

# ══════════════════════════════════════════════════════════════════
# LANGUAGE TOGGLE UI
# ══════════════════════════════════════════════════════════════════
def render_lang_toggle():
    col1, col2, col3 = st.columns([3, 1, 1])
    with col2:
        if st.button("বাংলা", key="lang_bn",
                     type="primary" if st.session_state.lang == "bn" else "secondary"):
            st.session_state.lang = "bn"
            st.rerun()
    with col3:
        if st.button("EN", key="lang_en",
                     type="primary" if st.session_state.lang == "en" else "secondary"):
            st.session_state.lang = "en"
            st.rerun()

# ══════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════
def page_home():
    render_lang_toggle()
    st.markdown(f"""
    <div class="home-page">
        <div class="mirror-container">
            <div class="mirror-glow"></div>
            <div class="mirror-circle">🪞</div>
        </div>
        <div class="ayna-title">Ayna</div>
        <div class="div-row">
            <div class="div-line"></div>
            <div class="div-dot"></div>
            <div class="div-line r"></div>
        </div>
        <div class="tagline-en">{T("tagline")}</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if st.button(T("start"), type="primary", use_container_width=True):
            pic = random.choice(PICTURES)
            st.session_state.vs_picture  = pic
            st.session_state.vs_captions = random.sample(pic["captions"], 4)
            st.session_state.page = "stage1"
            st.rerun()


def page_stage1():
    render_lang_toggle()
    st.markdown(f'<div class="pill">{T("stage1_pill")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-title">{T("stage1_title")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-sub">{T("stage1_sub")}</div>', unsafe_allow_html=True)

    picture  = st.session_state.vs_picture
    captions = st.session_state.vs_captions

    if not st.session_state.vs_done:
        img_path = os.path.join(os.path.dirname(__file__), "assets", "scenes", picture["file"])
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            st.info(f"📷 [{picture['file']}]")

        st.markdown(f'<div class="q-text">{T("stage1_q")}</div>', unsafe_allow_html=True)

        for i, cap in enumerate(captions):
            if st.button(f'"{cap["text"]}"', key=f"vs_{i}"):
                _add_scores(cap["scores"])
                st.session_state.vs_done = True
                st.rerun()
    else:
        st.markdown(f'<div class="info-box">✓ {T("stage1_done")}</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1.5,1])
        with col2:
            if st.button(T("next"), type="primary", use_container_width=True):
                st.session_state.fc_cards  = random.sample(FC_CARDS, 5)
                st.session_state.fc_index  = 0
                st.session_state.fc_scores = {"withdrawal":0.0,"energy":0.0,"openness":0.0}
                st.session_state.fc_done   = False
                st.session_state.page      = "stage2"
                st.rerun()


def page_stage2():
    render_lang_toggle()
    st.markdown(f'<div class="pill">{T("stage2_pill")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-title">{T("stage2_title")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-sub">{T("stage2_sub")}</div>', unsafe_allow_html=True)

    cards = st.session_state.fc_cards
    idx   = st.session_state.fc_index

    st.progress(idx / 5, text=f"{T('card_of')} {idx+1} {T('of')} 5")

    if not st.session_state.fc_done:
        card = cards[idx]
        st.markdown(f'<div class="q-text">{card["question"]}</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        for ci, (col, opt) in enumerate(zip([col1, col2], card["options"])):
            with col:
                if st.button(opt["text"], key=f"fc_{idx}_{ci}"):
                    s = st.session_state.fc_scores
                    s["withdrawal"] += opt["w"]
                    s["energy"]     += opt["e"]
                    s["openness"]   += opt["o"]
                    _add_scores(opt["conditions"])
                    st.session_state.fc_index += 1
                    if st.session_state.fc_index >= 5:
                        st.session_state.fc_done = True
                        w = min((s["withdrawal"] / 10.0) * 10, 10)
                        e = min((s["energy"]     / 10.0) * 10, 10)
                        if w > 6:
                            _add_scores({"social_withdrawal":0.5,"depression":0.5})
                        if e < 3:
                            _add_scores({"burnout":0.5,"emotional_exhaustion":0.5})
                        st.session_state.fc_w = round(w,1)
                        st.session_state.fc_e = round(e,1)
                        st.session_state.fc_o = round(min((s["openness"]/10.0)*10,10),1)
                    st.rerun()
    else:
        st.progress(1.0, text=T("all_done"))
        st.markdown(f'<div class="info-box">{T("stage2_done")}</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1.5,1])
        with col2:
            if st.button(T("next"), type="primary", use_container_width=True):
                st.session_state.page = "stage3"
                st.rerun()


def page_stage3():
    render_lang_toggle()
    st.markdown(f'<div class="pill">{T("stage3_pill")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-title">{T("stage3_title")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-sub">{T("stage3_sub")}</div>', unsafe_allow_html=True)

    if "s3_scenarios" not in st.session_state:
        st.session_state.s3_scenarios = random.sample(SCENARIOS, 3)
        st.session_state.s3_index = 0
        st.session_state.s3_done = False

    if not st.session_state.s3_done:
        idx   = st.session_state.s3_index
        total = len(st.session_state.s3_scenarios)

        st.progress(idx / total, text=f"{T('q_of')} {idx+1} {T('of')} {total}")

        scenario = st.session_state.s3_scenarios[idx]
        st.markdown(f'<div class="q-text">{scenario["q"]}</div>', unsafe_allow_html=True)

        opts = scenario["options"][:]
        random.shuffle(opts)

        for i, opt in enumerate(opts):
            if st.button(opt["text"], key=f"s3_{idx}_{i}"):
                for cond, val in opt["scores"].items():
                    if cond in st.session_state.condition_scores:
                        st.session_state.condition_scores[cond] += val
                st.session_state.s3_index += 1
                if st.session_state.s3_index >= total:
                    st.session_state.s3_done = True
                st.rerun()
    else:
        st.markdown(f'<div class="info-box">{T("stage3_done")}</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            if st.button(T("next"), type="primary", use_container_width=True):
                st.session_state.page = "stage4"
                st.rerun()


def page_stage4():
    render_lang_toggle()
    st.markdown(f'<div class="pill">{T("stage4_pill")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-title">{T("stage4_title")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-sub">{T("stage4_sub")}</div>', unsafe_allow_html=True)

    # Voice input
    st.markdown(f'<div class="sec-sub" style="font-weight:600;color:#2C5F4A;">{T("stage4_voice")}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:12px;color:#6B6B6B;">{T("stage4_voice_sub")}</p>', unsafe_allow_html=True)
    st.components.v1.html(VOICE_JS, height=100)

    # If voice captured, pre-fill
    voice_default = st.session_state.get("voice_captured", "")

    journal_text = st.text_area(
        label="তোমার লেখা",
        value=voice_default,
        placeholder=T("stage4_placeholder"),
        height=180,
        max_chars=600,
        label_visibility="collapsed"
    )

    word_count = len(journal_text.split()) if journal_text.strip() else 0
    if word_count > 0:
        st.markdown(f"<p style='font-size:0.75rem;color:#9B9B9B;text-align:right;'>{word_count} {T('words')}</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if st.button(T("see_report"), type="primary", use_container_width=True):
            if journal_text.strip():
                nlp_scores   = analyze_journal(journal_text)
                gemini_scores= analyze_journal_gemini(journal_text, prior_signals=st.session_state.condition_scores)
                for cond, val in gemini_scores.items():
                    if cond in nlp_scores:
                        nlp_scores[cond] = (nlp_scores[cond] * 0.4) + (val * 0.6)
                    else:
                        nlp_scores[cond] = val
                for cond, val in nlp_scores.items():
                    if cond in st.session_state.condition_scores:
                        st.session_state.condition_scores[cond] += val
            st.session_state.page = "result"
            st.rerun()

    st.markdown(f"<p style='font-size:0.75rem;color:#B0A898;text-align:center;margin-top:0.5rem;'>{T('stage4_skip')}</p>", unsafe_allow_html=True)


def get_level(score: float):
    if score < 2.0:
        return "low", "#2C5F4A", "🟢", T("low")
    elif score < 4.0:
        return "medium", "#B8956A", "🟡", T("medium")
    else:
        return "high", "#C0392B", "🔴", T("high")


def page_result_main():
    render_lang_toggle()

    condition_scores = st.session_state.condition_scores

    st.markdown(f"""
    <div class="report-header">
        <div class="report-name">{T("report_title")}</div>
        <div class="report-sub">{T("report_sub")}</div>
    </div>
    """, unsafe_allow_html=True)

    scored = {k: v for k, v in condition_scores.items() if v > 0}
    top5   = sorted(scored.items(), key=lambda x: x[1], reverse=True)[:5]

    if not top5:
        st.markdown(f"""
        <div class="positive-box" style="text-align:center;padding:2rem;">
            {T("report_none")}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='color:#6B6B6B;font-size:0.85rem;margin:0.5rem 0 1rem;'>{T('report_found')}</p>", unsafe_allow_html=True)

        highest_cond = top5[0][0]

        for cond, score in top5:
            level, color, emoji, label = get_level(score)
            label_en  = CONDITION_LABELS.get(cond, cond)
            pct       = min(int((score / 6.0) * 100), 100)
            pos_title, pos_msg = POSITIVE_REFRAME.get(cond, ("", ""))

            st.markdown(f"""
            <div class="condition-card {level}">
                <div class="cond-top">
                    <span class="cond-name">{emoji} {label_en}</span>
                    <span class="cond-badge {level}">{label}</span>
                </div>
                <div class="meter-track">
                    <div class="meter-fill" style="width:{pct}%;background:{color};"></div>
                </div>
                <div class="might-have">{T("might_have")}</div>
                <div class="positive-box">
                    💚 <strong>{pos_title}</strong> — {pos_msg}
                </div>
            </div>
            """, unsafe_allow_html=True)

        suggestion = SUGGESTIONS.get(highest_cond, "আজকে নিজের জন্য একটু সময় রাখো।")
        st.markdown(f"""
        <div class="suggestion-box">
            <div class="suggestion-title">{T("today_step")}</div>
            <div class="suggestion-text">{suggestion}</div>
        </div>
        """, unsafe_allow_html=True)

        high_conditions = [c for c, s in top5 if s >= 4.0]
        critical = {"depression", "grief", "rage_suppression", "dissociation"}
        if any(c in critical for c in high_conditions):
            st.markdown(f"""
            <div class="helpline-box">{T("helpline")}</div>
            """, unsafe_allow_html=True)

        # ── SHARE REPORT ──
        st.markdown("---")
        encoded = encode_scores(condition_scores)
        base_url = "https://your-ayna-app.streamlit.app"  # Replace with actual URL
        share_url = f"{base_url}?r={encoded}"

        st.markdown(f"""
        <div class="share-box">
            <strong>{T("share")}</strong><br>
            <span style="font-size:12px;">{T("share_note")}</span>
            <div class="share-link">{share_url}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="disclaimer">{T("disclaimer")}</div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if st.button(T("restart"), type="primary", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.query_params.clear()
            st.rerun()


# ══════════════════════════════════════════════════════════════════
# NLP ANALYSIS
# ══════════════════════════════════════════════════════════════════
def analyze_journal_gemini(text: str, prior_signals: dict = None) -> dict:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        prior_context = ""
        if prior_signals:
            top_prior = sorted(prior_signals.items(), key=lambda x: x[1], reverse=True)[:3]
            prior_context = f"Earlier stages already detected these signals: {dict(top_prior)}. Use this as context but analyze the journal independently."

        prompt = f"""You are analyzing a short personal journal entry from a Bangladeshi woman (18-40) for emotional pattern signals. The text may be Bengali script or Banglish (romanized Bengali like "ami onek thakte parina" = I can't take it anymore).

{prior_context}

SCORING RULES:
- Score 0.5 = mild hint of this pattern
- Score 1.0 = moderate, fairly clear signal
- Score 1.5 = strong, prominent signal
- Only score conditions that have CLEAR textual evidence
- Do not over-diagnose — if unsure, do not include

VALID CONDITIONS (only use these exact keys):
anxiety, burnout, emotional_exhaustion, loneliness, chronic_stress, emotional_suppression, low_self_worth, caregiver_fatigue, social_withdrawal, emotional_numbness, depression, identity_loss, hypervigilance, perfectionism_anxiety, imposter_syndrome, emotional_dependency, grief, rage_suppression, decision_fatigue, dissociation

Journal entry: "{text}"

Return ONLY a valid JSON object. No explanation, no markdown, no extra text.
Example: {{"depression": 1.0, "anxiety": 0.5}}
If nothing clear detected: {{}}"""

        response = model.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r'```(?:json)?', '', raw).strip().strip('`')

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r'\{[^{}]*\}', raw)
            result = json.loads(match.group()) if match else {}

        valid = {}
        for k, v in result.items():
            if k in CONDITIONS and isinstance(v, (int, float)):
                valid[k] = max(0.0, min(2.0, float(v)))
        return valid

    except Exception as e:
        return {}


def analyze_journal(text: str) -> dict:
    if not text or len(text.strip()) < 5:
        return {}

    words = text.split()
    total = max(len(words), 1)
    scores = {}

    hedge_count = sum(1 for h in HEDGING if h in text)
    abs_count   = sum(1 for a in ABSOLUTIST if a in text)
    neg_count   = sum(1 for n in NEGATIVE_WORDS if n in text)
    fp_count    = sum(1 for w in words if w in FIRST_PERSON)
    pos_count   = sum(1 for p in POSITIVE_WORDS if p in text)

    sentences    = [s.strip() for s in re.split(r'[।.!?]', text) if s.strip()]
    avg_sent_len = total / max(len(sentences), 1)

    if hedge_count >= 3:
        scores["anxiety"] = scores.get("anxiety", 0) + 1.5
        scores["emotional_suppression"] = scores.get("emotional_suppression", 0) + 1.0
    elif hedge_count >= 1:
        scores["anxiety"] = scores.get("anxiety", 0) + 0.5

    if abs_count >= 2:
        scores["depression"] = scores.get("depression", 0) + 1.5
        scores["anxiety"]    = scores.get("anxiety", 0) + 1.0
    elif abs_count == 1:
        scores["depression"] = scores.get("depression", 0) + 0.5

    if neg_count >= 3:
        scores["depression"]           = scores.get("depression", 0) + 1.5
        scores["emotional_exhaustion"] = scores.get("emotional_exhaustion", 0) + 1.0
    elif neg_count >= 1:
        scores["depression"] = scores.get("depression", 0) + 0.5

    fp_ratio = fp_count / total
    if fp_ratio > 0.15:
        scores["depression"] = scores.get("depression", 0) + 1.0

    if avg_sent_len < 4:
        scores["emotional_numbness"] = scores.get("emotional_numbness", 0) + 1.0

    if total < 10:
        scores["social_withdrawal"] = scores.get("social_withdrawal", 0) + 1.0

    if pos_count >= 2:
        for k in scores:
            scores[k] = max(0, scores[k] - 0.5)

    return scores


# ══════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════
PAGE_MAP = {
    "home":   page_home,
    "stage1": page_stage1,
    "stage2": page_stage2,
    "stage3": page_stage3,
    "stage4": page_stage4,
    "result": page_result_main,
}
PAGE_MAP.get(st.session_state.page, page_home)()
