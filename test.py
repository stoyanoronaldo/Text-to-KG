from llamaapi import LlamaAPI
import requests

llama = LlamaAPI("LL-oZZ3DbV8EBPzVAdh7ylv5pQP3y0ryH77l7x50ELwEzDymcHuVOA3BnhH66HdFIZh")


api_request_json = {
                        "model": "llama3-70b",
                        "max_tokens": 5000,
                        "messages": [
                            {"role": "system", "content": f"For the given text provide all concepts and relations between them in turtle format. Use Rdfs schema, XML schema, schema.org. In addition for concepts use example.org."},
                            {"role": "user", "content": f"Star Wars is an American epic space opera media franchise created by George Lucas, which began with the eponymous 1977 film[a] and quickly became a worldwide pop culture phenomenon. The franchise has been expanded into various films and other media, including television series, video games, novels, comic books, theme park attractions, and themed areas, comprising an all-encompassing fictional universe.[b] Star Wars is one of the highest-grossing media franchises of all time. The original 1977 film, retroactively subtitled Episode IV: A New Hope, was followed by the sequels Episode V: The Empire Strikes Back (1980) and Episode VI: Return of the Jedi (1983), forming the original Star Wars trilogy. Lucas later returned to the series to write and direct a prequel trilogy, consisting of Episode I: The Phantom Menace (1999), Episode II: Attack of the Clones (2002), and Episode III: Revenge of the Sith (2005). In 2012, Lucas sold his production company to Disney, relinquishing his ownership of the franchise. This led to a sequel trilogy, consisting of Episode VII: The Force Awakens (2015), Episode VIII: The Last Jedi (2017), and Episode IX: The Rise of Skywalker (2019)."},
                        ]
                    }
response = None
try:
    response = llama.run(api_request_json)
    response.raise_for_status()
    answer_content = response.json()["choices"][0]["message"]["content"]
    print(answer_content)
except requests.exceptions.JSONDecodeError as e:
    print(f"Error: {e}")
    print(response.text)
