import streamlit as st
import math
import os
from datetime import datetime
from fpdf import FPDF

# 1. 語言字典
LANG = {
    'en': {
        'title': "Live Platform - Quotation System",
        'input_title': "Requirement Specifications",
        'ac_section': "Access Control System",
        'load_setting': "Controller Load Strategy",
        'load_16': "Stable (16)",
        'load_32': "Standard (32)",
        'load_64': "Extreme (64)",
        'card_readers': "Card Readers",
        'input_points': "Input Points",
        'output_points': "Output Points",
        'face_panels': "Face Panels",
        'hw_type': "Hardware Type",
        'mercury_model': "Mercury Model",
        'has_main': "Customer has Main Controller",
        'cctv_section': "CCTV System",
        'ip_cameras': "IP Cameras",
        'has_3rd_nvr': "3rd Party NVR",
        'plat_section': "Platform Settings",
        'desktop': "Desktop Clients",
        'web': "Web Clients",
        'badging': "Badging Software",
        'badging_clients': "Badging Clients",
        'has_server': "Customer has Server",
        'has_face_func': "Face Function",
        'has_ibox': "Intelligent Box (iBox)",
        'result_title': "Quotation Summary (USD)",
        'hw_header': "Hardware List",
        'sw_header': "Software Licenses",
        'raw_total': "Grand Total",
        'export_pdf': "Export Official PDF"
    },
    'zh': {
        'title': "Live Platform - 報價系統",
        'input_title': "需求規格",
        'ac_section': "門禁控制系統",
        'load_setting': "主控板負載策略",
        'load_16': "最穩定 (16)",
        'load_32': "標準 (32)",
        'load_64': "極限 (64)",
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
        'badging': "製證軟件 (Badging)",
        'badging_clients': "製證客戶端數量",
        'has_server': "客戶已擁有 Server 授權",
        'has_face_func': "開啟人臉識別功能",
        'has_ibox': "智能管理盒子 (iBox)",
        'result_title': "報價匯總 (USD)",
        'hw_header': "硬體設備清單",
        'sw_header': "軟體授權清單",
        'raw_total': "總價合計",
        'export_pdf': "匯出正式 PDF 報價單"
    }
}

# 2. 數據庫
IBOX_PRICE = 1500.00 
MAIN_CONTROLLERS = {
    "MP4502": {"en": "MP4502 Main Controller", "zh": "MP4502 主控制器", "p": 3937.50},
    "MP1502": {"en": "MP1502 Main Controller", "zh": "MP1502 主控制器", "p": 2812.50},
    "MP2500": {"en": "MP2500 Main Controller", "zh": "MP2500 主控制器", "p": 2887.50},
    "X1100A": {"en": "X1100A Main Controller", "zh": "X1100A 主控制器", "p": 750.00},
}
EXP_MODS = {
    "MR52-S3": {"en": "MR52-S3 Module", "zh": "MR52-S3 擴充板", "p": 1612.50, "r": 2},
    "X100A": {"en": "X100A Reader Module", "zh": "X100A 讀卡模組", "p": 412.50, "r": 2},
    "MR16IN": {"en": "MR16IN Module", "zh": "MR16IN 輸入板", "p": 1650.00},
    "MR16OUT": {"en": "MR16OUT Module", "zh": "MR16OUT 輸出板", "p": 1650.00},
    "X200A": {"en": "X200A Module", "zh": "X200A 輸入板", "p": 425.00},
    "X300A": {"en": "X300A Module", "zh": "X300A 輸出板", "p": 500.00},
}
LICENSES_INFO = {
    "LV-SWS-AC": {"en": "Base Platform", "zh": "基礎平台授權", "p": 937.50},
    "LV-SWI-RD8": {"en": "8-Reader License", "zh": "8門門禁授權", "p": 300.00},
    "LV-SWC-ACD": {"en": "Extra Desktop", "zh": "額外 Desktop", "p": 187.50},
    "LV-SWC-ACW": {"en": "Extra Web (10-set)", "zh": "額外 Web 組", "p": 375.00},
    "LV-SWI-CV": {"en": "CCTV Channel", "zh": "CCTV 頻道授權", "p": 37.50},
    "LV-SWI-VMS": {"en": "3rd Party VMS", "zh": "第三方 NVR 整合", "p": 937.50},
    "LV-SWI-FRT": {"en": "Face Recog Base", "zh": "人臉識別基礎", "p": 937.50},
    "LV-SWI-FRD": {"en": "Face Panel Link", "zh": "人臉面板機接入", "p": 37.50},
    "LV-SWS-ID": {"en": "Badging Software", "zh": "製證系統授權", "p": 937.50},
    "LV-SWC-ID": {"en": "Badging Client", "zh": "製證客戶端", "p": 187.50},
}

# 3. 輔助功能
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("System Login")
        pwd = st.text_input("Password", type="password")
        if st.button("Access"):
            if pwd == "Live2026":
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Access Denied")
        return False
    return True

