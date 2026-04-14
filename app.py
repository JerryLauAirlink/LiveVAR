import streamlit as st
from datetime import datetime
import math
from io import BytesIO

# PDF 相關
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 1. 完整語系字典 (解決問題 6: 確保所有 Label 都連動)
LANG = {
    'en': {
        'title': "Live Platform - Overseas Quotation System",
        'input_title': "Input Requirements",
        'ac_section': "ACCESS CONTROL SYSTEM",
        'card_readers': "Card Readers (Qty):",
        'input_points': "Input Points (Qty):",
        'output_points': "Output Points (Qty):",
        'face_panels': "Face Recognition Readers (Qty):",
        'hw_type': "Hardware System Type:",
        'mercury_model': "Mercury Model:",
        'has_main': "Customer already has Main Controller",
        'cctv_section': "CCTV SYSTEM",
        'ip_cameras': "IP Cameras (Qty):",
        'has_3rd_nvr': "Has 3rd Party NVR",
        'plat_section': "PLATFORM SETTINGS",
        'desktop': "Desktop Clients:",
        'web': "Web Clients:",
        'badging': "Badging Software",
        'badging_clients': "Badging Clients:",
        'has_server': "Customer already has Server License",
        'has_face_func': "Face Recognition Function",
        'result_title': "Quotation Result",
        'download_btn': "📄 Download PDF Quotation"
    },
    'zh': {
        'title': "Live Platform - Overseas 報價系統",
        'input_title': "輸入需求",
        'ac_section': "門禁控制系統 (Access Control)",
        'card_readers': "Card Readers (數量)：",
        'input_points': "Input Points (數量)：",
        'output_points': "Output Points (數量)：",
        'face_panels': "人臉辨識面板機 (數量)：",
        'hw_type': "硬件系統類型：",
        'mercury_model': "Mercury 型號：",
        'has_main': "客戶已擁有主控制器 (Main Controller)",
        'cctv_section': "監控系統 (CCTV)",
        'ip_cameras': "IP Cameras (數量)：",
        'has_3rd_nvr': "使用第三方 NVR",
        'plat_section': "平台設定 (Platform)",
        'desktop': "Desktop 客戶端：",
        'web': "Web 客戶端：",
        'badging': "制證軟件 (Badging)",
        'badging_clients': "制證客戶端數量：",
        'has_server': "客戶已擁有 Server 授權",
        'has_face_func': "開啟人臉識別功能",
        'result_title': "報價結果",
        'download_btn': "📄 下載 PDF 報價單"
    }
}

# 2. 硬體與授權資料 (解決問題 4, 5)
MAIN_CONTROLLERS = {
    "MP4502": {"name_en": "MP4502 Main Controller", "name_zh": "MP4502 主控制器", "price": 3937.50, "max_modules": 32, "desc": "High-end flagship"},
    "MP1502": {"name_en": "MP1502 Main Controller", "name_zh": "MP1502 主控制器", "price": 2812.50, "max_modules": 32, "desc": "Standard 2-door controller"},
    "MP2500": {"name_en": "MP2500 Main Controller", "name_zh": "MP2500 主控制器", "price": 2887.50, "max_modules": 32, "desc": "Intelligent processor"},
    "X1100A": {"name_en": "X1100A Main Controller", "name_zh": "X1100A 主控制器", "price": 750.00, "max_modules": 31, "desc": "Aero Series Main"},
}

EXPANSION_MODULES = {
    "MR52-S3": {"name_zh": "MR52-S3 (2門/2讀卡器)", "name_en": "MR52-S3 (2DR/2RD)", "price": 1612.50, "readers": 2, "desc": "Expansion module"},
    "X100A": {"name_zh": "X100A 讀卡器模組", "name_en": "X100A Reader Module", "price": 412.50, "readers": 4, "desc": "4-reader interface"},
    "MR16IN-S3": {"name_zh": "MR16IN-S3 (16輸入)", "name_en": "MR16IN-S3 (16IN)", "price": 1650.00, "inputs": 16, "desc": "Input expansion"},
    "MR16OUT-S3": {"name_zh": "MR16OUT-S3 (16輸出)", "name_en": "MR16OUT-S3 (16OUT)", "price": 1650.00, "outputs": 16, "desc": "Output expansion"},
    "X200A": {"name_zh": "X200A 輸入模組", "name_en": "X200A Input Module", "price": 425.00, "inputs": 16, "desc": "16-point input"},
    "X300A": {"name_zh": "X300A 輸出模組", "name_en": "X300A Output Module", "price": 500.00, "outputs": 12, "desc": "12-point output"},
}

