import streamlit as st
import math
import os
from datetime import datetime
from fpdf import FPDF

# 1. 語言字典 (UI 優化文字)
LANG = {
    'en': {
        'title': "Live Platform - Overseas Quotation",
        'settings': "Global Settings",
        'discount_label': "Apply Discount (%)",
        'input_title': "1. Requirement Specifications",
        'ac_section': "ACCESS CONTROL SYSTEM",
        'card_readers': "Card Readers (Qty)",
        'input_points': "Input Points (Qty)",
        'output_points': "Output Points (Qty)",
        'face_panels': "Face Recognition Readers (Qty)",
        'hw_type': "Hardware System Type",
        'mercury_model': "Mercury Model",
        'has_main': "Customer has Main Controller",
        'cctv_section': "CCTV SYSTEM",
        'ip_cameras': "IP Cameras (Qty)",
        'has_3rd_nvr': "Has 3rd Party NVR",
        'plat_section': "PLATFORM SETTINGS",
        'desktop': "Desktop Clients",
        'web': "Web Clients",
        'badging': "Badging Software",
        'badging_clients': "Badging Clients (Qty)",
        'has_server': "Customer has Server License",
        'has_face_func': "Face Recognition Function",
        'has_ibox': "Intelligent Box (LV-HW-ACSE)",
        'result_title': "2. Quotation Summary (USD)",
        'hw_header': "HARDWARE LIST",
        'sw_header': "SOFTWARE LICENSES",
        'raw_total': "Subtotal",
        'final_total': "Final Price",
        'export_pdf': "Download Official PDF"
    },
    'zh': {
        'title': "Live Platform - 海外報價系統",
        'settings': "全局設定",
        'discount_label': "套用折扣 (%)",
        'input_title': "1. 輸入需求規格",
        'ac_section': "門禁控制系統",
        'card_readers': "Card Readers 數量",
        'input_points': "Input Points 數量",
        'output_points': "Output Points 數量",
        'face_panels': "人臉辨識面板機數量",
        'hw_type': "硬件系統類型",
        'mercury_model': "Mercury 型號",
        'has_main': "客戶已擁有主控制器",
        'cctv_section': "監控系統",
        'ip_cameras': "IP Cameras 數量",
        'has_3rd_nvr': "使用第三方 NVR",
        'plat_section': "平台設定",
        'desktop': "Desktop 客戶端",
        'web': "Web 客戶端",
        'badging': "制證軟件 (Badging)",
        'badging_clients': "制證客戶端數量",
        'has_server': "客戶已擁有 Server 授權",
        'has_face_func': "開啟人臉識別功能",
        'has_ibox': "智能管理盒子 (LV-HW-ACSE)",
        'result_title': "2. 報價匯總 (美金 USD)",
        'hw_header': "硬體設備清單",
        'sw_header': "軟體授權清單",
        'raw_total': "原始總計",
        'final_total': "折實總價",
        'export_pdf': "下載正式 PDF 報價單"
    }
}

# 2. 數據庫
IBOX_PRICE = 1500.00 
MAIN_CONTROLLERS = {
    "MP4502": {"en": "MP4502 Main Controller", "zh": "MP4502 主控制器", "p": 3937.50, "note_en": "Pure Processor", "note_zh": "中央處理器"},
    "MP1502": {"en": "MP1502 Main Controller", "zh": "MP1502 主控制器", "p": 2812.50, "note_en": "Pure Processor", "note_zh": "中央處理器"},
    "MP2500": {"en": "MP2500 Main Controller", "zh": "MP2500 主控制器", "p": 2887.50, "note_en": "Pure Processor", "note_zh": "中央處理器"},
    "X1100A": {"en": "X1100A Main Controller", "zh": "X1100A 主控制器", "p": 750.00, "note_en": "Aero Main", "note_zh": "Aero 主控"},
}
EXP_MODS = {
    "MR52-S3": {"en": "MR52-S3 Module", "zh": "MR52-S3 擴充板", "p": 1612.50, "r": 2, "note_en": "Wiegand 2-RD", "note_zh": "2隻讀卡器"},
    "X100A": {"en": "X100A Reader Module", "zh": "X100A 讀卡模組", "p": 412.50, "r": 2, "note_en": "Wiegand 2-RD", "note_zh": "2隻讀卡器"},
    "MR16IN": {"en": "MR16IN Module", "zh": "MR16IN 輸入板", "p": 1650.00, "note_zh": "16路輸入"},
    "MR16OUT": {"en": "MR16OUT Module", "zh": "MR16OUT 輸出板", "p": 1650.00, "note_zh": "16路輸出"},
    "X200A": {"en": "X200A Module", "zh": "X200A 輸入板", "p": 425.00, "note_zh": "16路輸入"},
    "X300A": {"en": "X300A Module", "zh": "X300A 輸出板", "p": 500.00, "note_zh": "12路輸出"},
}
LICENSES_INFO = {
    "LV-SWS-AC": {"en": "Base Platform", "zh": "基礎平台授權", "p": 937.50, "note_zh": "含 10Web/1Desktop"},
    "LV-SWI-RD8": {"en": "8-Reader License", "zh": "8門門禁授權", "p": 300.00, "note_zh": "每 8 讀卡器/組"},
    "LV-SWC-ACD": {"en": "Extra Desktop", "zh": "額外 Desktop", "p": 187.50, "note_zh": "按工作站"},
    "LV-SWC-ACW": {"en": "Extra Web (10-set)", "zh": "額外 Web 組", "p": 375.00, "note_zh": "10併發用戶"},
    "LV-SWI-CV": {"en": "CCTV Channel", "zh": "CCTV 頻道授權", "p": 37.50, "note_zh": "單路 IP Cam"},
    "LV-SWI-VMS": {"en": "3rd Party VMS", "zh": "第三方 NVR 整合", "p": 937.50, "note_zh": "海康/大華等"},
    "LV-SWI-FRT": {"en": "Face Recog Base", "zh": "人臉識別基礎", "p": 937.50, "note_zh": "系統功能"},
    "LV-SWI-FRD": {"en": "Face Panel Link", "zh": "人臉面板機接入", "p": 37.50, "note_zh": "按台計費"},
    "LV-SWS-ID": {"en": "Badging Software", "zh": "制證系統授權", "p": 937.50, "note_zh": "證卡設計"},
    "LV-SWC-ID": {"en": "Badging Client", "zh": "制證客戶端", "p": 187.50, "note_zh": "按工作站"},
}

