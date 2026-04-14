import streamlit as st
from datetime import datetime
import math
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# 1. 資料定義
LANG = {
    'en': {
        'title': "Live Platform - Overseas Quotation System",
        'input_title': "Input Requirements",
        'card_readers': "Card Readers (Qty):",
        'input_points': "Input Points (Qty):",
        'output_points': "Output Points (Qty):",
        'face_recognition_readers': "Face Recognition Readers (Qty):",
        'hardware_system_type': "Hardware System Type:",
        'mercury_model': "Mercury Model:",
        'has_main_controller': "Customer already has Aero / Mercury Main Controller",
        'has_server_license': "Customer already has SERVER License",
        'has_3rd_party_nvr': "Has 3rd Party NVR - HIKVISION, Dahua",
        'has_face_recognition': "Face Recognition",
        'has_badging': "Badging software",
        'ip_cameras': "IP Cameras (Qty):",
        'platform_desktop': "Platform Desktop Clients:",
        'platform_web': "Platform Web Clients:",
        'badging_clients': "Badging Clients (Qty):",
        'base_platform': "1 × LV-SWS-AC ($937.50) ← Base Platform (incl. 1 Desktop + 10 Web)",
        'extra_desktop': "Extra Desktop Client",
        'extra_web': "Extra Web Client (10 users/set)",
        'no_hardware': "No Hardware (Software Only / Third-Party Integration)",
    },
    'zh': {
        'title': "Live Platform - Overseas 報價系統",
        'input_title': "輸入需求",
        'card_readers': "Card Readers (數量)：",
        'input_points': "Input Points (數量)：",
        'output_points': "Output Points (數量)：",
        'face_recognition_readers': "Face Recognition Readers (數量)：",
        'hardware_system_type': "Hardware System Type：",
        'mercury_model': "Mercury 型號：",
        'has_main_controller': "客戶已擁有 Aero / Mercury Main Controller",
        'has_server_license': "客戶已擁有 SERVER License",
        'has_3rd_party_nvr': "使用 3rd Party NVR - HIKVISION, Dahua",
        'has_face_recognition': "Face Recognition",
        'has_badging': "Badging software",
        'ip_cameras': "IP Cameras (數量)：",
        'platform_desktop': "Platform Desktop Clients：",
        'platform_web': "Platform Web Clients：",
        'badging_clients': "Badging Clients (數量)：",
        'base_platform': "1 × LV-SWS-AC ($937.50) ← 基礎平台 (已包含 1 Desktop + 10 Web)",
        'extra_desktop': "額外 Desktop Client",
        'extra_web': "額外 Web Client (10用戶/組)",
        'no_hardware': "無硬件 (只計算軟件授權 / 第三方整合)",
    }
}

MAIN_CONTROLLERS = {
    "MP4502": {"name_en": "MP4502 Main (Server)", "name_zh": "MP4502 主控", "price": 3937.50, "max_modules": 32},
    "MP1502": {"name_en": "MP1502 Main (Server)", "name_zh": "MP1502 主控", "price": 2812.50, "max_modules": 32},
    "MP2500": {"name_en": "MP2500 Main (Server)", "name_zh": "MP2500 主控", "price": 2887.50, "max_modules": 32},
    "LP1502": {"name_en": "LP1502 Main (Server)", "name_zh": "LP1502 主控", "price": 1687.50, "max_modules": 32},
    "X1100A": {"name_en": "X1100A Main (Server)", "name_zh": "X1100A 主控", "price": 750.00, "max_modules": 31},
}

EXPANSION_MODULES = {
    "MR52-S3": {"name_en": "MR52-S3 (2 Doors/2 Readers)", "name_zh": "MR52-S3 (2門/2讀卡器)", "price": 1612.50, "readers": 2},
    "X100A": {"name_en": "X100A Reader Module", "name_zh": "X100A 讀卡器模組", "price": 412.50, "readers": 4},
    "MR16IN-S3": {"name_en": "MR16IN-S3 (16 Inputs)", "name_zh": "MR16IN-S3 (16輸入)", "price": 1650.00, "inputs": 16},
    "MR16OUT-S3": {"name_en": "MR16OUT-S3 (16 Outputs)", "name_zh": "MR16OUT-S3 (16輸出)", "price": 1650.00, "outputs": 16},
    "X200A": {"name_en": "X200A Input Module", "name_zh": "X200A 輸入模組", "price": 425.00, "inputs": 16},
    "X300A": {"name_en": "X300A Output Module", "name_zh": "X300A 輸出模組", "price": 500.00, "outputs": 12},
}

LICENSE_PRICES = {
    "LV-SWS-AC": 937.50, "LV-SWI-RD8": 300.00,
    "LV-SWC-ACD": 187.50, "LV-SWC-ACW": 375.00,
    "LV-SWI-CV": 37.50, "LV-SWI-VMS": 937.50,
    "LV-SWI-FRT": 937.50, "LV-SWS-ID": 937.50,
    "LV-SWC-ID": 187.50, "LV-SWI-FRD": 37.50,
}

