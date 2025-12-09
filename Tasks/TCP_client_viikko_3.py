import socket
import urllib.request
import os
import csv
import json
import pandas as pd
from bs4 import BeautifulSoup

HOST = "172.20.241.9"  # The server's hostname or IP address
PORT = 20000  # The port used by the server
URL = "http://172.20.241.9/luedataa_kannasta_groupid_csv.php?groupid=15"
OUT_CSV = "output.csv"
RAW_HTML = "raw_response.html"


def fetch_url(url):
    resp = urllib.request.urlopen(url)
    raw = resp.read()
    try:
        charset = resp.headers.get_content_charset() or "utf-8"
    except Exception:
        charset = "utf-8"
    text = raw.decode(charset, errors="replace")
    return raw, text


def parse_html_table(soup):
    import re
    from collections import Counter

    table = soup.find("table")
    if table is None:
        return None, None

    rows_by_tr = []
    for tr in table.find_all("tr"):
        cells = [cell.get_text(strip=True) for cell in tr.find_all(["th", "td"])]
        if cells:
            rows_by_tr.append(cells)

    if len(rows_by_tr) > 1:
        headers = None
        data_rows = rows_by_tr
        thead = table.find("thead")
        if thead:
            headers = rows_by_tr[0]
            data_rows = rows_by_tr[1:]
        else:
            first = rows_by_tr[0]
            if any(any(c.isalpha() for c in cell) for cell in first) and all(len(r) == len(first) for r in rows_by_tr[:6]):
                headers = first
                data_rows = rows_by_tr[1:]

        return headers, data_rows

    td_elems = table.find_all("td")
    td_texts = [td.get_text(strip=True) for td in td_elems]
    if not td_texts:
        return None, None

    ts_re = re.compile(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}")
    ts_indices = [i for i, t in enumerate(td_texts) if ts_re.search(t)]

    if len(ts_indices) >= 2:
        diffs = [j - i for i, j in zip(ts_indices, ts_indices[1:])]
        most = Counter(diffs).most_common(1)
        cols = most[0][0] if most else 11
    else:
        cols = 11

    rows = []
    if ts_indices:
        start = ts_indices[0] - 1
        if start < 0:
            start = 0
        for s in range(start, len(td_texts), cols):
            chunk = td_texts[s : s + cols]
            if len(chunk) == cols:
                rows.append(chunk)
    else:
        for s in range(0, len(td_texts), cols):
            chunk = td_texts[s : s + cols]
            if len(chunk) == cols:
                rows.append(chunk)

    return None, rows


def parse_pre_or_br(soup):
    pre = soup.find("pre")
    lines = []
    if pre:
        text = pre.get_text("\n", strip=True)
        lines = [l for l in (ln.strip() for ln in text.splitlines()) if l]
        return lines

    parts = []
    for tag in soup.find_all(["p", "li"]):
        t = tag.get_text(" ", strip=True)
        if t:
            parts.append(t)

    body = soup.body or soup
    br_lines = []
    for elem in body.descendants:
        try:
            name = elem.name
        except Exception:
            txt = str(elem).strip()
            if txt:
                br_lines.append(txt)
            continue

    if br_lines:
        parts.extend(br_lines)

    if parts:
        return parts

    body_text = body.get_text("\n", strip=True)
    lines = [l for l in (ln.strip() for ln in body_text.splitlines()) if l]
    return lines


def write_csv(out_file, headers, rows, delimiter=","):
    if not rows:
        print("No rows to write.")
        return
    file_exists = os.path.exists(out_file)
    encoding = "utf-8-sig" if not file_exists else "utf-8"
    with open(out_file, "a", newline="", encoding=encoding) as f:
        writer = csv.writer(f, delimiter=delimiter)
        if not file_exists and headers:
            writer.writerow(headers)
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out_file} (append mode={file_exists}, delimiter='{delimiter}').")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        raw, text = fetch_url(URL)
        try:
            with open(RAW_HTML, "wb") as rf:
                rf.write(raw)
        except Exception as e:
            print(f"Could not write raw response file: {e}")

        try:
            data = json.loads(text)
            if isinstance(data, list) and data:
                headers = list(data[0].keys())
                rows = [[item.get(h, "") for h in headers] for item in data]
                write_csv(OUT_CSV, headers, rows)
                return
            if isinstance(data, dict):
                keys = list(data.keys())
                if keys and all(isinstance(data[k], list) for k in keys):
                    length = max(len(data[k]) for k in keys)
                    rows = []
                    for i in range(length):
                        row = [data[k][i] if i < len(data[k]) else "" for k in keys]
                        rows.append(row)
                    write_csv(OUT_CSV, keys, rows)
                    return
        except json.JSONDecodeError:
            pass

        soup = BeautifulSoup(text, "html.parser")
        headers, rows = parse_html_table(soup)
        if headers is not None and rows:
            write_csv(OUT_CSV, headers, rows)
            return

        lines = parse_pre_or_br(soup)
        if not lines:
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if not lines:
            print("No readable content returned from URL")
            return

        first = lines[0]
        if ";" in first:
            used_delim = ";"
            sample_cols = first.split(used_delim)
        else:
            for delim in [",", "\t", " "]:
                sample_cols = first.split(delim)
                if len(sample_cols) > 1:
                    used_delim = delim
                    break
            else:
                sample_cols = [first]
                used_delim = ","
        try:
            non_numeric = sum(1 for c in sample_cols if not c.replace('.', '', 1).isdigit())
            is_header = non_numeric >= len(sample_cols) / 2
        except Exception:
            is_header = False

        rows_out = []
        start_idx = 0
        headers_out = None
        if is_header:
            headers_out = [c.strip() for c in sample_cols]
            start_idx = 1

        for ln in lines[start_idx:]:
            row = [c.strip() for c in ln.split(used_delim)]
            rows_out.append(row)

        if used_delim == ";" and not headers_out:
            headers_out = [
                "id",
                "timestamp",
                "GroupID",
                "src_mac",
                "device",
                "X",
                "Y",
                "Z",
                "val4",
                "val5",
                "val6",
            ]

        if headers_out:
            desired_len = len(headers_out)
            norm_rows = []
            for r in rows_out:
                if len(r) < desired_len:
                    r = r + [""] * (desired_len - len(r))
                elif len(r) > desired_len:
                    r = r[:desired_len]
                norm_rows.append(r)
            rows_out = norm_rows

    write_csv(OUT_CSV, headers_out, rows_out, delimiter=used_delim)


if __name__ == "__main__":
    main()