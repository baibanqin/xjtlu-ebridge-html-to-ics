import argparse
import csv
import hashlib
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup


DAY_MAP = {
    "MON": 1,
    "TUE": 2,
    "WED": 3,
    "THU": 4,
    "FRI": 5,
    "SAT": 6,
    "SUN": 7,
}


@dataclass
class CourseRecord:
    course: str
    weekday: int  # Monday=1 ... Sunday=7
    start_time: time
    end_time: time
    weeks: List[int]
    location: str = ""
    teacher: str = ""
    extra: str = ""


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").replace("\xa0", " ").replace("\u200b", " ")).strip()


def parse_hhmm(text: str) -> time:
    match = re.fullmatch(r"\s*(\d{1,2}):(\d{2})\s*", text)
    if not match:
        raise ValueError(f"Invalid time format: {text}")
    return time(int(match.group(1)), int(match.group(2)))


def parse_time_range(text: str) -> Optional[Tuple[time, time]]:
    normalized = clean_text(text)
    match = re.search(r"(\d{1,2}:\d{2})\s*(?:-|~|–|—|至)\s*(\d{1,2}:\d{2})", normalized)
    if not match:
        return None
    return parse_hhmm(match.group(1)), parse_hhmm(match.group(2))


def parse_weeks(text: str, max_week: int = 16) -> List[int]:
    normalized = clean_text(text).lower()
    if not normalized:
        return []

    normalized = (
        normalized.replace("，", ",")
        .replace("、", ",")
        .replace("~", "-")
        .replace("—", "-")
        .replace("–", "-")
        .replace("至", "-")
        .replace("（", "(")
        .replace("）", ")")
    )

    if any(token in normalized for token in ["every week", "每周", "全周"]):
        return list(range(1, max_week + 1))

    odd_only = any(token in normalized for token in ["单周", "(单)", "odd"])
    even_only = any(token in normalized for token in ["双周", "(双)", "even"])

    weeks_set = set()

    for start_str, end_str in re.findall(r"(\d{1,2})\s*-\s*(\d{1,2})", normalized):
        start_week, end_week = int(start_str), int(end_str)
        if start_week > end_week:
            start_week, end_week = end_week, start_week
        weeks_set.update(range(start_week, end_week + 1))

    normalized_no_ranges = re.sub(r"\d{1,2}\s*-\s*\d{1,2}", " ", normalized)
    for week_str in re.findall(r"\b(\d{1,2})\b", normalized_no_ranges):
        weeks_set.add(int(week_str))

    weeks = sorted(week for week in weeks_set if 1 <= week <= max_week)

    if odd_only:
        weeks = [week for week in weeks if week % 2 == 1]
    if even_only:
        weeks = [week for week in weeks if week % 2 == 0]

    return weeks


