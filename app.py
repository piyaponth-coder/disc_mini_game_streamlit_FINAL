
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random, io, os

st.set_page_config(page_title="DiSC – What Cat Are You!!", page_icon="🐱", layout="wide")

# ================= Settings =================
COMBO_THRESHOLD = st.sidebar.slider("Combo threshold (points)", min_value=1, max_value=6, value=3, help="Use a combo cat if the top-2 styles differ by this many points or less.")
lang = st.sidebar.radio("Language / ภาษา", ["EN","TH"], index=1)
st.sidebar.caption("Toggle language here. Questions, UI, and poster will switch.")
# ============================================

# ---------- Data (EN + TH casual) -----------
# Each statement is (EN, STYLE, TH)
WORKPLACE = [
    [("I take initiative in projects.", "D", "ฉันชอบเป็นคนเริ่มต้นโปรเจกต์ก่อน"),
     ("I enjoy networking events.", "I", "ฉันชอบเข้าสังคม/คุยรู้จักคนใหม่ๆ"),
     ("I support coworkers consistently.", "S", "ฉันคอยช่วยและซัพพอร์ตเพื่อนร่วมงานเสมอ"),
     ("I focus on policies and compliance.", "C", "ฉันใส่ใจนโยบายและทำตามกฎเป๊ะๆ")],
    [("I am competitive about results.", "D", "ฉันจริงจังกับผลลัพธ์และชอบแข่งขัน"),
     ("I bring energy to the team.", "I", "ฉันชอบสร้างพลังบวกให้ทีม"),
     ("I value loyalty in coworkers.", "S", "ฉันให้ค่ากับความซื่อสัตย์และไว้ใจกัน"),
     ("I rely on facts before decisions.", "C", "ฉันต้องมีข้อมูลชัดๆ ก่อนตัดสินใจ")],
    [("I set ambitious targets.", "D", "ฉันตั้งเป้าที่ท้าทายไว้เสมอ"),
     ("I like recognition for my enthusiasm.", "I", "ฉันชอบถูกชมเวลามีพลังและกระตือรือร้น"),
     ("I maintain long-term stability.", "S", "ฉันรักษาความนิ่งและความเสถียรในระยะยาว"),
     ("I want tasks done perfectly.", "C", "ฉันอยากให้งานออกมาสมบูรณ์แบบ")],
    [("I argue for my ideas strongly.", "D", "ฉันกล้าดันไอเดียของตัวเองแบบตรงๆ"),
     ("I enjoy persuading others.", "I", "ฉันสนุกกับการชวน/โน้มน้าวคนอื่น"),
     ("I avoid workplace conflict.", "S", "ฉันพยายามเลี่ยงความขัดแย้งในที่ทำงาน"),
     ("I double-check data accuracy.", "C", "ฉันเช็กความถูกต้องของข้อมูลซ้ำเสมอ")],
    [("I like to control outcomes.", "D", "ฉันอยากคุมผลลัพธ์ได้ด้วยตัวเอง"),
     ("I enjoy team celebrations.", "I", "ฉันชอบกิจกรรมทีม/ฉลองความสำเร็จ"),
     ("I prefer predictable workflows.", "S", "ฉันชอบงานที่คาดเดาได้เป็นขั้นเป็นตอน"),
     ("I analyze risks before acting.", "C", "ฉันวิเคราะห์ความเสี่ยงก่อนลงมือทำ")],
    [("I move fast when deadlines are tight.", "D", "ฉันเร่งเครื่องได้ดีเมื่อเดดไลน์ใกล้"),
     ("I am optimistic with coworkers.", "I", "ฉันมองบวกกับคนรอบข้าง"),
     ("I stay calm under pressure.", "S", "ฉันใจเย็นแม้เจอแรงกดดัน"),
     ("I carefully plan before action.", "C", "ฉันวางแผนอย่างละเอียดก่อนลงมือ")],
    [("I challenge colleagues directly.", "D", "ฉันท้าทาย/คุยตรงกับเพื่อนได้"),
     ("I build relationships easily.", "I", "ฉันคุยง่าย สนิทกับคนได้ไม่ยาก"),
     ("I am seen as reliable.", "S", "คนมักมองว่าฉันไว้ใจได้"),
     ("I rely on procedures.", "C", "ฉันทำงานตามขั้นตอน/วิธีการอย่างเคร่งครัด")],
    [("I want to be a leader.", "D", "ฉันอยากเป็นผู้นำ"),
     ("I thrive in group brainstorming.", "I", "ฉันสนุกกับการระดมไอเดียเป็นทีม"),
     ("I prefer steady routines.", "S", "ฉันชอบรูทีนที่ชัดเจน"),
     ("I prefer step-by-step methods.", "C", "ฉันชอบงานที่มีวิธีการทีละสเต็ป")],
    [("I like taking bold decisions.", "D", "ฉันตัดสินใจเด็ดขาดได้"),
     ("I love being expressive at work.", "I", "ฉันชอบแสดงออก/แชร์ความคิด"),
     ("I ensure others feel comfortable.", "S", "ฉันพยายามให้ทุกคนรู้สึกสบายใจ"),
     ("I like systematic problem-solving.", "C", "ฉันชอบแก้ปัญหาแบบเป็นระบบ")],
    [("I focus on achieving results fast.", "D", "ฉันโฟกัสให้ได้ผลลัพธ์ไว"),
     ("I inspire coworkers with my energy.", "I", "ฉันสร้างแรงบันดาลใจด้วยพลังบวก"),
     ("I prefer peace and balance.", "S", "ฉันชอบบรรยากาศสงบๆ สมดุล"),
     ("I organize tasks carefully.", "C", "ฉันจัดระเบียบงานอย่างเรียบร้อย")],
    [("I compete for promotions.", "D", "ฉันตั้งใจแข่งเพื่อก้าวหน้า"),
     ("I enjoy motivating people.", "I", "ฉันชอบปลุกพลังให้คนอื่น"),
     ("I patiently help teammates.", "S", "ฉันช่วยเหลือทีมด้วยความอดทน"),
     ("I value accuracy in reporting.", "C", "ฉันเน้นความแม่นยำของรายงาน")],
    [("I thrive on challenges.", "D", "ฉันสนุกกับความท้าทาย"),
     ("I talk positively to encourage others.", "I", "ฉันพูดให้กำลังใจแบบบวกๆ"),
     ("I stay loyal to leaders.", "S", "ฉันซื่อสัตย์และสนับสนุนหัวหน้า"),
     ("I ensure compliance with standards.", "C", "ฉันยึดมาตรฐาน/ข้อกำหนดอย่างเคร่งครัด")]
]

