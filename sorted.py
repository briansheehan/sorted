from music21 import *
from copy import deepcopy
import random
import importlib as imp
import math

MUSE4_SCORES = '/home/brian/Documents/MuseScore4/Scores/'
CHORD_SCORE = 'Diatonic Sevenths-Piano.mxl'

# https://music21.org/music21docs/moduleReference/moduleHarmony.html#chordsymbol

CHORD_SYMBOLS = ['', 'm', '+', 'dim', '7',
           'M7', 'm7', 'dim7', '7+', 'm7b5',  # half-diminished
           'mM7', '6', 'm6', '9', 'Maj9', 'm9',
           '11', 'Maj11', 'm11', '13',
           'Maj13', 'm13', 'sus2', 'sus4',
           'N6', 'It+6', 'Fr+6', 'Gr+6', 'pedal',
           'power', 'tristan', '/E', 'm7/E-', 'add2',
           '7omit3',]

ROMAN_NUMERALS = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii/o']

DIATONIC_CHORDS = list(map(lambda n: roman.RomanNumeral(n+'13', 'C'), ROMAN_NUMERALS))

def partition(a, pred):
   ain = []
   aout = []
   for x in a:
     if pred(x):
       ain.append(x)
     else:
       aout.append(x)
   return (ain, aout)

def make_exec_rest(length=0.5):
    return note.Rest(length, offset=None)  

def bubbleSort(arr):
    intermediate_lists = [arr.copy()]
    n = len(arr)
    for i in range(n):
        rests = []
        swapped = False; rests.append(make_exec_rest())
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]; rests.append(make_exec_rest())
                swapped = True; rests.append(make_exec_rest())
        intermediate_lists.append(rests + arr.copy())
        if not swapped:
            return intermediate_lists

def insertion_sort(arr):
    intermediate_lists = [arr.copy()]
    # using for loop until len(arr)
    # but start from 1 (cause we gonna compare it with i-1)
    for i in range(1, len(arr)):
        rests = []    
        key = arr[i]; rests.append(make_exec_rest())
        j = i - 1; rests.append(make_exec_rest())

        # using while loop cause we wanna compare a condition
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]; rests.append(make_exec_rest()) # replace every array[j+1] with [j]
            j -= 1;rests.append(make_exec_rest()) # until j = 0 OR key > array[j]
            #intermediate_lists.append(arr.copy())
        arr[j + 1] = key; rests.append(make_exec_rest()) # insert key on array[j+1]
        intermediate_lists.append(rests + arr.copy())
    return intermediate_lists

def selectionSort(arr):
    size = len(arr)
    intermediate_lists = [arr.copy()]
    for ind in range(size):
        rests = []  
        min_index = ind; rests.append(make_exec_rest())

        for j in range(ind + 1, size):
            if arr[j] < arr[min_index]:
                min_index = j; rests.append(make_exec_rest())
        arr[ind], arr[min_index] = arr[min_index], arr[ind]; rests.append(make_exec_rest())
        intermediate_lists.append(rests + arr.copy())
    return intermediate_lists

def make_arpeggio(r_numeral, key):
    chord = roman.RomanNumeral(f'{r_numeral}13', key)
    chord_pitches = list(chord.pitches)
    chord_pitches.append(pitch.Pitch(step=chord.root().step, octave=chord.root().octave + 2))
    return list(map(lambda p: note.Note(p, type='eighth', offset=None), chord_pitches))

# def make_notes(pitch_list):
#     return list(map(lambda p: note.Note(p, type='eighth'), pitch_list))

def get_dur(note_list):
    st = stream.Stream()
    st.append(note_list)
    return deepcopy(st.duration)

