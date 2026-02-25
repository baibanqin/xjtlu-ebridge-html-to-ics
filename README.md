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

如果学校后续更新页面结构（DOM changes），脚本可能需要调整。  
If the school updates the page structure (DOM changes) in the future, the script may need to be updated.

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

> **重要 / Important:**  
> 必须保存的是“实际课表内容页（timetable content page）”，不是登录页（login page）或门户壳页（portal shell page）。  
> You must save the actual timetable content page, not the login page or a portal shell page.

---

## 第二步：保存网页为 HTML / Step 2: Save the webpage as HTML

### 推荐方式（Recommended）
在浏览器中按 `Ctrl + S`（Windows）或 `Cmd + S`（macOS），选择：

- **网页，完整（Webpage, Complete）**（推荐 / recommended）
- 或 **网页，仅 HTML（HTML only）**

保存后通常会得到：
- 一个 HTML 主文件（例如 `XJTLU e-Bridge.html`）
- 一个资源文件夹（例如 `XJTLU e-Bridge_files/`）

After saving, you will usually get:
- One main HTML file (e.g., `XJTLU e-Bridge.html`)
- One resource folder (e.g., `XJTLU e-Bridge_files/`)

### 关键点 / Key point
本项目脚本通常需要读取资源文件夹中的：
`XJTLU e-Bridge_files/saved_resource.html`

This project usually reads:
`XJTLU e-Bridge_files/saved_resource.html`

因为主 HTML 往往只是外层页面（shell page），真正课表内容在 iframe 对应的 `saved_resource.html` 中。  
The main HTML is often only a shell page, while the actual timetable content is inside the iframe file `saved_resource.html`.

---

## 第三步：准备脚本文件 / Step 3: Prepare the script

确保项目目录（project folder）中包含以下文件：  
Make sure your project folder contains the following files:

- `ebridge_html_to_ics.py`
- `requirements.txt`

---

## 第四步：运行脚本生成 .ics / Step 4: Run the script to generate `.ics`

### 参数说明 / Arguments

- `--html`：保存的课表 HTML 路径（通常是 `saved_resource.html`）  
  Path to the saved timetable HTML (usually `saved_resource.html`)
- `--week1`：第 1 教学周周一日期（格式 `YYYY-MM-DD`）  
  Monday date of teaching week 1 (format `YYYY-MM-DD`)
- `--out`：输出 `.ics` 文件路径  
  Output `.ics` file path
- `--max-week`：最大教学周（如 13 / 16）  
  Maximum teaching week number (e.g., 13 / 16)

> **重要 / Important:**  
> `--week1` 一定要填“第 1 教学周的周一”，否则所有课程日期会整体偏移（shift）。  
> `--week1` must be the Monday of teaching week 1, otherwise all event dates will be shifted.

### Windows 示例 / Windows Example

```bash
python ebridge_html_to_ics.py --html "XJTLU e-Bridge_files/saved_resource.html" --week1 "2026-03-02" --out "xjtlu_timetable.ics" --max-week 13
```

### macOS 示例 / macOS Example

```bash
python3 ebridge_html_to_ics.py --html "XJTLU e-Bridge_files/saved_resource.html" --week1 "2026-03-02" --out "xjtlu_timetable.ics" --max-week 13
```

---

## 第五步：检查输出文件 / Step 5: Check the outputs

脚本运行成功后会生成：  
If the script runs successfully, it will generate:

- `xjtlu_timetable.ics`（日历文件 / calendar file）
- `parsed_timetable_preview.csv`（解析预览 / parsed preview）

控制台（console）会显示：
- 解析课程条目数量（parsed course records）
- 生成日历事件数量（generated calendar events）
- 前几条解析结果（first parsed records）

建议先检查 `parsed_timetable_preview.csv` 是否与网页课表一致（课程名、周次、时间、地点等）。  
It is recommended to check `parsed_timetable_preview.csv` first and verify it matches the timetable page (course name, weeks, time, location, etc.).

