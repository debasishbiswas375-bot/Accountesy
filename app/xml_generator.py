def generate_xml(vouchers):
    xml="<ENVELOPE><BODY><DATA>"
    for v in vouchers:
        xml += f"<VOUCHER><DATE>{v['date']}</DATE><NARRATION>{v['narration']}</NARRATION><AMOUNT>{v['amount']}</AMOUNT></VOUCHER>"
    xml+="</DATA></BODY></ENVELOPE>"
    return xml
