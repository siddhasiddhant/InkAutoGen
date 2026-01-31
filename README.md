# InkAutoGen

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/siddhasiddhant/InkAutoGen)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](docs/LICENSE)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)

**InkAutoGen** is a powerful Inkscape extension for automated batch processing of SVG templates using CSV data. Transform static designs into dynamic, data-driven documents with mass customization capabilities.

## 🚀 Key Features

- **📊 CSV-Driven Design**: Populate SVG templates with spreadsheet data
- **🔄 Batch Processing**: Generate hundreds of customized files automatically
- **🎨 Dynamic Elements**: Replace text, images, colors, fonts, and more
- **📁 Multi-Format Export**: PNG, PDF, SVG, JPG, EPS, TIFF, WebP support
- **🌍 Unicode Support**: Full international character and emoji handling
- **🔒 Security Focused**: Input validation and safe file handling
- **⚡ Performance Optimized**: Efficient processing with caching

## 📋 Quick Start

1. **Install the Extension**
   ```bash
   ./setup.sh
   ```

2. **Create SVG Template**
   - Add labeled elements in Inkscape (`Object → Object Properties`)
   - Use labels like `<name>`, `<photo>`, `<title>`

3. **Prepare CSV Data**
   ```csv
   name,title,photo
   John Doe,Engineer,john.jpg
   Jane Smith,Designer,jane.png
   ```

4. **Generate Files**
   - Open SVG template in Inkscape
   - Go to `Extensions → Export → InkAutoGen`
   - Select CSV file and configure options
   - Click Apply to process

## 🎯 Basic Patterns - How It Works

### **Fundamental Concept**
InkAutoGen works by matching CSV column headers with SVG element labels. There are **two basic patterns**:

#### **1. Data Replacement Pattern: `<element_label>`**
Replace content in SVG elements (text, images, etc.)
Replace the visibility of layer (layer: visible, hide, show etc.)

#### **2. Property Modification Pattern: `<element_label>##<property>`**  
Change properties/attributes of SVG elements (colors, fonts, sizes, etc.)

### **Step-by-Step Usage**

#### **Step 1: Label Your SVG Elements**
In Inkscape, select each element and set its label:
1. Select element (text, image, shape, etc.)
2. Open `Object → Object Properties` (or `Shift+Ctrl+O`)
3. Set ID/Label using angle brackets:
   - Text: `<name>`, `<title>`, `<email>`
   - Images: `<photo>`, `<logo>`, `<background>`
   - Shapes: `<button>`, `<frame>`, `<badge>`

#### **Step 2: Create Your CSV Data**
Create CSV file with headers matching your element labels:

```csv
# Basic data replacement
name,title,email,photo
John Doe,CEO,john@company.com,john.jpg
Jane Smith,CTO,jane@company.com,jane.png

# Including property changes  
name,title,email,photo,button##fill,title##font-size
John Doe,CEO,john@company.com,john.jpg,#ff0000,24
Jane Smith,CTO,jane@company.com,jane.png,#00ff00,32
```

#### **Step 3: Run the Extension**
1. Open your labeled SVG in Inkscape
2. `Extensions → Export → InkAutoGen`
3. Select your CSV file and configure options
4. Click Apply to process

### **Pattern Examples**

#### **Text Element Replacement**
```
SVG Label:  <name>
CSV Header:  name
CSV Value:   John Doe
Result:      Text element shows "John Doe"
```

#### **Layer Visibility Control**
```
SVG Layer Name:  <show_background>
CSV Header:      show_background
CSV Value:       true/false
Result:          Layer is shown/hidden based on CSV value
```

#### **Image Element Replacement**
```
SVG Label:  <photo>
CSV Header:  photo  
CSV Value:   john.jpg
Result:      Image element displays john.jpg
```

#### **Property Modification**
```
SVG Label:      <button>
CSV Header:      button##fill
CSV Value:       #ff0000
Result:          Button background becomes red
```

#### **Font Size Change**
```
SVG Label:      <title>
CSV Header:      title##font-size
CSV Value:       32
Result:          Title text becomes 32px font size
```

#### **Color Change**
```
SVG Label:      <frame>
CSV Header:      frame##stroke
CSV Value:       #00ff00
Result:          Frame border becomes green
```


## 🎯 Common Use Cases