NORMAL_LIFE = [
    [("I like making decisions for the group.", "D", "ฉันชอบเป็นคนตัดสินใจให้กลุ่ม"),
     ("I am outgoing with friends.", "I", "ฉันเฟรนด์ลี่กับเพื่อนๆ"),
     ("I enjoy predictable routines.", "S", "ฉันชอบกิจวัตรที่คาดเดาได้"),
     ("I keep track of small details.", "C", "ฉันใส่ใจรายละเอียดเล็กๆ น้อยๆ")],
    [("I dislike delays.", "D", "ฉันไม่ชอบอะไรช้าๆ/ล่าช้า"),
     ("I tell stories often.", "I", "ฉันชอบเล่าเรื่อง/แชร์ประสบการณ์"),
     ("I avoid arguments.", "S", "ฉันเลี่ยงการทะเลาะ"),
     ("I prefer structured plans.", "C", "ฉันชอบแผนที่เป็นระเบียบชัดเจน")],
    [("I insist on my point in discussions.", "D", "ฉันยืนยันความคิดของตัวเองเวลาถกเถียง"),
     ("I like entertaining others.", "I", "ฉันชอบเอนเตอร์เทน/ทำให้คนรอบข้างสนุก"),
     ("I value harmony.", "S", "ฉันรักความกลมกลืน/ไม่แตกแยก"),
     ("I want fairness in everything.", "C", "ฉันอยากให้ทุกอย่างยุติธรรม")],
    [("I love competition in games.", "D", "ฉันชอบความท้าทายในเกม/กิจกรรม"),
     ("I like to be noticed.", "I", "ฉันชอบเป็นที่สังเกตบ้าง"),
     ("I am steady and dependable.", "S", "ฉันนิ่ง มั่นคง ไว้ใจได้"),
     ("I point out rules.", "C", "ฉันชี้ชัดเรื่องกติกา/กฎ")],
    [("I make decisions quickly.", "D", "ฉันตัดสินใจเร็ว"),
     ("I am spontaneous.", "I", "ฉันค่อนข้างเป็นคน spontaneous/ตามใจฉัน"),
     ("I prefer traditions.", "S", "ฉันชอบทำอะไรแบบเดิมที่คุ้นเคย"),
     ("I track details carefully.", "C", "ฉันตามรายละเอียดอย่างระมัดระวัง")],
    [("I like control of situations.", "D", "ฉันชอบคุมสถานการณ์"),
     ("I talk easily to strangers.", "I", "ฉันคุยกับคนแปลกหน้าได้สบาย"),
     ("I am reliable to friends.", "S", "เพื่อนๆ ไว้ใจฉันได้"),
     ("I want things correct.", "C", "ฉันอยากให้ทุกอย่างถูกต้องเป๊ะ")],
    [("I enjoy being in charge.", "D", "ฉันชอบได้เป็นคนดูแล/คุมงาน"),
     ("I am cheerful with others.", "I", "ฉันร่าเริงกับคนรอบๆ"),
     ("I provide emotional support.", "S", "ฉันคอยซัพพอร์ตด้านใจให้คนอื่น"),
     ("I like structure in life.", "C", "ฉันชอบชีวิตที่เป็นระเบียบโครงสร้างชัด")],
    [("I focus on winning.", "D", "ฉันโฟกัสที่การชนะ/ทำให้สำเร็จ"),
     ("I spread positivity.", "I", "ฉันชอบกระจายพลังบวก"),
     ("I build peace around me.", "S", "ฉันพยายามทำให้บรรยากาศสงบ"),
     ("I organize my money well.", "C", "ฉันจัดการเงินเป็นระบบดี")],
    [("I speak directly even if blunt.", "D", "ฉันพูดตรง แม้จะดูแรงบ้าง"),
     ("I love sharing experiences.", "I", "ฉันชอบแชร์ประสบการณ์ที่เจอ"),
     ("I stay calm with family.", "S", "ฉันใจเย็นกับครอบครัว"),
     ("I analyze situations logically.", "C", "ฉันวิเคราะห์สถานการณ์แบบมีเหตุผล")],
    [("I like to lead group activities.", "D", "ฉันชอบนำกิจกรรมกลุ่ม"),
     ("I enjoy being the center of fun.", "I", "ฉันชอบเป็นตัวเอนเตอร์เทน"),
     ("I support friends quietly.", "S", "ฉันช่วยเพื่อนแบบเงียบๆ"),
     ("I plan things step by step.", "C", "ฉันวางแผนแบบทีละขั้นตอน")],
    [("I push for my way.", "D", "ฉันผลักดันความคิดของฉันเอง"),
     ("I like being lively.", "I", "ฉันชอบบรรยากาศคึกคัก"),
     ("I try to compromise.", "S", "ฉันพยายามหาทางกลาง"),
     ("I want clarity before acting.", "C", "ฉันต้องชัดเจนก่อนลงมือทำ")],
    [("I want to win arguments.", "D", "ฉันอยากชนะเวลาถกเถียง"),
     ("I enjoy humor and chatting.", "I", "ฉันชอบคุยเล่น/มีมุกตลก"),
     ("I am patient with others.", "S", "ฉันอดทนกับคนอื่นได้ดี"),
     ("I seek accurate information.", "C", "ฉันต้องการข้อมูลที่แม่นยำ")]
]

