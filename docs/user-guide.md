# InkAutoGen User Guide

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [Creating SVG Templates](#creating-svg-templates)
3. [Preparing CSV Data](#preparing-csv-data)
4. [Running the Extension](#running-the-extension)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)
7. [Examples and Demos](#examples-and-demos)

## 🚀 Getting Started

### Prerequisites
- **Inkscape** 1.0 or higher installed
- **Python** 3.7+ (usually comes with Inkscape)
- Basic understanding of CSV files

### Installation
1. Download the extension files
2. Run the setup script:
   ```bash
   ./setup.sh
   ```
3. Restart Inkscape
4. Verify installation: `Extensions → Export → InkAutoGen`

## 🎨 Creating SVG Templates

### Understanding the Basic Patterns

InkAutoGen uses **two fundamental patterns** to connect your CSV data with SVG elements:

#### **Pattern 1: Data Replacement `<element_label>`**
- **Purpose**: Replace the content of SVG elements
- **Used for**: Text content, image files, visibility states
- **Example**: `name`, `photo`, `title`

#### **Pattern 2: Property Modification `<element_label>##<property>`**
- **Purpose**: Change properties/attributes of SVG elements  
- **Used for**: Colors, fonts, sizes, positions, transformations
- **Example**: `button##fill`, `title##font-size`, `frame##stroke`

### Step 1: Design Your Template
Create any SVG design in Inkscape that you want to customize with data.

### Step 2: Add Element Labels
For each element you want to customize:

1. **Select the element** (text, image, shape, etc.)
2. **Open Object Properties**: `Object → Object Properties` (or `Shift+Ctrl+O`)
3. **Set the ID/Label** using angle brackets:
   - Text elements: `name`, `title`, `description`
   - Images: `photo`, `logo`, `background`
   - Shapes: `button`, `frame`, `badge`

### Step 3: Label Naming Conventions

#### Basic Data Replacement Labels
```
<name>          # Replace text content
<photo>         # Replace with image file
<title>         # Replace text content
<email>         # Replace text content
<show_layer>    # Control layer visibility (true/false)
```

#### Property Modification Labels
```
button##fill           # Change button background color
title##font-size       # Change title text size
frame##stroke          # Change frame border color
text##font-family      # Change text font
shape##width           # Change element width
logo##opacity          # Change logo transparency
```

### Pattern Examples with Visual Results

#### Example 1: Business Card Template
```
SVG Elements & Labels:
├── Text: name → "John Doe"
├── Text: title → "Software Engineer"  
├── Image: photo → "john.jpg"
├── Rectangle: card##fill → "#ffffff"
└── Text: title##font-size → "24"

CSV Headers:
name,title,photo,card##fill,title##font-size

Result: Personalized business card with white background and 24px title
```

#### Example 2: Certificate Template
```
SVG Elements & Labels:
├── Text: recipient_name → "Jane Smith"
├── Text: course_name → "Python Programming"
├── Text: completion_date → "2024-01-15"
├── Border: certificate##stroke → "#gold"
└── Seal: seal##opacity → "0.8"

CSV Headers:
recipient_name,course_name,completion_date,certificate##stroke,seal##opacity

Result: Custom certificate with gold border and semi-transparent seal
```

### Supported Properties
| Property | Description | Example Values |
|----------|-------------|----------------|
| `fill` | Background color | `#ff0000`, `red`, `rgb(255,0,0)` |
| `stroke` | Border color | `#000000`, `black` |
| `font-size` | Text size | `24`, `32px`, `2em` |
| `font-family` | Font name | `Arial`, `Times New Roman` |
| `font-weight` | Text weight | `bold`, `normal`, `600` |
| `width` | Element width | `100`, `200px` |
| `height` | Element height | `50`, `75px` |
| `opacity` | Transparency | `0.5`, `50%` |
| `rotate` | Rotation angle | `45`, `90deg` |
| `scale` | Scale factor | `1.5`, `200%` |

## 📊 Preparing CSV Data

### Understanding CSV Structure
Your CSV file acts as a **data map** that tells InkAutoGen how to modify your SVG template. Each column header matches an SVG element label or property.

### Basic CSV Structure
Create a CSV file with headers matching your element labels:

```csv
name,title,email,department,photo
John Doe,Senior Engineer,john@company.com,Engineering,john.jpg
Jane Smith,Lead Designer,jane@company.com,Marketing,jane.png
Bob Johnson,Project Manager,bob@company.com,Operations,bob.jpg
```

#### How It Works:
- `name` column → finds SVG element labeled `name` and replaces content with "John Doe"
- `title` column → finds SVG element labeled `title` and replaces content with "Senior Engineer"
- `photo` column → finds SVG element labeled `photo` and replaces with "john.jpg"

### CSV with Property Modifications
Include property columns using the `##` syntax to change element properties:

```csv
name,email,button##fill,title##font-size,frame##stroke
John Doe,john@company.com,#ff0000,24,#000000
Jane Smith,jane@company.com,#00ff00,32,#333333
Bob Johnson,bob@company.com,#0000ff,28,#666666
```

#### How Properties Work:
- `button##fill` → finds element labeled `button` and sets its background color
- `title##font-size` → finds element labeled `title` and sets font size to 24px
- `frame##stroke` → finds element labeled `frame` and sets border color

### Complete Example: Employee ID Cards

#### SVG Template Setup:
```
├── Text: employee_name
├── Text: employee_title
├── Text: employee_id
├── Image: employee_photo
├── Rectangle: card_background##fill
├── Text: company_logo##width
└── Border: card_border##stroke
```

#### CSV Data:
```csv
employee_name,employee_title,employee_id,employee_photo,card_background##fill,company_logo##width,card_border##stroke
John Smith,Software Engineer,EMP001,john.jpg,#ffffff,200,#0066cc
Jane Davis,Project Manager,EMP002,jane.png,#f0f0f0,180,#cc6600
```

#### Generated Results:
- **Row 1**: White background card with blue border, 200px logo, "John Smith" text
- **Row 2**: Light gray background card with orange border, 180px logo, "Jane Davis" text

### CSV Data Types and Formats

#### Text Content
```csv
name  # Simple text
title  # Multi-word text
description  # Longer text with spaces
```

#### Image Files
```csv
photo  # Image filename (john.jpg)
logo  # Image filename (company.png)
background  # Image filename (bg.svg)
```

#### Boolean Values (Layer Visibility)
```csv
show_header  # true/false, 1/0, yes/no
hide_watermark  # Controls layer visibility
```

#### Color Values
```csv
button##fill  # Hex: #ff0000, Name: red, RGB: rgb(255,0,0)
text##stroke  # Any valid CSS color format
```

#### Size Values
```csv
title##font-size  # 24, 32px, 2em, 1.5rem
logo##width  # 200, 200px, 50%
frame##height  # 100, 100px
```

### CSV File Guidelines

#### File Format
- **Encoding**: UTF-8 recommended (auto-detected)
- **Delimiter**: Comma (`,`)
- **Headers**: Required on first row
- **Row Limit**: Maximum 10,000 rows

#### Column Types
1. **Element Values**: Direct content replacement
   - `name` → "John Doe"
   - `photo` → "john.jpg"

2. **Properties**: Style modifications
   - `button##fill` → "#ff0000"
   - `title##font-size` → "24"

#### Special Values
- **Empty cells**: Skip replacement
- **Boolean values**: `true`/`false` for visibility
- **File paths**: Relative or absolute paths for images

## 🏃 Running the Extension

### Step 1: Open Your Template
1. Launch Inkscape
2. Open your labeled SVG template file

### Step 2: Access the Extension
`Extensions → Export → InkAutoGen`

### Step 3: Configure Options

#### File Selection
- **CSV File**: Choose your data file
- **Output Directory**: Where generated files will be saved

#### Export Settings
- **Export Format**: PNG, PDF, SVG, JPG, etc.
- **DPI**: Resolution for raster formats (72-1200)
- **Filename Pattern**: How to name output files

#### Processing Options
- **Row Range**: Which CSV rows to process
- **Overwrite**: Replace existing files
- **Merge PDFs**: Combine PDF outputs
- **Logging**: Create detailed log file

### Step 4: Execute
Click **Apply** to start processing. Progress will be shown in the console.

## 🎯 Working with Patterns - Complete Examples

### Pattern-Based File Naming
Generate dynamic filenames using CSV data and system values:

#### Available Placeholders
| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{column_name}` | CSV column value | `{name}` → "John_Doe" |
| `{count}` | Sequential number | `output_{count}` → "output_1" |
| `{date}` | Current date | `file_{date}` → "file_20260126" |
| `{date:format}` | Current date | `file_{date:dd-mm-yyy}` → "file_26-01-2026" |
| `{time}` | Current time | `file_{time}` → "file_143022" |
| `{timestamp}` | Date + time | `{timestamp}` → "20260126_143022" |

#### Pattern Examples
```
certificate_{name}_{date}.png         # certificate_John_Doe_20260126.png
badge_{department}_{count}.pdf        # badge_Engineering_001.pdf
id_card_{employee_id}_{timestamp}.svg  # id_card_EMP001_20260126_143022.svg
```

### Real-World Pattern Examples

#### Example 1: Conference Badges
```
SVG Template Labels:
├── Text: attendee_name
├── Text: company_name
├── Image: company_logo
├── Rectangle: badge_color##fill
└── Text: attendee_type

CSV Data:
attendee_name,company_name,company_logo,badge_color##fill,attendee_type
John Smith,TechCorp,techcorp.png,#ff6b6b,Speaker
Jane Doe,InnovateCo,innovateco.png,#4ecdc4,Attendee

Result Files:
badge_John_Smith_Speaker.pdf
badge_Jane_Doe_Attendee.pdf
```

#### Example 2: Product Labels
```
SVG Template Labels:
├── Text: product_name
├── Text: product_sku
├── Text: product_price
├── Rectangle: label_background##fill
├── Text: price_text##font-size
└── Barcode: product_barcode

CSV Data:
product_name,product_sku,product_price,label_background##fill,price_text##font-size,product_barcode
Widget A,W001,$19.99,#ffffff,24,W001123456
Widget B,W002,$29.99,#f8f9fa,32,W002654321

Result Files:
label_Widget_A_W001.pdf
label_Widget_B_W002.pdf
```

#### Example 3: Event Invitations
```
SVG Template Labels:
├── Text: guest_name
├── Text: event_title
├── Text: event_date
├── Text: event_time
├── Rectangle: invitation_style##fill
└── Text: title_text##font-weight

CSV Data:
guest_name,event_title,event_date,event_time,invitation_style##fill,title_text##font-weight
Alice Johnson,Birthday Party,2024-02-14,19:00,#ff69b4,bold
Bob Williams,Wedding,2024-06-15,15:00,#e6e6fa,normal

Result Files:
invitation_Alice_Johnson_Birthday_Party.pdf
invitation_Bob_Williams_Wedding.pdf
```

### Pattern Tips and Best Practices

#### 1. Consistent Labeling
- Use descriptive labels: `customer_name` instead of `name1`
- Group related elements: `header_text`, `header_size##font-size`
- Use underscores for multi-word labels: `first_name`, `last_name`

#### 2. Organized CSV Structure
```
# Good organization - grouped by function
first_name,last_name,email,photo,card_background##fill,title_font_size

# Also works but less organized
name,email,photo,background_color,title_size
```

#### 3. Validation Checklist
Before running batch processing:
- [ ] All SVG elements have matching CSV columns
- [ ] Property names are spelled correctly (case-sensitive)
- [ ] Image files exist in specified locations
- [ ] Color values use valid CSS formats
- [ ] Font sizes are reasonable numbers

#### 4. Common Pattern Mistakes to Avoid

❌ **Incorrect**: `nameFontSize` (missing ## separator)
✅ **Correct**: `name##font-size`

❌ **Incorrect**: `button color` (spaces in property names)
✅ **Correct**: `button##fill` or `button##background-color`
certificate_{name}_{date}.png
badge_{department}_{count}.pdf
id_card_{name}_{timestamp}.svg
```

## 🔧 Advanced Features

### Layer Visibility Control
Control which layers are visible based on CSV data:

1. **Label your layers**: Use layer names like `show_layer`, `hide_layer`
2. **Add CSV columns**: Include columns matching layer names
3. **Use boolean values**: `true`/`false` or `1`/`0`

```csv
name,show_background,show_logo
John Doe,true,true
Jane Smith,false,true
```

### Image Search Paths
Configure how InkAutoGen finds image files:

#### Search Order
1. **Absolute paths**: `/path/to/image.jpg`
2. **Relative to CSV**: Same directory as CSV file
3. **Relative to SVG**: Same directory as SVG template
4. **Specified folders**: Additional search directories

#### Image Formats Supported
- PNG, JPG, JPEG, GIF, BMP, TIFF, SVG

### PDF Operations
#### PDF Merging
Combine multiple PDF outputs into a single file:
- Enable **"Merge PDFs"** option
- Choose merge strategy: All files or by groups

#### Individual PDF Cleanup
Automatically delete individual PDF files after merging:
- Enable **"Delete individual PDFs"** option
- Saves disk space for large batches

### Row Filtering
Process specific rows from your CSV:

#### Range Syntax
- `1-10`: Rows 1 through 10
- `5,8,12`: Specific rows
- `1-5,8,10-15`: Combined ranges
- `even`: Even-numbered rows only
- `odd`: Odd-numbered rows only

#### Examples
```
1-100          # First 100 rows
5,10,15        # Specific rows
1-50,100-150   # Multiple ranges
even           # Even rows only
```

## 🛠️ Troubleshooting

### Common Issues

#### Extension Not Found
**Problem**: InkAutoGen doesn't appear in Extensions menu
**Solution**: 
1. Verify installation with `./setup.sh`
2. Restart Inkscape completely
3. Check extensions directory permissions

#### CSV Not Loading
**Problem**: "Cannot read CSV file" error
**Solution**:
1. Check file encoding (save as UTF-8)
2. Verify CSV format (comma-separated)
3. Ensure headers exist on first row
4. Check file permissions

#### Elements Not Replaced
**Problem**: SVG elements not being updated
**Solution**:
1. Verify element labels use angle brackets: `<name>`
2. Check CSV headers match element labels exactly
3. Ensure elements are not locked or grouped
4. Check for typos in label names

#### Images Not Found
**Problem**: Image substitution not working
**Solution**:
1. Verify image file paths in CSV
2. Check image files exist in expected locations
3. Ensure image formats are supported
4. Check file permissions for image directories

#### Export Fails
**Problem**: Files not being generated
**Solution**:
1. Check output directory permissions
2. Verify disk space is available
3. Ensure export format is supported
4. Check Inkscape command-line access

### Debug Mode
Enable detailed logging for troubleshooting:

1. Enable **"Create log file"** option
2. Check `inkautogen.log` in output directory
3. Look for error messages and warnings

### Performance Tips

#### Large CSV Files
- Limit to 10,000 rows per file
- Use row filtering to process in batches
- Close other applications to free memory

#### Complex Templates
- Simplify SVG designs when possible
- Avoid excessive nested groups
- Use optimized image formats

## 📚 Examples and Demos

### Example 1: Certificate Generation
**Template**: Certificate with name, date, and signature
**CSV Data**:
```csv
name,course,date,instructor
John Doe,Python Basics,2024-01-15,Dr. Smith
Jane Smith,Web Design,2024-01-16,Prof. Johnson
```

**Element Labels**:
- `name`: Recipient name
- `course`: Course title
- `date`: Completion date
- `instructor`: Instructor name

### Example 2: Business Cards
**Template**: Business card with employee information
**CSV Data**:
```csv
name,title,email,phone,photo,card##fill
John Doe,Engineer,john@company.com,555-0123,john.jpg,#ffffff
Jane Smith,Designer,jane@company.com,555-0124,jane.png,#f0f0f0
```

**Element Labels**:
- `name`: Employee name
- `title`: Job title
- `email`: Email address
- `phone`: Phone number
- `photo`: Employee photo
- `card##fill`: Background color

### Example 3: Product Labels
**Template**: Product label with dynamic information
**CSV Data**:
```csv
product,price,sku,description,logo##width
Widget A,19.99,W001,Premium widget,150
Widget B,29.99,W002,Deluxe widget,200
```

**Element Labels**:
- `product`: Product name
- `price`: Price
- `sku`: Product code
- `description`: Product description
- `logo##width`: Logo width

## 📋 Quick Reference - Pattern Cheat Sheet

### Basic Syntax
| Pattern Type | Syntax | Example | Use Case |
|-------------|---------|---------|-----------|
| Data Replacement | `<element_label>` | `name`, `photo` | Replace text, images |
| Property Change | `<element_label>##<property>` | `button##fill`, `text##font-size` | Change colors, fonts sizes |

### Common Property Names
| Property | What It Changes | Valid Values |
|----------|----------------|---------------|
| `fill` | Background color | `#ff0000`, `red`, `rgb(255,0,0)` |
| `stroke` | Border/outline color | `#000000`, `black` |
| `font-size` | Text size | `24`, `32px`, `2em` |
| `font-family` | Font type | `Arial`, `Times New Roman` |
| `font-weight` | Text thickness | `bold`, `normal`, `600` |
| `width` | Element width | `100`, `200px`, `50%` |
| `height` | Element height | `50`, `75px`, `25%` |
| `opacity` | Transparency | `0.5`, `50%` |
| `rotate` | Rotation | `45`, `90deg` |
| `scale` | Size scale | `1.5`, `200%` |

### CSV Column Examples

#### Text Elements
```csv
name,         # <name>
title,        # <title>
description,   # <description>
email,         # <email>
phone,         # <phone>
```

#### Image Elements
```csv
photo,         # <photo>
logo,          # <logo>
background,     # <background>
icon,          # <icon>
```

#### Style Properties
```csv
button##fill,              # <button> background color
title##font-size,           # <title> text size
frame##stroke,              # <frame> border color
text##font-family,          # <text> font type
card##opacity,              # <card> transparency
```

#### Layout Properties
```csv
logo##width,                # <logo> element width
header##height,             # <header> element height
badge##rotate,              # <badge> rotation angle
content##scale,             # <content> size scale
```

## 🎓 Best Practices

### Template Design
1. **Keep it simple**: Avoid overly complex designs
2. **Use consistent labeling**: Follow naming conventions
3. **Test with sample data**: Verify before large batches
4. **Backup templates**: Keep original designs safe

### CSV Preparation
1. **Validate data**: Check for errors before processing
2. **Use consistent formatting**: Standardize dates, numbers
3. **Plan file paths**: Organize images logically
4. **Test with small samples**: Process 5-10 rows first

### File Management
1. **Organize output**: Use descriptive filename patterns
2. **Monitor disk space**: Large batches consume storage
3. **Clean up regularly**: Remove temporary files
4. **Backup results**: Keep important outputs safe

## 📞 Getting Help

### Resources
- **Documentation**: [Project Wiki](https://github.com/siddha-siddhant/InkAutoGen/wiki)
- **Issues**: [GitHub Issues](https://github.com/siddha-siddhant/InkAutoGen/issues)
- **Community**: [Discussion Forum](https://github.com/siddha-siddhant/InkAutoGen/discussions)

### Reporting Issues
When reporting problems, include:
1. **Inkscape version**: Help → About Inkscape
2. **Operating system**: Windows/macOS/Linux version
3. **Extension version**: Check extension files
4. **Error messages**: Console output and log files
5. **Sample files**: Template and CSV (if possible)

---

**Happy designing with InkAutoGen!** 🎨✨
