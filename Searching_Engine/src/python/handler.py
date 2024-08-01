from tornado.web import RequestHandler
from static_data import *
from json import dumps
from string import ascii_letters


# load home
class home_page(RequestHandler):
    def get(self):
        return self.render(r"../HTML/home.html")


# frontend get a copy of possible urls for input suggestion
class Autocomplete(RequestHandler):
    def get(self):
        self.set_header("Content-Type", "application/json")
        # Return the indexed URLs as a JSON response
        self.write(dumps(indexed_urls))


# search for url
class search(RequestHandler):
    def post(self):
        search_results = []
        search_area: dict
        # area of searching
        search_area = self.request.arguments["search_area"][0].decode()
        # order of display results
        search_order = self.request.arguments["result_order"][0].decode()
        # keys of searching in this area
        search_keys = self.request.arguments["search_keywords"][0].decode().split(" ")
        # filter out unwanted characters
        for key in search_keys:
            key = "".join(
                filter(lambda x: x in (list(ascii_letters) + [" ", "&", "!"]), key)
            )
        # title for html return page
        searching_title = "<br>searching area: {}<br> keywords: {}".format(
            search_area,
            (
                self.request.arguments["search_keywords"][0]
                .decode()
                .replace("!", "NOT ")
                .replace("&", "AND ")
            ),
        )

        # no records in given area, no url for sure
        if search_area not in indexed_urls:
            return self.write(
                searching_result_page_html
                % (
                    searching_title,
                    "<h1>Sorry, No Matching Result Found for {}</h1>".format(
                        searching_title
                    ),
                )
            )

        # get urls in this area
        area_contents = indexed_urls[search_area]
        # if no key specified, return all urls in this area
        if search_keys == [""]:
            search_results = [area_contents[x] for x in area_contents]

        else:
            AND_keys = []
            OR_keys = []
            NOT_keys = []

            # categorize the keys
            for keyword in search_keys:
                if keyword.startswith("&"):
                    AND_keys.append(keyword[1:])
                    continue
                elif keyword.startswith("!"):
                    NOT_keys.append(keyword[1:])
                else:
                    OR_keys.append(keyword)

            # or
            first_filter = []
            # and
            second_filter = []
            # not
            third_filter = []

            # get all urls with this key in it keys_desc
            for or_key in OR_keys:
                for item in area_contents:
                    if or_key in area_contents[item][3]:
                        first_filter.append(area_contents[item])

            second_filter = first_filter

            # then filter the last result with and
            for and_key in AND_keys:
                for item in first_filter:
                    if and_key not in item[3]:
                        second_filter.remove(item)

            third_filter = second_filter

            # finally filter again with not
            for not_key in NOT_keys:
                for item in second_filter:
                    if not_key in item[3]:
                        third_filter.remove(item)

            # final result
            search_results = third_filter

        # if nothing left
        if len(search_results) == 0:
            return self.write(
                searching_result_page_html
                % (
                    searching_title,
                    "<h1>Sorry, No Matching Result Found for {}</h1>".format(
                        searching_title
                    ),
                )
            )

        else:
            # sort based on given order
            if search_order == "decending":
                search_results.sort(reverse=True, key=lambda x: x[3])
            elif search_order == "ascending":
                search_results.sort(reverse=False, key=lambda x: x[3])
            else:
                # the weight based ordering from prototype was removed,
                # but may re-enable in the future so still calculate weight and remove duplicate urls
                result_count = {}
                res_copy = []
                for item in search_results:
                    if item[0] not in result_count:
                        result_count[item[0]] = 1
                        res_copy.append(item)
                    else:
                        result_count[item[0]] += 1
                search_results = res_copy

        # create return page
        injection_text = "".join(
            [
                """
            <div class="result-item">
                <b><a href="{}">{}</a></b>
                <p>{}</p>
            </div>
            """.format(
                    result[0], result[0], result[1]
                )
                for result in search_results
            ]
        )
        # add number of results
        searching_title += "<br>{} results found".format(len(search_results))
        return self.write(
            searching_result_page_html % (searching_title, injection_text)
        )


# first working version, abandoned after rewritten the search and
# reconstruct the structure of urls index dict.
# the old version was just to test if search using indexing works (and it did).

# class search(RequestHandler):
#     def get(self):
#         self.send_error(503)

#     def post(self):

#         # list of all keywords
#         searching_keywords = self.request.arguments["search_keywords"][0].decode()
#         searching_title = searching_keywords
#         searching_keywords = searching_keywords.split(" ")

#         print(self.request.arguments)

#         # 0: OR
#         # 1: AND
#         # 2: MIXED: allowing mixture of AND&OR searching, use leading & to represent and, and ! to represent not
#         searching_criteria = {"OR": 0, "AND": 1, "MIXED": 2}[
#             self.request.arguments["search_mode"][0].decode()
#         ]

#         # 0: rank by association
#         # 1: rank by asscending
#         # 2: rank by decending
#         result_ordering = {"association": 0, "ascending": 1, "decending": 2}[
#             self.request.arguments["result_order"][0].decode()
#         ]


#         search_results = {}
#         ranked_resuls = []

#         # OR/AND search get results from the indexed urls