CRISIS = [
    [("I take charge fast.", "D", "ฉันเข้าคุมสถานการณ์ได้ไว"),
     ("I lift people’s spirits.", "I", "ฉันช่วยยกระดับกำลังใจคนอื่น"),
     ("I stay calm.", "S", "ฉันยังคงนิ่ง/ใจเย็น"),
     ("I focus on facts.", "C", "ฉันยึดข้อเท็จจริงเป็นหลัก")],
    [("I give firm instructions.", "D", "ฉันสั่งการชัดเจนเด็ดขาด"),
     ("I encourage optimism.", "I", "ฉันชวนให้คิดบวก"),
     ("I keep stability.", "S", "ฉันรักษาสถานการณ์ให้คงที่"),
     ("I analyze risks.", "C", "ฉันวิเคราะห์ความเสี่ยง")],
    [("I confront problems head-on.", "D", "ฉันเผชิญปัญหาแบบตรงไปตรงมา"),
     ("I use humor to ease stress.", "I", "ฉันใช้มุก/อารมณ์ขันช่วยลดความเครียด"),
     ("I comfort others.", "S", "ฉันปลอบและคอยอยู่ข้างๆ"),
     ("I check for accurate info.", "C", "ฉันเช็กข้อมูลให้ชัวร์ก่อน")],
    [("I decide quickly.", "D", "ฉันตัดสินใจได้รวดเร็ว"),
     ("I keep talking to reassure.", "I", "ฉันพูดคุยให้คนรู้สึกอุ่นใจ"),
     ("I am patient.", "S", "ฉันอดทน รอได้"),
     ("I follow tested methods.", "C", "ฉันทำตามวิธีที่พิสูจน์แล้วว่าเวิร์ก")],
    [("I push through obstacles.", "D", "ฉันดันงานฝ่าอุปสรรคไปให้ได้"),
     ("I make people cooperate.", "I", "ฉันชวนทุกคนมาช่วยกัน"),
     ("I stay loyal and calm.", "S", "ฉันซื่อสัตย์และนิ่ง"),
     ("I check safety rules.", "C", "ฉันตรวจเรื่องความปลอดภัย/กฎ")],
    [("I control situations even if tough.", "D", "ต่อให้ยาก ฉันก็พยายามคุมอยู่"),
     ("I influence with encouragement.", "I", "ฉันชักชวนด้วยคำให้กำลังใจ"),
     ("I support consistently.", "S", "ฉันซัพพอร์ตอย่างสม่ำเสมอ"),
     ("I take logical steps.", "C", "ฉันเดินตามขั้นตอนอย่างมีเหตุผล")],
    [("I demand fast action.", "D", "ฉันต้องการให้ลงมือเร็ว"),
     ("I talk to reduce fear.", "I", "ฉันใช้การคุยช่วยลดความกลัว"),
     ("I stabilize emotions.", "S", "ฉันประคองอารมณ์ให้คงที่"),
     ("I seek clarity.", "C", "ฉันหาความชัดเจนก่อน")],
    [("I fight to win.", "D", "ฉันลุยเพื่อคว้าชัย"),
     ("I keep people united.", "I", "ฉันทำให้ทุกคนร่วมมือกัน"),
     ("I remain consistent.", "S", "ฉันคงเส้นคงวา"),
     ("I rely on rules.", "C", "ฉันยึดกฎระเบียบ")],
    [("I make bold emergency moves.", "D", "ฉันกล้าตัดสินใจฉุกเฉิน"),
     ("I use energy to inspire hope.", "I", "ฉันใช้พลังบวกสร้างความหวัง"),
     ("I reassure people.", "S", "ฉันทำให้คนรู้สึกมั่นใจขึ้น"),
     ("I check data before acting.", "C", "ฉันตรวจข้อมูลก่อนลงมือ")],
    [("I give orders quickly.", "D", "ฉันสั่งงานได้เร็ว"),
     ("I use stories to motivate.", "I", "ฉันเล่าเรื่องเพื่อกระตุ้นใจ"),
     ("I provide steady support.", "S", "ฉันช่วยเหลืออย่างสม่ำเสมอ"),
     ("I double-check details.", "C", "ฉันเช็กละเอียดอีกรอบ")],
    [("I drive decisions under pressure.", "D", "ฉันผลักดันการตัดสินใจแม้กดดัน"),
     ("I talk positively in crisis.", "I", "ฉันพูดให้กำลังใจในยามวิกฤติ"),
     ("I remain peaceful.", "S", "ฉันรักษาความสงบ"),
     ("I need accurate procedures.", "C", "ฉันต้องการขั้นตอนที่แม่นยำ")],
    [("I push aggressively for solutions.", "D", "ฉันดันไปให้ถึงทางออก"),
     ("I keep morale high.", "I", "ฉันพยายามรักษากำลังใจให้สูง"),
     ("I stay patient under stress.", "S", "ฉันยังคงอดทนแม้เครียด"),
     ("I focus on logical steps.", "C", "ฉันโฟกัสขั้นตอนที่เป็นเหตุเป็นผล")]
]

