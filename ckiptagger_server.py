
from ckiptagger import data_utils, construct_dictionary, WS, POS, NER
from concurrent import futures

import ckiptagger_pb2
import ckiptagger_pb2_grpc
import grpc
import json
import logging
import os

ws, pos, ner = None, None, None
external_delimiter_set = {",", "。", ":", "?", "!", ";"}
external_recommend, external_coerce = {}, {}

class Tagger(ckiptagger_pb2_grpc.TaggerServicer):
    def __init__(self):
        global ws, pos, ner, external_delimiter_set, external_recommend, external_coerce

        if not os.path.exists("./data/model_ws"): return

        ws = WS("./data")
        pos = POS("./data")
        ner = NER("./data")

        if os.path.exists("./data/delimiter.json"):
            with open("./data/delimiter.json", "r") as f:
                external_delimiter_set = set(json.load(f))
                f.close()

        if os.path.exists("./data/recommend.json"):
            with open("./data/recommend.json", "r") as f:
                external_recommend = json.load(f)
                f.close()

        if os.path.exists("./data/coerce.json"):
            with open("./data/coerce.json", "r") as f:
                external_coerce = json.load(f)
                f.close()

    def GetWordSegmentation(self, request, context):
        if (ws == None):
            return ckiptagger_pb2.GetWordSegmentationRequest.Result()

        sentence_list = request.sentences

        segment_delimiter_set = external_delimiter_set.copy()
        if request.delimiter.value.strip() != "": segment_delimiter_set.update(set(request.delimiter.value.strip()))

        recommend_dictionary = external_recommend.copy()
        if request.recommend: recommend_dictionary.update(request.recommend)

        coerce_dictionary = external_coerce.copy()
        if request.coerce: coerce_dictionary.update(request.coerce)

        word_sentence_list = ws(sentence_list, construct_dictionary(recommend_dictionary), construct_dictionary(coerce_dictionary), segment_delimiter_set=segment_delimiter_set)
        pos_sentence_list = [] if not request.enablePOS.value else pos(word_sentence_list, segment_delimiter_set=segment_delimiter_set)
        entity_sentence_list = [] if not (request.enableNER.value and request.enablePOS.value) else ner(word_sentence_list, pos_sentence_list)

        result = ckiptagger_pb2.GetWordSegmentationRequest.Result()

        for i, sentence in enumerate(sentence_list):
            wp = get_word_pos_sentence(word_sentence_list[i],  pos_sentence_list[i]) if request.enablePOS.value else word_sentence_list[i]
            item = ckiptagger_pb2.GetWordSegmentationRequest.Result.Sentence(words=wp)
            result.sentences.append(item)

            if request.enableNER.value and request.enablePOS.value:
                entities = []
                for entity in sorted(entity_sentence_list[i]):
                    entities.append(f"{entity}")
                item = ckiptagger_pb2.GetWordSegmentationRequest.Result.Sentence(words=entities)
                result.entities.append(item)

        return result

def get_word_pos_sentence(word_sentence, pos_sentence):
    result = []

    assert len(word_sentence) == len(pos_sentence)

    for word, pos in zip(word_sentence, pos_sentence):
        result.append(f"{word}({pos})")

    return result


def serve(max_workers = 10, port = 80):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    ckiptagger_pb2_grpc.add_TaggerServicer_to_server(Tagger(), server)
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()

    if not os.path.exists("./data/model_ws"):
        logging.info(msg="Downloading data model...")
        data_utils.download_data("./")

    max_workers = int(os.getenv('MAX_WORKERS', 10))
    port = int(os.getenv('PORT', 80))
    serve(max_workers, port)
