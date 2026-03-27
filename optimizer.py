#!/usr/bin/env python3
"""
Google Merchant Center Feed Optimizer
Optimizes product feeds for SEO and Google compliance
Works with any product category feed.
"""

import csv
import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# ============================================================================
# KEYWORD RESEARCH DATABASE
# ============================================================================
# Curated 3-5 keywords per category based on search volume & intent
# Covers broad Google Product Taxonomy verticals

CATEGORY_KEYWORDS = {
    # Apparel & Accessories
    "apparel": {
        "primary": ["clothing", "fashion", "wear"],
        "features": ["breathable", "comfortable", "durable", "stylish"],
        "modifiers": ["premium", "classic", "everyday", "versatile"]
    },
    "tops": {
        "primary": ["t-shirt", "shirt", "top", "tee"],
        "features": ["cotton", "breathable", "soft", "lightweight"],
        "modifiers": ["classic", "casual", "oversized", "fitted"]
    },
    "bottoms": {
        "primary": ["pants", "jeans", "shorts", "trousers"],
        "features": ["stretch", "slim fit", "relaxed fit", "durable"],
        "modifiers": ["casual", "everyday", "comfortable", "stylish"]
    },
    "footwear": {
        "primary": ["shoes", "sneakers", "boots", "sandals"],
        "features": ["cushioned", "breathable", "supportive", "lightweight"],
        "modifiers": ["athletic", "casual", "performance", "comfortable"]
    },
    "outerwear": {
        "primary": ["jacket", "coat", "hoodie", "windbreaker"],
        "features": ["waterproof", "insulated", "windproof", "packable"],
        "modifiers": ["all-weather", "lightweight", "warm", "versatile"]
    },
    "accessories": {
        "primary": ["bag", "backpack", "hat", "belt", "wallet"],
        "features": ["durable", "functional", "stylish", "lightweight"],
        "modifiers": ["premium", "everyday", "compact", "versatile"]
    },

    # Electronics
    "electronics": {
        "primary": ["electronics", "device", "gadget", "tech"],
        "features": ["high performance", "energy efficient", "wireless", "smart"],
        "modifiers": ["advanced", "professional", "compact", "portable"]
    },
    "computers": {
        "primary": ["laptop", "computer", "PC", "notebook"],
        "features": ["fast processor", "long battery life", "lightweight", "high resolution"],
        "modifiers": ["portable", "powerful", "ultra-thin", "business"]
    },
    "phones": {
        "primary": ["smartphone", "mobile phone", "cell phone"],
        "features": ["5G", "long battery", "high resolution camera", "fast charging"],
        "modifiers": ["flagship", "compact", "durable", "waterproof"]
    },
    "audio": {
        "primary": ["headphones", "earbuds", "speaker", "audio"],
        "features": ["noise cancelling", "wireless", "high fidelity", "bass"],
        "modifiers": ["premium", "portable", "studio quality", "immersive"]
    },

    # Home & Garden
    "home & garden": {
        "primary": ["home decor", "furniture", "garden", "household"],
        "features": ["durable", "easy assembly", "space-saving", "modern design"],
        "modifiers": ["premium", "elegant", "functional", "stylish"]
    },
    "furniture": {
        "primary": ["furniture", "chair", "table", "sofa", "desk"],
        "features": ["solid wood", "ergonomic", "easy assembly", "durable"],
        "modifiers": ["modern", "contemporary", "minimalist", "classic"]
    },
    "kitchen": {
        "primary": ["kitchen", "cookware", "appliance", "utensil"],
        "features": ["non-stick", "dishwasher safe", "heat resistant", "durable"],
        "modifiers": ["professional", "everyday", "premium", "eco-friendly"]
    },
    "tools": {
        "primary": ["tool", "drill", "saw", "wrench", "power tool"],
        "features": ["cordless", "heavy duty", "ergonomic grip", "long battery"],
        "modifiers": ["professional", "compact", "powerful", "reliable"]
    },

    # Beauty & Personal Care
    "beauty": {
        "primary": ["beauty", "skincare", "makeup", "cosmetics"],
        "features": ["natural ingredients", "cruelty-free", "long lasting", "hydrating"],
        "modifiers": ["organic", "premium", "gentle", "dermatologist tested"]
    },
    "skincare": {
        "primary": ["moisturiser", "serum", "face cream", "sunscreen"],
        "features": ["hydrating", "anti-aging", "SPF protection", "vitamin C"],
        "modifiers": ["gentle", "daily", "clinically tested", "natural"]
    },

    # Sports & Outdoors
    "sports": {
        "primary": ["sports", "athletic", "fitness", "exercise"],
        "features": ["performance", "breathable", "moisture wicking", "flexible"],
        "modifiers": ["professional", "lightweight", "durable", "high performance"]
    },
    "outdoor": {
        "primary": ["outdoor", "camping", "hiking", "adventure gear"],
        "features": ["weatherproof", "durable", "lightweight", "compact"],
        "modifiers": ["all-terrain", "rugged", "portable", "expedition"]
    },

    # Food & Beverages
    "food": {
        "primary": ["food", "snack", "organic food", "gourmet"],
        "features": ["organic", "natural", "non-GMO", "gluten-free"],
        "modifiers": ["premium", "artisan", "healthy", "delicious"]
    },
    "beverages": {
        "primary": ["drink", "beverage", "juice", "coffee", "tea"],
        "features": ["natural", "no artificial flavours", "refreshing", "premium blend"],
        "modifiers": ["organic", "artisan", "cold brew", "single origin"]
    },

    # Toys & Games
    "toys": {
        "primary": ["toy", "game", "puzzle", "educational toy"],
        "features": ["safe materials", "educational", "durable", "engaging"],
        "modifiers": ["fun", "interactive", "creative", "award winning"]
    },

    # Health & Wellness
    "health": {
        "primary": ["health supplement", "vitamin", "wellness", "nutrition"],
        "features": ["natural ingredients", "clinically tested", "high potency", "easy to digest"],
        "modifiers": ["daily", "premium", "certified", "pharmaceutical grade"]
    },

    # Pet Supplies
    "pet supplies": {
        "primary": ["pet food", "dog food", "cat food", "pet toy"],
        "features": ["natural ingredients", "grain-free", "vet approved", "durable"],
        "modifiers": ["premium", "healthy", "all-natural", "breed-specific"]
    },

    # Automotive
    "automotive": {
        "primary": ["car accessory", "auto part", "vehicle", "car care"],
        "features": ["universal fit", "durable", "easy install", "high performance"],
        "modifiers": ["professional", "heavy duty", "OEM quality", "reliable"]
    },

    # Gift & Specialty
    "gift": {
        "primary": ["gift", "gift set", "gift box", "present"],
        "features": ["premium packaging", "curated", "luxury", "personalised"],
        "modifiers": ["exclusive", "thoughtful", "unique", "memorable"]
    },

    # General fallback
    "general": {
        "primary": ["product", "item", "quality product"],
        "features": ["premium quality", "durable", "reliable", "well-made"],
        "modifiers": ["excellent", "professional", "trusted", "best-selling"]
    }
}

