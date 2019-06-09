# -*— coding: utf-8 -*-
import re

import jieba
import jieba.analyse
import jieba.posseg
import synonyms


class WordbaseGenerator:
    keywords_allow_pos = ('a', 'an', 'n', 'ns', 'nr', 'nrt', 'nz', 'nt', 'vn')
    detailwords_allow_pos = ('an', 'n', 'ns', 'nr', 'nrt', 'nz', 'nt', 'vn', 'm', 's')
    sentence_separator = '。|？|！'

    @classmethod
    def generate_wordbase(cls, content):
        """
        针对文本 content 生成关键词
        """
        if len(content) == 0:
            return cls.__get_none_return()
        else:
            sentences = re.split(WordbaseGenerator.sentence_separator, content)[:-1]
            if len(sentences) == 0:
                return cls.__get_none_return()
            else:
                key_sentence = sentences[0]
                # print(self.__segment_all(key_sentence))
                keywords = cls.__duplication_removal_single(cls.__get_keywords(sentence=key_sentence))
                # keywords = [synonyms.nearby(word)[0] if len(synonyms.nearby(word)[0]) > 0 else [word] for word in keywords]
                # print(keywords)
                detail_sentences = sentences[1:]
                detailwords = []
                for detail_sentence in detail_sentences:
                    temp = cls.__duplication_removal_single(cls.__get_detailwords(sentence=detail_sentence))
                    temp = cls.__duplication_removal_merge(keywords, temp)
                    for words in detailwords:
                        temp = cls.__duplication_removal_merge(words, temp)
                    detailwords.append(temp)
                    # detailwords.append(
                    #     [synonyms.nearby(word)[0] if len(synonyms.nearby(word)[0]) > 0 else [word] for word in temp])
                wordbase = {
                    'keywords': keywords,
                    'detailwords': detailwords
                }
                return cls.__expand_synonyms(wordbase)

    @staticmethod
    def __get_none_return():
        return {
            'keywords': [[]],
            'detailwords': [[[]]]
        }

    @staticmethod
    def __get_keywords(sentence):
        x = jieba.analyse.extract_tags(sentence, topK=5, withWeight=False,
                                       allowPOS=WordbaseGenerator.keywords_allow_pos)
        return x

    @staticmethod
    def __get_detailwords(sentence):
        x = jieba.analyse.extract_tags(sentence, topK=5, withFlag=False,
                                       allowPOS=WordbaseGenerator.detailwords_allow_pos)
        return x

    @staticmethod
    def __duplication_removal_single(word_list):
        remove_index = []
        result = []
        length = len(word_list)
        for i in range(length):
            for j in range(i + 1, length):
                if word_list[i] in word_list[j]:
                    remove_index.append(i)
                elif word_list[j] in word_list[i]:
                    remove_index.append(j)
        for i in range(length):
            if i not in remove_index:
                result.append(word_list[i])
        return result

    @staticmethod
    def __duplication_removal_merge(word_list1, word_list2):
        return [word for word in word_list2 if word not in word_list1]

    @staticmethod
    def __segment_all(sentence):
        """
        打印分词词性
        """
        sentence_seged = jieba.posseg.cut(sentence.strip())
        string = ''
        for x in sentence_seged:
            string += '{}/{},'.format(x.word, x.flag)
        return string

    @staticmethod
    def __expand_synonyms(wordbase):
        """
        对 wordbase 进行同义词拓展
        """

        # expand keywords
        pre_keywords = wordbase.get('keywords')
        cur_keywords = [[]]
        if len(pre_keywords) > 0:
            cur_keywords = [synonyms.nearby(word)[0] if len(synonyms.nearby(word)[0]) > 0 else [word] for word in
                            pre_keywords]

        # expand detailwords
        pre_detailwords = wordbase.get('detailwords')
        cur_detailwords = []
        if len(pre_detailwords) == 0:
            cur_detailwords = [[[]]]
        else:
            for temp in pre_detailwords:
                cur_detailwords.append([synonyms.nearby(word)[0] if len(synonyms.nearby(word)[0]) > 0 else [word]
                                        for word in temp])

        # reset the wordbase
        wordbase['keywords'] = cur_keywords
        wordbase['detailwords'] = cur_detailwords
        return wordbase