# 2. 計算邏輯
def calculate_quotation(ip_cameras, readers, inputs, outputs, desktop, web, badging_clients, face_panels,
                        system, mercury_model, has_server, has_main, has_3rd_nvr, has_face, has_badging, lang):
    hw_items = []
    hw_cost = 0.0
    hw_text = ""

    if system == "None":
        hw_text = LANG[lang]['no_hardware']
    else:
        # 設定模組類型
        if system == "Mercury":
            main_key = mercury_model if mercury_model else "MP4502"
            main_info = MAIN_CONTROLLERS[main_key]
            exp = EXPANSION_MODULES["MR52-S3"]
            in_mod = EXPANSION_MODULES["MR16IN-S3"]
            out_mod = EXPANSION_MODULES["MR16OUT-S3"]
            max_mod = main_info["max_modules"]
        else: # Aero
            main_info = MAIN_CONTROLLERS["X1100A"]
            exp = EXPANSION_MODULES["X100A"]
            in_mod = EXPANSION_MODULES["X200A"]
            out_mod = EXPANSION_MODULES["X300A"]
            max_mod = main_info["max_modules"]

        # 計算各板卡數量 (MR52-S3 現在除以 2)
        r_mod_qty = math.ceil(readers / exp["readers"]) if readers > 0 else 0
        i_mod_qty = math.ceil(inputs / in_mod.get("inputs", 16)) if inputs > 0 else 0
        o_mod_qty = math.ceil(outputs / out_mod.get("outputs", 16)) if outputs > 0 else 0
        
        total_mod = r_mod_qty + i_mod_qty + o_mod_qty

        # 如果客戶沒有主控，計算需要多少台主控
        if not has_main:
            num_main = math.ceil(total_mod / max_mod) if total_mod > 0 else 1
            hw_items.append({"name": main_info[f"name_{lang}"], "qty": num_main, "price": main_info["price"]})
            hw_cost += num_main * main_info["price"]

        # 加入擴充板到清單
        if r_mod_qty > 0:
            hw_items.append({"name": exp[f"name_{lang}"], "qty": r_mod_qty, "price": exp["price"]})
            hw_cost += r_mod_qty * exp["price"]
        if i_mod_qty > 0:
            hw_items.append({"name": in_mod[f"name_{lang}"], "qty": i_mod_qty, "price": in_mod["price"]})
            hw_cost += i_mod_qty * in_mod["price"]
        if o_mod_qty > 0:
            hw_items.append({"name": out_mod[f"name_{lang}"], "qty": o_mod_qty, "price": out_mod["price"]})
            hw_cost += o_mod_qty * out_mod["price"]

        hw_text = "\n".join([f"• {item['qty']} × {item['name']} — ${item['price']*item['qty']:,.2f}" for item in hw_items])

    # 3. 軟體授權計算
    licenses = []
    sw_cost = 0.0

    # 基礎平台 (只有在沒選「已有 Server」且有 Reader 時觸發)
    if not has_server and readers > 0:
        licenses.append(LANG[lang]['base_platform'])
        sw_cost += LICENSE_PRICES["LV-SWS-AC"]

    # Reader 授權 (RD8)
    if readers > 0:
        # 如果是已有 Server 或已買了基礎平台，超過的部分 (或全部) 需計算 RD8
        rd8_qty = math.ceil(readers / 8)
        licenses.append(f"{rd8_qty} × LV-SWI-RD8 (${LICENSE_PRICES['LV-SWI-RD8']})")
        sw_cost += rd8_qty * LICENSE_PRICES['LV-SWI-RD8']

    # 客戶端授權
    desktop_extra = max(0, desktop - 1)
    if desktop_extra > 0:
        licenses.append(f"{desktop_extra} × LV-SWC-ACD (${LICENSE_PRICES['LV-SWC-ACD']})")
        sw_cost += desktop_extra * LICENSE_PRICES['LV-SWC-ACD']

    web_extra = max(0, web - 10)
    if web_extra > 0:
        web_sets = math.ceil(web_extra / 10)
        licenses.append(f"{web_sets} × LV-SWC-ACW (${LICENSE_PRICES['LV-SWC-ACW']})")
        sw_cost += web_sets * LICENSE_PRICES['LV-SWC-ACW']

    # CCTV 授權
    if ip_cameras > 0:
        cv_total = ip_cameras * LICENSE_PRICES["LV-SWI-CV"]
        licenses.append(f"{ip_cameras} × LV-SWI-CV — ${cv_total:,.2f}")
        sw_cost += cv_total

    if has_3rd_nvr:
        licenses.append(f"1 × LV-SWI-VMS — ${LICENSE_PRICES['LV-SWI-VMS']:,.2f}")
        sw_cost += LICENSE_PRICES["LV-SWI-VMS"]

    # 其他功能
    if has_face:
        licenses.append(f"1 × LV-SWI-FRT — ${LICENSE_PRICES['LV-SWI-FRT']:,.2f}")
        sw_cost += LICENSE_PRICES["LV-SWI-FRT"]
    if has_badging:
        licenses.append(f"1 × LV-SWS-ID — ${LICENSE_PRICES['LV-SWS-ID']:,.2f}")
        sw_cost += LICENSE_PRICES["LV-SWS-ID"]
    if badging_clients > 0:
        bc_total = badging_clients * LICENSE_PRICES["LV-SWC-ID"]
        licenses.append(f"{badging_clients} × LV-SWC-ID — ${bc_total:,.2f}")
        sw_cost += bc_total
    if face_panels > 0:
        frd_total = face_panels * LICENSE_PRICES["LV-SWI-FRD"]
        licenses.append(f"{face_panels} × LV-SWI-FRD — ${frd_total:,.2f}")
        sw_cost += frd_total

    total = hw_cost + sw_cost

    # 組合結果文本
    result_text = f"""
**System Type**: {system}  
**Card Readers**: {readers} | **IP Cameras**: {ip_cameras}

**[ Hardware Recommended ]**  
{hw_text if hw_text else "None"}

**[ Software Licenses ]**  
""" + ("\n".join(f"• {lic}" for lic in licenses) if licenses else "None") + f"""

**Software Total**: ${sw_cost:,.2f}  
**Hardware Total**: ${hw_cost:,.2f}  
---
### **GRAND TOTAL (USD): ${total:,.2f}**
"""

    return {
        'result_text': result_text,
        'total': total,
        'hw_items': hw_items,
        'licenses': licenses,
        'hw_cost': hw_cost,
        'sw_cost': sw_cost
    }