# 3. 計算邏輯
def calculate_all(L):
    hw_items, sw_items = [], []
    if st.session_state.has_ibox:
        hw_items.append({"n": "LV-HW-ACSE Intelligent Box", "q": 1, "p": IBOX_PRICE, "note": "Embedded Server (8RD/1DT/10Web)"})

    if st.session_state.system != "None":
        m_key = st.session_state.m_model if st.session_state.system == "Mercury" else "X1100A"
        m_info = MAIN_CONTROLLERS[m_key]
        exp = EXP_MODS["MR52-S3"] if st.session_state.system == "Mercury" else EXP_MODS["X100A"]
        
        r_qty = math.ceil(st.session_state.readers / exp["r"]) if st.session_state.readers > 0 else 0
        i_mod = EXP_MODS["MR16IN"] if st.session_state.system == "Mercury" else EXP_MODS["X200A"]
        o_mod = EXP_MODS["MR16OUT"] if st.session_state.system == "Mercury" else EXP_MODS["X300A"]
        i_qty = math.ceil(st.session_state.inputs / 16) if st.session_state.inputs > 0 else 0
        o_div = 16 if st.session_state.system == "Mercury" else 12
        o_qty = math.ceil(st.session_state.outputs / o_div) if st.session_state.outputs > 0 else 0

        if not st.session_state.has_main:
            num_main = math.ceil(st.session_state.readers / 64) if st.session_state.readers > 64 else 1
            hw_items.append({"n": m_info[L], "q": num_main, "p": m_info["p"], "note": m_info[f"note_{L}"]})
        if r_qty > 0: hw_items.append({"n": exp[L], "q": r_qty, "p": exp["p"], "note": exp[f"note_{L}"]})
        if i_qty > 0: hw_items.append({"n": i_mod[L], "q": i_qty, "p": i_mod["p"], "note": i_mod.get(f"note_{L}", "16IN")})
        if o_qty > 0: hw_items.append({"n": o_mod[L], "q": o_qty, "p": o_mod["p"], "note": o_mod.get(f"note_{L}", "OUT Module")})

    def add_sw(key, qty):
        if qty > 0:
            info = LICENSES_INFO[key]
            sw_items.append({"n": f"{info[L]} ({key})", "q": qty, "p": info["p"], "note": info.get(f"note_{L}", "")})

    if not st.session_state.has_ibox and not st.session_state.has_server and (st.session_state.readers > 0 or st.session_state.face_panels > 0):
        add_sw("LV-SWS-AC", 1)
    if st.session_state.readers > 0: add_sw("LV-SWI-RD8", math.ceil(st.session_state.readers/8))
    add_sw("LV-SWC-ACD", max(0, st.session_state.desktop - 1))
    add_sw("LV-SWC-ACW", math.ceil(max(0, st.session_state.web - 10)/10))
    add_sw("LV-SWI-CV", st.session_state.ipc)
    if st.session_state.has_3rd: add_sw("LV-SWI-VMS", 1)
    if st.session_state.has_face: add_sw("LV-SWI-FRT", 1)
    add_sw("LV-SWI-FRD", st.session_state.face_panels)
    if st.session_state.has_badging: add_sw("LV-SWS-ID", 1)
    add_sw("LV-SWC-ID", st.session_state.badging_clients)

    total = sum(i['q']*i['p'] for i in hw_items) + sum(i['q']*i['p'] for i in sw_items)
    return hw_items, sw_items, total

