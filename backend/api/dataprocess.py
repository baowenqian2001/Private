import string

def gopt_pre_process(wav_name, content):
    scp_file = r"data/test/wav.scp"
    spk2utt = r"data/test/spk2utt"
    utt2spk = r"data/test/utt2spk"
    text = r"data/test/text"

    with open("data/resource/lexicon.txt", 'r') as f:
        lexicon_raw = f.read()
        rows = lexicon_raw.splitlines()
    clean_rows = [row.split() for row in rows]
    lexicon_dict_l = dict()
    for row in clean_rows:
        c_row = row.copy()
        key = c_row.pop(0)
        if len(c_row) == 1:
            c_row[0] = c_row[0] + '_S'
        if len(c_row) >= 2:
            c_row[0] = c_row[0] + '_B'
            c_row[-1] = c_row[-1] + '_E'
        if len(c_row) > 2:
            for i in range(1,len(c_row)-1):
                c_row[i] = c_row[i] + '_I'
        val = " ".join(c_row)
        lexicon_dict_l[key] = val

    # wav_name = "1679044959342.wav"
    # content = "WE CALL IT BEAR"
    content = content.translate(str.maketrans("", "", string.punctuation))
    words = content.split(' ')
    spk = "0001"
    utt = "000010011"

    scp_str = utt + '	' + f"WAVE/SPEAKER0001/{wav_name}\n"
    spk2utt_str = spk + '	' + utt + "\n"
    utt2spk_str = utt + '	' + spk + "\n"
    text_str = utt + '	' + content + "\n"
    text_phone = ""

    for i in range(len(words)):
        text_phone = text_phone + utt + f'.{i} ' + lexicon_dict_l[words[i].upper()] + '\n'

    with open(scp_file, 'w') as f:
        f.write(scp_str)

    with open(spk2utt, 'w') as f:
        f.write(spk2utt_str)

    with open(utt2spk, 'w') as f:
        f.write(utt2spk_str)

    with open(text, 'w') as f:
        f.write(text_str)

    with open('data/resource/text-phone', 'w') as f:
        f.write(text_phone)