#         # OR search
#         if searching_criteria == 0:
#             # print("searching or")
#             for keyword in searching_keywords:
#                 if keyword in indexed_urls:
#                     for url_key in indexed_urls[keyword]:
#                         # new result
#                         if url_key not in search_results:
#                             search_results[url_key] = indexed_urls[keyword][url_key]
#                         # increase priority
#                         else:
#                             search_results[url_key][2] += 1
#         # AND search
#         elif searching_criteria == 1:
#             # print("searching and")
#             # fill result with first keyword, then filter out with other keys
#             first_keyword = 1
#             AND_search_results = {}
#             for keyword in searching_keywords:
#                 if first_keyword:
#                     # fill dictionary with results of first key
#                     if keyword in indexed_urls:
#                         for url_key in indexed_urls[keyword]:
#                             search_results[url_key] = indexed_urls[keyword][url_key]
#                     else:
#                         # first key has no result, AND return none
#                         return self.write(
#                             searching_result_page_html.format(
#                                 searching_title,
#                                 "<h1>Sorry, No Matching Result Found for {}</h1>".format(
#                                     searching_title
#                                 ),
#                             )
#                         )
#                 else:
#                     # filter out results with remaining keys
#                     # get all the search result remaining
#                     if keyword in indexed_urls:
#                         for url_key in indexed_urls[keyword]:
#                             AND_search_results[url_key] = indexed_urls[keyword][url_key]

#                     keys_to_remove = []
#                     # if a key from first run not in remining run, mark as to remove
#                     for url_key in search_results:
#                         if url_key not in AND_search_results:
#                             keys_to_remove.append(url_key)

#                     # remove urls
#                     for url_key in keys_to_remove:
#                         search_results.pop(url_key)

#                 # no longer the first key
#                 first_keyword = 0

#         # MIXED search mode
#         elif searching_criteria == 2:
#             # print("searching mix")
#             not_keywords = []
#             and_keywords = []

#             # get all the keys that not supposed to be in result
#             for keyword in searching_keywords:
#                 if keyword.startswith("!"):
#                     not_keywords.append(keyword[1:])

#             # remove NOT from regular search keys
#             for nk in not_keywords:
#                 searching_keywords.remove("!" + nk)

#             # get all the keys that supposed to be AND in result
#             for keyword in searching_keywords:
#                 if keyword.startswith("&"):
#                     and_keywords.append(keyword[1:])

#             # remove AND from regular search keys
#             for ak in and_keywords:
#                 searching_keywords.remove("&" + ak)

#             # do the OR search first, then remove AND and NOT
#             for keyword in searching_keywords:
#                 if keyword in indexed_urls:
#                     for url_key in indexed_urls[keyword]:
#                         # new result
#                         if url_key not in search_results:
#                             search_results[url_key] = indexed_urls[keyword][url_key]
#                         # increase priority
#                         else:
#                             search_results[url_key][2] += 1

#             AND_search_result = {}
#             NOT_search_result = {}

#             # get AND results
#             for keyword in and_keywords:
#                 if keyword in indexed_urls:
#                     for url_key in indexed_urls[keyword]:
#                         # new result
#                         if url_key not in AND_search_result:
#                             AND_search_result[url_key] = indexed_urls[keyword][url_key]
#                         # increase priority
#                         else:
#                             AND_search_result[url_key][2] += 1

#             # get NOT results
#             for keyword in not_keywords:
#                 if keyword in indexed_urls:
#                     for url_key in indexed_urls[keyword]:
#                         # new result
#                         if url_key not in NOT_search_result:
#                             NOT_search_result[url_key] = indexed_urls[keyword][url_key]
#                         # increase priority
#                         else:
#                             NOT_search_result[url_key][2] += 1

#             # print(search_results)
#             # print(NOT_search_result)
#             # print(AND_search_result)

#             keys_to_remove = []
#             # iterate through all the results, find those need to be removed
#             for url_key in search_results:
#                 if (url_key in NOT_search_result) or (url_key not in AND_search_result):
#                     keys_to_remove.append(url_key)

#             # remove urls
#             for url_key in keys_to_remove:
#                 search_results.pop(url_key)

#         # unknown searching criteria, might be a fake request
#         else:
#             # print(searching_criteria)
#             # I am a teapot
#             self.send_error(418)

#         # no result, return no result page
#         if len(search_results) == 0:
#             return self.write(
#                 searching_result_page_html.format(
#                     searching_title,
#                     "<h1>Sorry, No Matching Result Found for {}</h1>".format(
#                         searching_title
#                     ),
#                 )
#             )

#         # insert results
#         for url_key in search_results:
#             try:
#                 ranked_resuls.append(
#                     [
#                         url_key,
#                         search_results[url_key][0],
#                         search_results[url_key][1],
#                         search_results[url_key][2],
#                     ]
#                 )
#             except Exception as e:
#                 continue

#         # sort by priority based on appearance in keys
#         ranked_resuls.sort(key=lambda x: x[3], reverse=True)

#         # create a search result ranked by priority
#         injection_text = ""
#         for result in ranked_resuls:
#             injection_text += """
#             <b><a href="{}">{}</a></b>
#             <p style="font-size: small;display: flex;">{}</p>
#             <p>{}</p>
#             <br>
#             """.format(
#                 result[1], result[0], result[1], result[2]
#             )
#             # print(result)

#         # inject into html
#         return self.write(
#             searching_result_page_html.format(searching_title, injection_text)
#         )