# ============================================================================
# GOOGLE TAXONOMY MAPPING
# Maps taxonomy path keywords to our internal category buckets
# ============================================================================

TAXONOMY_CATEGORY_MAP = [
    # Apparel
    (["apparel", "clothing", "shirt", "t-shirt", "top", "blouse", "jersey"], "tops"),
    (["pants", "jeans", "shorts", "trousers", "leggings", "skirt"], "bottoms"),
    (["shoes", "footwear", "sneakers", "boots", "sandals", "heels", "loafers"], "footwear"),
    (["jacket", "coat", "hoodie", "outerwear", "windbreaker", "parka"], "outerwear"),
    (["bag", "handbag", "backpack", "wallet", "hat", "cap", "belt", "scarf", "gloves"], "accessories"),

    # Electronics
    (["laptop", "computer", "notebook", "desktop"], "computers"),
    (["phone", "smartphone", "mobile", "tablet"], "phones"),
    (["headphone", "earphone", "earbuds", "speaker", "audio", "sound"], "audio"),
    (["camera", "television", "tv", "monitor", "electronics", "gadget"], "electronics"),

    # Home & Garden
    (["furniture", "chair", "table", "sofa", "desk", "shelf", "bed", "cabinet"], "furniture"),
    (["kitchen", "cookware", "pan", "pot", "bakeware", "utensil", "appliance"], "kitchen"),
    (["tool", "drill", "saw", "wrench", "hardware", "power tool"], "tools"),
    (["home", "garden", "decor", "lamp", "rug", "curtain", "bedding"], "home & garden"),

    # Beauty
    (["skincare", "moisturiser", "serum", "sunscreen", "face cream"], "skincare"),
    (["beauty", "makeup", "cosmetics", "lipstick", "foundation", "mascara"], "beauty"),

    # Sports
    (["outdoor", "camping", "hiking", "tent", "sleeping bag", "backpack trail"], "outdoor"),
    (["sports", "fitness", "exercise", "gym", "athletic", "yoga", "cycling"], "sports"),

    # Food & Beverages
    (["coffee", "tea", "juice", "drink", "beverage", "water"], "beverages"),
    (["food", "snack", "grocery", "organic food", "gourmet", "supplement", "vitamin", "nutrition"], "food"),

    # Toys
    (["toy", "game", "puzzle", "doll", "board game", "kids"], "toys"),

    # Health
    (["health", "wellness", "vitamin", "supplement", "medicine", "medical"], "health"),

    # Pets
    (["pet", "dog", "cat", "animal", "bird", "fish"], "pet supplies"),

    # Automotive
    (["car", "automotive", "vehicle", "truck", "auto", "tyre"], "automotive"),

    # Gift
    (["gift", "hamper", "gift basket", "gift box", "gift set", "gift card"], "gift"),
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_category_type(google_category: str, title: str = "", product_type: str = "") -> str:
    """
    Extract internal category type from Google Product Category path,
    falling back to title and product_type inference.
    """
    combined = f"{google_category} {title} {product_type}".lower()

    for keywords, category in TAXONOMY_CATEGORY_MAP:
        if any(kw in combined for kw in keywords):
            return category

    return "general"


def get_keywords_for_category(category_type: str) -> Dict[str, List[str]]:
    """Retrieve keyword set for a category type"""
    return CATEGORY_KEYWORDS.get(category_type, CATEGORY_KEYWORDS["general"])


def build_optimized_title(product: Dict, category_type: str, keywords: Dict) -> str:
    """
    Build SEO-optimized title following best practices:
    [Brand] [Key Product Name] [Key Attribute]
    Target: 40-70 characters
    """
    brand = product.get("brand", "").strip()
    original_title = product.get("title", "").strip()
    size = product.get("size", "").strip()
    color = product.get("color", "").strip()

    parts = []

    # Add brand if present
    if brand:
        parts.append(brand)

    if original_title:
        clean_title = original_title

        # Remove brand from start of title to avoid duplication
        if brand and clean_title.lower().startswith(brand.lower()):
            clean_title = clean_title[len(brand):].strip(" -–:")

        parts.append(clean_title)

    # Add color if not already in title and space permits
    if color and color.lower() not in ["unknown", ""] and color.lower() not in " ".join(parts).lower():
        parts.append(color)

    # Add size/format at the end if present and not already in title
    if size and size.lower() not in ["unknown", ""] and size.lower() not in " ".join(parts).lower():
        parts.append(size)

    optimized = " ".join(p for p in parts if p).strip()

    # Trim to 70 chars if needed
    if len(optimized) > 70:
        optimized = optimized[:67] + "..."

    return optimized


def build_optimized_description(product: Dict, category_type: str, keywords: Dict) -> str:
    """
    Build SEO-optimized description (150-200 words)
    Structure: Brand + Product + Keywords → Features → Attributes → Use case
    """
    brand = product.get("brand", "").strip() or ""
    description = product.get("description", "").strip()
    size = product.get("size", "").strip()
    color = product.get("color", "").strip()
    product_type = product.get("product type", "").strip() or "product"

    # Clean up existing description (remove HTML, extra whitespace)
    description = re.sub(r'<[^>]+>', '', description)
    description = re.sub(r'\s+', ' ', description).strip()

    lines = []

    # Opening: Brand + Product Type + Primary Keyword
    primary_keyword = keywords["primary"][0] if keywords["primary"] else product_type.lower()
    brand_part = f"{brand} " if brand else ""
    opening = f"{brand_part}{product_type} – a {primary_keyword} built for quality and performance."
    lines.append(opening)

    # Features paragraph: use original description first, then supplement with keywords
    features = []
    if description and len(description) > 20:
        sentences = description.split(". ")[:2]
        features.extend([s.strip() for s in sentences if s.strip()])

    for feature in keywords["features"][:2]:
        if feature.lower() not in " ".join(features).lower():
            features.append(f"Features {feature} construction and design.")

    if features:
        lines.append(" ".join(features))

    # Attributes paragraph
    attrs = []
    if color and color.lower() not in ["unknown", ""]:
        attrs.append(f"Color: {color}")
    if size and size.lower() not in ["unknown", ""]:
        attrs.append(f"Size: {size}")
    if attrs:
        lines.append(". ".join(attrs) + ".")

    # Closing
    modifier = keywords["modifiers"][0] if keywords["modifiers"] else "premium"
    closing = f"Ideal for those seeking a {modifier} option. Perfect for everyday use or as a gift."
    lines.append(closing)

    full_desc = " ".join(lines).strip()

    # Trim to ~1200 chars (~200 words)
    if len(full_desc) > 1200:
        full_desc = full_desc[:1197] + "..."

    return full_desc


def build_product_highlights(product: Dict, keywords: Dict) -> str:
    """
    Build product highlights as pipe-separated bullet points
    Format: "Feature 1 | Feature 2 | Feature 3"
    """
    highlights = []

    brand = product.get("brand", "").strip()
    if brand:
        highlights.append(brand)

    if keywords["features"]:
        highlights.append(keywords["features"][0].title())

    if keywords["modifiers"]:
        highlights.append(keywords["modifiers"][0].title())

    return " | ".join(highlights[:3])


def build_product_details(product: Dict) -> str:
    """
    Build structured product details in Google format.
    Format: section_name:attribute_name:attribute_value,...
    Google requires exactly 2 colons per entry.
    """
    details = []

    product_type = product.get("product type", "").strip()
    if product_type:
        details.append(f"General:Product Type:{product_type}")

    size = product.get("size", "").strip()
    if size and size.lower() not in ["unknown", ""]:
        details.append(f"Specifications:Size:{size}")

    color = product.get("color", "").strip()
    if color and color.lower() not in ["unknown", ""]:
        details.append(f"Specifications:Color:{color}")

    material = product.get("material", "").strip()
    if material and material.lower() not in ["unknown", ""]:
        details.append(f"Specifications:Material:{material}")

    shipping_weight = product.get("shipping weight", "").strip()
    if shipping_weight and shipping_weight not in ["0 kg", "0 lb", ""]:
        details.append(f"Shipping:Weight:{shipping_weight}")

    brand = product.get("brand", "").strip()
    if brand:
        details.append(f"General:Brand:{brand}")

    return ",".join(details)


def assign_gender(product: Dict) -> str:
    """
    Assign gender attribute. Infer from title/description if possible,
    default to 'unisex'.
    """
    gender = product.get("gender", "").strip()
    if gender and gender.lower() not in ["", "unknown"]:
        return gender.lower()

    combined = f"{product.get('title', '')} {product.get('description', '')}".lower()

    if any(w in combined for w in ["womens", "women's", "female", "ladies", "girls"]):
        return "female"
    if any(w in combined for w in ["mens", "men's", "male", "boys"]):
        return "male"

    return "unisex"


def assign_age_group(product: Dict) -> str:
    """
    Assign age group. Default to 'adult' unless product is clearly for children.
    """
    age_group = product.get("age group", "").strip()
    if age_group and age_group.lower() not in ["", "unknown"]:
        return age_group

    combined = f"{product.get('title', '')} {product.get('description', '')}".lower()

    if any(w in combined for w in ["kids", "child", "children", "boy", "girl", "baby", "toddler", "infant", "youth"]):
        return "kids"

    return "adult"


def assign_condition(product: Dict) -> str:
    """
    Assign condition. Uses existing value if present, defaults to 'new'.
    """
    condition = product.get("condition", "").strip().lower()
    if condition in ["new", "refurbished", "used"]:
        return condition
    return "new"


def fill_missing_category(product: Dict) -> str:
    """
    Fill in missing Google Product Category using title and product type.
    Returns the most specific category path available.
    """
    category = product.get("google product category", "").strip()

    if category and category.lower() not in ["", "unknown"]:
        return category

    title = product.get("title", "").lower()
    product_type = product.get("product type", "").lower()
    combined = f"{title} {product_type}"

    # Apparel
    if any(w in combined for w in ["shirt", "t-shirt", "tee", "top", "blouse"]):
        return "Apparel & Accessories > Clothing > Tops"
    if any(w in combined for w in ["pants", "jeans", "shorts", "trousers"]):
        return "Apparel & Accessories > Clothing > Bottoms"
    if any(w in combined for w in ["shoes", "sneakers", "boots", "sandals", "footwear"]):
        return "Apparel & Accessories > Shoes"
    if any(w in combined for w in ["jacket", "coat", "hoodie", "outerwear"]):
        return "Apparel & Accessories > Clothing > Outerwear"
    if any(w in combined for w in ["bag", "backpack", "handbag", "wallet"]):
        return "Apparel & Accessories > Handbags, Wallets & Cases"

    # Electronics
    if any(w in combined for w in ["laptop", "computer", "notebook"]):
        return "Electronics > Computers > Laptops"
    if any(w in combined for w in ["phone", "smartphone", "mobile"]):
        return "Electronics > Communications > Phones"
    if any(w in combined for w in ["headphone", "earbuds", "speaker"]):
        return "Electronics > Audio > Headphones"
    if any(w in combined for w in ["electronics", "gadget", "device"]):
        return "Electronics"

    # Home & Garden
    if any(w in combined for w in ["furniture", "chair", "table", "sofa", "desk"]):
        return "Furniture"
    if any(w in combined for w in ["kitchen", "cookware", "pan", "pot"]):
        return "Kitchen & Dining > Cookware"
    if any(w in combined for w in ["tool", "drill", "saw", "hardware"]):
        return "Hardware > Tools"
    if any(w in combined for w in ["home", "decor", "garden"]):
        return "Home & Garden"

    # Beauty
    if any(w in combined for w in ["skincare", "moisturiser", "serum", "sunscreen"]):
        return "Health & Beauty > Personal Care > Skin Care"
    if any(w in combined for w in ["makeup", "cosmetics", "beauty"]):
        return "Health & Beauty > Beauty > Makeup"

    # Sports
    if any(w in combined for w in ["camping", "hiking", "outdoor"]):
        return "Sporting Goods > Outdoor Recreation > Camping & Hiking"
    if any(w in combined for w in ["sports", "fitness", "gym", "athletic"]):
        return "Sporting Goods"

    # Food & Beverages
    if any(w in combined for w in ["coffee", "tea", "beverage", "drink"]):
        return "Food, Beverages & Tobacco > Beverages"
    if any(w in combined for w in ["food", "snack", "grocery", "gourmet"]):
        return "Food, Beverages & Tobacco > Food Items"

    # Toys
    if any(w in combined for w in ["toy", "game", "puzzle", "kids"]):
        return "Toys & Games"

    # Health
    if any(w in combined for w in ["supplement", "vitamin", "health", "wellness"]):
        return "Health & Beauty > Health Care > Vitamins & Supplements"

    # Pets
    if any(w in combined for w in ["pet", "dog", "cat", "animal"]):
        return "Animals & Pet Supplies"

    # Automotive
    if any(w in combined for w in ["car", "automotive", "vehicle", "auto"]):
        return "Vehicles & Parts > Vehicle Accessories"

    # Gift
    if any(w in combined for w in ["gift", "hamper", "gift basket", "gift set"]):
        return "Arts & Entertainment > Party & Celebration > Gift Wrapping"

    return "Shopping"


def create_item_group_mapping(products: List[Dict]) -> Dict[str, List[int]]:
    """
    Create item_group_id for product variations.
    Groups by base product name (excluding size/color suffixes).
    """
    group_map = defaultdict(list)

    for idx, product in enumerate(products):
        title = product.get("title", "").strip()
        product_type = product.get("product type", "").strip()
        item_group_id = product.get("item group id", "").strip()

        if item_group_id:
            group_map[item_group_id].append(idx)
        else:
            # Strip common variation suffixes to find base product name
            base_name = re.sub(
                r'\s*[-–]?\s*(size|colour|color|variant|pack|set|bundle|small|medium|large|xl|xxl|xs|\d+ml|\d+g|\d+oz)\b.*',
                '', title, flags=re.IGNORECASE
            ).strip()
            group_key = f"{base_name}_{product_type}".lower()
            group_key = re.sub(r'[^a-z0-9_]', '_', group_key)
            group_map[group_key].append(idx)

    return dict(group_map)


# ============================================================================
# MAIN OPTIMIZER
# ============================================================================

class MerchantFeedOptimizer:
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.products = []
        self.output_file = None
        self.report = {
            "total_processed": 0,
            "categories": defaultdict(int),
            "missing_gtin": [],
            "missing_category": [],
            "variations_grouped": 0,
            "keyword_stats": defaultdict(list)
        }

    def load_feed(self):
        """Load TSV/CSV feed file"""
        print(f"Loading feed from {self.input_file}...")

        with open(self.input_file, 'r', encoding='utf-8') as f:
            sample = f.readline()
            delimiter = '\t' if '\t' in sample else ','
            f.seek(0)

            reader = csv.DictReader(f, delimiter=delimiter)
            self.products = list(reader)

        print(f"✓ Loaded {len(self.products)} products")

    def optimize_products(self):
        """Run optimization on all products"""
        print("\nOptimizing products...")

        # Step 1: Create item group mapping for variations
        item_group_mapping = create_item_group_mapping(self.products)

        # Step 2: Optimize each product
        optimized_products = []

        for idx, product in enumerate(self.products):
            category_type = extract_category_type(
                product.get("google product category", ""),
                product.get("title", ""),
                product.get("product type", "")
            )
            keywords = get_keywords_for_category(category_type)

            # Build optimized fields
            optimized = {
                **product,
                "title": build_optimized_title(product, category_type, keywords),
                "description": build_optimized_description(product, category_type, keywords),
                "product_highlight": build_product_highlights(product, keywords),
                "product_details": build_product_details(product),
                "google_product_category": fill_missing_category(product),
                "gender": assign_gender(product),
                "age_group": assign_age_group(product),
                "condition": assign_condition(product),
            }

            # Handle item_group_id
            if not product.get("item group id", "").strip():
                title = product.get("title", "").strip()
                product_type_val = product.get("product type", "").strip()
                base_name = re.sub(
                    r'\s*[-–]?\s*(size|colour|color|variant|pack|set|bundle|small|medium|large|xl|xxl|xs|\d+ml|\d+g|\d+oz)\b.*',
                    '', title, flags=re.IGNORECASE
                ).strip()
                group_key = f"{base_name}_{product_type_val}".lower()
                group_key = re.sub(r'[^a-z0-9_]', '_', group_key)
                optimized["item_group_id"] = group_key
            else:
                optimized["item_group_id"] = product.get("item group id", "")

            # Track reporting
            self.report["total_processed"] += 1
            self.report["categories"][category_type] += 1
            self.report["keyword_stats"][category_type].append(keywords)

            if not product.get("gtin", "").strip():
                self.report["missing_gtin"].append(product.get("id", "unknown"))

            if not product.get("google product category", "").strip():
                self.report["missing_category"].append(product.get("id", "unknown"))

            optimized_products.append(optimized)

        self.products = optimized_products
        print(f"✓ Optimized {len(self.products)} products")

    def save_output(self, output_file: str = None):
        """Save optimized feed as CSV"""
        if output_file is None:
            input_path = Path(self.input_file)
            output_file = input_path.parent / f"{input_path.stem}_optimized.csv"

        self.output_file = output_file

        print(f"\nSaving optimized feed to {output_file}...")

        # Columns to exclude (API-interfering fields)
        exclude_cols = {
            'price', 'sale price', 'availability', 'all clicks', 'channel', 'language',
            'update type', 'feed label'
        }

        # Define output column order (important fields first)
        standard_cols = [
            'id', 'item_group_id', 'title', 'description', 'brand', 'google_product_category',
            'gtin', 'mpn', 'color', 'size', 'product type', 'gender', 'age_group', 'condition',
            'product_highlight', 'product_details',
            'image link', 'link', 'sku'
        ]

        # Collect all columns from output, minus excluded
        all_cols = set()
        for product in self.products:
            all_cols.update(product.keys())
        all_cols = all_cols - exclude_cols

        # Put standard cols first, then remaining
        fieldnames = []
        for col in standard_cols:
            if col in all_cols:
                fieldnames.append(col)
        for col in sorted(all_cols):
            if col not in fieldnames:
                fieldnames.append(col)

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(self.products)

        print(f"✓ Saved {len(self.products)} products to {output_file}")

    def generate_report(self) -> str:
        """Generate optimization report"""
        report = []
        report.append("\n" + "="*70)
        report.append("GOOGLE MERCHANT CENTER FEED OPTIMIZATION REPORT")
        report.append("="*70)

        report.append(f"\nTotal Products Processed: {self.report['total_processed']}")

        report.append("\n📊 Products by Category:")
        for category, count in sorted(self.report["categories"].items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {category.title()}: {count}")

        report.append(f"\n⚠️  Products Missing GTIN: {len(self.report['missing_gtin'])}")
        if self.report['missing_gtin'][:5]:
            report.append(f"  First 5: {', '.join(self.report['missing_gtin'][:5])}")

        report.append(f"\n⚠️  Products Missing Category: {len(self.report['missing_category'])}")

        report.append(f"\n✓ Optimizations Applied:")
        report.append("  • Titles optimized for SEO (brand + product + key attribute)")
        report.append("  • Descriptions enhanced with category-specific keywords")
        report.append("  • Product highlights added (pipe-separated)")
        report.append("  • Product details structured (Google format)")
        report.append("  • Google Product Category auto-classified")
        report.append("  • Gender and age_group inferred and assigned")
        report.append("  • Condition standardised")
        report.append("  • Item group IDs created for variation grouping")

        report.append(f"\n📁 Output File: {self.output_file}")
        report.append("="*70 + "\n")

        return "\n".join(report)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys

    input_file = sys.argv[1] if len(sys.argv) > 1 else "products.tsv"
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    optimizer = MerchantFeedOptimizer(input_file)
    optimizer.load_feed()
    optimizer.optimize_products()
    optimizer.save_output(output_file)

    print(optimizer.generate_report())
