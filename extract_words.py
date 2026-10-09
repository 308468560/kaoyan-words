# -*- coding: utf-8 -*-
import pdfplumber, re, json, warnings
warnings.filterwarnings('ignore')

PDF = r'D:\2\WEB\墨墨单词本-3502-20260921225949.pdf'

IPA_CHARS = set('[]ˈˌɪʌəɜɔɒʊʊæɑeɪaɪɔɪəʊɡθðʃŋʒtrdw')
WORD_RE = re.compile(r"^[A-Za-z][A-Za-z\-']*$")
NUM_RE = re.compile(r'^\d{1,3}$')

def has_cjk(s):
    return any('一' <= c <= '鿿' for c in s)

def is_ipa(tok):
    return any(c in IPA_CHARS for c in tok) and not has_cjk(tok)

pdf = pdfplumber.open(PDF)
result = {}

for pi, page in enumerate(pdf.pages):
    tokens = page.extract_words(extra_attrs=['size', 'fontname'])
    for t in tokens:
        t['text'] = t['text'].replace('\x00', '-')
    # 找所有列表标题行 (size≈12, top<780)
    headers = []
    for t in tokens:
        if abs(t['size'] - 12) < 1.5 and t['top'] < 780:
            headers.append(t)
    # 组合成标题字符串
    hdr_rows = {}
    for t in headers:
        row = round(t['top'])
        hdr_rows.setdefault(row, []).append(t)
    # 筛选含 List 的行
    sections = []
    for row, toks in sorted(hdr_rows.items()):
        s = ' '.join(t['text'] for t in sorted(toks, key=lambda t: t['x0']))
        m = re.search(r'(\S+)\s*Day\s*(\d+)\s*List\s*(\d+)', s)
        if m:
            sections.append((row, m.group(1), int(m.group(2)), int(m.group(3))))
    if not sections:
        continue
    # 按 section 拆分 tokens
    bounds = [s[0] - 10 for s in sections] + [801]
    for si, (row, cat, day, lno) in enumerate(sections):
        key = f'{cat} Day {day:02d} List {lno}'
        lo, hi = bounds[si], bounds[si + 1]
        sec_tokens = [t for t in tokens if lo <= t['top'] < hi and t['top'] < 780]
        # 分左栏右栏 (x分隔线约297)
        for col_x, def_x in ((0, 150), (297, 420)):
            col = [t for t in sec_tokens if col_x <= t['x0'] < col_x + 298]
            if col_x == 0:
                col = [t for t in col if t['x0'] < 297]
            # 序号: 纯数字, size≈11, x0<60
            nums = [t for t in col if NUM_RE.match(t['text']) and abs(t['size'] - 11) < 1.5 and t['x0'] < col_x + 60]
            if not nums:
                continue
            nums.sort(key=lambda t: t['top'])
            n_bounds = [n['top'] - 16 for n in nums] + [hi]
            for i, n in enumerate(nums):
                y0, y1 = n_bounds[i], n_bounds[i + 1]
                region = [t for t in col if y0 <= t['top'] < y1]
                num = int(n['text'])
                # 单词 (可能跨行, 不同行直接拼接)
                wtoks = [t for t in region if 'ENVF_500wght' in t['fontname']
                         and t['size'] >= 9.5 and WORD_RE.match(t['text'])]
                wtoks.sort(key=lambda t: (round(t['top']), t['x0']))
                wparts = []
                for j, t in enumerate(wtoks):
                    if j and t['top'] - wtoks[j - 1]['top'] <= 4:
                        wparts.append(' ')
                    wparts.append(t['text'])
                word = ''.join(wparts)
                # 音标
                ptoks = [t for t in region if t['x0'] < def_x and t['size'] < 9
                         and is_ipa(t['text'])]
                ptoks.sort(key=lambda t: (round(t['top']), t['x0']))
                phon = ''.join(t['text'] for t in ptoks)
                # 释义
                dtoks = [t for t in region if t['x0'] >= def_x]
                dtoks.sort(key=lambda t: (round(t['top']), t['x0']))
                parts, prev_top = [], None
                for t in dtoks:
                    need_sp = parts and not has_cjk(parts[-1][-1]) and not has_cjk(t['text'][0])
                    if prev_top is not None and t['top'] - prev_top > 4:
                        if need_sp:
                            parts.append(' ')
                    elif need_sp:
                        parts.append(' ')
                    parts.append(t['text'])
                    prev_top = t['top']
                defin = ''.join(parts).strip()
                if key not in result:
                    result[key] = {}
                if num in result[key]:
                    # 重复时保留有单词的
                    if word and not result[key][num]['word']:
                        result[key][num] = {'word': word, 'phon': phon, 'def': defin}
                else:
                    result[key][num] = {'word': word, 'phon': phon, 'def': defin}

pdf.close()

# 报告
total = 0
for key in sorted(result):
    nums = sorted(result[key])
    total += len(nums)
    missing = [i for i in range(1, (nums[-1] if nums else 0) + 1) if i not in result[key]]
    print(f'{key}: {len(nums)} {"缺:"+str(missing) if missing else ""}')
print(f'\n总词条: {total}')

with open(r'D:\2\WEB\words.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
print('已保存 words.json')

# 生成 Markdown 和 CSV
import csv

def sort_key(k):
    m = re.search(r'Day (\d+) List (\d+)', k)
    return (int(m.group(1)), int(m.group(2)))

md = ['# 墨墨背单词 2026十天搞定考研词汇便携版\n',
      f'共 20 个 List，{total} 个词条\n']
for key in sorted(result, key=sort_key):
    ents = result[key]
    md.append(f'\n## {key}（{len(ents)} 词）\n')
    md.append('| # | 单词 | 音标 | 释义 |')
    md.append('|---|---|---|---|')
    for n in sorted(ents):
        e = ents[n]
        defin = e['def'].replace('|', '\\|')
        md.append(f"| {n} | {e['word']} | {e['phon']} | {defin} |")

with open(r'D:\2\WEB\墨墨单词本-3502-单词表.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(md))

with open(r'D:\2\WEB\墨墨单词本-3502-单词表.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['List', '序号', '单词', '音标', '释义'])
    for key in sorted(result, key=sort_key):
        for n in sorted(result[key]):
            e = result[key][n]
            w.writerow([key, n, e['word'], e['phon'], e['def']])
print('已生成 墨墨单词本-3502-单词表.md / .csv')
