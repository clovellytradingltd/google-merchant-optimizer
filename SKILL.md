---
name: google-merchant-optimizer
description: |
  Optimize Google Merchant Center feed files for maximum SEO performance and Google compliance.
  Use this skill whenever you need to: enhance product titles and descriptions with high-volume keywords,
  auto-classify products using Google Product Taxonomy, structure product variations with item_group_id,
  add product highlights and structured details,
  or ensure brand names and attributes (size, color, material, gender) are properly formatted.
  Input: TSV or CSV feed file (raw or partially optimized).
  Output: SEO-optimized CSV feed ready for Google Merchant Center upload.
---

# Google Merchant Center Feed Optimizer

## Overview

This skill transforms raw or partially-optimized product feeds into SEO-optimized, Google-compliant feeds. It handles all key requirements: keyword research by category, product taxonomy classification, title/description optimization, and attribute structuring.

## Workflow

### Step 1: Load and Analyze the Feed

- Load the input feed (TSV, CSV, or other delimited format)
- Identify the current schema: which columns exist, which are missing
- Sample 5-10 products to understand data quality and variation
- Ask the user to clarify **brand information**:
  - Is a "brand" column present? If so, which column name?
  - Should the skill use official brand names from the data, or correct/standardize them?
  - Any brand naming conventions to follow?

### Step 2: Auto-Classify Products by Google Product Taxonomy

- Use Google's official Product Taxonomy: https://www.google.com/basepages/producttype/taxonomy.en-US.txt
- For each product, use the title and description to infer the most specific category
- Assign the full taxonomy path (e.g., `Home & Garden > Furniture > Chairs > Armchairs`)
- Store in a `google_product_category` column
- Document classification reasoning (useful for manual review later)

### Step 3: Keyword Research by Category

For each category discovered in Step 2:
- Identify 3-5 high-intent keywords specific to that product type
- Use educated estimation based on common search patterns and industry knowledge (no external API calls needed)
- Keywords should address:
  - Primary product type (e.g., "womens running shoes" for footwear)
  - Quality/feature signals (e.g., "breathable," "waterproof," "ergonomic")
  - Common modifiers (e.g., "lightweight," "organic," "eco-friendly")
- Document keywords by category so they can be reused across products

**Example: Women's T-Shirts category**
- Primary: "womens t shirt," "womens tee"
- Features: "organic cotton," "breathable," "stretch"
- Modifiers: "classic," "vintage," "oversized"

### Step 4: Optimize Titles

**Title Structure (Google Best Practice):**
```
[Brand] [Product Type] [Key Attribute] [Optional Feature/Benefit]
```

**Rules:**
- Include the primary keyword for the category
- Always include the brand name (from the feed or corrected)
- Aim for 40-70 characters (balance for readability and search)
- Include one key attribute if space allows (size, color, material, or benefit)
- Avoid keyword stuffing; maintain natural readability

**Example transformations:**
- Input: `Blue Shirt`
- Output: `Nike Womens Running Shirt Breathable Blue`

- Input: `XL Organic Cotton T-Shirt`
- Output: `Patagonia Organic Cotton Womens T-Shirt XL`

### Step 5: Optimize Descriptions

**Structure:**
1. Open with brand + primary product type + key keyword
2. Highlight 2-3 top features/benefits (material, fit, sustainability)
3. Include secondary keywords naturally
4. Add size/fit guidance if applicable
5. Close with a call-to-action or use case

