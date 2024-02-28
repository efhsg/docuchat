from components.chunker.fixed_length_chunker import FixedLengthChunker
from components.chunker.fixed_length_overlap_chunker import FixedLengthOverLapChunker


class ChunkerConfig:

    @property
    def chunker_options(self):
        return {
            "Fixed-Length": {
                "class": FixedLengthChunker,
                "params": {
                    "chunk_size": {
                        "label": "Chunk size",
                        "type": "number",
                        "min_value": 1,
                        "default": 1000,
                    },
                },
            },
            "Fixed-Length Overlap": {
                "class": FixedLengthOverLapChunker,
                "params": {
                    "chunk_size": {
                        "label": "Chunk size",
                        "type": "number",
                        "min_value": 1,
                        "default": 1000,
                    },
                    "overlap": {
                        "label": "Overlap size",
                        "type": "number",
                        "min_value": 0,
                        "default": 100,
                    },
                },
            },
            # "Some-Other-Method": {
            #     "class": SomeOtherChunker,
            #     "params": {
            #         "option": {
            #             "label": "Option",
            #             "type": "select",
            #             "options": ["Option 1", "Option 2"],
            #             "default": "Option 1",
            #         },
            #         "flag": {
            #             "label": "Enable Feature",
            #             "type": "checkbox",
            #             "default": False,
            #         },
            #     },
            # },
        }
