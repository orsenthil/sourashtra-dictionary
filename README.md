# https://dictionary.thinnal.org

This is Sourashtra-English, and Sourashtra-Tamil dictionary.

[Sourashtra language](https://en.wikipedia.org/wiki/Saurashtra_language), an offshoot of Sauraseni Prakrit, once spoken in the Saurashtra region of Gujarat, is now chiefly a spoken language in various places in Tamil Nadu and is mostly concentrated in Madurai, Thanjavur and Salem Districts. 

## Motivation 

When I first came across the article, [Alar: The making of an open source dictionary](https://zerodha.tech/blog/alar-the-making-of-an-open-source-dictionary/) by [Kailash Nadh](https://nadh.in/), introducing a Kannada dictionary in [Alar](https://alar.ink/) and a Malayalam Dictionary in [Olam](https://olam.in/), I was extremely interested in that undertaking.

It demonstrated a dictionary engine, [dictpress](https://github.com/knadh/dictpress), written in Go, utilizing a PostgreSQL database, introducing phonetic schemes and algorithms for Indic languages like Malayalam, [MLPhone](https://github.com/knadh/mlphone) and for Kannada, [KNPhone](https://github.com/knadh/knphone).

I was excited and I wanted to do it for the language I speak. Hence, this project.

## Corpus

In developing this dictionary corpus, I have referenced and incorporated lexical data from linguistic resources created by experts under the purview and collaboration with the Central Institute of Indian Languages. It was shared with me by experts who contributed to the corpus. 
The data, and review ensures that correct words and spelling is used for the words in the language.

### Technical Details

PostgreSQL database has full-text search capability implemented using a concept called TSVECTORS. In supported languages, words like "running", "runs" and "ran" can automatically be mapped to a term "run". It exists for about 16 languages including English, Tamil and Hindi.

It does not exist for Sourashtra, and instead of creating a phonetic scheme for the lipi, and since Sourashtra is primarily a spoken language, the TSVECTORS for Sourashtra search are programmatically populated to include Sourashtra words written in English, Tamil, Hindi in addition to Sourashtra. The variation in writing can be a challenge in searching too. Since speakers will assume the spelling as they think might be correct. This can be addressed if the motivated learner searches in related terms (like dov instead of dhov or simply god) and if required, the additional phonetic term can be contributed directly in the interface.

### Contribute

You can add / edit the words in the [words](https://github.com/orsenthil/sourashtra-dictionary/tree/main/words) directory. The words in [dictpress](https://github.com/orsenthil/sourashtra-dictionary/tree/main/dictpress) directory are auto-generated from files in the words directory, so do not edit those.
You can create a new file in the words and add as per the structure and format of the rest of the files in the words directory.

## Contact

Senthil Kumaran.

For any discussions related to this project, open a topic at https://thinnal.org