**Length:** 150-200 words for descriptions (Google's sweet spot)

**Example:**
```
Patagonia Organic Cotton Womens T-Shirt combines sustainable materials with everyday comfort.
Made from 100% organic cotton, this classic tee offers breathable, soft-touch fabric perfect
for casual wear. Features a relaxed fit suitable for most body types and is available in XL
for comfortable, oversized styling. Ideal for eco-conscious shoppers seeking quality basics.
GTIN: 123456789012.
```

### Step 6: Add Product Highlights & Product Details

**Product Highlights** (for Google Shopping feed):
- Add a new `product_highlight` column with 2-3 bullet-point highlights
- Format: pipe-separated (`|`) or use Google's structured format
- Focus on differentiators: "Organic certified," "Waterproof," "Sustainably made"

**Product Details** (Google-compliant structured field):
- Add a `product_details` column with Google's required format
- Format: `section_name:attribute_name:attribute_value,section_name:attribute_name:attribute_value`
- **Critical:** Each entry must have exactly 2 colons (3 sub-attributes)
- Multiple attributes separated by comma (`,`)
- Sections: General, Specifications, Shipping, Features

**Example:**
```
product_highlight: "Melton Estate | Estate-Grown | Premium"

product_details: "General:Product Type:Wine,Specifications:Size:Bottle 750ml,Shipping:Weight:1 kg,General:Brand:Melton Estate"
```

### Step 7: Structure Variations with item_group_id

For products with multiple variations (sizes, colors):
- Create a unique `item_group_id` for each product family
- Give each variation a unique `id`
- Include variation-specific attributes in dedicated columns:
  - `size`
  - `color`
  - `material` (if varies)
  - `gender` (if varies)
- All variations of the same product share the same `item_group_id`

**Example:**
```
item_group_id     | id              | title                                  | color | size
T-SHIRT-001       | T-SHIRT-001-BLU | Nike Womens Running Shirt Breathable Blue | Blue  | M
T-SHIRT-001       | T-SHIRT-001-BL-L| Nike Womens Running Shirt Breathable Blue | Blue  | L
T-SHIRT-001       | T-SHIRT-001-RED | Nike Womens Running Shirt Breathable Red  | Red   | M
```

### Step 8: Ensure GTIN & MPN Fields

- If `gtin` column exists, keep it; validate format (UPC/EAN/ISBN)
- If `mpn` (manufacturer part number) exists, keep it
- If both are missing, note in a review column for manual addition later
- GTINs are critical for Google eligibility; flag any products missing them

### Step 9: Finalize & Output

**Output columns (CSV format):**
```
id, item_group_id, title, description, brand, google_product_category,
gtin, mpn, color, size, product type, gender, age_group, condition,
product_highlight, product_details,
image link, link, sku, [other original columns]
```

**Removed columns (API safety):**
- price, sale price
- availability (supplementary feed)
- all clicks, channel, language (metadata)
- update type, feed label (Shopify-specific)

**Output characteristics:**
- All products have gender (unisex by default) and age_group (adult by default)
- All products have condition set to "new"
- Missing categories auto-filled based on product type/title
- Variations grouped by item_group_id for proper Google Merchant Center handling
- Ready as a supplementary feed (no pricing/availability conflicts)

---

## What You Need to Provide

1. **Your feed file** (TSV, CSV, or other delimited format)
   - The skill auto-detects the format and processes accordingly

2. **Product data** - The skill handles variable data quality:
   - Titles and descriptions (required for optimization)
   - Brand names (will standardize and use consistently)
   - Product types/categories (skill auto-classifies if missing)
   - GTINs (optional but recommended for Google eligibility)
   - Any other custom fields (preserved in output)

3. **No action needed** on:
   - Gender/age group/condition assignment (automatically handled)
   - Category filling (automated based on product data)
   - Variation grouping (uses item_group_id or auto-generates)

---

## Best Practices Applied

- **Google Documentation Reference:** Uses Google's Product Taxonomy and Merchant Center feed specs
- **SEO Optimization:** Keywords placed naturally in titles and descriptions; structured highlights for visibility
- **Variation Handling:** item_group_id ensures color/size variants are properly grouped
- **Data Integrity:** GTIN/MPN validation; flagging of incomplete records
- **Scalability:** Handles 100s of products efficiently; documented approach for 1000s

---

## Output Deliverables

1. **Optimized CSV Feed** - Ready to upload to Google Merchant Center
2. **Processing Report** - Summary of classifications, keywords by category, flagged issues
3. **Before/After Sample** - 5-10 products showing original vs. optimized versions (for review)
4. **Keyword Reference** - By-category keyword list for future optimization rounds
