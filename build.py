#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default

if __name__ == "__main__":

    builder = build_template_default.get_builder(pure_c=False)

    # Todo: re-enable shared builds when issue resolved
    # github issue: https://github.com/google/protobuf/issues/2502
    builder.items = filter(lambda build: build.options["protobuf:shared"] == False, builder.items)

    builder.run()