CONTEXTS = {"Workplace": WORKPLACE, "Normal Life": NORMAL_LIFE, "Crisis": CRISIS}
CONTEXT_TITLES = {"EN":["Workplace","Normal Life","Crisis"], "TH":["ที่ทำงาน","ชีวิตประจำวัน","เวลาเจอวิกฤติ"]}
STYLE_EMOJI = {"D":"🔴","I":"🟠","S":"🟢","C":"🔵"}

BREED_MAP = {
    "D": {"EN":("Bengal","Bold, energetic, decisive."),
          "TH":("แมวเบงกอล","กล้าแสดงออก กระฉับกระเฉง ตัดสินใจไว")},
    "I": {"EN":("Abyssinian","Playful, social, inspiring."),
          "TH":("แมวอะบิสซิเนียน","ร่าเริง ชอบเข้าสังคม สร้างแรงบันดาลใจ")},
    "S": {"EN":("Oriental Shorthair","Calm, peace‑seeking, supportive."),
          "TH":("แมวโอเรียนทัล ชอร์ตแฮร์","ใจเย็น รักความสงบ คอยซัพพอร์ต")},
    "C": {"EN":("British Shorthair","Careful, precise, structured."),
          "TH":("แมวบริติช ชอร์ตแฮร์","ละเอียดรอบคอบ เป๊ะ เป็นระบบ")},
}

