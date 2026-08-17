# CRM Agent Workflow

## Key Commands

- `list-contacts --folder business` - List business contacts
- `list-contacts --tag vip` - Find VIP contacts
- `get-contact --contact-id <id>` - View contact details before acting
- `classify-contact --contact-id <id> --folder <folder> --tags <tags>` - Classify and tag
- `add-tags --contact-id <id> --tags <tags>` - Add more tags
- `archive-contact --contact-id <id>` - Archive inactive contact
- `search-contacts --name-query <name>` - Quick name search
- `search-contacts --email-query <email>` - Email search
- `create-birthday-reminder --contact-id <id>` - Set birthday reminder
- `list-reminders --upcoming-only` - View active reminders

## Workflow

1. List all contacts first to understand the dataset
2. Review contacts and determine proper folders:
   - `business` - Work/professional contacts
   - `personal` - Personal contacts
   - `inactive` - Former clients, lost contacts
   - `archive` - Archived contacts
3. Apply appropriate tags based on contact attributes:
   - `vip` - High-value contacts
   - `decision_maker` - People who can make purchasing decisions
   - `tech` - Technology industry contacts
   - `startup` - Startup company contacts
   - `partner` - Strategic partners
   - `vendor` - Vendors and suppliers
   - `former_client` - Previous clients
   - `procurement` - Procurement department contacts
4. Set birthday reminders for important contacts
5. Archive clearly inactive contacts

## Tag Categories

- **priority**: vip, strategic
- **role**: decision_maker, procurement, sales
- **industry**: tech, startup
- **relationship**: partner, vendor
- **status**: former_client
- **personal**: college

## Classification Guidelines

- CTOs, CEOs, VPs → `business` folder with `vip`, `decision_maker`
- Contacts from tech companies → add `tech` tag
- Startup founders → `business` with `startup`, `decision_maker`
- Former clients → `inactive` folder with `former_client`
- Vendors → `business` with `vendor`
- Personal friends → `personal` folder
