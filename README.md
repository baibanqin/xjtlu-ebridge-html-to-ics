# XJTLU eBridge Timetable HTML to ICS

将 XJTLU eBridge 课表网页（保存为 HTML）转换为 `.ics` 日历文件，方便导入苹果日历（Apple Calendar）等日历应用。  
Convert a saved XJTLU eBridge timetable webpage (HTML) into an `.ics` calendar file for Apple Calendar and other calendar apps.

---

## 功能 / Features

- 从 XJTLU eBridge Timetable Plus 网格视图（grid view）保存的 HTML 中解析课程信息  
  Parse course information from saved XJTLU eBridge Timetable Plus grid-view HTML.
- 提取课程名、星期、时间、周次、教室、教师  
  Extract course name, weekday, time range, teaching weeks, room, and teacher.
- 生成 `.ics`（iCalendar）文件  
  Generate an `.ics` (iCalendar) file.
- 可导入苹果日历（Apple Calendar）/ Google Calendar / Outlook 等  
  Importable into Apple Calendar, Google Calendar, Outlook, etc.

---

## 适用范围 / Scope

本脚本当前适配 **XJTLU eBridge Timetable Plus 的网格视图（grid view）** 页面结构（DOM structure）。  
This script currently targets the **XJTLU eBridge Timetable Plus grid-view** page structure (DOM structure).

---

## 环境要求 / Requirements

- Python 3.9+（推荐 Python 3.10 或更高）  
  Python 3.9+ (Python 3.10+ recommended)
- `beautifulsoup4`

安装依赖（Install dependencies）：

### Windows
```bash
pip install -r requirements.txt
```

### macOS
```bash
pip3 install -r requirements.txt
```

---

## 第一步：在 eBridge 打开课表页面 / Step 1: Open the timetable page in eBridge

1. 登录 XJTLU eBridge（如需要）。  
   Log in to XJTLU eBridge (if required).

2. 打开 **My Timetable / Timetable Plus** 页面。  
   Open the **My Timetable / Timetable Plus** page.

3. 确认你看到的是完整课表（包含 MON~SUN 列、时间轴、彩色课程块）。  
   Make sure the full timetable is visible (MON~SUN columns, time axis, and colored course blocks).

---

## 第二步：必须使用 Chrome 保存网页为 HTML / Step 2: You must use Chrome to save the webpage as HTML

### 必须项 / Requirement
**必须使用 Google Chrome（Chrome）**（或 Chromium-based 浏览器，推荐直接 Chrome）。  
**You must use Google Chrome (Chrome)** (or Chromium-based browsers; Chrome is recommended).

> 不支持 Safari 的 `.webarchive`（webarchive）格式。  
> Safari `.webarchive` format is not supported.

### Chrome 保存方式 / How to save in Chrome
在课表页面按 `Ctrl + S`（Windows）或 `Cmd + S`（macOS），并选择：  
Press `Ctrl + S` (Windows) or `Cmd + S` (macOS), then choose:

- **Webpage, Complete（网页，完整）**  ✅

保存后你会得到两个东西：  
After saving, you will get two items:

1) 一个主文件（main file）：  
`Check Staff _ Student's Timetable.html`（文件名可能不同 / filename may differ）

2) 一个同名文件夹（resource folder）：  
`Check Staff _ Student's Timetable_files/`（文件夹名可能不同 / folder name may differ）

在该文件夹里，找到：  
Inside that folder, locate:

- `saved_resource.html`

> 注意（Note）：你的文件名/文件夹名可能是 `My Timetable.html` / `My Timetable_files/` 等，只要结构是 “`.html` + `_files/`” 即可。  
> Your names may be `My Timetable.html` / `My Timetable_files/`, etc. As long as it is “`.html` + `_files/`”, it’s fine.

---

## 第三步：运行脚本生成 .ics / Step 3: Run the script to generate `.ics`

### 参数说明 / Arguments

- `--html`：指向 `*_files/saved_resource.html`（不是主 `.html`）  
  Point to `*_files/saved_resource.html` (not the main `.html`)
- `--week1`：第 1 教学周周一日期（格式 `YYYY-MM-DD`）  
  Monday date of teaching week 1 (format `YYYY-MM-DD`)
