import csv
from tqdm import tqdm
import nlp2


# {
#     "input": [
#         example1 input,
#         example2 input,
#         ...
#     ],
#     "target": [
#         example1 target,
#         example2 target,
#         ...
#     ]
# }

class MiddleFormat:

    def __init__(self, type):
        self.pairs = []
        self.Type = type

    def add_data(self, input, target):
        self.pairs.append([input, target])

    def __run_pair_utility(self, path, pairsu_func=[]):
        processed_pair = []
        if len(pairsu_func) > 0:
            for func_pack in pairsu_func:
                func, func_arg = func_pack
                if len(processed_pair) > 0:
                    new_pp = []
                    for pp in processed_pair:
                        path, pairs = pp
                        new_pp.extend(func(path, pairs, **func_arg))
                    processed_pair = new_pp
                else:
                    processed_pair = func(path, self.pairs, **func_arg)
        else:
            processed_pair = [[path, self.pairs]]
        return processed_pair

    def __run_sent_utility(self, sents, sentu_func=[]):
        for ind, sent in enumerate(sents):
            for func, func_arg in sentu_func:
                sents[ind] = func(sent, **func_arg)
        return sents

    def convert_to_taskformat(self, task, input, target, sentu_func):
        if task == "tag":
            input = " ".join(input)
            target = " ".join(target)
            input = self.__run_sent_utility([input], sentu_func)[0]
        elif task == "gen":
            if not nlp2.is_all_english(input):
                input = " ".join(nlp2.split_sentence_to_array(input))
                target = " ".join(nlp2.split_sentence_to_array(target))
            input, target = self.__run_sent_utility([input, target], sentu_func)
        elif task == "clas":
            if not nlp2.is_all_english(input):
                input = " ".join(nlp2.split_sentence_to_array(input))
            input, target = self.__run_sent_utility([input, target], sentu_func)
        elif task == "qa":
            input = " ".join(input)
            input = self.__run_sent_utility([input], sentu_func)[0]
        return input, target

    def dump(self, path, task, pairsu_func=[], sentu_func=[]):
        processed_pair = self.__run_pair_utility(path, pairsu_func)
        for pp in processed_pair:
            path, pairs = pp
            with open(path + ".csv", 'w', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                for input, target in tqdm(pairs):
                    input, target = self.convert_to_taskformat(task, input, target, sentu_func)
                    row = [input] + target if isinstance(target, list) else [input, target]
                    writer.writerow(row)
        return [i[0] + ".csv" for i in processed_pair]