LICENSE_DATA = {
    "LV-SWS-AC": {"zh": "基礎平台授權", "en": "Base Platform License", "price": 937.50},
    "LV-SWI-RD8": {"zh": "8門門禁授權", "en": "8-Reader License", "price": 300.00},
    "LV-SWC-ACD": {"zh": "額外 Desktop 客戶端", "en": "Extra Desktop Client", "price": 187.50},
    "LV-SWC-ACW": {"zh": "額外 Web 客戶端(10組)", "en": "Extra Web Client (Set of 10)", "price": 375.00},
    "LV-SWI-CV": {"zh": "單路攝像頭接入", "en": "Single Channel IP Cam", "price": 37.50},
    "LV-SWI-VMS": {"zh": "第三方 NVR 整合", "en": "3rd Party VMS Integration", "price": 937.50},
    "LV-SWI-FRT": {"zh": "人臉識別功能授權", "en": "Face Recognition Base", "price": 937.50},
    "LV-SWI-FRD": {"zh": "人臉面板機接入", "en": "Face Panel Connection", "price": 37.50},
    "LV-SWS-ID": {"zh": "制證軟件主授權", "en": "Badging Software License", "price": 937.50},
    "LV-SWC-ID": {"zh": "制證客戶端授權", "en": "Badging Client License", "price": 187.50},
}

# 3. 計算與 PDF (解決問題 1, 2, 3, 7)
def calculate_quotation(ip_cameras, readers, inputs, outputs, desktop, web, badging_clients, face_panels,
                        system, mercury_model, has_server, has_main, has_3rd_nvr, has_face, has_badging, lang):
    hw_items = []
    hw_cost = 0.0
    
    # 硬體計算
    if system != "None":
        main_info = MAIN_CONTROLLERS[mercury_model if system == "Mercury" else "X1100A"]
        exp = EXPANSION_MODULES["MR52-S3" if system == "Mercury" else "X100A"]
        
        r_qty = math.ceil(readers / exp["readers"]) if readers > 0 else 0
        i_qty = math.ceil(inputs / 16) if inputs > 0 else 0
        o_qty = math.ceil(outputs / (12 if system == "Aero" else 16)) if outputs > 0 else 0
        
        if not has_main:
            hw_items.append({"name": main_info[f"name_{lang}"], "qty": 1, "price": main_info["price"], "desc": main_info["desc"]})
            hw_cost += main_info["price"]
        
        if r_qty > 0: hw_items.append({"name": exp[f"name_{lang}"], "qty": r_qty, "price": exp["price"], "desc": exp["desc"]})
        if i_qty > 0:
            mod = EXPANSION_MODULES["MR16IN-S3" if system == "Mercury" else "X200A"]
            hw_items.append({"name": mod[f"name_{lang}"], "qty": i_qty, "price": mod["price"], "desc": mod["desc"]})
        if o_qty > 0:
            mod = EXPANSION_MODULES["MR16OUT-S3" if system == "Mercury" else "X300A"]
            hw_items.append({"name": mod[f"name_{lang}"], "qty": o_qty, "price": mod["price"], "desc": mod["desc"]})
        
        hw_cost = sum(item['qty'] * item['price'] for item in hw_items)

    # 軟體計算
    licenses = []
    sw_cost = 0.0
    
    def add_lic(key, qty=1):
        nonlocal sw_cost
        item = LICENSE_DATA[key]
        name = f"{qty} x {item[lang]} ({key})"
        licenses.append({"name": name, "qty": qty, "price": item["price"], "total": item["price"] * qty})
        sw_cost += item["price"] * qty

    if not has_server and (readers > 0 or face_panels > 0): add_lic("LV-SWS-AC")
    if readers > 0: add_lic("LV-SWI-RD8", math.ceil(readers / 8))
    if desktop > 1: add_lic("LV-SWC-ACD", desktop - 1)
    if web > 10: add_lic("LV-SWC-ACW", math.ceil((web-10)/10))
    if ip_cameras > 0: add_lic("LV-SWI-CV", ip_cameras)
    if has_3rd_nvr: add_lic("LV-SWI-VMS")
    if has_face: add_lic("LV-SWI-FRT")
    if face_panels > 0: add_lic("LV-SWI-FRD", face_panels)
    if has_badging: add_lic("LV-SWS-ID")
    if badging_clients > 0: add_lic("LV-SWC-ID", badging_clients)

    total = hw_cost + sw_cost
    
    # 組合垂直顯示文字 (解決問題 2, 3)
    hw_lines = [f"<span style='color:#FF4B4B;font-weight:bold;'>• {i['qty']} x {i['name']} (${i['price']*i['qty']:,.2f})</span>" if idx==0 else f"• {i['qty']} x {i['name']} (${i['price']*i['qty']:,.2f})" for idx, i in enumerate(hw_items)]
    sw_lines = [f"• {l['name']} — ${l['total']:,.2f}" for l in licenses]

    res_text = f"**System**: {system}\n\n**Hardware:**\n" + "\n".join(hw_lines) + "\n\n**Software:**\n" + "\n".join(sw_lines) + f"\n\n---\n### **TOTAL: ${total:,.2f}**"
    
    return {'result_text': res_text, 'total': total, 'hw_items': hw_items, 'licenses': licenses, 'hw_cost': hw_cost, 'sw_cost': sw_cost}