- `--out`：输出 `.ics` 文件路径  
  Output `.ics` file path
- `--max-week`：最大教学周（如 13 / 16）  
  Maximum teaching week number (e.g., 13 / 16)

> 关键（Important）：`--week1` 一定要填“第 1 教学周的周一”，否则所有课程日期会整体偏移（shift）。  
> `--week1` must be the Monday of teaching week 1, otherwise all event dates will be shifted.

---

### 默认命令（按 Chrome 默认保存结构）/ Default command (Chrome default save structure)

把下面命令里的 `--html` 路径按你的实际文件夹名改一下即可（只要指向 `saved_resource.html`）。  
Edit the `--html` path to match your folder name (it must point to `saved_resource.html`).

#### Windows
```bash
python ebridge_html_to_ics.py --html "Check Staff _ Student's Timetable_files/saved_resource.html" --week1 "2026-03-02" --out "xjtlu_timetable.ics" --max-week 13
```

#### macOS
```bash
python3 ebridge_html_to_ics.py --html "Check Staff _ Student's Timetable_files/saved_resource.html" --week1 "2026-03-02" --out "xjtlu_timetable.ics" --max-week 13
```

---

## 第四步：检查输出 / Step 4: Check outputs

脚本运行成功后会生成：  
If the script runs successfully, it will generate:

- `xjtlu_timetable.ics`（日历文件 / calendar file）
- `parsed_timetable_preview.csv`（解析预览 / parsed preview）

建议先检查 `parsed_timetable_preview.csv` 是否与网页课表一致（课程名、周次、时间、地点等）。  
It is recommended to check `parsed_timetable_preview.csv` first and verify it matches the timetable page (course name, weeks, time, location, etc.).

---

## 第五步：导入苹果日历（Apple Calendar）/ Step 5: Import into Apple Calendar

### macOS 导入 / macOS Import
1. 打开 **Calendar（日历）**  
   Open **Calendar**.

2. （推荐）先新建一个单独日历（例如 `XJTLU Timetable`）  
   (Recommended) Create a separate calendar (e.g., `XJTLU Timetable`).

3. 菜单栏：`File > Import...`  
   Menu bar: `File > Import...`

4. 选择 `xjtlu_timetable.ics` 并导入到目标日历  
   Select `xjtlu_timetable.ics` and import into the target calendar.

---

## 常见问题 / Troubleshooting

### 1) 解析到 0 门课 / Parsed 0 courses
**常见原因 / Common causes**
- 没用 Chrome 保存为 “Webpage, Complete（网页，完整）”  
  Not saved by Chrome as “Webpage, Complete”
- `--html` 指向了主 `.html`，而不是 `*_files/saved_resource.html`  
  `--html` points to the main `.html` instead of `*_files/saved_resource.html`
- 保存时课表没加载完（timetable not fully loaded）  
  Timetable not fully loaded when saving

**解决 / Fix**
- 用 Chrome 重新保存（Webpage, Complete）  
  Re-save with Chrome (Webpage, Complete)
- 确认 `--html` 指向 `saved_resource.html`  
  Make sure `--html` points to `saved_resource.html`

### 2) 所有课程日期整体错一周 / All dates are shifted by one week
`--week1` 填错（不是第 1 教学周周一）。  
`--week1` is incorrect (not the Monday of teaching week 1).  
用正确日期重新生成 `.ics`。  
Regenerate the `.ics` with the correct date.

---

## 隐私与安全 / Privacy and Security

- **不要上传你的课表 HTML 文件（HTML files）或资源文件夹（resource folder）到公开仓库（public repo）**  
  **Do not upload your timetable HTML files or resource folder to a public repository.**
- 不要公开分享带会话参数（session token）的 eBridge 链接  
  Do not publicly share eBridge links containing session tokens.

推荐 `.gitignore`：  
Recommended `.gitignore`:

```gitignore
__pycache__/
*.pyc
*.ics
*.csv
XJTLU e-Bridge.html
XJTLU e-Bridge_files/
saved_resource.html
.DS_Store
```

---

## License

建议使用 MIT License（MIT License）。  
MIT License is recommended.