- **Certificates**: Personalize with `name`, `course`, `date`
- **Business Cards**: `name`, `title`, `email`, `photo`, `card##fill`
- **Marketing Materials**: Location-specific data using `location`, `price`, `banner##background`
- **ID Badges**: `employee_name`, `employee id`, `photo`, `badge##stroke`
- **Product Labels**: `product name`, `sku`, `price`, `label##font-weight`

## 🏗️ Architecture

```
InkAutoGen/
├── inkautogen.py              # Main extension orchestrator
├── modules/                   # Core processing modules
│   ├── csv_reader.py         # CSV import with encoding detection
│   ├── svg_processor.py      # SVG template processing
│   ├── file_exporter.py      # Multi-format file export
│   ├── utilities.py          # Helper functions
│   ├── config.py            # Configuration constants
│   ├── security.py          # Security validation
│   ├── exceptions.py        # Custom exceptions
│   └── performance.py       # Performance monitoring
├── tests/                     # Comprehensive test suite
├── demo/                      # Example templates and data
└── docs/                      # Documentation
```

## 📖 Documentation

- **[User Guide](docs/user-guide.md)** - Step-by-step usage instructions
- **[Developer Docs](docs/developer-guide.md)** - Architecture and API reference
- **[Testing Guide](docs/testing-guide.md)** - Testing procedures and guidelines
- **[API Reference](docs/api-reference.md)** - Detailed module documentation

## 🔧 Requirements

- **Inkscape** 1.0+
- **Python** 3.7+
- **Dependencies**: lxml, chardet, PyPDF2 (auto-installed)

## 🎯 Demo
A sample csv file and svg file with required resources are given in demo folder. Please try it yourself using the InkAutoGen extension in Inkscape. - see the [demo](demo).

## 📦 Installation

### Method 1: Setup Script (Recommended)
```bash
git clone https://github.com/siddhasiddhant/InkAutoGen.git
cd InkAutoGen
./setup.sh
```

### Method 2: Manual Installation
```bash
# Copy extension files to Inkscape extensions directory
cp inkautogen.py ~/.config/inkscape/extensions/
cp -r modules/ ~/.config/inkscape/extensions/
cp inkautogen.inx ~/.config/inkscape/extensions/
```

## 🎨 Template Creation

### Element Labels
- **Text Replacement**: `name`, `title`, `description`
- **Image Substitution**: `photo`, `logo`, `background`
- **Property Modification**: `button##fill`, `text##font-size`

### Supported Properties
- Colors: `fill`, `stroke`
- Typography: `font-size`, `font-family`, `font-weight`
- Dimensions: `width`, `height`
- Transformations: `rotate`, `scale`, `translate`
- And more...

## 💻 CSV Format

### Basic Structure
```csv
name,email,photo,department
John Doe,john@company.com,john.jpg,Engineering
Jane Smith,jane@company.com,jane.png,Marketing
```

### Property Columns
```csv
name,button##fill,title##font-size
John,#ff0000,24
Jane,#00ff00,32
```

## 🚀 Advanced Features

- **Layer Visibility**: Control layer display with CSV data
- **PDF Merging**: Combine multiple outputs into single PDF
- **Filename Patterns**: Dynamic naming with `{column}`, `{date}`, `{count}`
- **Row Filtering**: Process specific rows or ranges
- **Encoding Detection**: Automatic handling of 15+ file encodings

## 🧪 Testing

Run the test suite:
```bash
cd tests
python3 -m pytest test_*.py -v
```

Or use the test runner:
```bash
cd tests
python3 run_tests.py
```

## 📊 Performance

- **Batch Size**: Up to 10,000 rows per CSV
- **Memory**: Optimized XML processing with cleanup
- **Speed**: Caching and batch operations
- **Monitoring**: Built-in performance tracking

## 🔒 Security

- **Input Validation**: Prevents path traversal attacks
- **File Extensions**: Restricts to safe file types
- **Content Scanning**: Detects dangerous patterns
- **Error Handling**: Graceful failure with detailed logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Siddha Siddhant** - *Initial development* - [Siddha Siddhant](https://github.com/siddhasiddhant)

## 🙏 Acknowledgments

- Inkscape development team for the excellent extension API
- Contributors and testers who helped improve the project
- Open source libraries that make this project possible

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/siddhasiddhant/InkAutoGen/issues)
- **Documentation**: [Project Wiki](https://github.com/siddhasiddhant/InkAutoGen/wiki)
- **Email**: dev@siddhasiddhant.com

---

**Transform your design workflow with InkAutoGen - from static templates to dynamic, data-driven graphics in seconds!** 🎨✨