def calculate_all(L):
    hw_items, sw_items = [], []
    s = st.session_state
    base_readers, base_desktop, base_web = 0, 0, 0
    
    # 讀取負載標準
    load_map = {"Stable": 16, "Standard": 32, "Extreme": 64}
    max_load = load_map.get(s.get('load_strategy', "Standard"), 32)
    
    if s.get('has_ibox', False):
        hw_items.append({"n": "LV-HW-ACSE iBox", "q": 1, "p": IBOX_PRICE})
        base_readers, base_desktop, base_web = 8, 1, 10

    current_system = s.get('system', "None")
    if current_system != "None":
        m_key = s.get('m_model', "MP4502") if current_system == "Mercury" else "X1100A"
        m_info = MAIN_CONTROLLERS[m_key]
        exp = EXP_MODS["MR52-S3"] if current_system == "Mercury" else EXP_MODS["X100A"]
        
        readers = s.get('readers', 0)
        if not s.get('has_main', False) and readers > 0:
            # 根據選擇的 16/32/64 計算主控數量
            num_main = math.ceil(readers / max_load)
            hw_items.append({"n": m_info[L], "q": num_main, "p": m_info["p"]})
            
        r_qty = math.ceil(readers / exp["r"]) if readers > 0 else 0
        if r_qty > 0: hw_items.append({"n": exp[L], "q": r_qty, "p": exp["p"]})
        
        i_qty = math.ceil(s.get('inputs', 0) / 16) if s.get('inputs', 0) > 0 else 0
        i_mod = EXP_MODS["MR16IN"] if current_system == "Mercury" else EXP_MODS["X200A"]
        if i_qty > 0: hw_items.append({"n": i_mod[L], "q": i_qty, "p": i_mod["p"]})
        
        o_div = 16 if current_system == "Mercury" else 12
        o_qty = math.ceil(s.get('outputs', 0) / o_div) if s.get('outputs', 0) > 0 else 0
        o_mod = EXP_MODS["MR16OUT"] if current_system == "Mercury" else EXP_MODS["X300A"]
        if o_qty > 0: hw_items.append({"n": o_mod[L], "q": o_qty, "p": o_mod["p"]})

    def add_sw(key, qty):
        if qty > 0:
            info = LICENSES_INFO[key]
            sw_items.append({"n": f"{info[L]} ({key})", "q": qty, "p": info["p"]})

    readers, face_panels = s.get('readers', 0), s.get('face_panels', 0)
    if not s.get('has_ibox') and not s.get('has_server') and (readers > 0 or face_panels > 0):
        add_sw("LV-SWS-AC", 1)
        base_readers, base_desktop, base_web = 8, 1, 10
    
    if s.get('has_server'):
        base_readers, base_desktop, base_web = 8, 1, 10

    if base_readers > 0 or s.get('has_server'):
        add_sw("LV-SWI-RD8", math.ceil(max(0, readers - base_readers)/8))
        add_sw("LV-SWC-ACD", max(0, s.get('desktop', 1) - base_desktop))
        add_sw("LV-SWC-ACW", math.ceil(max(0, s.get('web', 10) - base_web)/10))

    add_sw("LV-SWI-CV", s.get('ipc', 0))
    if s.get('has_3rd'): add_sw("LV-SWI-VMS", 1)
    if s.get('has_face'): add_sw("LV-SWI-FRT", 1)
    add_sw("LV-SWI-FRD", face_panels)
    if s.get('has_badging'): add_sw("LV-SWS-ID", 1)
    add_sw("LV-SWC-ID", s.get('badging_clients', 0))
    
    total = sum(i['q']*i['p'] for i in hw_items) + sum(i['q']*i['p'] for i in sw_items)
    return hw_items, sw_items, total

def inline_input(label, key, type="number", **kwargs):
    c1, c2 = st.columns([1.5, 1])
    with c1: st.markdown(f"<div style='padding-top:7px; font-size: 14px; font-weight: 500;'>{label}</div>", unsafe_allow_html=True)
    with c2:
        if type == "number": return st.number_input("", 0, key=key, label_visibility="collapsed", **kwargs)
        if type == "checkbox": return st.checkbox("", key=key, label_visibility="collapsed", **kwargs)
        if type == "selectbox": return st.selectbox("", key=key, label_visibility="collapsed", **kwargs)