# def make_cello_part_old(note_list):
#     rests = [n for n in note_list if n.isRest]
#     all_notes = [n.transpose('-P15') for n in note_list if not n.isRest] # Transpose all notes down 2 octaves
#     note1, note4, note7 = all_notes[::3] # take every third note from the 8-note source material
#     note1.duration = duration.Duration(1)
#     for n in [note1, note4, note7]: n.articulations.append(articulations.Staccato())
#     if len(rests) > 1:
#         rests = rests[:-2] # remove the last two rests because they are being replaced by the extra note below.
#         extra = deepcopy(note1)
#         cello_notes = [extra, note1, note.Rest(0.5, offset=None), note4, note.Rest(1, offset=None), note7, deepcopy(note7)]
#     else:
#         note1.duration = duration.Duration(1)
#         cello_notes = [note1, note.Rest(0.5, offset=None), note4, note.Rest(1, offset=None), note7, deepcopy(note7)]
#     return rests + cello_notes

# def make_cello_part(note_list):
#     rests = [n for n in note_list if n.isRest]
#     all_notes = [n.transpose('-P15') for n in note_list if not n.isRest] # Transpose all notes down 2 octaves
#     note1, note4, note7 = all_notes[::3] # take every third note from the 8-note source material
#     note1.duration = duration.Duration(1)
#     for n in [note1, note4, note7]: n.articulations.append(articulations.Staccato())
#     # if len(rests) > 1:
#     #     rests = rests[:-2] # remove the last two rests because they are being replaced by the extra note below.
#     #     extra = deepcopy(note1)
#     #     cello_notes = [extra, note1, note.Rest(0.5, offset=None), note4, note.Rest(1, offset=None), note7, deepcopy(note7)]
#     # else:
#     note1.duration = duration.Duration(1)
#     cello_notes = [note1, note.Rest(0.5, offset=None), note4, note.Rest(1, offset=None), note7, deepcopy(note7)]
#     return rests + cello_notes

def append_cello_part(part, note_list):
    rests = [n for n in note_list if n.isRest]
    all_notes = [n.transpose('-P15') for n in note_list if not n.isRest] # Transpose all notes down 2 octaves
    note1, note4, note7 = all_notes[::3] # take every third note from the 8-note source material
    note1.duration = duration.Duration(1)
    for n in [note1, note4, note7]: n.articulations.append(articulations.Staccato())
    # if len(rests) > 1:
    #     rests = rests[:-2] # remove the last two rests because they are being replaced by the extra note below.
    #     extra = deepcopy(note1)
    #     cello_notes = [extra, note1, note.Rest(0.5, offset=None), note4, note.Rest(1, offset=None), note7, deepcopy(note7)]
    # else:
    cello_notes = [note1, note.Rest(0.5, offset=None), note4, note.Rest(1, offset=None), note7, deepcopy(note7)]
    if len(rests) > 0:
        part.append(meter.TimeSignature(f'{len(rests)}/8'))
        part.append(rests)
    part.append(meter.TimeSignature('4/4'))
    part.append(cello_notes)

def make_perc_figure(q_length):
        notes = []
        end_note = note.Unpitched(quarterLength=0.5, offset=None)
        q_length -= 0.5
        while q_length > 0:
            for i in range(2): notes.append(note.Unpitched(quarterLength=0.25, offset=None))
            q_length -= 0.5
        return notes + [end_note]

# The structure of each melodic segment is:
# [play variable number of rests, play melodic figure of 4-beats]
# The first melodic segment contains no rests, the others all have at least one rest.
#
# The structure of percusions part is to play where melody rests, and to rest
# where melody plays (apart from very last eight-note of melody which is an 8th note of percussion):
# [play rhythmic figure, rest, play 8th note]
# 
# [get_dur(melody_rests), get_dur(melody_notes)- 0.5, 0.5]
def make_perc_part(note_list):
    melody_rests = [n for n in note_list if n.isRest]
    melody_notes = [n for n in note_list if not n.isRest]
    l_perc_figure, l_perc_rests, l_perc_end = [get_dur(melody_rests).quarterLength,
                                        get_dur(melody_notes).quarterLength - 0.5, 0.5]

    perc_rests = note.Rest(quarterLength=l_perc_rests, offset=None)
    perc_end = note.Unpitched(quarterLength=l_perc_end, offset=None)

    if l_perc_figure == 0:
        return [perc_rests, perc_end]
    else:
        perc_figure = make_perc_figure(l_perc_figure)
        return perc_figure + [perc_rests, perc_end]
 
