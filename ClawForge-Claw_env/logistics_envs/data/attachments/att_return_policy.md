# LogiFlow Returns Processing Policy

## Return Request Submission

Customers may submit return requests within 30 days of delivery. All requests must include:
- Order ID
- Reason for return
- Items being returned

## Return Status Flow

```
requested -> pending_review -> approved/rejected
                        |
                        v
              pending_inspection -> received -> inspected
                                             |
                                             v
                                   resolved -> refund/exchange/rejected
```

## Inspection Requirements

1. **Timeline**: All returns must be inspected within 5 business days of receipt at warehouse
2. **Inspection Checklist**:
   - Verify item matches return request
   - Check item condition (new/used/damaged)
   - Verify original packaging if applicable
   - Document any discrepancies

## Approval Criteria

### Auto-Approve (No Manager Review Required)
- Item confirmed defective
- Wrong item shipped
- Damaged in transit (with proof)
- Refund amount ≤ $100

### Requires Manager Approval
- Refund amount > $100
- Customer loyalty tier exceptions
- Replacement instead of refund requested

## Resolution Types

1. **Full Refund**: Item returned in acceptable condition
2. **Partial Refund**: Item has minor damage/wear
3. **Exchange**: Same item or equivalent replacement
4. **Store Credit**: Customer preference
5. **Rejected**: Policy violation or late submission

## Documentation Requirements

All return decisions must be logged with:
- Decision date
- Inspector ID
- Reason code
- Resolution type
- Refund amount (if applicable)
