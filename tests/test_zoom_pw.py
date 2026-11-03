import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        card_html = """
        <div class="marbete-grande">
            <div class="mg-inner">
                <div class="mg-header-row">
                    <div class="mg-header-label">CLAVE</div>
                    <div class="mg-header-clave">531.345.0263</div>
                </div>
                <div class="mg-number-row">
                    <div class="mg-number-center">0263</div>
                    <div class="mg-status-side">
                        <span>Verde</span>
                        <span>Amarillo</span>
                        <span>Rojo</span>
                    </div>
                </div>
                <div class="mg-desc-container">
                    <div class="mg-desc-title">Descripción</div>
                    <div class="mg-desc-text">ANALIZADORES BIOSENSOR PARA MONITOREO DE GLUCOSA</div>
                </div>
                <div class="mg-lote-cad-titles">
                    <div class="mg-col-half">Lote</div>
                    <div class="mg-col-half">Caducidad</div>
                </div>
                <div class="mg-lote-cad-vals">
                    <div class="mg-lote-val">73N5E0143</div>
                    <div class="mg-cad-val">2027-05-10</div>
                </div>
                <table class="mg-table-ctrl">
                    <tr>
                        <th class="header-col">Fecha</th>
                        <td class="val-col">2026-09-14</td>
                        <td class="val-col"></td><td class="val-col"></td><td class="val-col"></td><td class="val-col"></td><td class="val-col"></td>
                    </tr>
                    <tr>
                        <th class="header-col">Cantidad</th>
                        <td class="val-col first-val">96</td>
                        <td class="val-col"></td><td class="val-col"></td><td class="val-col"></td><td class="val-col"></td><td class="val-col"></td>
                    </tr>
                </table>
            </div>
        </div>
        """
        
        html = f"""<!DOCTYPE html>
<html>
<head>
<style>
@page {{ size: Letter portrait; margin: 12mm 13mm 12mm 13mm; }}
body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
.print-page {{
    width: 186mm;
    display: flex;
    flex-direction: column;
    gap: 6mm;
    margin: 0 auto;
    page-break-after: always;
    break-after: page;
}}
.print-page:last-child {{
    page-break-after: auto;
    break-after: auto;
}}
.marbete-grande {{
    width: 185mm;
    height: 120mm;
    box-sizing: border-box;
    border: 1.5px solid #000000;
    background: #ffffff;
    color: #000000;
    overflow: hidden;
}}
.mg-inner {{
    width: 180mm;
    height: 115mm;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    transform: scale(calc(185 / 180), calc(120 / 115));
    transform-origin: top left;
}}
.mg-header-row {{ display: flex; border-bottom: 1.2px solid #000000; height: 12.5mm; }}
.mg-header-label {{ width: 63%; border-right: 1.2px solid #000000; font-size: 15.5pt; font-weight: bold; display: flex; align-items: center; padding-left: 10px; }}
.mg-header-clave {{ width: 37%; font-size: 15pt; font-weight: bold; display: flex; align-items: center; justify-content: center; }}
.mg-number-row {{ display: flex; border-bottom: 1.2px solid #000000; height: 27.5mm; align-items: center; position: relative; }}
.mg-number-center {{ flex: 1; text-align: center; font-size: 62pt; font-weight: 800; line-height: 1; }}
.mg-status-side {{ position: absolute; right: 18px; top: 50%; transform: translateY(-50%); display: flex; flex-direction: column; gap: 2px; font-size: 7.5pt; font-weight: bold; line-height: 1.15; }}
.mg-desc-container {{ border-bottom: 1.2px solid #000000; padding: 0; height: 26mm; display: flex; flex-direction: column; overflow: hidden; }}
.mg-desc-title {{ text-align: center; font-size: 10pt; font-weight: bold; height: 7mm; display: flex; align-items: center; justify-content: center; border-bottom: 1.2px solid #000000; margin: 0; }}
.mg-desc-text {{ font-size: 8.5pt; font-weight: bold; text-align: center; line-height: 1.25; text-transform: uppercase; padding: 2px 8px; flex: 1; display: flex; align-items: center; justify-content: center; overflow: hidden; }}
.mg-lote-cad-titles {{ display: flex; border-bottom: 1.2px solid #000000; font-size: 10.5pt; font-weight: bold; text-align: center; height: 8mm; align-items: center; }}
.mg-col-half {{ width: 50%; padding: 0 4px; }}
.mg-col-half:first-child {{ border-right: 1.2px solid #000000; }}
.mg-lote-cad-vals {{ display: flex; text-align: center; height: 25mm; align-items: center; }}
.mg-lote-val, .mg-cad-val {{ width: 50%; height: 100%; font-size: 28pt; font-weight: bold; display: flex; align-items: center; justify-content: center; text-align: center; box-sizing: border-box; word-break: break-all; overflow-wrap: anywhere; line-height: 1.15; padding: 0 4px; overflow: hidden; }}
.mg-lote-val {{ border-right: 1.2px solid #000000; }}
.mg-table-ctrl {{ width: 100%; border-collapse: collapse; margin-top: auto; }}
.mg-table-ctrl th, .mg-table-ctrl td {{ border: 1.2px solid #000000; text-align: center; font-weight: bold; }}
.mg-table-ctrl tr:first-child th, .mg-table-ctrl tr:first-child td {{ height: 5.2mm; font-size: 8pt; }}
.mg-table-ctrl tr:last-child th, .mg-table-ctrl tr:last-child td {{ height: 10.2mm; font-size: 8pt; }}
.mg-table-ctrl tr:last-child td.first-val {{ font-size: 15pt; font-weight: bold; }}
.mg-table-ctrl th.header-col {{ width: 12.5%; }}
.mg-table-ctrl td.val-col {{ width: 12.5%; }}
</style>
</head>
<body>
<div class="print-page">
    {card_html}
    {card_html}
</div>
</body>
</html>"""
        await page.set_content(html)
        pdf = await page.pdf(format='Letter')
        
        import pdfplumber
        import io
        with pdfplumber.open(io.BytesIO(pdf)) as p_doc:
            print("Total pages in PDF with 2 cards:", len(p_doc.pages))
        await page.screenshot(path='downloads/test_2cards_page.png', full_page=True)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test())