def extract_records_from_grid(html_text: str, max_week: int) -> List[CourseRecord]:
    soup = BeautifulSoup(html_text, "html.parser")
    records: List[CourseRecord] = []

    # Only parse event blocks to avoid picking up time-axis labels.
    for event_block in soup.select("td.day-cell > div.event"):
        day_cell = event_block.parent
        day_code = (day_cell.get("data-day") or "").upper()
        weekday = DAY_MAP.get(day_code)
        if weekday is None:
            continue

        name_element = event_block.select_one(".event-name")
        course_name = clean_text(
            name_element.get_text(" ", strip=True) if name_element else event_block.get_text(" ", strip=True)
        )

        if not course_name or re.fullmatch(r"\d{1,2}:\d{2}", course_name):
            continue

        info_lines = [clean_text(elem.get_text(" ", strip=True)) for elem in event_block.select(".event-info")]
        info_lines = [line for line in info_lines if line]

        weeks_text = ""
        time_text = ""
        misc_lines: List[str] = []

        for line in info_lines:
            if line.lower().startswith("week:"):
                weeks_text = line.split(":", 1)[1].strip()
            elif re.search(r"\d{1,2}:\d{2}\s*(?:-|~|–|—|至)\s*\d{1,2}:\d{2}", line):
                time_text = line
            else:
                misc_lines.append(line)

        # Typical layout: teacher -> location -> week -> time
        teacher = misc_lines[0] if len(misc_lines) >= 1 else ""
        location = misc_lines[1] if len(misc_lines) >= 2 else ""
        if len(misc_lines) > 2:
            teacher = " | ".join(misc_lines[:-1])
            location = misc_lines[-1]

        time_range = parse_time_range(time_text)
        weeks = parse_weeks(weeks_text, max_week=max_week)

        # Fallback: infer duration from td attributes (30-minute slots in this page layout)
        if time_range is None or not weeks:
            data_time = day_cell.get("data-time", "")
            rowspan = day_cell.get("rowspan", "")
            if time_range is None and data_time and str(rowspan).isdigit():
                start_time = parse_hhmm(data_time)
                end_dt = datetime.combine(date(2000, 1, 1), start_time) + timedelta(minutes=30 * int(rowspan))
                time_range = (start_time, end_dt.time())

        if time_range is None or not weeks:
            continue

        start_time, end_time = time_range

        records.append(
            CourseRecord(
                course=course_name,
                weekday=weekday,
                start_time=start_time,
                end_time=end_time,
                weeks=weeks,
                location=location,
                teacher=teacher,
                extra=" | ".join(info_lines),
            )
        )

    # Deduplicate records
    deduped_records: List[CourseRecord] = []
    seen = set()
    for record in records:
        key = (
            record.course.lower(),
            record.weekday,
            record.start_time.strftime("%H:%M"),
            record.end_time.strftime("%H:%M"),
            tuple(record.weeks),
            record.location.lower(),
            record.teacher.lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped_records.append(record)

    return deduped_records


def escape_ics_text(text: str) -> str:
    text = text or ""
    return (
        text.replace("\\", "\\\\")
        .replace(";", r"\;")
        .replace(",", r"\,")
        .replace("\n", r"\n")
    )


def fold_ics_line(line: str, limit: int = 75) -> str:
    if len(line) <= limit:
        return line
    chunks = []
    while len(line) > limit:
        chunks.append(line[:limit])
        line = " " + line[limit:]
    chunks.append(line)
    return "\r\n".join(chunks)


def to_ics_datetime_local(target_date: date, target_time: time) -> str:
    return f"{target_date:%Y%m%d}T{target_time:%H%M%S}"


def make_uid(seed: str, domain: str = "local.xjtlu") -> str:
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:20]
    return f"{digest}@{domain}"