def append_perc_part(part, note_list):
    (melody_rests, melody_notes) = partition(note_list, lambda n: n.isRest)
    l_perc_figure, l_perc_rests, l_perc_end = [get_dur(melody_rests).quarterLength,
                                        get_dur(melody_notes).quarterLength - 0.5, 0.5]

    perc_rests = note.Rest(quarterLength=l_perc_rests, offset=None)
    perc_end = note.Unpitched(quarterLength=l_perc_end, offset=None)

    # if l_perc_figure == 0:
    #     return [perc_rests, perc_end]
    # else:
    #     perc_figure = make_perc_figure(l_perc_figure)
    #     return perc_figure + [perc_rests, perc_end]
    if len(melody_rests) > 0:
        part.append(meter.TimeSignature(f'{len(melody_rests)}/8'))
        part.append(make_perc_figure(l_perc_figure))
    part.append(meter.TimeSignature('4/4'))
    part.append([perc_rests, perc_end])

def concat(list_of_lists):
    return [sum(l, []) for l in list_of_lists]


def pad_to_length(target_len, note_list):
    for i in range(target_len - len(note_list)):
        note_list.append(note.Rest(0.5, offset=None))
    return note_list

def ceiling_multiple_of(multiplier, lower_limit):
    rem = lower_limit % multiplier
    if rem == 0:
        return lower_limit
    else:
        return lower_limit - rem + multiplier

def pad_to_longest(list_of_note_lists):
    max_len = max(map(lambda nl: len(nl), list_of_note_lists))
    target_len = ceiling_multiple_of(8, max_len)
    #extra_eights = max_len % 8
    #target_len = max_len - extra_eights + 8
    return list(map(lambda nl: pad_to_length(target_len, nl), list_of_note_lists))

def notes_to_rests(note_list):
    return list(map(lambda n: note.Rest(quarterLength=n.quarterLength, offset=None), note_list))

def strip_rests(note_list):
    (rests, notes) = partition(note_list, lambda n: n.isRest)
    if len(notes) % 8 != 0:
        raise Exception(f"Phrase length is not a multiple of 8 quarter notes: {notes}")   
    return notes

def split_every(n:int, l):
    return [l[i*n:(i+1)*n] for i in range(int(math.ceil(len(l) / n)))]

#assumes every group of 8 notes is a melodic phrase
def rm_dup_phrases(note_list):
    phrases = split_every(8, note_list)
    phrase_tuples = list(map(tuple, phrases))
    no_dup_phrases = list(dict.fromkeys(phrase_tuples))
    no_dup_phrases = list(map(list, no_dup_phrases))
    return sum(list(no_dup_phrases), [])


