# DAG Run External View Plugin - Professional Design

This is a **modular Airflow 3 external view plugin** for DAG run pages, built with professional design patterns and your brand color palette.

## 📁 File Structure

```
ev_dag_run/
├── ev_dag_run.py          # 🐍 Main plugin file
├── templates/
│   └── hello.html         # 📄 HTML template with DAG/Run context
├── static/
│   ├── style.css          # 🎨 Professional CSS with brand colors
│   └── script.js          # ⚡ Interactive JavaScript
└── README.md              # 📚 This documentation
```

## 🎯 What It Does

- ➕ Adds **"Plugin Example - DAG Run"** link to individual DAG run pages
- 🎨 Displays DAG ID and Run ID in an elegant info panel
- 🎯 Professional "Analyze Run" button with interactions
- 📋 Click-to-copy functionality for DAG/Run IDs
- ✨ Beautiful animations and professional feedback

## 🔧 Technical Features

### **DAG Run Context**
- ✅ **URL templating** with `{DAG_ID}` and `{RUN_ID}`
- ✅ **Dynamic content** based on actual DAG run
- ✅ **Context-aware messaging** and notifications

### **Professional Design**
- 🎨 **Brand color palette** (Moonshot, Amethyst, Sapphire, Emerald)
- ✨ **Smooth animations** and hover effects
- 📱 **Responsive design** for mobile devices
- ♿ **Accessibility** with ARIA attributes and keyboard support

### **Interactive Features**
- 🎯 **Smart button** with context-aware text
- 📋 **Copy-to-clipboard** for DAG and Run IDs
- 🎉 **Toast notifications** with DAG run context
- 🔍 **Visual feedback** and state management

## 🌍 URL Structure

- **Plugin endpoint**: `/ev-dag-run-plugin/hello/{DAG_ID}/{RUN_ID}`
- **CSS file**: `/ev-dag-run-plugin/static/style.css`
- **JS file**: `/ev-dag-run-plugin/static/script.js`

## 🎨 Design Highlights

### **Color Usage**
- **Sapphire 400** (`#0AA6FF`) - Primary button and DAG info values
- **Moonshot 700** (`#2B215B`) - Headers and labels
- **Moonshot 50** (`#EBE9F8`) - Background gradients
- **Emerald 400** (`#0BCD93`) - Success notifications

### **Professional Elements**
- 🌈 **Gradient top border** (Sapphire → Amethyst → Emerald)
- 💎 **Monospace font** for DAG/Run IDs
- ✨ **Ripple effects** on button interactions
- 🎯 **Context-aware notifications** with DAG run details

## 📍 Location

This plugin appears on **individual DAG run pages** in Airflow's UI, providing DAG run specific functionality and information.

Perfect for building more complex DAG run analysis, monitoring, or administrative tools! 🚀