def build_ics(records: List[CourseRecord], week1_monday: date, calendar_name: str, tzid: str) -> str:
    lines: List[str] = []
    now_utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    def add(line: str) -> None:
        lines.append(fold_ics_line(line))

    add("BEGIN:VCALENDAR")
    add("PRODID:-//OpenAI//XJTLU Timetable Grid HTML to ICS//CN")
    add("VERSION:2.0")
    add("CALSCALE:GREGORIAN")
    add("METHOD:PUBLISH")
    add(f"X-WR-CALNAME:{escape_ics_text(calendar_name)}")
    add(f"X-WR-TIMEZONE:{tzid}")

    add("BEGIN:VTIMEZONE")
    add(f"TZID:{tzid}")
    add("X-LIC-LOCATION:Asia/Shanghai")
    add("BEGIN:STANDARD")
    add("TZOFFSETFROM:+0800")
    add("TZOFFSETTO:+0800")
    add("TZNAME:CST")
    add("DTSTART:19700101T000000")
    add("END:STANDARD")
    add("END:VTIMEZONE")

    for record in records:
        for week in record.weeks:
            class_date = week1_monday + timedelta(weeks=week - 1, days=record.weekday - 1)
            uid = make_uid(
                f"{record.course}|{class_date}|{record.start_time}|{record.end_time}|{record.location}|{record.teacher}"
            )

            description_parts = []
            if record.teacher:
                description_parts.append(f"Teacher: {record.teacher}")
            description_parts.append("Weeks: " + ",".join(map(str, record.weeks)))
            if record.extra:
                description_parts.append("Raw: " + record.extra)
            description = "\n".join(description_parts)

            add("BEGIN:VEVENT")
            add(f"UID:{uid}")
            add(f"DTSTAMP:{now_utc}")
            add(f"SUMMARY:{escape_ics_text(record.course)}")
            add(f"DTSTART;TZID={tzid}:{to_ics_datetime_local(class_date, record.start_time)}")
            add(f"DTEND;TZID={tzid}:{to_ics_datetime_local(class_date, record.end_time)}")
            if record.location:
                add(f"LOCATION:{escape_ics_text(record.location)}")
            add(f"DESCRIPTION:{escape_ics_text(description)}")
            add("STATUS:CONFIRMED")
            add("TRANSP:OPAQUE")
            add("END:VEVENT")

    add("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def write_preview_csv(records: List[CourseRecord], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["course", "weekday", "start_time", "end_time", "weeks", "location", "teacher", "extra"])
        for record in records:
            writer.writerow(
                [
                    record.course,
                    record.weekday,
                    record.start_time.strftime("%H:%M"),
                    record.end_time.strftime("%H:%M"),
                    ",".join(map(str, record.weeks)),
                    record.location,
                    record.teacher,
                    record.extra,
                ]
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert saved XJTLU Timetable Plus grid HTML to ICS")
    parser.add_argument("--html", required=True, help="Path to saved_resource.html")
    parser.add_argument("--week1", required=True, help="Monday date of teaching week 1 (YYYY-MM-DD)")
    parser.add_argument("--out", default="xjtlu_timetable.ics", help="Output ICS file path")
    parser.add_argument("--calendar-name", default="XJTLU Timetable", help="Calendar name in the ICS file")
    parser.add_argument("--tz", default="Asia/Shanghai", help="Timezone ID for ICS events")
    parser.add_argument("--max-week", type=int, default=16, help="Maximum teaching week number used in parsing")
    parser.add_argument("--preview-csv", default="parsed_timetable_preview.csv", help="Preview CSV output path")
    args = parser.parse_args()

    html_path = Path(args.html)
    if not html_path.exists():
        print(f"File not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    try:
        week1_monday = date.fromisoformat(args.week1)
    except ValueError:
        print("Invalid --week1 format. Use YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)

    html_text = html_path.read_text(encoding="utf-8", errors="ignore")
    records = extract_records_from_grid(html_text, max_week=args.max_week)

    if not records:
        print("No course records were parsed from the HTML file.", file=sys.stderr)
        sys.exit(2)

    invalid_time_like_titles = sum(1 for record in records if re.fullmatch(r"\d{1,2}:\d{2}", record.course))
    if invalid_time_like_titles > 0:
        print("Parsing error detected: time-axis labels may have been parsed as course names.", file=sys.stderr)
        sys.exit(3)

    preview_path = Path(args.preview_csv)
    write_preview_csv(records, preview_path)

    ics_text = build_ics(
        records=records,
        week1_monday=week1_monday,
        calendar_name=args.calendar_name,
        tzid=args.tz,
    )

    out_path = Path(args.out)
    out_path.write_text(ics_text, encoding="utf-8", newline="")

    total_events = sum(len(record.weeks) for record in records)
    print(f"Parsed course records: {len(records)}")
    print(f"Generated calendar events: {total_events}")
    print(f"ICS file written to: {out_path.resolve()}")
    print(f"Preview CSV written to: {preview_path.resolve()}")

    print("\nFirst 10 parsed records:")
    for record in records[:10]:
        print(
            f"- {record.course} | Day {record.weekday} | "
            f"{record.start_time:%H:%M}-{record.end_time:%H:%M} | "
            f"weeks={record.weeks} | loc={record.location} | teacher={record.teacher}"
        )


if __name__ == "__main__":
    main()