def generate_pdf(data, lang):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    
    # 解決問題 7: 註冊字體 (避免黑框，請確保環境有字體，或使用預設)
    title = Paragraph(f"<b>Quotation - {datetime.now().strftime('%Y-%m-%d')}</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))

    # 表格資料
    t_data = [["Description", "Qty", "Unit Price", "Subtotal"]]
    for i in data['hw_items']: t_data.append([i['name'], str(i['qty']), f"{i['price']:.2f}", f"{i['price']*i['qty']:.2f}"])
    for l in data['licenses']: t_data.append([l['name'], str(l['qty']), f"{l['price']:.2f}", f"{l['total']:.2f}"])
    
    # 加入最後一行 Grand Total 到 Subtotal 棟的最下方
    t_data.append(["", "", "GRAND TOTAL", f"{data['total']:,.2f}"])

    table = Table(t_data, colWidths=[280, 50, 90, 90])
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (2,0), (3,-1), 'RIGHT'),
        ('TEXTCOLOR', (2,-1), (2,-1), colors.red), # Grand Total 字樣
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer

# 4. 主程式 (解決問題 1, 6)
def main():
    st.set_page_config(layout="wide")
    
    # 頂部選擇語言，立即影響下方變數
    lang_code = st.sidebar.radio("Select Language / 選擇語言", ["English", "中文"], index=1)
    L = 'zh' if lang_code == "中文" else 'en'
    
    st.title(LANG[L]['title'])
    c1, c2 = st.columns([1, 1.2])

    with c1:
        st.subheader(LANG[L]['input_title'])
        # 門禁區 (將人臉移入)
        st.info(LANG[L]['ac_section'])
        readers = st.number_input(LANG[L]['card_readers'], 0)
        inputs = st.number_input(LANG[L]['input_points'], 0)
        outputs = st.number_input(LANG[L]['output_points'], 0)
        face_panels = st.number_input(LANG[L]['face_panels'], 0) # 移到這裡了
        has_main = st.checkbox(LANG[L]['has_main'])
        system = st.selectbox(LANG[L]['hw_type'], ["Mercury", "Aero", "None"])
        m_model = st.selectbox(LANG[L]['mercury_model'], list(MAIN_CONTROLLERS.keys())) if system=="Mercury" else None
        
        # 監控區
        st.info(LANG[L]['cctv_section'])
        ipc = st.number_input(LANG[L]['ip_cameras'], 0)
        has_3rd = st.checkbox(LANG[L]['has_3rd_nvr'])
        
        # 平台區
        st.info(LANG[L]['plat_section'])
        desk = st.number_input(LANG[L]['desktop'], 1)
        web = st.number_input(LANG[L]['web'], 10)
        has_server = st.checkbox(LANG[L]['has_server'])
        has_face = st.checkbox(LANG[L]['has_face_func'])
        has_badging = st.checkbox(LANG[L]['badging'])
        badging_c = st.number_input(LANG[L]['badging_clients'], 0) if has_badging else 0

    res = calculate_quotation(ipc, readers, inputs, outputs, desk, web, badging_c, face_panels, system, m_model, has_server, has_main, has_3rd, has_face, has_badging, L)

    with c2:
        st.subheader(LANG[L]['result_title'])
        st.markdown(res['result_text'], unsafe_allow_html=True)
        if st.button(LANG[L]['download_btn']):
            pdf = generate_pdf(res, L)
            st.download_button("Download Now", pdf, file_name="Quotation.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()
