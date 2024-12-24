import treepoem
import os
os.system("mkdir images")
image = treepoem.generate_barcode(
    barcode_type="code128",  # One of the BWIPP supported codes.
    # barcode_type="qrcode",
    # One of the BWIPP supported codes.
    # barcode_type="interleaved2of5",  # One of the BWIPP supported codes.
    # barcode_type="code128",  # One of the BWIPP supported codes.
    #    # barcode_type="isbn",  # One of the BWIPP supported codes.
    #    # data="978-3-16-148410-0",
    #   barcode_type="code128",  # One of the BWIPP supported codes.
    #   barcode_type="micropdf417",  # One of the BWIPP supported codes.
    #   barcode_type="ean13",  # One of the BWIPP supported codes.
    data="0000000000001",
)
image.convert("1").save("images/output_qrcode_or_barcode.png")
