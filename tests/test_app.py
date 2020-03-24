import unittest
import nloo.application as app


class NlooTestCase(unittest.TestCase):

    def test_inverted_dict(self):

        syn_dict = {"москва": ["мск", "msk"],
                    "санкт-петербург": ["питер", "петроград"]}

        correct_inverted_dict = {
            "мск": "москва",
            "msk": "москва",
            "питер": "санкт-петербург",
            "петроград": "санкт-петербург"
        }

        inverted_dict = app._synonyms_inverted_dict(syn_dict)

        self.assertDictEqual(correct_inverted_dict, inverted_dict)

    def test_synonyms_list(self):
        syn_dict = {"москва": ["мск", "msk"],
                    "санкт-петербург": ["питер", "петроград"]}

        correct_synonyms_list = [
            "мск",
            "msk",
            "питер",
            "петроград"
        ]

        synonyms_list = app._synonyms_list(syn_dict)

        self.assertListEqual(correct_synonyms_list, synonyms_list)

    def test_detect_city(self):

        all_cities = ["москва", "санкт-петербург"]
        syn_dict = {"москва": ["мск", "msk"],
                    "санкт-петербург": ["питер", "петроград"]}
        syn_list = app._synonyms_list(syn_dict)
        syn_inverted_dict = app._synonyms_inverted_dict(syn_dict)

        self.assertEqual(("москва", 100), app.detect_city("мск", 80, all_cities, syn_list, syn_inverted_dict))
        self.assertEqual(("москва", 100), app.detect_city("москва", 80, all_cities, syn_list, syn_inverted_dict))

        self.assertEqual(("санкт-петербург", 100), app.detect_city("питер", 80, all_cities, syn_list, syn_inverted_dict))
        self.assertEqual(("санкт-петербург", 90), app.detect_city("петер", 80, all_cities, syn_list, syn_inverted_dict))
        self.assertEqual(("санкт-петербург", 30), app.detect_city("хей", 0, all_cities, syn_list, syn_inverted_dict))

        self.assertEqual(None, app.detect_city("хей", 80, all_cities, syn_list, syn_inverted_dict))


if __name__ == '__main__':
    unittest.main()