COMBO_DESC = {
    "DI": {"EN":"DI cat: bold challenger with social spark.",
           "TH":"DI: กล้าลุยและชอบชวนคนอื่นให้ฮึกเหิม"},
    "DS": {"EN":"DS cat: competitive but steady.",
           "TH":"DS: แข่งได้ แต่ก็ประคองทีมให้นิ่ง"},
    "DC": {"EN":"DC cat: fast with standards.",
           "TH":"DC: เร็ว แต่ยังต้องได้คุณภาพ/มาตรฐาน"},
    "IS": {"EN":"IS cat: lively encourager, harmony builder.",
           "TH":"IS: ร่าเริง คอยเสริมพลัง สร้างบรรยากาศดีๆ"},
    "IC": {"EN":"IC cat: expressive yet detail-aware.",
           "TH":"IC: พูดเก่ง แต่ก็ใส่ใจรายละเอียด"},
    "ID": {"EN":"ID cat: persuasive and daring.",
           "TH":"ID: โน้มน้าวเก่ง กล้าตัดสินใจ"},
    "SC": {"EN":"SC cat: patient organizer, reliable.",
           "TH":"SC: ใจเย็น จัดระบบเก่ง วางใจได้"},
    "SD": {"EN":"SD cat: calm but decisive when needed.",
           "TH":"SD: โดยรวมใจเย็น แต่ถึงเวลาต้องตัดสินใจก็ทำได้"},
    "SI": {"EN":"SI cat: warm, friendly, dependable.",
           "TH":"SI: อบอุ่น เข้ากับคนง่าย และไว้ใจได้"},
    "CD": {"EN":"CD cat: analytical driver—facts first.",
           "TH":"CD: ขับเคลื่อนแบบมีข้อมูล นำด้วยเหตุผล"},
    "CI": {"EN":"CI cat: precise communicator.",
           "TH":"CI: สื่อสารชัดเจน เป๊ะ และสุภาพ"},
    "CS": {"EN":"CS cat: quality guardian—steady & consistent.",
           "TH":"CS: สายคุณภาพ รักษามาตรฐานและความสม่ำเสมอ"},
}

# ---------- Helpers ----------
def shuffled_groups(groups):
    out = []
    for g in groups:
        opts = g[:]
        random.shuffle(opts)
        out.append(opts)
    return out

if "questions" not in st.session_state:
    st.session_state.questions = {k: shuffled_groups(v) for k,v in CONTEXTS.items()}
if "answers" not in st.session_state:
    st.session_state.answers = {}   # key: (ctx, idx) -> {"M":i,"L":j}
for k in CONTEXTS.keys():
    st.session_state.setdefault(f"{k}_g", 1)

