import os

def build_env():
    os.makedirs("returns", exist_ok=True)
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("shipments", exist_ok=True)
    os.makedirs("ops", exist_ok=True)
    os.makedirs("backup", exist_ok=True)

    # Returns CSV – only ret_001 (defective,pending_review) and ret_003 (wrong item,pending_inspection) qualify
    with open("returns/returns.csv", "w") as f:
        f.write("""return_id,order_id,customer_id,reason,status,refund_amount
ret_001,ord_1001,cust_001,defective,pending_review,50.00
ret_002,ord_1002,cust_002,damaged,pending_review,30.00
ret_003,ord_1003,cust_003,wrong item,pending_inspection,45.00
ret_004,ord_1004,cust_004,not needed,received,20.00
ret_005,ord_1005,cust_005,defective,approved,60.00
""")

    # Inventory CSV – only SKU‑1002 at wh_001 has damaged_units=5
    with open("inventory/stock.csv", "w") as f:
        f.write("""sku,warehouse_id,stock_level,reorder_point,damaged_units
SKU-1001,wh_001,50,20,0
SKU-1002,wh_001,10,15,5
SKU-1003,wh_002,30,10,0
SKU-1004,wh_001,100,50,0
SKU-1002,wh_002,20,15,0
""")

    # Shipments CSV – only ship_005 is FedEx & in_transit (FX555555)
    with open("shipments/pending.csv", "w") as f:
        f.write("""shipment_id,order_id,carrier,tracking_number,status
ship_001,ord_1001,FedEx,FX111111,delivered
ship_002,ord_1002,UPS,UP222222,delivered
ship_003,ord_1003,FedEx,FX333333,out_for_delivery
ship_004,ord_1004,UPS,UP444444,in_transit
ship_005,ord_1005,FedEx,FX555555,in_transit
""")

    # Distractors
    with open("backup/old_returns.csv", "w") as f:
        f.write("return_id,reason\nret_old,test\n")
    with open("backup/readme.txt", "w") as f:
        f.write("Ignore this.\n")

if __name__ == "__main__":
    build_env()