# 3. PDF 生成
def generate_pdf_bytes(data, lang):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    title = "Live Platform - Overseas Quotation" if lang == 'en' else "Live Platform - Overseas 報價單"
    story.append(Paragraph(f"<b>{title}</b>", styles['Title']))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
    story.append(Spacer(1, 20))

    table_data = [["Item Description", "Qty", "Unit Price", "Subtotal"]]
    
    # 硬體行
    for item in data.get('hw_items', []):
        table_data.append([item['name'], str(item['qty']), f"${item['price']:.2f}", f"${item['price']*item['qty']:.2f}"])
    
    # 軟體行 (簡易顯示)
    for lic in data.get('licenses', []):
        table_data.append([lic, "-", "-", "-"])

    table = Table(table_data, colWidths=[280, 50, 90, 90])
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (2,0), (3,-1), 'RIGHT'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    story.append(table)

    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<b>GRAND TOTAL (USD) : ${data['total']:,.2f}</b>", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

# 4. Streamlit 主介面
def main():
    st.set_page_config(page_title="Live Quotation System", layout="wide")
    st.title("📊 Live Platform - Overseas Quotation System")

    lang_select = st.radio("Language", ["中文", "English"], horizontal=True)
    lang = 'zh' if lang_select == "中文" else 'en'

    col_input, col_result = st.columns([1, 1.2])

    with col_input:
        st.subheader("1. 需求輸入")
        
        with st.expander("門禁需求 (Access Control)", expanded=True):
            readers = st.number_input("Card Readers 數量", value=0, min_value=0)
            inputs = st.number_input("Input Points 數量", value=0, min_value=0)
            outputs = st.number_input("Output Points 數量", value=0, min_value=0)
            has_main = st.checkbox("已有主控制器 (Main Controller)")
            system = st.selectbox("硬體系統", ["Mercury", "Aero", "None"], index=0)
            mercury_model = None
            if system == "Mercury":
                mercury_model = st.selectbox("Mercury 型號", ["MP1502", "MP2500", "MP4502"], index=0)

        with st.expander("監控與平台 (CCTV & Platform)", expanded=True):
            ip_cameras = st.number_input("IP Cameras 數量", value=0, min_value=0)
            face_panels = st.number_input("人臉面板機數量", value=0, min_value=0)
            desktop = st.number_input("Desktop Client 數量", value=1, min_value=1)
            web = st.number_input("Web Client 數量", value=10, min_value=0)
            has_server = st.checkbox("已有 Server 授權")
            has_3rd_nvr = st.checkbox("整合第三方 NVR")
            has_face = st.checkbox("開啟人臉識別功能")
            has_badging = st.checkbox("開啟制證系統 (Badging)")
            badging_clients = st.number_input("制證客戶端數量", value=0, min_value=0)

    # 執行計算
    result = calculate_quotation(
        ip_cameras, readers, inputs, outputs, desktop, web, badging_clients, face_panels,
        system, mercury_model, has_server, has_main, has_3rd_nvr, has_face, has_badging, lang
    )

    with col_result:
        st.subheader("2. 報價清單")
        st.info("下方結果會隨輸入即時更新")
        st.markdown(result['result_text'])

        if st.button("📄 生成並下載 PDF 報價單", type="primary"):
            pdf_data = {
                'total': result['total'],
                'hw_items': result['hw_items'],
                'licenses': result['licenses']
            }
            pdf_bytes = generate_pdf_bytes(pdf_data, lang)
            st.download_button(
                label="Confirm Download",
                data=pdf_bytes,
                file_name=f"Quotation_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
