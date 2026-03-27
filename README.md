# Google Merchant Center Feed Optimizer — How to Use

This guide walks you through downloading your product data, running the optimizer, and uploading a clean supplementary feed back to Google Merchant Center via Google Sheets.

---

## Step 1: Download Your Product Data from Google Merchant Center

1. Log in to [Google Merchant Center](https://merchants.google.com)
2. In the left sidebar go to **Products → All products**
3. Click the **download icon** (↓) in the top right of the product table
4. Choose **TSV** as the format and download the file
5. Save the file somewhere easy to find (e.g. your Downloads folder)

> **Tip:** If you have multiple feeds, download from the feed that contains the most complete product data. The optimizer works best with titles, descriptions, brand, and product type populated.

---

## Step 2: Run the Optimizer

### Option A — Via Claude (Cowork / Chat)

1. Open a new Claude session
2. Upload your downloaded TSV file
3. Type: *"Optimise this product feed"*
4. Claude will automatically trigger the **google-merchant-optimizer** skill
5. Follow any clarifying questions Claude asks (e.g. brand column name)
6. Download the optimised CSV file when Claude provides it

### Option B — Run the Python Script Directly

If you prefer to run it locally:

```bash
# Install Python 3 if not already installed
python optimizer.py your_feed.tsv output_feed.csv
```

The optimized CSV will be saved in the same folder as your input file.

---

## Step 3: Review the Optimised CSV

Before uploading, open the CSV in Excel or Google Sheets and do a quick sense-check:

- **Titles** — confirm they follow the `[Brand] [Product Type] [Key Attribute]` format and are under 70 characters
- **Descriptions** — confirm they read naturally and contain relevant keywords
- **google_product_category** — spot-check a few products to confirm the taxonomy path looks right
- **item_group_id** — confirm that product variants (different sizes/colours of the same item) share the same group ID
- **product_details** — confirm each entry has exactly 2 colons per attribute (e.g. `General:Brand:Nike`)
- **Missing GTINs** — the processing report will flag these; leave them blank rather than guessing

---

## Step 4: Create a Supplementary Feed in Google Merchant Center

A supplementary feed adds or overrides specific attributes without replacing your primary feed. This keeps pricing and availability untouched.

1. In Merchant Center go to **Products → Feeds**
2. Click the **blue + button** to add a new feed
3. Choose your **target country and language**
4. Select **Supplementary feed** as the feed type
5. Name it something clear, e.g. `SEO Optimized Attributes`
6. Choose **Google Sheets** as the input method
7. Select **Generate a new Google Sheet from a template** — Merchant Center will create a blank sheet with the correct column headers
8. Click **Continue** and note the Google Sheet URL it creates

---

## Step 5: Paste the Optimised CSV into the Google Sheet

1. Open the Google Sheet that Merchant Center created
2. Open your optimised CSV in Excel or Google Sheets
3. **Before pasting**, remove any columns from the CSV that could clash with your primary feed (see the list below)
4. Copy the remaining data and paste it into the Merchant Center Google Sheet, matching the column headers

### Columns to Remove Before Pasting

These attributes are managed by your primary feed. Including them in the supplementary feed can cause conflicts or policy warnings:

| Column | Why Remove |
|---|---|
| `price` | Managed by primary feed; conflicts cause disapprovals |
| `sale_price` | Same as above |
| `availability` | Must match primary feed exactly or products disapprove |
| `condition` | Only include if you intentionally want to override |
| `shipping` | Complex rules; safer to manage in primary feed or Merchant Center settings |
| `tax` | Same as shipping |
| `channel` | Shopify-specific metadata, not a valid supplementary field |
| `feed_label` | Internal Shopify field, not recognised by Google |
| `update_type` | Internal Shopify field, not recognised by Google |
| `language` | Set at the feed level, not per-product |

### Columns That Are Safe (and Recommended) to Include

| Column | Purpose |
|---|---|
| `id` | **Required** — links supplementary data to the right product |
| `title` | Overrides the primary feed title with the SEO-optimised version |
| `description` | Overrides the primary feed description |
| `google_product_category` | Ensures correct taxonomy classification |
| `product_highlight` | Adds bullet-point highlights (only in supplementary) |
| `product_details` | Adds structured attributes (only in supplementary) |
| `gender` | Fills in missing gender attribute |
| `age_group` | Fills in missing age group attribute |
| `item_group_id` | Groups variants for correct Shopping display |
| `brand` | Standardises brand name if inconsistent in primary feed |
| `color` | Adds or corrects colour attribute |
| `size` | Adds or corrects size attribute |
| `mpn` | Manufacturer part number, safe to include |
| `gtin` | Safe to include if correcting missing GTINs |

---

## Step 6: Fetch and Activate the Feed

1. Back in Merchant Center, go to your supplementary feed
2. Click **Fetch now** to trigger an immediate import from the Google Sheet
3. Wait a few minutes, then go to **Products → All products**
4. Check a few products to confirm the updated titles and descriptions are showing
5. Review the **Diagnostics** tab for any new errors or warnings introduced by the supplementary feed

---

## Troubleshooting

**Products disapproved after upload**
Check the Diagnostics tab. Common causes are malformed `product_details` (must have exactly 2 colons per entry) or a `google_product_category` path that doesn't match Google's official taxonomy exactly.

**Titles not updating**
Confirm the `id` column in your supplementary feed exactly matches the `id` in your primary feed — including case and any prefixes (e.g. `shopify_NZ_123` vs `123`).

**product_details not showing**
Each attribute must follow the exact format: `SectionName:AttributeName:Value`. Multiple attributes are comma-separated with no spaces around the commas.

**Feed fetch failing**
Ensure the Google Sheet is shared with the Merchant Center service account email shown in the feed settings (usually ending in `@merchantapi.iam.gserviceaccount.com`).