---

## 第六步：导入苹果日历（Apple Calendar） / Step 6: Import into Apple Calendar

### macOS Apple Calendar 导入步骤 / macOS Apple Calendar Import Steps

1. 打开 **Calendar（日历）** 应用  
   Open the **Calendar** app.

2. （推荐）先新建一个单独日历（例如 `XJTLU Timetable`）  
   (Recommended) Create a separate calendar first (e.g., `XJTLU Timetable`).

3. 菜单栏选择：`File > Import...`  
   In the menu bar, choose: `File > Import...`

4. 选择生成的 `xjtlu_timetable.ics` 文件  
   Select the generated `xjtlu_timetable.ics` file.

5. 选择导入到哪个日历（calendar）  
   Choose which calendar to import into.

6. 导入后抽查几门课（尤其是单周/双周或间隔周课程）  
   After importing, spot-check a few classes (especially odd/even-week or sparse-week classes).

---

## 常见问题 / Troubleshooting

### 1) 解析到 0 门课 / Parsed 0 courses

**可能原因 / Possible causes**
- 保存的是登录页（login page）或门户壳页（portal shell page）
- 保存时课表尚未加载完成（timetable not fully loaded）
- 用错了文件（应使用 `saved_resource.html`）
- eBridge 页面结构已更新（DOM changed）

**解决方法 / Fix**
- 重新打开课表页面，确认看到完整课程块后再保存
- 使用 `XJTLU e-Bridge_files/saved_resource.html`
- 提交 issue（issue）并附上脱敏后的 HTML 结构信息（不要上传个人课表）

### 2) 解析结果像时间轴（如 `17:00`）/ Parsed results look like time-axis labels (e.g., `17:00`)

**原因 / Cause**  
脚本抓到了时间轴元素而不是课程块（event blocks）。  
The parser picked up time-axis elements instead of course event blocks.

**说明 / Note**  
当前版本已针对 `td.day-cell > div.event` 做过滤，正常情况下不会出现。  
The current version filters `td.day-cell > div.event`, so this should not happen in normal cases.

### 3) 所有课程日期整体错一周 / All dates are shifted by one week

**原因 / Cause**  
`--week1` 填错了（不是第 1 教学周周一）。  
The `--week1` date is incorrect (not the Monday of teaching week 1).

**解决 / Fix**  
使用正确的第 1 教学周周一日期重新生成 `.ics`。  
Regenerate the `.ics` with the correct Monday date of teaching week 1.

### 4) macOS 上命令找不到 `python` / `python` not found on macOS

使用 `python3` 和 `pip3`。  
Use `python3` and `pip3`.

---

## 隐私与安全 / Privacy and Security

- **不要上传你的课表 HTML 文件（HTML files）或资源文件夹（resource folder）到公开仓库（public repo）**  
  **Do not upload your timetable HTML files or resource folder to a public repository.**
- 不要公开分享带会话参数（session token）的 eBridge 链接  
  Do not publicly share eBridge links containing session tokens.

建议在 `.gitignore` 中忽略以下文件（推荐）：  
Recommended `.gitignore` entries:

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

## 项目结构建议 / Suggested Project Structure

```text
xjtlu-ebridge-html-to-ics/
├─ ebridge_html_to_ics.py
├─ requirements.txt
├─ README.md
├─ .gitignore
└─ LICENSE
```

---

## 贡献 / Contributing

欢迎提交 issue（issue）或 pull request（PR）来改进：
- 新版 eBridge 页面结构适配
- 更友好的课程标题格式（cleaner summary）
- 不同课表布局（layout）支持
- 其他日历导入兼容性优化

Issues and pull requests are welcome for:
- New eBridge DOM updates
- Cleaner event summaries
- Support for additional timetable layouts
- Compatibility improvements for calendar imports

---

## License

建议使用 MIT License（MIT 许可证）。  
MIT License is recommended.