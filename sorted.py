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
    intermediate_lists = [deepcopy(arr)]
    n = len(arr)
    for i in range(n):
        rests = []
        swapped = False; rests.append(make_exec_rest())
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]; rests.append(make_exec_rest())
                swapped = True; rests.append(make_exec_rest())
        intermediate_lists.append(rests + deepcopy(arr))
        if not swapped:
            return intermediate_lists

def insertion_sort(arr):
    intermediate_lists = [deepcopy(arr)]
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
            #intermediate_lists.append(deepcopy(arr))
        arr[j + 1] = key; rests.append(make_exec_rest()) # insert key on array[j+1]
        intermediate_lists.append(rests + deepcopy(arr))
    return intermediate_lists

def selectionSort(arr):
    size = len(arr)
    intermediate_lists = [deepcopy(arr)]
    for ind in range(size):
        rests = []  
        min_index = ind; rests.append(make_exec_rest())

        for j in range(ind + 1, size):
            if arr[j] < arr[min_index]:
                min_index = j; rests.append(make_exec_rest())
        arr[ind], arr[min_index] = arr[min_index], arr[ind]; rests.append(make_exec_rest())
        intermediate_lists.append(rests + deepcopy(arr))
    return intermediate_lists

def make_arpeggio(r_numeral, key):
    chord = roman.RomanNumeral(f'{r_numeral}13', key)
    chord_pitches = list(chord.pitches)
    chord_pitches.append(pitch.Pitch(step=chord.root().step, octave=chord.root().octave + 2))
    return list(map(lambda p: note.Note(p, type='eighth', offset=None), chord_pitches))

# def make_notes(pitch_list):
#     return list(map(lambda p: note.Note(p, type='eighth'), pitch_list))

#<music21.stream.Stream 0x7bf3db1bb380>
def get_q_length(note_list):
    st = stream.Stream()
    st.append(deepcopy(note_list))
    return st.duration.quarterLength

CELLO_RHYTHM = [1, 0.5, 0.5, 1, 0.25, 0.25, 0.25, 0.25]

def append_cello_part(part, note_list):
    rests = [n for n in note_list if n.isRest]
    all_notes = [n.transpose('-P15') for n in note_list if not n.isRest] # Transpose all notes down 2 octaves
    note1, note4, note7 = all_notes[::3] # take every third note from the 8-note source material

    for n in [note1, note4]: n.articulations.append(articulations.Staccato())

    cello_notes = [note1, note.Rest(offset=None), note4, note.Rest(offset=None),
                   note7, deepcopy(note7), deepcopy(note7), deepcopy(note7)]
    
    for c_note, q_length in zip(cello_notes, CELLO_RHYTHM): c_note.quarterLength = q_length

    if len(rests) > 0:
        part.append(meter.TimeSignature(f'{len(rests)}+{len(rests)}/16'))
        part.append(rests)
    part.append(meter.TimeSignature('4/4'))
    part.append(cello_notes)

# The structure of each melodic segment is:
# [play variable number of rests, play melodic figure of 4-beats]
# The first melodic segment contains no rests, the others all have at least one rest.
#
# The structure of percusions part is to play where melody rests, and to rest
# where melody plays (apart from very last eight-note of melody which is an 8th note of percussion):
# [play rhythmic figure, rest, play 8th note]
# 
# [get_q_length(melody_rests), get_q_length(melody_notes)- 0.5, 0.5]

def make_perc_solo(num_of_eights:int):
    quot, rem = divmod(num_of_eights, 2)
    eights = [0.5 for i in range(0, quot)]
    sixteenths = [0.25 for i in range(0, rem)] # Will be one sixteenth, or none
    figure =  eights + sixteenths + eights + sixteenths
    figure_notes = [note.Unpitched(quarterLength=l, offset=None) for l in figure]
    [n.articulations.append(articulations.Accent()) for n in figure_notes[::quot+rem]] 
    return figure_notes

# def compound_partition(num_of_eights:int):
#     quot, rem = divmod(num_of_eights, 2)
#     eights = [0.5 for i in range(0, quot)]
#     sixteenths = [0.25 for i in range(0, rem)] # Will be one sixteenth, or none

#     match num_of_eights:
#         case 5:
#             p_list = '5/16+5/16'
#             #p_list = [f'{len(eights)}/8', f'{len(sixteenths)}/16', f'{len(eights)}/8', f'{len(sixteenths)}/16']
#         case 7:
#             p_list = ['3/8', '7/16', '1/16' ]
#         case 9:
#             p_list = ['1/2', '1/16', '1/2', '1/16']
#         case _:
#             p_list =[f'{num_of_eights}/8']

#     return p_list


# def beam_time_sig(ts: meter.TimeSignature):
#     match ts.denominator:
#         case 8:
#             ts.beamSequence.partition(compound_partition(ts.numerator)) 
#     return ts

def append_sect1_perc(part, note_list):
    melody_rests, melody_notes = partition(note_list, lambda n: n.isRest)
    l_perc_solo = len(melody_rests)

    if l_perc_solo > 0:
        ts = meter.TimeSignature(f'{l_perc_solo}+{l_perc_solo}/16')
        ts.beamSequence.partition(2)
        part.append(ts)
        part.append(make_perc_solo(l_perc_solo))

    l_perc_start = 1 # 1 eight note
    l_perc_end = 0.5
    l_perc_rests = len(melody_notes) - l_perc_start - l_perc_end
    
    perc_start = note.Unpitched(quarterLength=l_perc_start/2, offset=None) 
    perc_start.articulations.append(articulations.Accent())  
    perc_rests = note.Rest(quarterLength=l_perc_rests/2, offset=None)
    perc_end = note.Unpitched(quarterLength=l_perc_end/2, offset=None)
    # m = stream.Measure()
    # m.stafflines = 1
    part.append(meter.TimeSignature('4/4'))
    part.append([perc_start, perc_rests, perc_end])
    # part.append(m.makeBeams())

