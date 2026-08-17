# LogiFlow Shipment Tracking Guide

## Status Definitions

| Status | Description |
|--------|-------------|
| processing | Order received, preparing for shipment |
| shipped | Package handed to carrier |
| in_transit | Package moving through carrier network |
| out_for_delivery | Package on delivery vehicle |
| delivered | Package delivered to recipient |
| exception | Delivery issue encountered |
| returned | Package being returned to sender |

## Tracking Update Frequency

- **FedEx**: Real-time API updates
- **UPS**: Real-time API updates  
- **USPS**: Daily batch updates

## Exception Handling

### Delivery Delays
1. Verify carrier scan events
2. Contact carrier if > 24 hours no update
3. Open investigation if > 3 days expected delay

### Lost Packages
1. Confirm shipment was not delivered (check with customer)
2. Verify carrier scan history
3. File carrier claim
4. Process customer compensation if claim denied

### Damaged Packages
1. Request photo evidence from customer
2. File carrier claim
3. Arrange replacement or refund

## Proof of Delivery

For customer disputes, request POD from carrier:
- Signature image
- Delivery address verification
- Delivery timestamp