# 4. 主介面
def main():
    st.set_page_config(layout="wide", page_title="Live Quotation Tool", page_icon="🏢")

    # --- Sidebar Settings ---
    with st.sidebar:
        # LOGO 放置位置
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            st.title("🏢 COMPANY LOGO")
        
        st.divider()
        st.subheader("⚙️ " + "Global Settings")
        st.radio("Language / 語言", ["中文", "English"], key="lang_radio", horizontal=True)
        L = 'zh' if st.session_state.lang_radio == "中文" else 'en'
        
        discount = st.slider(LANG[L]['discount_label'], 0, 50, 0, 5)
        st.caption("Pricing in USD")

    # --- Main Header ---
    st.title(f"📊 {LANG[L]['title']}")
    st.divider()

    col_in, col_out = st.columns([1, 1.4], gap="large")

    with col_in:
        st.subheader(f"📝 {LANG[L]['input_title']}")
        with st.expander(LANG[L]['ac_section'], expanded=True):
            st.number_input(LANG[L]['card_readers'], 0, key="readers")
            st.number_input(LANG[L]['face_panels'], 0, key="face_panels")
            st.selectbox(LANG[L]['hw_type'], ["Mercury", "Aero", "None"], key="system")
            if st.session_state.system == "Mercury":
                st.selectbox(LANG[L]['mercury_model'], ["MP1502", "MP2500", "MP4502"], key="m_model")
            st.checkbox(LANG[L]['has_main'], key="has_main")
            st.number_input(LANG[L]['input_points'], 0, key="inputs")
            st.number_input(LANG[L]['output_points'], 0, key="outputs")
        
        with st.expander(LANG[L]['plat_section'], expanded=True):
            st.checkbox(LANG[L]['has_ibox'], key="has_ibox")
            st.checkbox(LANG[L]['has_server'], key="has_server")
            st.number_input(LANG[L]['desktop'], 1, key="desktop")
            st.number_input(LANG[L]['web'], 10, key="web")
            st.checkbox(LANG[L]['has_face_func'], key="has_face")
            st.checkbox(LANG[L]['badging'], key="has_badging")
            st.number_input(LANG[L]['badging_clients'], 0, key="badging_clients")

        with st.expander(LANG[L]['cctv_section'], expanded=False):
            st.number_input(LANG[L]['ip_cameras'], 0, key="ipc")
            st.checkbox(LANG[L]['has_3rd_nvr'], key="has_3rd")

    # 計算
    hw, sw, raw_total = calculate_all(L)
    final_total = raw_total * (1 - discount/100)

    with col_out:
        st.subheader(f"💰 {LANG[L]['result_title']}")
        
        # 指標卡片 (Metric)
        m1, m2, m3 = st.columns(3)
        m1.metric(LANG[L]['raw_total'], f"${raw_total:,.2f}")
        m2.metric("Discount", f"{discount}%")
        m3.metric(LANG[L]['final_total'], f"${final_total:,.2f}", delta=f"{(final_total-raw_total):,.2f} USD")

        res_col1, res_col2 = st.columns(2)
        with res_col1:
            with st.container(border=True):
                st.markdown(f"**🛠️ {LANG[L]['hw_header']}**")
                if not hw: st.caption("No Hardware Recommended")
                for i, item in enumerate(hw):
                    color = "#FF4B4B" if i == 0 else "#2E86C1"
                    st.markdown(f"<small><span style='color:{color}'>● {item['q']} x {item['n']}</span></small>", unsafe_allow_html=True)
                    st.caption(f"Subtotal: ${item['q']*item['p']:,.2f}")
        
        with res_col2:
            with st.container(border=True):
                st.markdown(f"**🔑 {LANG[L]['sw_header']}**")
                if not sw: st.caption("No Licenses Required")
                for item in sw:
                    st.markdown(f"<small>● {item['q']} x {item['n']}</small>", unsafe_allow_html=True)
                    st.caption(f"Subtotal: ${item['q']*item['p']:,.2f}")
        
        st.divider()
        if st.button(f"📥 {LANG[L]['export_pdf']}", use_container_width=True, type="primary"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "OFFICIAL QUOTATION (USD)", ln=True, align='C')
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='R')
            pdf.ln(10)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(90, 10, "Description", 1); pdf.cell(15, 10, "Qty", 1); pdf.cell(35, 10, "Price", 1); pdf.cell(35, 10, "Subtotal", 1, ln=True)
            pdf.set_font("Helvetica", "", 9)
            for item in hw + sw:
                name = str(item['n']).encode('ascii', 'ignore').decode('ascii')
                pdf.cell(90, 8, name, 1); pdf.cell(15, 8, str(item['q']), 1); pdf.cell(35, 8, f"{item['p']:,.2f}", 1); pdf.cell(35, 8, f"{item['q']*item['p']:,.2f}", 1, ln=True)
            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(105, 10, "", 0); pdf.cell(35, 10, "GRAND TOTAL", 1); pdf.cell(35, 10, f"${final_total:,.2f}", 1)
            
            st.download_button("Click to Confirm Download", data=bytes(pdf.output()), file_name="Live_Quote.pdf", mime="application/pdf", use_container_width=True)

if __name__ == "__main__":
    main()