def make_sect2_perc(note_list):
    rhythm_fig = [note.Unpitched(quarterLength=1.5), note.Unpitched(quarterLength=0.5), note.Unpitched(quarterLength=1.5), note.Unpitched(quarterLength=0.5)]
    melody_rests, melody_notes = partition(note_list, lambda n: n.isRest)
    return melody_rests + rhythm_fig

def concat(list_of_lists):
    return sum(list_of_lists, [])


def pad_to_length(target_len, note_list):
    for i in range(target_len - int(get_q_length(note_list) * 2)):
        note_list.append(note.Rest(0.5, offset=None))
    return note_list

def ceiling_multiple_of(multiplier, lower_limit):
    rem = lower_limit % multiplier
    if rem == 0:
        return lower_limit
    else:
        return lower_limit - rem + multiplier

def pad_to_longest(list_of_note_lists):
    # max_len = max(map(lambda nl: len(nl), list_of_note_lists))
    max_len = max(map(lambda nl: get_q_length(nl), list_of_note_lists))
    max_len_eight_notes = int(2*max_len)
    target_len = ceiling_multiple_of(8, max_len_eight_notes)

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
    return concat(no_dup_phrases)


def make_score(key):
    arpegg_ii = make_arpeggio('ii', key)
    rootI, thirdI, fifthI = deepcopy(arpegg_ii[0:3])
    rootI.quarterLength = get_q_length(arpegg_ii)
    thirdI.quarterLength = get_q_length(arpegg_ii)
    fifthI.quarterLength = get_q_length(arpegg_ii)
    random.seed(100)
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
                melody_part.append(meter.TimeSignature(f'{len(rests)}+{len(rests)}/16'))
                melody_part.append(deepcopy(rests))
            melody_part.append(meter.TimeSignature('4/4'))
            melody_part.append(deepcopy(notes))
            for (hpart, hnote) in zip(harmony_parts, [fifthI, rootI]):
                # hpart.append(note.Note(pitch, duration=duration.Duration(4)))
                if len(rests) > 0:
                    hpart.append(meter.TimeSignature(f'{len(rests)}+{len(rests)}/16'))
                    hpart.append(deepcopy(rests))
                hpart.append(meter.TimeSignature('4/4'))
                hpart.append(deepcopy(hnote))
            #perc_part.repeatAppend(note.Unpitched(duration=duration.Duration(0.5)), len(note_list))
            append_cello_part(cello_part, deepcopy(note_list))
            # perc_part.append(make_perc_part(note_list))
            append_sect1_perc(perc_part, deepcopy(note_list))

    # Section 2
    perc_note_lists = []
    for note_list in ssort_lists: # ssort_lists is the material used for the trombone part
        perc_note_lists.append(make_sect2_perc(deepcopy(note_list)))
  
    [isort_list, bsort_list, ssort_list, perc_note_list] = list(map(concat, [isort_lists, bsort_lists, ssort_lists, perc_note_lists]))
    pnl = get_q_length(perc_note_list)
    ssl = get_q_length(ssort_list)
    [isort_list, bsort_list, ssort_list, perc_note_list] = pad_to_longest([isort_list, bsort_list, ssort_list, perc_note_list])
    for (part, note_list) in zip(melody_parts + (perc_part,), [isort_list, bsort_list, ssort_list, perc_note_list]):
        for n in note_list:
            part.append(deepcopy(n))

    # for part in [cello_part, perc_part]:
    #     for n in isort_list:
    #         part.append(note.Rest(0.5, offset=None))

    for n in isort_list:
        cello_part.append(note.Rest(0.5, offset=None))
    

    # perc_note_list = [note.Unpitched(quarterLength=1), note.Unpitched(quarterLength=0.5), note.Unpitched(quarterLength=0.5),
    #                   note.Unpitched(quarterLength=1), note.Rest(quarterLength=0.5), note.Unpitched(quarterLength=0.5)]
    # perc_note_list = [note.Unpitched(quarterLength=1.5), note.Unpitched(quarterLength=0.5), note.Unpitched(quarterLength=1.5), note.Unpitched(quarterLength=0.5)]
    # for bar in isort_list[::8]:
    #     perc_part.append(deepcopy(perc_note_list))    
    

    # Section 3
    [isort_list, bsort_list, ssort_list] = list(map(strip_rests, [isort_list, bsort_list, ssort_list]))
    #[isort_list, bsort_list, ssort_list] = list(map(rm_dup_phrases, [isort_list, bsort_list, ssort_list]))
    [isort_list, bsort_list, ssort_list] = pad_to_longest([isort_list, bsort_list, ssort_list])
    cello_note_list = notes_to_rests(isort_list)
    #perc_note_list = deepcopy(cello_note_list)
    for (part, note_list) in zip(melody_parts + (cello_part,),
                                 [isort_list, bsort_list, ssort_list, cello_note_list]):
        for n in note_list:
            part.append(deepcopy(n))
    
    perc_note_list = [note.Unpitched(quarterLength=0.5), note.Unpitched(quarterLength=0.5), note.Unpitched(quarterLength=0.5), note.Unpitched(quarterLength=0.25),
                    note.Unpitched(quarterLength=0.5), note.Unpitched(quarterLength=0.5), note.Unpitched(quarterLength=0.5), note.Unpitched(quarterLength=0.5), note.Unpitched(quarterLength=0.25)]
    for bar in isort_list[::8]:
        perc_part.append(deepcopy(perc_note_list))   

    score = stream.Score()
    for part in [flute_part, violin_part, tromb_part, cello_part, perc_part]:
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