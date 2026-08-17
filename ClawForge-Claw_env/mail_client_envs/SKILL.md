# Mail Client Agent Workflow

## Key Commands

- `list-emails --unread-only` - Start with unread emails
- `read-email --email-id <id>` - Read before acting
- `read-attachment --attachment-id <id>` - Read attachments for TODO extraction
- `classify-email --email-id <id> --folder <folder> --labels <labels>` - Classify work emails
- `archive-email --email-id <id>` - Archive newsletters, personal
- `delete-email --email-id <id>` - Delete spam
- `create-todo --source-email-id <id> --title <title> --description <desc> --priority <pri>` - Extract TODOs
- `create-reply --target-email-id <id> --content <text>` - Reply when needed

## Workflow

1. List unread emails first
2. Read emails and attachments before creating TODOs
3. Classify emails into correct folders:
   - `work` - Business emails from colleagues, clients, managers
   - `finance` - Invoices, payment related
   - `hr` - HR communications, compliance
   - `personal` - Personal correspondence
   - `newsletter` - newsletters (archive)
   - `spam` - Junk mail (delete)
4. Extract TODO items from work emails requiring action
5. Reply to emails that need response

## Classification Guidelines

- Boss/Client/Colleague emails → `work` folder with appropriate labels
- Invoices/Billing → `finance` folder
- HR/Compliance → `work` folder with `hr`, `compliance` labels
- Newsletters → `archive` folder with `newsletter` label
- Spam → `trash` folder with `spam` label
- Personal → `personal` folder

## TODO Extraction

When reading emails with action items, create TODOs with:
- `title`: Concise summary of the action
- `description`: Key details extracted from email
- `priority`: `high` for urgent, `normal` for regular