def make_score(key):
    arpegg_ii = make_arpeggio('ii', key)
    rootI, thirdI, fifthI = deepcopy(arpegg_ii[0:3])
    rootI.duration = get_dur(arpegg_ii)
    thirdI.duration = get_dur(arpegg_ii)
    fifthI.duration = get_dur(arpegg_ii)
    random.seed(1)
    #random.shuffle(arpegg_ii)
    arpegg_ii.sort(reverse=True)

    isort_lists = insertion_sort(deepcopy(arpegg_ii))
    bsort_lists = bubbleSort(deepcopy(arpegg_ii))
    ssort_lists = selectionSort(deepcopy(arpegg_ii))

    flute_part = stream.Part(instrument.Flute())
    violin_part = stream.Part(instrument.Violin())
    cello_part = stream.Part(instrument.Violoncello())
    tromb_part = stream.Part(instrument.Trombone())
    perc_part = stream.Part(instrument.SnareDrum())

    melody_parts = (flute_part, violin_part, tromb_part)
    perc_part.append([clef.PercussionClef(), dynamics.Dynamic('mp')])
    perc_part.staffLines = 1

    # Section 1
    for i, note_lists in enumerate([isort_lists, bsort_lists, ssort_lists]):
        melody_part = melody_parts[i]
        harmony_parts = list(melody_parts)
        harmony_parts.remove(melody_part)

        melody_part.append(dynamics.Dynamic('mf'))
        list(map(lambda part: part.append(dynamics.Dynamic('pp')), harmony_parts))     

        for note_list in note_lists:
            (rests, notes) = partition(note_list, lambda n: n.isRest)
            if len(rests) > 0:
                melody_part.append(meter.TimeSignature(f'{len(rests)}/8'))
                melody_part.append(deepcopy(rests))
            melody_part.append(meter.TimeSignature('4/4'))
            melody_part.append(deepcopy(notes))
            for (hpart, hnote) in zip(harmony_parts, [fifthI, rootI]):
                # hpart.append(note.Note(pitch, duration=duration.Duration(4)))
                if len(rests) > 0:
                    hpart.append(meter.TimeSignature(f'{len(rests)}/8'))
                    hpart.append(deepcopy(rests))
                hpart.append(meter.TimeSignature('4/4'))
                hpart.append(deepcopy(hnote))
            #perc_part.repeatAppend(note.Unpitched(duration=duration.Duration(0.5)), len(note_list))
            append_cello_part(cello_part, deepcopy(note_list))
            # perc_part.append(make_perc_part(note_list))
            append_perc_part(perc_part, deepcopy(note_list))

    # Section 2    
    [isort_list, bsort_list, ssort_list] = concat([isort_lists, bsort_lists, ssort_lists])
    [isort_list, bsort_list, ssort_list] = pad_to_longest([isort_list, bsort_list, ssort_list])
    for (part, note_list) in zip(melody_parts, [isort_list, bsort_list, ssort_list]):
        for n in note_list:
            part.append(deepcopy(n))

    for part in [cello_part, perc_part]:
        for n in isort_list:
            part.append(note.Rest(0.5, offset=None))

    # Section 3
    [isort_list, bsort_list, ssort_list] = list(map(strip_rests, [isort_list, bsort_list, ssort_list]))
    #[isort_list, bsort_list, ssort_list] = list(map(rm_dup_phrases, [isort_list, bsort_list, ssort_list]))
    [isort_list, bsort_list, ssort_list] = pad_to_longest([isort_list, bsort_list, ssort_list])
    cello_note_list = notes_to_rests(isort_list)
    perc_note_list = deepcopy(cello_note_list)
    for (part, note_list) in zip(melody_parts + (cello_part, perc_part),
                                 [isort_list, bsort_list, ssort_list, cello_note_list, perc_note_list]):
        for n in note_list:
            part.append(deepcopy(n))

    score = stream.Score()
    for part in [flute_part, violin_part, tromb_part, cello_part, perc_part]:
        #stream.makeNotation.consolidateCompletedTuplets(part, recurse=True)
        #part.makeMeasures(inPlace=True)
        #part.makeBeams(inPlace=True)
        part.makeNotation(inPlace=True)
        score.insert(part)

    score.show()

make_score('C')

#make_first_score()
    # for chord in score.recurse().getElementsByClass(chord.Chord):
    #     print(chord)


def mergeSort(arr):
  if len(arr) <= 1:
    return arr

  mid = len(arr) // 2
  leftHalf = arr[:mid]
  rightHalf = arr[mid:]

  sortedLeft = mergeSort(leftHalf)
  sortedRight = mergeSort(rightHalf)

  return merge(sortedLeft, sortedRight)

def merge(left, right):
  result = []
  i = j = 0

  while i < len(left) and j < len(right):
    if left[i] < right[j]:
      result.append(left[i])
      i += 1
    else:
      result.append(right[j])
      j += 1

  result.extend(left[i:])
  result.extend(right[j:])

  return result