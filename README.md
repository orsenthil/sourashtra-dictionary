# https://dictionary.thinnal.org

[Sourashtra language](https://en.wikipedia.org/wiki/Saurashtra_language), an offshoot of Shauraseni Prakrit, once spoken in the Saurashtra region of Gujarat, is now chiefly a spoken language in various places of Tamil Nadu and are mostly concentrated in Madurai, Thanjavur and Salem Districts.

## Story

When I first came across the article, [Alar: The making of an open source dictionary](https://zerodha.tech/blog/alar-the-making-of-an-open-source-dictionary/) by [Kailash Nadh](https://nadh.in/), introducing a Kannada dictionary in [Alar](https://alar.ink/) and a Malayalam Dictionary in [Olam](https://olam.in/), demonstrating dictionary engine based out of postgres database called [dictpress](https://github.com/knadh/dictpress), and introducing phonetic scheme and algorithms for Indic languages like Malayalam in [MLPhone](https://github.com/knadh/mlphone) and for Kannada in [KNPhone](https://github.com/knadh/knphone), I was excited and I wanted to do it for the language that I speak. Hence, this project.


In developing this dictionary corpus, I have referenced and incorporated lexical data from linguistic resources made by experts
under the purview and collaboration with the Central Institute of Indian Languages. I had been shared those resources by experts who contributed to the corpus. The license of the corpus is in public domain. Sourashtra itself is an ancient language and preservation of words is lost upon the community.

## Technical Details

Postgres database has full-text search capability implemented using a a concept called TSVECTORS. In supported languages, words like "running", "runs" and "ran" can automatically be mapped to a term "run". It exists for about 16 languages including English, Tamil and Hindi.

It does not exist for Sourashtra, and instead of creating phonetic scheme for the lipi, and since Sourashtra is primarily a spoken language, 
the TSVECTORS for Sourashtra search are programatically populated to include Sourashtra words written in English, Tamil, Hindi in addition to Sourashtra. The variation is writing can be challenge in searching too. Since speakers will assume the spelling as they think might be correct. This can be addressed if the motivated learner searches in related terms (like dov instead of dhov or simply god) and if required, the additional phonetic term can be suggested directly in the interface.


## Contact

For any dicussions related to this project, feel free to dicuss at https://thinnal.org