def show_context(ctx_name, label):
    st.subheader(label)
    groups = st.session_state.questions[ctx_name]
    answered = sum(1 for (c,_) in st.session_state.answers if c==ctx_name)
    st.progress(answered/len(groups))
    st.caption(f"{answered}/{len(groups)}")

    # quick jump grid
    cols = st.columns(12)
    for i in range(12):
        if cols[i].button(str(i+1), key=f"{ctx_name}_jump_{i}"):
            st.session_state[f"{ctx_name}_g"] = i+1
            st.rerun()

    gnum = st.session_state[f"{ctx_name}_g"]
    idx = gnum-1
    opts = groups[idx]
    # Show choices with language
    def fmt(opt):
        return opt[0] if lang=="EN" else opt[2]
    st.write("**Pick one _Most (M)_ and one _Least (L)_**" if lang=="EN" else "**เลือก _มากที่สุด (M)_ และ _น้อยที่สุด (L)_ อย่างละ 1**")
    for i,opt in enumerate(opts):
        st.write(f"{i+1}. {fmt(opt)}")

    key = (ctx_name, idx)
    prev = st.session_state.answers.get(key, {"M":0,"L":1})
    m_sel = st.radio("Most (M)" if lang=="EN" else "มากที่สุด (M)",
                     list(range(4)), index=prev.get("M",0),
                     format_func=lambda i: f"Option {i+1}", key=f"{ctx_name}_M_{idx}")
    l_candidates = [i for i in range(4) if i!=m_sel]
    l_default = prev.get("L", l_candidates[0])
    if l_default == m_sel or l_default not in l_candidates:
        l_default = l_candidates[0]
    l_idx = l_candidates.index(l_default)
    l_sel = st.radio("Least (L)" if lang=="EN" else "น้อยที่สุด (L)",
                     l_candidates, index=l_idx,
                     format_func=lambda i: f"Option {i+1}", key=f"{ctx_name}_L_{idx}")
    st.session_state.answers[key] = {"M":m_sel,"L":l_sel}
    st.caption("Auto-saved ✅" if lang=="EN" else "บันทึกอัตโนมัติแล้ว ✅")

    c1,c2 = st.columns(2)
    if c1.button("⟵ Prev"):
        if gnum>1:
            st.session_state[f"{ctx_name}_g"] -= 1; st.rerun()
    if c2.button("Next ⟶"):
        if gnum<12:
            st.session_state[f"{ctx_name}_g"] += 1; st.rerun()

def compute_scores():
    nets = {ctx: {"D":0,"I":0,"S":0,"C":0} for ctx in CONTEXTS}
    per = {ctx: {"D":{"M":0,"L":0},"I":{"M":0,"L":0},"S":{"M":0,"L":0},"C":{"M":0,"L":0}} for ctx in CONTEXTS}
    for (ctx, idx), choice in st.session_state.answers.items():
        opts = st.session_state.questions[ctx][idx]
        m_style = opts[choice["M"]][1]; l_style = opts[choice["L"]][1]
        per[ctx][m_style]["M"] += 1; per[ctx][l_style]["L"] += 1
    for ctx in CONTEXTS:
        for k in "DISC":
            nets[ctx][k] = per[ctx][k]["M"] - per[ctx][k]["L"]
    overall = {k: sum(nets[c][k] for c in CONTEXTS) for k in "DISC"}
    return per, nets, overall

def normalize_percent(overall):
    mn = min(overall.values())
    shift = abs(mn)+1 if mn<=0 else 0
    shifted = {k: overall[k]+shift for k in "DISC"}
    s = sum(shifted.values())
    return {k: round(100*shifted[k]/s) for k in "DISC"}

def top_two(overall):
    ordered = sorted(overall.items(), key=lambda x: x[1], reverse=True)
    return ordered[0][0], ordered[1][0], ordered[0][1]-ordered[1][1]

def load_icon(code, size):
    path = f"assets/{code}.png"
    if not os.path.exists(path): return None
    try:
        return Image.open(path).convert("RGBA").resize((size,size), Image.LANCZOS)
    except Exception:
        return None

def icon_for(primary, secondary=None, size=1200):
    # try combo first
    if secondary:
        key = (primary+secondary).lower()
        ic = load_icon(key, size)
        if ic: return ic, key.upper()
    pure_file = {"D":"bengal","I":"abyssinian","S":"oriental","C":"british_shorthair"}[primary]
    ic = load_icon(pure_file, size)
    return ic, primary