# 4. 主程式
def main():
    if not check_password(): return
    st.set_page_config(layout="wide", page_title="Live Quotation Tool")

    st.markdown("""
        <style>
        @media (min-width: 992px) {
            [data-testid="column"]:nth-child(2) {
                position: fixed; right: 2rem; width: 35%;
                max-height: 85vh; overflow-y: auto;
                background: #fdfdfd; padding: 1.5rem;
                border: 1px solid #eee; border-radius: 8px;
            }
        }
        .stMetric { background: #f8f9fa; padding: 10px; border-radius: 5px; }
        div[data-testid="stExpander"] { border: none !important; box-shadow: none !important; }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.radio("Language / 語言", ["中文", "English"], key="lang_radio", horizontal=True)
        L = 'zh' if st.session_state.lang_radio == "中文" else 'en'
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    st.title(LANG[L]['title'])
    st.divider()

    col_in, col_out = st.columns([1.6, 1], gap="large")

    with col_in:
        st.subheader(LANG[L]['input_title'])
        with st.expander(LANG[L]['plat_section'], expanded=True):
            inline_input(LANG[L]['has_ibox'], "has_ibox", "checkbox")
            inline_input(LANG[L]['has_server'], "has_server", "checkbox")
            inline_input(LANG[L]['desktop'], "desktop", value=1)
            inline_input(LANG[L]['web'], "web", value=10)
            inline_input(LANG[L]['badging'], "has_badging", "checkbox")
            if st.session_state.get('has_badging'):
                inline_input(LANG[L]['badging_clients'], "badging_clients", value=0)

        with st.expander(LANG[L]['ac_section'], expanded=True):
            # 新增：打橫的三個策略按鈕
            st.markdown(f"<div style='font-size: 14px; font-weight: 500; margin-bottom:5px;'>{LANG[L]['load_setting']}</div>", unsafe_allow_html=True)
            st.radio(
                "Load Strategy", 
                options=["Stable", "Standard", "Extreme"], 
                format_func=lambda x: LANG[L][f'load_{"16" if x=="Stable" else ("32" if x=="Standard" else "64")}'],
                key="load_strategy", 
                horizontal=True, 
                label_visibility="collapsed"
            )
            st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

            inline_input(LANG[L]['hw_type'], "system", "selectbox", options=["Mercury", "Aero", "None"], index=2)
            if st.session_state.get('system') == "Mercury":
                inline_input(LANG[L]['mercury_model'], "m_model", "selectbox", options=["MP1502", "MP2500", "MP4502"])
            
            inline_input(LANG[L]['card_readers'], "readers")
            inline_input(LANG[L]['input_points'], "inputs")
            inline_input(LANG[L]['output_points'], "outputs")
            inline_input(LANG[L]['has_face_func'], "has_face", "checkbox")
            inline_input(LANG[L]['face_panels'], "face_panels")
            inline_input(LANG[L]['has_main'], "has_main", "checkbox")

        with st.expander(LANG[L]['cctv_section'], expanded=True):
            inline_input(LANG[L]['ip_cameras'], "ipc")
            inline_input(LANG[L]['has_3rd_nvr'], "has_3rd", "checkbox")

    hw, sw, total = calculate_all(L)

    with col_out:
        st.subheader(LANG[L]['result_title'])
        st.metric(LANG[L]['raw_total'], f"USD ${total:,.2f}")
        
        st.markdown(f"**{LANG[L]['hw_header']}**")
        if hw:
            for item in hw:
                c1, c2, c3 = st.columns([3, 1, 1.5])
                c1.markdown(f"<div style='font-size:13px'>{item['n']}</div>", unsafe_allow_html=True)
                c2.markdown(f"<div style='font-size:13px'>x{item['q']}</div>", unsafe_allow_html=True)
                c3.markdown(f"<div style='font-size:13px; text-align:right;'>${item['q']*item['p']:,.1f}</div>", unsafe_allow_html=True)
        else: st.caption("No hardware selected")
        
        st.divider()
        st.markdown(f"**{LANG[L]['sw_header']}**")
        if sw:
            for item in sw:
                c1, c2, c3 = st.columns([3, 1, 1.5])
                c1.markdown(f"<div style='font-size:13px'>{item['n']}</div>", unsafe_allow_html=True)
                c2.markdown(f"<div style='font-size:13px'>x{item['q']}</div>", unsafe_allow_html=True)
                c3.markdown(f"<div style='font-size:13px; text-align:right;'>${item['q']*item['p']:,.1f}</div>", unsafe_allow_html=True)
        else: st.caption("No licenses needed")
        
        st.divider()

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "OFFICIAL QUOTATION (USD)", ln=True, align='C')
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='R')
            
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(95, 10, " Item", 1, 0, 'L', True)
            pdf.cell(15, 10, " Qty", 1, 0, 'C', True)
            pdf.cell(35, 10, " Unit Price", 1, 0, 'C', True)
            pdf.cell(35, 10, " Subtotal", 1, 1, 'C', True)
            
            pdf.set_font("Helvetica", "", 9)
            for item in hw + sw:
                name = str(item['n']).encode('ascii', 'ignore').decode('ascii')
                pdf.cell(95, 8, f" {name}", 1)
                pdf.cell(15, 8, str(item['q']), 1, 0, 'C')
                pdf.cell(35, 8, f"{item['p']:,.2f}", 1, 0, 'R')
                pdf.cell(35, 8, f"{item['q']*item['p']:,.2f}", 1, 1, 'R')
            
            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(110, 10, "", 0)
            pdf.cell(35, 10, "GRAND TOTAL", 1, 0, 'C', True)
            pdf.cell(35, 10, f" ${total:,.2f}", 1, 1, 'R')
            
            st.download_button(
                label=LANG[L]['export_pdf'],
                data=bytes(pdf.output()),
                file_name=f"Quote_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error generating PDF: {e}")

if __name__ == "__main__":
    main()
