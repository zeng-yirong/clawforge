Subject: Urgent – Clean up the sales dump

Hi there,

I’m Samantha from Sales Ops. We just got a fresh dump of raw transactions dumped into `data/sales_raw.csv`. I took a quick peek and it’s a mess – duplicate rows, missing product names, and some records with zero amounts that shouldn’t be there.

I need you to get this cleaned up and produce a quick summary so I can present it at the 4pm review. Here’s what I’m after:

- Get rid of exact duplicates – keep only the first occurrence.
- Some rows have empty product names; luckily the same product ID appears elsewhere in the file with the name filled in. Please fill those blanks with the correct name.
- Drop any transaction where either sales_amount or quantity is zero or negative – those are junk.
- Then group the remaining valid sales by product category and **sum up the sales_amount** for each category.

Put the result into a file called `report/product_summary.json`. I need it in a simple format – just an object where each key is the category name and the value is the total sales amount for that category.

I need this done before the meeting. Thanks!

Samantha