def a4_poster(overall, perc, nets, poster_lang="TH"):
    W,H = 2480,3508  # A4 300DPI
    canvas = Image.new("RGBA",(W,H),(247,250,255,255))
    d = ImageDraw.Draw(canvas)
    try:
        title_font = ImageFont.truetype("arial.ttf", 100)
        big_font = ImageFont.truetype("arial.ttf", 60)
        small_font = ImageFont.truetype("arial.ttf", 40)
    except:
        title_font = ImageFont.load_default(); big_font=title_font; small_font=title_font

    title = "DiSC – What Cat Are You!!" if poster_lang=="EN" else "DiSC – คุณเป็นแมวแบบไหน!!"
    d.text((W//2, 140), title, anchor="mm", font=title_font, fill=(50,60,90))

    p1,p2,diff = top_two(overall)
    use_combo = diff <= COMBO_THRESHOLD
    icon, which = icon_for(p1, p2 if use_combo else None, size=1400)
    if icon:
        canvas.alpha_composite(icon, (W//2-700, 360))

    # Bubbles
    color = {"D":(230,70,70), "I":(255,140,60), "S":(60,170,110), "C":(70,120,230)}
    pos = {"I":(W//2, 260), "D":(W//2+540, 980), "C":(W//2-540, 980), "S":(W//2, 1700)}
    for k in "DISC":
        cx,cy = pos[k]; r = 120 if k!="I" else 150
        d.ellipse((cx-r,cy-r,cx+r,cy+r), fill=color[k])
        d.text((cx,cy-22), k, anchor="mm", font=big_font, fill=(255,255,255))
        d.text((cx,cy+24), f"{perc[k]}%", anchor="mm", font=small_font, fill=(255,255,255))

    # Texts
    if len(which)==2:
        code = which
        desc = COMBO_DESC[code][poster_lang]
        title_line = f"Your style: {code} cat" if poster_lang=="EN" else f"สไตล์ของคุณ: {code}"
        b1 = BREED_MAP[code[0]][poster_lang][0]; b2 = BREED_MAP[code[1]][poster_lang][0]
        d.text((W//2, 2050), title_line, anchor="mm", font=big_font, fill=(40,50,90))
        d.text((W//2, 2120), f"({b1} + {b2})", anchor="mm", font=small_font, fill=(90,90,120))
        d.text((W//2, 2190), desc, anchor="mm", font=small_font, fill=(90,90,120))
    else:
        code = which
        breed, bdesc = BREED_MAP[code][poster_lang]
        title_line = f"Your style: {code} → {breed}" if poster_lang=="EN" else f"สไตล์ของคุณ: {code} → {breed}"
        d.text((W//2, 2050), title_line, anchor="mm", font=big_font, fill=(40,50,90))
        d.text((W//2, 2120), bdesc, anchor="mm", font=small_font, fill=(90,90,120))

    labels = CONTEXT_TITLES[poster_lang]
    y = 2320
    for ctx_name, label in zip(["Workplace","Normal Life","Crisis"], labels):
        d.text((240, y), f"{label}:", font=big_font, fill=(50,60,90))
        v = nets[ctx_name]
        d.text((700, y), f"D:{v['D']}  I:{v['I']}  S:{v['S']}  C:{v['C']}", font=big_font, fill=(90,90,120))
        y += 80

    d.text((W//2, H-120), "Educational DiSC-style summary" if poster_lang=="EN" else "สรุปผลแบบ DiSC (เพื่อการเรียนรู้)",
           anchor="mm", font=small_font, fill=(120,120,140))
    return canvas.convert("RGB")

# --------------- UI ---------------
st.title("🐱 DiSC – What Cat Are You!!")
tabs = st.tabs(CONTEXT_TITLES[lang] + (["Results"] if lang=="EN" else ["ผลลัพธ์"]))

show_context("Workplace", CONTEXT_TITLES[lang][0])
show_context("Normal Life", CONTEXT_TITLES[lang][1])
show_context("Crisis", CONTEXT_TITLES[lang][2])

with tabs[3]:
    total = len(st.session_state.answers)
    if total < 36:
        st.warning(f"Progress: {total}/36 – finish all groups to see results." if lang=="EN"
                   else f"ความคืบหน้า: {total}/36 – กรุณาตอบครบทุกกลุ่มก่อนดูผลลัพธ์")
        st.stop()

    per, nets, overall = compute_scores()
    perc = normalize_percent(overall)

    c1,c2,c3,c4 = st.columns(4)
    for c,k in zip([c1,c2,c3,c4],"DISC"):
        c.metric(f"{k} {STYLE_EMOJI[k]}", f"{perc[k]}%")

    poster_lang = st.radio("Poster language" if lang=="EN" else "ภาษาในโปสเตอร์", ["EN","TH"], index=0)
    img = a4_poster(overall, perc, nets, poster_lang=poster_lang)
    buf = io.BytesIO(); img.save(buf, format="PNG")
    st.download_button("🖼️ Download A4 Poster", data=buf.getvalue(), file_name="disc_cat_poster_a4.png", mime="image/png")
    st.image(img, caption="Preview", use_column_width=True)
